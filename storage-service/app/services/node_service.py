from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from ..models import StorageNode, FileChunk, NodeStatus
from ..schemas import NodeResponse, NodeHealthResponse, SystemOverview, NodeStatistics
from ..storage_client import storage_client


class NodeService:
    """Service for storage node management"""
    
    @staticmethod
    def create_node(
        db: Session,
        node_id: str,
        host: str,
        port: int,
        capacity_bytes: int = 5 * 1024 * 1024 * 1024
    ) -> StorageNode:
        """Register a new storage node"""
        # Check if node already exists
        existing = db.query(StorageNode).filter(StorageNode.node_id == node_id).first()
        if existing:
            raise HTTPException(status_code=400, detail="Node already exists")
        
        node = StorageNode(
            node_id=node_id,
            host=host,
            port=port,
            capacity_bytes=capacity_bytes,
            status=NodeStatus.ONLINE
        )
        db.add(node)
        db.commit()
        db.refresh(node)
        return node
    
    @staticmethod
    def get_all_nodes(db: Session) -> List[NodeResponse]:
        """Get all storage nodes"""
        nodes = db.query(StorageNode).all()
        return [NodeResponse.model_validate(n) for n in nodes]
    
    @staticmethod
    def get_available_nodes(db: Session) -> List[NodeResponse]:
        """Get available (online) storage nodes for file operations"""
        nodes = db.query(StorageNode).filter(
            StorageNode.status == NodeStatus.ONLINE
        ).all()
        return [NodeResponse.model_validate(n) for n in nodes]
    
    @staticmethod
    def get_node(db: Session, node_id: str) -> StorageNode:
        """Get a specific node"""
        node = db.query(StorageNode).filter(StorageNode.node_id == node_id).first()
        if not node:
            raise HTTPException(status_code=404, detail="Node not found")
        return node
    
    @staticmethod
    async def check_node_health(db: Session, node_id: str) -> NodeHealthResponse:
        """Check health of a specific node"""
        node = NodeService.get_node(db, node_id)
        
        # Query node via gRPC
        health = await storage_client.get_node_health(node.host, node.port)
        
        # Update node status
        if health["status"] == "online":
            node.status = NodeStatus.ONLINE
            node.last_heartbeat = datetime.utcnow()
        else:
            node.status = NodeStatus.OFFLINE
        
        db.commit()
        
        available_bytes = node.capacity_bytes - node.used_bytes
        utilization = (node.used_bytes / node.capacity_bytes * 100) if node.capacity_bytes > 0 else 0
        
        return NodeHealthResponse(
            node_id=node.node_id,
            status=node.status,
            capacity_bytes=node.capacity_bytes,
            used_bytes=node.used_bytes,
            available_bytes=available_bytes,
            utilization_percent=round(utilization, 2)
        )
    
    @staticmethod
    async def check_all_nodes_health(db: Session) -> List[NodeHealthResponse]:
        """Check health of all nodes"""
        nodes = db.query(StorageNode).all()
        health_reports = []
        
        for node in nodes:
            health = await NodeService.check_node_health(db, node.node_id)
            health_reports.append(health)
        
        return health_reports
    
    @staticmethod
    def delete_node(db: Session, node_id: str) -> bool:
        """Delete a storage node (admin only)"""
        node = NodeService.get_node(db, node_id)
        
        # Check if node has chunks
        chunk_count = db.query(func.count(FileChunk.id)).filter(
            FileChunk.node_id == node.id
        ).scalar()
        
        if chunk_count > 0:
            raise HTTPException(
                status_code=400,
                detail=f"Cannot delete node with {chunk_count} chunks. Migrate data first."
            )
        
        db.delete(node)
        db.commit()
        return True
    
    @staticmethod
    def get_system_overview(db: Session) -> SystemOverview:
        """Get system-wide storage overview"""
        nodes = db.query(StorageNode).all()
        
        total_nodes = len(nodes)
        online_nodes = sum(1 for n in nodes if n.status == NodeStatus.ONLINE)
        total_capacity = sum(n.capacity_bytes for n in nodes)
        total_used = sum(n.used_bytes for n in nodes)
        total_available = total_capacity - total_used
        utilization = (total_used / total_capacity * 100) if total_capacity > 0 else 0
        
        from ..models import File, User
        total_files = db.query(func.count(File.id)).scalar()
        total_users = db.query(func.count(User.id)).scalar()
        
        return SystemOverview(
            total_nodes=total_nodes,
            online_nodes=online_nodes,
            total_capacity_bytes=total_capacity,
            total_used_bytes=total_used,
            total_available_bytes=total_available,
            system_utilization_percent=round(utilization, 2),
            total_users=total_users,
            total_files=total_files
        )
    
    @staticmethod
    def get_node_statistics(db: Session, node_id: str) -> NodeStatistics:
        """Get detailed statistics for a node"""
        node = NodeService.get_node(db, node_id)
        
        # Get chunk statistics
        chunks = db.query(FileChunk).filter(FileChunk.node_id == node.id).all()
        chunk_count = len(chunks)
        file_count = len(set(c.file_id for c in chunks))
        avg_chunk_size = sum(c.chunk_size for c in chunks) / chunk_count if chunk_count > 0 else 0
        
        # Calculate uptime (time since last offline status)
        uptime_hours = (datetime.utcnow() - node.created_at).total_seconds() / 3600
        uptime_percent = 99.9  # Mock value - would track in production
        
        return NodeStatistics(
            node_id=node.node_id,
            status=node.status,
            capacity_bytes=node.capacity_bytes,
            used_bytes=node.used_bytes,
            file_count=file_count,
            chunk_count=chunk_count,
            avg_chunk_size=avg_chunk_size,
            uptime_percent=uptime_percent
        )
