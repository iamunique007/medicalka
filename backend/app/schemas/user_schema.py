import re

from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

class SRefreshTokenInput(BaseModel):
    refresh_token: str


class SAccessTokenResponse(BaseModel):
    access_token: str


class SUserUpdateInput(BaseModel):
    username: str | None = Field(None, min_length=3, max_length=32)
    full_name: str | None = Field(None, min_length=2, max_length=100)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str | None) -> str | None:
        if v is None:
            return v
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username faqat lotin harflari, raqamlar va '_' belgisidan iborat bo'lishi kerak!"
            )
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str | None) -> str | None:
        if v is None:
            return v
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned or not cleaned.isalpha():
            raise ValueError(
                "Full name faqat harflar, bo'sh joy va defisdan iborat bo'lishi kerak!"
            )
        return v


class SUserLoginInput(BaseModel):
    username_or_email: str = Field(..., description="Email or Username")
    password: str


class STokenResponse(BaseModel):
    access_token: str
    refresh_token: str


class SUserResponseOutput(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: EmailStr
    username: str
    full_name: str
    is_verified: bool

class SUserRegisterOutput(SUserResponseOutput):
    verification_token: str

class SUserRegisterInput(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=32)
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6)

    @field_validator("username")
    @classmethod
    def validate_username(cls, v: str) -> str:
        if not re.match(r"^[a-zA-Z0-9_]+$", v):
            raise ValueError(
                "Username faqat lotin harflari, raqamlar va '_' belgisidan iborat bo'lishi kerak!"
            )
        return v

    @field_validator("full_name")
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        cleaned = v.replace(" ", "").replace("-", "")
        if not cleaned or not cleaned.isalpha():
            raise ValueError(
                "Full name faqat harflar (lotin/kirill), bo'sh joy va defisdan iborat bo'lishi kerak!"
            )
        return v