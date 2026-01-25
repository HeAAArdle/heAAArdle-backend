# standard library
from typing import Annotated

# schemas
from pydantic import BaseModel, Field


class GetUserResponse(BaseModel):
    username: str
    token: str


class SignInRequest(BaseModel):
    username: str
    password: str


class SignInResponse(BaseModel):
    access_token: str
    token_type: str


class SignUpRequest(BaseModel):
    username: Annotated[str, Field(min_length=4, max_length=36)]
    password: Annotated[str, Field(min_length=8, max_length=72)]


class SignUpResponse(BaseModel):
    username: str
    token: str
