from fastapi import Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, List
from jose import JWTError, jwt
from datetime import datetime
from repositories.user_repository import get_user_by_email
from sqlalchemy.orm import Session
from database.database import get_db
from fastapi import Depends
import os
from config import settings

SECRET_KEY = settings.secret_key
ALGORITHM = settings.algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True, allowed_roles: Optional[List[str]] = None):
        super().__init__(auto_error=auto_error)
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, db: Session = Depends(get_db)) -> Optional[HTTPAuthorizationCredentials]:
        # Skip authentication for certain paths
        if request.url.path in ["/api/v1/auth/login", "/api/v1/auth/register", "/docs", "/openapi.json"]:
            return None

        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        
        if not credentials:
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authorization code."
                )
            return None

        if credentials.scheme != "Bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid authentication scheme."
                )
            return None

        if not await self._verify_jwt(credentials.credentials, db):
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Invalid token or expired token."
                )
            return None

        # Check role-based access if allowed_roles is specified
        if self.allowed_roles:
            token_data = self._decode_token(credentials.credentials)
            if not token_data or "role" not in token_data or token_data["role"] not in self.allowed_roles:
                if self.auto_error:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Insufficient permissions."
                    )
                return None

        return credentials

    async def _verify_jwt(self, token: str, db: Session) -> bool:
        try:
            payload = self._decode_token(token)
            if not payload:
                return False
            
            # Check if token is expired
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp) < datetime.utcnow():
                return False     
            
            # Check user email is in the database
            user_email = payload.get("sub")
            if not user_email:
                return False
                
            user = get_user_by_email(user_email)
            if not user:
                return False
            
            return True
        except Exception as e:
            print(f"Error verifying JWT: {str(e)}")
            return False

    def _decode_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None
        except Exception:
            return None 