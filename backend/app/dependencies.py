from app.db import get_db
from app.models import User
from app.config import SECRET_KEY, JWT_ALGORITHM
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import get_user_by_id
from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.security import decode_access_token

security = HTTPBearer(auto_error=False)

async def login_required(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    
    user_id = decode_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token.")
    
    user = await get_user_by_id(db, id=user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="User not found."
        )
    
    request.state.user = user

    return user


async def login_required_or_none(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User | None:
    if credentials is not None:
        user_id = decode_access_token(credentials.credentials)

        if user_id is not None:
            user = await get_user_by_id(db, id=user_id)

            if user is not None:
                request.state.user = user

                return user



    return None


async def verified_required_and_return_user(user: User = Depends(login_required)) -> User:
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu amal uchun akkountingiz tasdiqlangan bo'lishi kerak",
        )
    
    return user