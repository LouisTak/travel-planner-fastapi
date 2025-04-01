from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
import jwt
from config import settings
from fastapi import HTTPException, Depends, status
from typing import Annotated
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from repositories.user_repository import get_user_by_email
from fastapi.security import OAuth2PasswordBearer
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Token(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str
    
class TokenData(BaseModel):
    """Schema for token data."""
    user_email: str

class TokenPayload(BaseModel):
    """Schema for token payload."""
    sub: str
    exp: int
    iat: int
    nbf: int
    jti: str
    iss: str
    aud: str
    user_id: str

class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    refresh_token: str

def create_access_token(data: dict):
    to_encode = data.copy()
    # Calculate expiration time
    expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    # Add expiration time to payload
    to_encode.update({"exp": expire})
    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    # Calculate expiration time
    expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    # Add expiration time to payload
    to_encode.update({"exp": expire})
    # Encode the JWT
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        user_email: str = payload.get("sub")
        if user_email is None:
            raise credentials_exception
        token_data = TokenData(user_email=user_email)
    except InvalidTokenError:
        raise credentials_exception
    
    # Pass the db session to get_user_by_email
    user = get_user_by_email(token_data.user_email)
    if user is None:
        raise credentials_exception
    return user
