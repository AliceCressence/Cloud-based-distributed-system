from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import get_db
from ..auth import get_admin_user
from ..models import User, UserRole, StorageNode, File, FileChunk, NodeStatus
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


@router.get("/stats")
def get_system_stats(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive system statistics (admin only)"""
    
    # User stats
    total_users = db.query(func.count(User.id)).scalar()
    active_users = db.query(func.count(User.id)).filter(User.is_active == True).scalar()
    
    # Storage node stats
    total_nodes = db.query(func.count(StorageNode.id)).scalar()
    online_nodes = db.query(func.count(StorageNode.id)).filter(StorageNode.status == NodeStatus.ONLINE).scalar()
    
    total_capacity = db.query(func.sum(StorageNode.capacity_bytes)).scalar() or 0
    total_used = db.query(func.sum(StorageNode.used_bytes)).scalar() or 0
    
    # File stats
    total_files = db.query(func.count(File.id)).scalar()
    total_file_size = db.query(func.sum(File.original_size)).scalar() or 0
    
    # Chunk stats - this is the key for fault tolerance visibility
    total_chunks = db.query(func.count(FileChunk.id)).scalar()
    chunks_per_node = db.query(
        FileChunk.node_id,
        func.count(FileChunk.id).label('chunk_count')
    ).group_by(FileChunk.node_id).all()
    
    # Calculate average chunks per file
    avg_chunks_per_file = total_chunks / total_files if total_files > 0 else 0
    
    # Get chunk distribution
    chunk_distribution = {node_id: count for node_id, count in chunks_per_node}
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "inactive": total_users - active_users
        },
        "nodes": {
            "total": total_nodes,
            "online": online_nodes,
            "offline": total_nodes - online_nodes
        },
        "storage": {
            "total_capacity_bytes": total_capacity,
            "total_used_bytes": total_used,
            "utilization_percent": (total_used / total_capacity * 100) if total_capacity > 0 else 0
        },
        "files": {
            "total_files": total_files,
            "total_size_bytes": total_file_size
        },
        "chunks": {
            "total_chunks": total_chunks,
            "avg_chunks_per_file": round(avg_chunks_per_file, 2),
            "chunk_distribution": chunk_distribution,
            "replication_factor": "Distributed across multiple nodes for fault tolerance"
        }
    }
