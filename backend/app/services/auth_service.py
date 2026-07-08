from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db
from app.models import User

from app.schemas.user_schema import (
    SUserRegisterInput, SUserLoginInput, SUserUpdateInput
)

from app.repositories.user_repository import (
    is_user_exists,
    get_user_by_email_or_username,
    get_user_by_username,
    get_user_by_id,
)

from app.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    generate_auth_tokens,
    decode_refresh_token,
    create_email_verification_token,
    decode_email_verification_token,
)


class UserAlreadyExists(Exception): ...
class InvalidCredentials(Exception): ...
class InvalidEmailToken(Exception): ...
class UserNotFound(Exception): ...
class EmailAlreadyVerified(Exception): ...
class UsernameTaken(Exception): ...
class NoUpdateData(Exception): ...
class InvalidRefreshToken(Exception): ...


class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register(self, data: SUserRegisterInput) -> User:
        if await is_user_exists(self.db, email=data.email, username=data.username):
            raise UserAlreadyExists

        new_user = User(
            is_verified=False,
            email=data.email,
            username=data.username,
            full_name=data.full_name,
            password_hash=get_password_hash(data.password),
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)

        # token = create_email_verification_token(new_user.id)
        
        # # TODO: haqiqiy email jo'natish. Hozircha konsolga chiqaramiz:
        # print(f"[EMAIL] {new_user.email} -> http://localhost:8000/auth/verify-email?token={token}")

        # new_user.verification_token = "http://localhost:8000/auth/verify-email?token={token}"

        return new_user
    
    async def refresh(self, refresh_token: str) -> dict:
        user_id = decode_refresh_token(refresh_token)
        if user_id is None:
            raise InvalidRefreshToken

        user = await get_user_by_id(self.db, id=user_id)
        if user is None:
            raise InvalidRefreshToken

        return {"access_token": create_access_token(user.id)}

    async def login(self, data: SUserLoginInput) -> dict:
        user = await get_user_by_email_or_username(
            self.db,
            email=data.username_or_email,
            username=data.username_or_email,
        )
        if not user:
            raise InvalidCredentials
        if not verify_password(plain_password=data.password, hashed_password=user.password_hash):
            raise InvalidCredentials

        return generate_auth_tokens(user_id=user.id)

    async def verify_email(self, token: str) -> User:
        user_id = decode_email_verification_token(token)
        if user_id is None:
            raise InvalidEmailToken

        user = await get_user_by_id(self.db, id=user_id)
        if not user:
            raise UserNotFound
        if user.is_verified:
            raise EmailAlreadyVerified

        user.is_verified = True
        self.db.add(user)
        await self.db.commit()
        return user

    async def update_me(self, user: User, data: SUserUpdateInput) -> User:
        if data.username is not None and data.username != user.username:
            existing = await get_user_by_username(self.db, username=data.username)
            if existing is not None:
                raise UsernameTaken

        update_data = data.model_dump(exclude_unset=True)
        if not update_data:
            raise NoUpdateData

        for key, value in update_data.items():
            setattr(user, key, value)

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    return AuthService(db)