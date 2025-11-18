"""
Authentication service for Google OAuth and user management
"""
from datetime import datetime
from typing import Optional, Dict, Any
from google.oauth2 import id_token
from google.auth.transport import requests
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User, UserRole
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, decode_token


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def verify_google_token(self, id_token_str: str) -> Dict[str, Any]:
        """
        Verify Google ID token
        
        Args:
            id_token_str: Google ID token
            
        Returns:
            User info from Google
            
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Verify token with Google
            idinfo = id_token.verify_oauth2_token(
                id_token_str,
                requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )
            
            # Verify issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Invalid token issuer')
            
            return {
                'google_uid': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', '')
            }
        except Exception as e:
            raise ValueError(f"Invalid Google token: {str(e)}")
    
    async def get_or_create_user(self, google_user_info: Dict[str, Any]) -> User:
        """
        Get existing user or create new one from Google info
        
        Args:
            google_user_info: User info from Google
            
        Returns:
            User object
        """
        # Check if user exists
        stmt = select(User).where(User.google_uid == google_user_info['google_uid'])
        result = await self.db.execute(stmt)
        user = result.scalar_one_or_none()
        
        if user:
            # Update last login
            user.last_login_at = datetime.utcnow()
            # Update picture if changed
            if google_user_info.get('picture'):
                user.picture = google_user_info['picture']
            await self.db.commit()
            await self.db.refresh(user)
            return user
        
        # Create new user
        new_user = User(
            email=google_user_info['email'],
            name=google_user_info['name'],
            google_uid=google_user_info['google_uid'],
            picture=google_user_info.get('picture'),
            role=UserRole.STUDENT,  # Default role
            is_active=True,
            last_login_at=datetime.utcnow()
        )
        
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        
        return new_user
    
    async def authenticate(self, id_token_str: str, user_data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Authenticate user with Google token
        
        Args:
            id_token_str: Google ID token
            user_data: Optional user data from client
            
        Returns:
            Auth response with tokens and user info
        """
        # Verify Google token
        google_user_info = await self.verify_google_token(id_token_str)
        
        # Override with user_data if provided
        if user_data:
            google_user_info.update(user_data)
        
        # Get or create user
        user = await self.get_or_create_user(google_user_info)
        
        if not user.is_active:
            raise ValueError("User account is inactive")
        
        # Create JWT tokens
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "google_uid": user.google_uid
        }
        
        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user.to_dict()
        }
    
    async def refresh_access_token(self, refresh_token_str: str) -> Dict[str, Any]:
        """
        Refresh access token using refresh token
        
        Args:
            refresh_token_str: Refresh token
            
        Returns:
            New access token
        """
        try:
            payload = decode_token(refresh_token_str)
            
            if payload.get('type') != 'refresh':
                raise ValueError("Invalid token type")
            
            # Create new access token
            token_data = {
                "sub": payload['sub'],
                "email": payload['email'],
                "role": payload['role'],
                "google_uid": payload['google_uid']
            }
            
            access_token = create_access_token(token_data)
            
            return {
                "access_token": access_token,
                "token_type": "bearer"
            }
        except Exception as e:
            raise ValueError(f"Invalid refresh token: {str(e)}")
    
    async def get_current_user(self, token: str) -> User:
        """
        Get current user from JWT token
        
        Args:
            token: JWT access token
            
        Returns:
            User object
            
        Raises:
            ValueError: If token is invalid or user not found
        """
        try:
            payload = decode_token(token)
            user_id = payload.get('sub')
            
            if not user_id:
                raise ValueError("Invalid token payload")
            
            stmt = select(User).where(User.id == user_id)
            result = await self.db.execute(stmt)
            user = result.scalar_one_or_none()
            
            if not user:
                raise ValueError("User not found")
            
            if not user.is_active:
                raise ValueError("User is inactive")
            
            return user
        except Exception as e:
            raise ValueError(f"Authentication failed: {str(e)}")
