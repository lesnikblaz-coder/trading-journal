from pydantic import BaseModel, EmailStr


# TOKENS
class AccessTokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class TokenPair(BaseModel):
    access_token: str
    refresh_token: str


# USERS
class UserCredentials(BaseModel):
    email: EmailStr
    password: str
class Register(UserCredentials): ...
class Login(UserCredentials): ...