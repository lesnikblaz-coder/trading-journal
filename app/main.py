from fastapi import FastAPI, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.exceptions.handler import register_exception_handlers
from app.schemas import auth as auth_sc
from app import dependencies as dep


app = FastAPI()

register_exception_handlers(app)

# ---------- ROOT ----------
@app.get("/", include_in_schema=False)
async def root() -> dict[str, str]:
    return {"status": "TRUE"}


# ---------- AUTH ----------
@app.post("/auth/register", response_model=auth_sc.TokenResponse)
async def register(service: dep.AuthServiceDep, request: auth_sc.Register) -> auth_sc.TokenResponse:
    return await service.register(request.email, request.password)

@app.post("/auth/login", response_model=auth_sc.TokenResponse)
async def login(service: dep.AuthServiceDep, request: auth_sc.Login) -> auth_sc.TokenResponse:
    return await service.login(request.email, request.password)

@app.post("/auth/token", response_model=auth_sc.TokenResponse)
async def token(service: dep.AuthServiceDep, request: OAuth2PasswordRequestForm = Depends()):
    return await service.login(request.username, request.password)