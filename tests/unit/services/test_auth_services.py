import pytest

from uuid import UUID, uuid4
from unittest.mock import AsyncMock, patch
from datetime import datetime, timezone, timedelta

from app import enums
from app.database.models.user import User
from app.repositories.user import UserRepo
from app.repositories.refresh_token import RefreshTokenRepo
from app.services.auth import AuthService
from app.schemas.auth import TokenPair
from app.exceptions import custom as c
from app.database.models.refresh_token import RefreshToken


def _make_user() -> User:
    return User(
        id=uuid4(),
        email="test@example.com",
        hashed_pw="hashed-password",
        role=enums.UserRole.REGULAR
    )

def _mocked_user_and_refresh_repos() -> tuple[UserRepo, RefreshTokenRepo]:
    repo = AsyncMock(spec=UserRepo)
    refresh_repo = AsyncMock(spec=RefreshTokenRepo)

    return repo, refresh_repo

def _mock_issue_tokens(service: AuthService):
    mock = AsyncMock(
        return_value=TokenPair(
            access_token="access_token",
            refresh_token="refresh_token",
        )
    )
    service._issue_tokens = mock
    return mock

def _make_refresh_token(
        *,
        user_id: UUID,
        expires_at: datetime,
        revoked_at: datetime | None = None,
        token_hash: str = "hashed-token"
) -> RefreshToken:
    return RefreshToken(
        id=uuid4(),
        user_id=user_id,
        token_hash=token_hash,
        expires_at=expires_at,
        revoked_at=revoked_at
    )


async def test_register_success():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)
    user = _make_user()

    repo.get_by_email.return_value = None
    repo.create.return_value = user

    _mock_issue_tokens(service)

    with patch("app.services.auth.security.get_hash", return_value="hashed-password"):
        result = await service.register(
            "test@example.com",
            "hashed-password"
        )

    assert result.access_token == "access_token"
    assert result.refresh_token == "refresh_token"

    repo.get_by_email.assert_awaited_once_with(
        "test@example.com"
    )

    repo.create.assert_awaited_once()

async def test_register_duplicate_email():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)

    existing_user = _make_user()
    repo.get_by_email.return_value = existing_user

    with pytest.raises(c.DuplicateEmailError):
        await service.register(
            existing_user.email,
            "password123"
        )

    repo.get_by_email.assert_awaited_once_with(
        existing_user.email
    )

    repo.create.assert_not_awaited()

async def test_login_success():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)

    user = _make_user()
    repo.get_by_email.return_value = user

    _mock_issue_tokens(service)
    with patch("app.services.auth.security.verify_pw", return_value=True):
        result = await service.login(
            user.email,
            "password123"
        )

    assert result == TokenPair(
        access_token="access_token",
        refresh_token="refresh_token"
    )

    repo.get_by_email.assert_awaited_once_with(
        user.email
    )

async def test_login_invalid_email():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)

    user = _make_user()
    repo.get_by_email.return_value = None

    with pytest.raises(c.InvalidCredentialsError):
        await service.login(
            user.email,
            "password123"
        )

    repo.get_by_email.assert_awaited_once_with(
        user.email
    )

async def test_login_wrong_password():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)

    user = _make_user()
    repo.get_by_email.return_value = user

    with patch("app.services.auth.security.verify_pw", return_value=False):
        with pytest.raises(c.InvalidCredentialsError):
            await service.login(
                user.email,
                "wrong-password",
            )

async def test_decode_user_success():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)

    user = _make_user()
    repo.get_by_id.return_value = user

    with patch("app.services.auth.decode_access_token", return_value=user.id):
        result = await service.decode_user("access-token")

    assert result is user

    repo.get_by_id.assert_awaited_once_with(user.id)

async def test_refresh_success():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service =  AuthService(repo, refresh_repo)
    user = _make_user()

    stored_token = _make_refresh_token(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=10),
    )

    new_stored_token = _make_refresh_token(
        user_id=user.id,
        token_hash="new-hash",
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )

    refresh_repo.get_by_hash.return_value = stored_token
    refresh_repo.create.return_value = new_stored_token
    repo.get_by_id.return_value = user

    with patch(
        "app.services.auth.security.hash_refresh_token",
        return_value="hashed-token"
    ), patch(
        "app.services.auth.security.create_access_token",
        return_value="new-access-token"
    ), patch(
        "app.services.auth.security.create_refresh_token",
        return_value="new-refresh-token"
    ):
        result = await service.refresh("old-refresh-token")

    assert result == TokenPair(
        access_token="new-access-token",
        refresh_token="new-refresh-token"
    )

    refresh_repo.get_by_hash.assert_awaited_once_with("hashed-token")

    repo.get_by_id.assert_awaited_once_with(user.id)

    refresh_repo.revoke.assert_awaited_once_with(
        stored_token
    )

    refresh_repo.create.assert_awaited_once()

    assert stored_token.replaced_by_id == new_stored_token.id

async def test_refresh_invalid_token():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)

    refresh_repo.get_by_hash.return_value = None

    with patch(
        "app.services.auth.security.hash_refresh_token",
        return_value="hashed-token"
    ):
        with pytest.raises(c.InvalidTokenError):
            await service.refresh("bad-token")

async def test_refresh_expired_token():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)
    user = _make_user()

    stored_token = _make_refresh_token(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) - timedelta(days=1)
    )

    refresh_repo.get_by_hash.return_value = stored_token

    with pytest.raises(c.InvalidTokenError):
        await service.refresh("refresh-token")

    repo.get_by_id.assert_not_awaited()
    refresh_repo.revoke.assert_not_awaited()
    refresh_repo.create.assert_not_awaited()

async def test_refresh_revoked_token():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)
    user = _make_user()

    stored_token = _make_refresh_token(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=10),
        revoked_at=datetime.now(timezone.utc)
    )

    refresh_repo.get_by_hash.return_value = stored_token

    with pytest.raises(c.InvalidTokenError):
        await service.refresh("refresh-token")

    repo.get_by_id.assert_not_awaited()
    refresh_repo.revoke.assert_not_awaited()
    refresh_repo.create.assert_not_awaited()

async def test_refresh_invalid_user():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)
    user = _make_user()

    stored_token = _make_refresh_token(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=10),
    )

    refresh_repo.get_by_hash.return_value = stored_token
    repo.get_by_id.return_value = None

    with pytest.raises(c.UserNotFoundError):
        await service.refresh("refresh-token")

    repo.get_by_id.assert_awaited_once_with(
        user.id
    )
    refresh_repo.revoke.assert_not_awaited()
    refresh_repo.create.assert_not_awaited()

async def test_logout_revokes_token():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)
    user = _make_user()

    token = _make_refresh_token(
        user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=30)
    )

    refresh_repo.get_by_hash.return_value = token

    with patch(
        "app.services.auth.security.hash_refresh_token",
        return_value="hashed-token"
    ):
        await service.logout("refresh-token")

    refresh_repo.get_by_hash.assert_awaited_once_with(
        "hashed-token"
    )

    refresh_repo.revoke.assert_awaited_once_with(token)

async def test_logout_invalid_token_does_nothing():
    repo, refresh_repo = _mocked_user_and_refresh_repos()
    service = AuthService(repo, refresh_repo)

    refresh_repo.get_by_hash.return_value = None

    with patch(
        "app.services.auth.security.hash_refresh_token",
        return_value="hashed-token",
    ):
        await service.logout("refresh-token")

    refresh_repo.revoke.assert_not_awaited()