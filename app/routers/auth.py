from fastapi import APIRouter, Depends, status, Cookie, Response
from fastapi.security import OAuth2PasswordRequestForm

from app import dependencies as dep
from app.schemas import auth as auth_sc
from app.exceptions.custom import InvalidTokenError
from app.core.config import settings


router = APIRouter()


REFRESH_COOKIE_NAME = "refresh_cookie"

def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=REFRESH_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.ENVIRONMENT == "production", # = True -> in production
        samesite="lax",
        max_age=settings.REFRESH_COOKIE_EXPIRE_TIME
    )

def delete_refresh_cookie(response: Response) -> None:
    response.delete_cookie(
        key=REFRESH_COOKIE_NAME
    )


@router.post("/auth/register", response_model=auth_sc.AccessTokenResponse)
async def register(service: dep.AuthServiceDep, response: Response, request: auth_sc.Register) -> auth_sc.AccessTokenResponse:
    tokens = await service.register(request.email, request.password)

    set_refresh_cookie(response, tokens.refresh_token)

    return auth_sc.AccessTokenResponse(
        access_token=tokens.access_token
    )

@router.post("/auth/login", response_model=auth_sc.AccessTokenResponse)
async def login(service: dep.AuthServiceDep, response: Response, request: auth_sc.Login) -> auth_sc.AccessTokenResponse:
    tokens = await service.login(request.email, request.password)

    set_refresh_cookie(response, tokens.refresh_token)

    return auth_sc.AccessTokenResponse(
        access_token=tokens.access_token
    )

@router.post("/auth/token", response_model=auth_sc.AccessTokenResponse)
async def token(service: dep.AuthServiceDep, response: Response, request: OAuth2PasswordRequestForm = Depends()) -> auth_sc.AccessTokenResponse:
    tokens = await service.login(request.username, request.password)

    set_refresh_cookie(response, tokens.refresh_token)

    return auth_sc.AccessTokenResponse(
        access_token=tokens.access_token
    )

@router.post("/auth/refresh", response_model=auth_sc.AccessTokenResponse)
async def refresh(
        service: dep.AuthServiceDep,
        response: Response,
        refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME)
) -> auth_sc.AccessTokenResponse:
    if refresh_token is None:
        raise InvalidTokenError()

    tokens = await service.refresh(refresh_token)

    set_refresh_cookie(response, tokens.refresh_token)

    return auth_sc.AccessTokenResponse(
        access_token=tokens.access_token
    )

@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
        service: dep.AuthServiceDep,
        response: Response,
        refresh_token: str | None = Cookie(default=None, alias=REFRESH_COOKIE_NAME)
) -> None:
    if refresh_token is not None:
        await service.logout(refresh_token)

    delete_refresh_cookie(response)