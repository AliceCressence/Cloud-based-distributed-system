from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from ..models import User, File, UserRole
from ..schemas import UserResponse, UserQuotaInfo
from ..auth import get_password_hash, calculate_quota_bytes


class UserService:
    """Service for user management"""
    
    @staticmethod
    def create_user(
        db: Session,
        user_id: str,
        email: str,
        password: str,
        role: UserRole = UserRole.STUDENT_UNDERGRAD
    ) -> User:
        """Create a new user"""
        # Check if user already exists
        existing = db.query(User).filter(
            (User.user_id == user_id) | (User.email == email)
        ).first()
        
        if existing:
            raise HTTPException(status_code=400, detail="User already exists")
        
        # Calculate quota based on role
        quota = calculate_quota_bytes(role)
        
        # Hash password
        hashed_password = get_password_hash(password)
        
        user = User(
            user_id=user_id,
            email=email,
            password_hash=hashed_password,
            role=role,
            storage_quota_bytes=quota,
            storage_used_bytes=0,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> User:
        """Get user by user_id"""
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        """Get user by email"""
        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user
    
    @staticmethod
    def get_all_users(db: Session, skip: int = 0, limit: int = 100) -> List[UserResponse]:
        """Get all users (admin only)"""
        users = db.query(User).offset(skip).limit(limit).all()
        return [UserResponse.model_validate(u) for u in users]
    
    @staticmethod
    def update_user_quota(
        db: Session,
        user_id: str,
        new_quota_bytes: int
    ) -> User:
        """Update user storage quota (admin only)"""
        user = UserService.get_user_by_id(db, user_id)
        
        if new_quota_bytes < user.storage_used_bytes:
            raise HTTPException(
                status_code=400,
                detail="New quota cannot be less than current usage"
            )
        
        user.storage_quota_bytes = new_quota_bytes
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def get_user_quota_info(db: Session, user: User) -> UserQuotaInfo:
        """Get detailed quota information for a user"""
        file_count = db.query(func.count(File.id)).filter(
            File.user_id == user.id,
            File.status == "active"
        ).scalar()
        
        available = user.storage_quota_bytes - user.storage_used_bytes
        utilization = (user.storage_used_bytes / user.storage_quota_bytes * 100) if user.storage_quota_bytes > 0 else 0
        
        return UserQuotaInfo(
            user_id=user.user_id,
            email=user.email,
            role=user.role,
            storage_quota_bytes=user.storage_quota_bytes,
            storage_used_bytes=user.storage_used_bytes,
            available_bytes=available,
            utilization_percent=round(utilization, 2),
            file_count=file_count
        )
    
    @staticmethod
    def deactivate_user(db: Session, user_id: str) -> User:
        """Deactivate a user (admin only)"""
        user = UserService.get_user_by_id(db, user_id)
        user.is_active = False
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def activate_user(db: Session, user_id: str) -> User:
        """Activate a user (admin only)"""
        user = UserService.get_user_by_id(db, user_id)
        user.is_active = True
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def update_user_role(db: Session, user_id: str, new_role: UserRole) -> User:
        """Update user role and adjust quota accordingly"""
        user = UserService.get_user_by_id(db, user_id)
        
        # Update role
        user.role = new_role
        
        # Update quota based on new role
        new_quota = calculate_quota_bytes(new_role)
        if new_quota >= user.storage_used_bytes:
            user.storage_quota_bytes = new_quota
        else:
            raise HTTPException(
                status_code=400,
                detail="New role quota is less than current usage. Free up space first."
            )
        
        db.commit()
        db.refresh(user)
        return user
