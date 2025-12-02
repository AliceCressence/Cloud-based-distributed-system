from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..auth import get_admin_user, get_current_user
from ..models import User
from ..schemas import (
    NodeCreate, NodeResponse, NodeHealthResponse,
    SystemOverview, NodeStatistics
)
from ..services.node_service import NodeService

router = APIRouter(prefix="/nodes", tags=["Storage Nodes"])


@router.post("/", response_model=NodeResponse)
def create_node(
    node_data: NodeCreate,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Create a new storage node (admin only)"""
    node = NodeService.create_node(
        db=db,
        node_id=node_data.node_id,
        host=node_data.host,
        port=node_data.port,
        capacity_bytes=node_data.capacity_bytes
    )
    return NodeResponse.model_validate(node)


@router.get("/", response_model=List[NodeResponse])
def list_nodes(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """List all storage nodes (admin only)"""
    return NodeService.get_all_nodes(db)


@router.get("/available", response_model=List[NodeResponse])
def get_available_nodes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get available online storage nodes for file upload (authenticated users)"""
    return NodeService.get_available_nodes(db)


@router.get("/health", response_model=List[NodeHealthResponse])
async def check_all_nodes_health(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Check health of all storage nodes (admin only)"""
    return await NodeService.check_all_nodes_health(db)


@router.get("/overview", response_model=SystemOverview)
def get_system_overview(
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get system-wide storage overview"""
    return NodeService.get_system_overview(db)


@router.get("/{node_id}", response_model=NodeResponse)
def get_node(
    node_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get a specific storage node"""
    node = NodeService.get_node(db, node_id)
    return NodeResponse.model_validate(node)


@router.get("/{node_id}/health", response_model=NodeHealthResponse)
async def check_node_health(
    node_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Check health of a specific node"""
    return await NodeService.check_node_health(db, node_id)


@router.get("/{node_id}/statistics", response_model=NodeStatistics)
def get_node_statistics(
    node_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Get detailed statistics for a node"""
    return NodeService.get_node_statistics(db, node_id)


@router.delete("/{node_id}")
def delete_node(
    node_id: str,
    current_user: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """Delete a storage node (admin only)"""
    success = NodeService.delete_node(db, node_id)
    return {"success": success, "message": "Node deleted successfully"}
