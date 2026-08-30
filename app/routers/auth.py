from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app import dependencies as dep
from app.schemas import auth as auth_sc


router = APIRouter()


@router.post("/auth/register", response_model=auth_sc.TokenResponse)
async def register(service: dep.AuthServiceDep, request: auth_sc.Register) -> auth_sc.TokenResponse:
    return await service.register(request.email, request.password)

@router.post("/auth/login", response_model=auth_sc.TokenResponse)
async def login(service: dep.AuthServiceDep, request: auth_sc.Login) -> auth_sc.TokenResponse:
    return await service.login(request.email, request.password)

@router.post("/auth/token", response_model=auth_sc.TokenResponse)
async def token(service: dep.AuthServiceDep, request: OAuth2PasswordRequestForm = Depends()):
    return await service.login(request.username, request.password)