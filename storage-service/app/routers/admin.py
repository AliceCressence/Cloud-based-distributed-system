from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_admin_user
from ..models import User, UserRole
from ..schemas import UserResponse, UserQuotaInfo
from ..services.user_service import UserService

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
def list_all_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all users (admin only)"""
    return UserService.get_all_users(db, skip, limit)


@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific user (admin only)"""
    user = UserService.get_user_by_id(db, user_id)
    return UserResponse.model_validate(user)


@router.get("/users/{user_id}/quota", response_model=UserQuotaInfo)
def get_user_quota(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get user quota information (admin only)"""
    user = UserService.get_user_by_id(db, user_id)
    return UserService.get_user_quota_info(db, user)


@router.put("/users/{user_id}/quota")
def update_user_quota(
    user_id: str,
    new_quota_gb: float,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user storage quota (admin only)"""
    new_quota_bytes = int(new_quota_gb * 1024 * 1024 * 1024)
    user = UserService.update_user_quota(db, user_id, new_quota_bytes)
    return UserResponse.model_validate(user)


@router.put("/users/{user_id}/role")
def update_user_role(
    user_id: str,
    new_role: UserRole,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Update user role (admin only)"""
    user = UserService.update_user_role(db, user_id, new_role)
    return UserResponse.model_validate(user)


@router.post("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)"""
    user = UserService.deactivate_user(db, user_id)
    return {"success": True, "message": f"User {user.email} deactivated"}


@router.post("/users/{user_id}/activate")
def activate_user(
    user_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Activate a user (admin only)"""
    user = UserService.activate_user(db, user_id)
    return {"success": True, "message": f"User {user.email} activated"}
