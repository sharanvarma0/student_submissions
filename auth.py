import os
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from models import User, TokenData
from database import users_collection

# Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 scheme - updated for JSON login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def verify_password(hashed_password_input: str, stored_hashed_password: str) -> bool:
    """Compare hashed password from frontend with stored hashed password"""
    return hashed_password_input == stored_hashed_password


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_user_by_username(username: str) -> Optional[User]:
    """Get user by username (user_id or user_name)"""
    # Try to find by user_id first, then by user_name
    user_data = await users_collection.find_one({
        "$or": [
            {"user_id": username},
            {"user_name": username}
        ]
    })
    
    if user_data:
        # Convert ObjectId to string for Pydantic compatibility
        if "_id" in user_data:
            user_data["_id"] = str(user_data["_id"])
        return User(**user_data)
    return None


async def authenticate_user(username: str, hashed_password: str) -> Union[User, bool]:
    """Authenticate a user with username and hashed password"""
    user = await get_user_by_username(username)
    if not user:
        return False
    if not verify_password(hashed_password, user.hashed_password):
        return False
    return user


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(token_data.user_id)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get the current active user"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
