from datetime import datetime, timedelta
from typing import Optional
from pathlib import Path
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from .database import get_db
from .models import User
from .config import get_settings

settings = get_settings()
_JWT_PRIV = None
_JWT_PUB = None
if settings.algorithm.upper() == "RS256":
    if settings.jwt_private_key_path:
        try:
            _JWT_PRIV = Path(settings.jwt_private_key_path).read_text()
        except Exception:
            _JWT_PRIV = None
    if settings.jwt_public_key_path:
        try:
            _JWT_PUB = Path(settings.jwt_public_key_path).read_text()
        except Exception:
            _JWT_PUB = None

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    key = _JWT_PRIV if settings.algorithm.upper() == "RS256" and _JWT_PRIV else settings.secret_key
    encoded_jwt = jwt.encode(to_encode, key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        key = _JWT_PUB if settings.algorithm.upper() == "RS256" and _JWT_PUB else settings.secret_key
        payload = jwt.decode(token, key, algorithms=[settings.algorithm])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    payload = decode_token(token)
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user is active"""
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Ensure user has admin role"""
    from .models import UserRole
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def calculate_quota_bytes(role: str) -> int:
    """Calculate storage quota based on user role"""
    from .models import UserRole
    
    quota_map = {
        UserRole.STUDENT_UNDERGRAD: settings.default_student_quota_gb * 1024 * 1024 * 1024,
        UserRole.STUDENT_GRAD: settings.default_grad_quota_gb * 1024 * 1024 * 1024,
        UserRole.FACULTY: settings.default_faculty_quota_gb * 1024 * 1024 * 1024,
        UserRole.ADMIN: 100 * 1024 * 1024 * 1024,  # 100GB for admins
    }
    
    return quota_map.get(role, settings.default_student_quota_gb * 1024 * 1024 * 1024)
