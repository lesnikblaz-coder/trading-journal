import pytest

from uuid import uuid4
from unittest.mock import AsyncMock, patch

from app import enums
from app.database.models.user import User
from app.repositories.user import UserRepo
from app.repositories.refresh_token import RefreshTokenRepo
from app.services.auth import AuthService
from app.schemas.auth import TokenPair
from app.exceptions import custom as c


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