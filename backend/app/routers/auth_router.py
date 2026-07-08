from fastapi import APIRouter, Depends, HTTPException, status

from app.models import User
from app.dependencies import login_required

from app.schemas.user_schema import (
    SUserRegisterInput, SUserResponseOutput, SRefreshTokenInput,
    SUserLoginInput, STokenResponse, SUserUpdateInput, SAccessTokenResponse, SUserRegisterOutput
)

from app.services.auth_service import (
    AuthService,
    get_auth_service,
    UserAlreadyExists,
    InvalidCredentials,
    InvalidEmailToken,
    UserNotFound,
    EmailAlreadyVerified,
    UsernameTaken,
    NoUpdateData,
    InvalidRefreshToken
)

from app.security import create_email_verification_token

router = APIRouter(tags=["auth"])


@router.post("/auth/register", response_model=SUserRegisterOutput, status_code=status.HTTP_201_CREATED)
async def register(
    body: SUserRegisterInput,
    service: AuthService = Depends(get_auth_service),
):
    try:
        user = await service.register(body)

        token = create_email_verification_token(user.id)

        user.verification_token = f"http://localhost:8000/auth/verify-email?token={token}"

        return user
    
    except UserAlreadyExists:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "This email or username is already registered!")


@router.post("/auth/login", response_model=STokenResponse)
async def login(
    body: SUserLoginInput,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.login(body)
    except InvalidCredentials:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Foydalanuvchi nomi yoki parol xato")


@router.get("/auth/me", response_model=SUserResponseOutput)
async def me(user: User = Depends(login_required)):
    return user


@router.get("/auth/verify-email", response_model=SUserResponseOutput)
async def verify_email(
    token: str,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.verify_email(token)
    except InvalidEmailToken:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Token noto'g'ri yoki muddati o'tgan")
    except UserNotFound:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Foydalanuvchi topilmadi")
    except EmailAlreadyVerified:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Email allaqachon tasdiqlangan")

@router.post("/auth/refresh", response_model=SAccessTokenResponse)
async def refresh(
    body: SRefreshTokenInput,
    service: AuthService = Depends(get_auth_service),
):
    try:
        return await service.refresh(body.refresh_token)
    
    except InvalidRefreshToken:
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED,
            "Refresh token noto'g'ri yoki muddati o'tgan",
        )
    

@router.patch("/users/me", response_model=SUserResponseOutput)
async def update_me(
    body: SUserUpdateInput,
    service: AuthService = Depends(get_auth_service),
    user: User = Depends(login_required),
):
    try:
        return await service.update_me(user=user, data=body)
    except UsernameTaken:
        raise HTTPException(
            status.HTTP_409_CONFLICT,
            "Bu username allaqachon band. Iltimos, boshqa username tanlang.",
        )
    except NoUpdateData:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "No fields provided for update")