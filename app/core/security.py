import jwt

from pwdlib import PasswordHash
from fastapi.security import OAuth2PasswordBearer
from uuid import UUID
from datetime import datetime, timezone, timedelta

from app.core.config import settings
from app.exceptions.custom import InvalidTokenError


pw_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_hash(pw: str) -> str:
    return pw_hash.hash(pw)


def verify_pw(plain_pw: str, hashed_pw: str) -> bool:
    return pw_hash.verify(plain_pw, hashed_pw)


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    payload = {
        "sub": user_id,
        "exp": expire
    }

    return jwt.encode(
        payload=payload,
        key=settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            jwt=token,
            key=settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        return UUID(payload["sub"])

    except (jwt.InvalidTokenError, ValueError, KeyError):
        raise InvalidTokenError()