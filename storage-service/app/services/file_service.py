import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, UploadFile
from ..models import File, FileChunk, User, StorageNode, FileStatus, NodeStatus
from ..schemas import FileMetadata, FileListResponse, ChunkMetadata, FileChunkMap
from ..storage_client import storage_client, chunk_file, calculate_checksum
from ..config import get_settings
from ..queue import safe_publish_event

settings = get_settings()


class FileService:
    """Service for file operations"""
    
    @staticmethod
    async def upload_file(
        db: Session,
        user: User,
        file: UploadFile,
        course_id: Optional[str] = None,
        folder_path: str = "/"
    ) -> File:
        """Upload a file and distribute chunks across nodes"""
        
        # Read file data
        file_data = await file.read()
        file_size = len(file_data)
        
        # Check quota
        if user.storage_used_bytes + file_size > user.storage_quota_bytes:
            raise HTTPException(
                status_code=400,
                detail=f"Storage quota exceeded. Available: {user.storage_quota_bytes - user.storage_used_bytes} bytes"
            )
        
        # Calculate file checksum
        file_checksum = calculate_checksum(file_data)
        
        # Create file record
        file_id = str(uuid.uuid4())
        db_file = File(
            file_id=file_id,
            filename=file.filename,
            original_size=file_size,
            content_type=file.content_type,
            checksum=file_checksum,
            status=FileStatus.UPLOADING,
            user_id=user.id,
            course_id=course_id,
            folder_path=folder_path
        )
        db.add(db_file)
        db.flush()
        
        # Split into chunks
        chunks = chunk_file(file_data, settings.chunk_size_mb)
        
        # Get available nodes
        nodes = db.query(StorageNode).filter(
            StorageNode.status == NodeStatus.ONLINE
        ).all()
        
        if not nodes:
            raise HTTPException(status_code=503, detail="No storage nodes available")
        
        # Store each chunk
        for idx, chunk_data in enumerate(chunks):
            chunk_id = f"{file_id}-chunk-{idx}"
            chunk_checksum = calculate_checksum(chunk_data)
            
            # Select node by highest free capacity ratio (prefer least utilized)
            candidates = [n for n in nodes if (n.capacity_bytes - n.used_bytes) >= len(chunk_data)]
            if not candidates:
                raise HTTPException(status_code=503, detail="Insufficient storage capacity across nodes")
            node = min(candidates, key=lambda n: (n.used_bytes / n.capacity_bytes) if n.capacity_bytes else 1.0)
            
            # Store chunk on node
            result = await storage_client.store_chunk(
                chunk_id=chunk_id,
                data=chunk_data,
                checksum=chunk_checksum,
                chunk_index=idx,
                file_id=file_id,
                node_host=node.host,
                node_port=node.port
            )
            
            if result["success"]:
                # Create chunk record
                db_chunk = FileChunk(
                    chunk_id=chunk_id,
                    file_id=db_file.id,
                    node_id=node.id,
                    chunk_index=idx,
                    chunk_size=len(chunk_data),
                    checksum=chunk_checksum
                )
                db.add(db_chunk)
                
                # Update node usage
                node.used_bytes += len(chunk_data)
                
                # Replicate chunk if configured (choose next best candidate)
                if settings.replication_factor > 1:
                    replica_candidates = [
                        n for n in nodes
                        if n.id != node.id and (n.capacity_bytes - n.used_bytes) >= len(chunk_data)
                    ]
                    if replica_candidates:
                        replica_node = min(
                            replica_candidates,
                            key=lambda n: (n.used_bytes / n.capacity_bytes) if n.capacity_bytes else 1.0
                        )
                        replica_chunk_id = f"{chunk_id}-replica"
                        await storage_client.store_chunk(
                            chunk_id=replica_chunk_id,
                            data=chunk_data,
                            checksum=chunk_checksum,
                            chunk_index=idx,
                            file_id=file_id,
                            node_host=replica_node.host,
                            node_port=replica_node.port
                        )

                        # Create replica chunk record
                        replica_chunk = FileChunk(
                            chunk_id=replica_chunk_id,
                            file_id=db_file.id,
                            node_id=replica_node.id,
                            chunk_index=idx,
                            chunk_size=len(chunk_data),
                            checksum=chunk_checksum,
                            is_replica=True,
                            replica_of_chunk_id=chunk_id
                        )
                        db.add(replica_chunk)
                        replica_node.used_bytes += len(chunk_data)
        
        # Update file status
        db_file.status = FileStatus.ACTIVE
        
        # Update user storage usage
        user.storage_used_bytes += file_size
        
        db.commit()
        db.refresh(db_file)

        # Publish upload completion event (best-effort)
        try:
            safe_publish_event(
                queue_name="uploads",
                payload={
                    "id": str(uuid.uuid4()),
                    "type": "STORAGE_UPLOAD_COMPLETED",
                    "file_id": file_id,
                    "db_file_id": db_file.id,
                    "user_id": user.user_id,
                    "original_size": file_size,
                    "chunk_count": len(chunks),
                    "replication_factor": settings.replication_factor,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                },
            )
        except Exception:
            # Do not fail the upload if queue is unavailable
            pass

        return db_file
    
    @staticmethod
    def get_user_files(
        db: Session,
        user: User,
        course_id: Optional[str] = None,
        folder_path: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> FileListResponse:
        """Get files for a user"""
        query = db.query(File).filter(
            File.user_id == user.id,
            File.status == FileStatus.ACTIVE
        )
        
        if course_id:
            query = query.filter(File.course_id == course_id)
        
        if folder_path:
            query = query.filter(File.folder_path == folder_path)
        
        total = query.count()
        files = query.order_by(File.created_at.desc()).offset(skip).limit(limit).all()
        
        return FileListResponse(
            files=[FileMetadata.model_validate(f) for f in files],
            total=total,
            storage_used=user.storage_used_bytes,
            storage_quota=user.storage_quota_bytes
        )
    
    @staticmethod
    async def download_file(
        db: Session,
        file_id: str,
        user: User
    ) -> bytes:
        """Download a file by reassembling chunks"""
        db_file = db.query(File).filter(
            File.file_id == file_id,
            File.user_id == user.id,
            File.status == FileStatus.ACTIVE
        ).first()
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Get all chunks in order
        chunks = db.query(FileChunk).filter(
            FileChunk.file_id == db_file.id,
            FileChunk.is_replica == False
        ).order_by(FileChunk.chunk_index).all()
        
        # Retrieve each chunk
        file_data = bytearray()
        for chunk in chunks:
            node = chunk.node
            result = await storage_client.retrieve_chunk(
                chunk_id=chunk.chunk_id,
                node_host=node.host,
                node_port=node.port
            )
            
            if result["success"]:
                # In production, this would have actual data
                # For now, we'll create mock data
                file_data.extend(b"0" * chunk.chunk_size)
            else:
                # Try replica if primary fails
                replica = db.query(FileChunk).filter(
                    FileChunk.replica_of_chunk_id == chunk.chunk_id
                ).first()
                
                if replica:
                    replica_node = replica.node
                    replica_result = await storage_client.retrieve_chunk(
                        chunk_id=replica.chunk_id,
                        node_host=replica_node.host,
                        node_port=replica_node.port
                    )
                    if replica_result["success"]:
                        file_data.extend(b"0" * chunk.chunk_size)
        
        return bytes(file_data)
    
    @staticmethod
    def delete_file(
        db: Session,
        file_id: str,
        user: User
    ) -> bool:
        """Soft delete a file"""
        db_file = db.query(File).filter(
            File.file_id == file_id,
            File.user_id == user.id,
            File.status == FileStatus.ACTIVE
        ).first()
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        # Mark as deleted
        db_file.status = FileStatus.DELETED
        db_file.deleted_at = datetime.utcnow()
        
        # Update user storage
        user.storage_used_bytes -= db_file.original_size
        
        db.commit()
        return True
    
    @staticmethod
    def get_file_chunks(
        db: Session,
        file_id: str,
        user: User
    ) -> FileChunkMap:
        """Get chunk map for a file"""
        db_file = db.query(File).filter(
            File.file_id == file_id,
            File.user_id == user.id
        ).first()
        
        if not db_file:
            raise HTTPException(status_code=404, detail="File not found")
        
        chunks = db.query(FileChunk).join(StorageNode).filter(
            FileChunk.file_id == db_file.id,
            FileChunk.is_replica == False
        ).order_by(FileChunk.chunk_index).all()
        
        chunk_metadata = [
            ChunkMetadata(
                chunk_id=c.chunk_id,
                chunk_index=c.chunk_index,
                chunk_size=c.chunk_size,
                node_id=c.node.node_id,
                checksum=c.checksum
            )
            for c in chunks
        ]
        
        return FileChunkMap(
            file_id=file_id,
            total_chunks=len(chunk_metadata),
            chunks=chunk_metadata
        )
