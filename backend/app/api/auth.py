"""
Authentication API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.auth_service import AuthService


router = APIRouter()


class GoogleAuthRequest(BaseModel):
    """Google authentication request"""
    id_token: str
    user_data: dict = None


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str


class TokenResponse(BaseModel):
    """Token response"""
    access_token: str
    refresh_token: str = None
    token_type: str = "bearer"
    user: dict = None


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    request: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Authenticate with Google OAuth token
    
    - Verifies Google ID token
    - Creates/updates user in database
    - Returns JWT access and refresh tokens
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.authenticate(
            id_token_str=request.id_token,
            user_data=request.user_data
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token
    
    - Validates refresh token
    - Returns new access token
    """
    try:
        auth_service = AuthService(db)
        result = await auth_service.refresh_access_token(request.refresh_token)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.get("/me")
async def get_current_user_info(
    token: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user information from token
    
    - Validates JWT token
    - Returns user details
    """
    try:
        auth_service = AuthService(db)
        user = await auth_service.get_current_user(token)
        return user.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get user info: {str(e)}"
        )
