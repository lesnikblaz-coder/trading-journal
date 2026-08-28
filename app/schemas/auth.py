from pydantic import BaseModel, EmailStr


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"

class UserCredentials(BaseModel):
    email: EmailStr
    password: str

class Register(UserCredentials): ...
class Login(UserCredentials): ...