import os
import hashlib
import json
from datetime import datetime
from typing import Dict, Optional


class VirtualDisk:
    """
    Virtual disk manager for storing file chunks
    Simulates a physical disk with capacity limits
    """
    
    def __init__(self, node_id: str, capacity_gb: int = 5, base_path: str = "./vdisks"):
        self.node_id = node_id
        self.capacity_bytes = capacity_gb * 1024 * 1024 * 1024  # Convert GB to bytes
        self.base_path = base_path
        self.disk_path = os.path.join(base_path, f"node{node_id}.vdisk")
        self.metadata_path = os.path.join(base_path, f"node{node_id}.metadata.json")
        
        # Ensure base directory exists
        os.makedirs(base_path, exist_ok=True)
        
        # Initialize or load metadata
        self.metadata = self._load_metadata()
        self.used_bytes = self._calculate_used_space()
    
    def _load_metadata(self) -> Dict:
        """Load metadata from disk or create new"""
        if os.path.exists(self.metadata_path):
            with open(self.metadata_path, 'r') as f:
                return json.load(f)
        return {
            "node_id": self.node_id,
            "chunks": {},
            "created_at": datetime.utcnow().isoformat(),
            "capacity_bytes": self.capacity_bytes
        }
    
    def _save_metadata(self):
        """Save metadata to disk"""
        with open(self.metadata_path, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _calculate_used_space(self) -> int:
        """Calculate total used space from metadata"""
        return sum(chunk["size"] for chunk in self.metadata["chunks"].values())
    
    def _get_chunk_path(self, chunk_id: str) -> str:
        """Get file path for a chunk"""
        chunk_dir = os.path.join(self.base_path, f"node{self.node_id}_chunks")
        os.makedirs(chunk_dir, exist_ok=True)
        return os.path.join(chunk_dir, f"{chunk_id}.chunk")
    
    def store_chunk(self, chunk_id: str, data: bytes, checksum: str, file_id: str, chunk_index: int) -> Dict:
        """Store a chunk on the virtual disk"""
        chunk_size = len(data)
        
        # Check if we have enough space
        if self.used_bytes + chunk_size > self.capacity_bytes:
            return {
                "success": False,
                "message": f"Insufficient space. Available: {self.capacity_bytes - self.used_bytes} bytes",
                "chunk_id": chunk_id,
                "bytes_written": 0
            }
        
        # Verify checksum
        calculated_checksum = hashlib.sha256(data).hexdigest()
        if calculated_checksum != checksum:
            return {
                "success": False,
                "message": "Checksum mismatch",
                "chunk_id": chunk_id,
                "bytes_written": 0
            }
        
        try:
            # Write chunk to disk
            chunk_path = self._get_chunk_path(chunk_id)
            with open(chunk_path, 'wb') as f:
                f.write(data)
            
            # Update metadata
            self.metadata["chunks"][chunk_id] = {
                "file_id": file_id,
                "chunk_index": chunk_index,
                "size": chunk_size,
                "checksum": checksum,
                "path": chunk_path,
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.used_bytes += chunk_size
            self._save_metadata()
            
            return {
                "success": True,
                "message": "Chunk stored successfully",
                "chunk_id": chunk_id,
                "bytes_written": chunk_size
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error storing chunk: {str(e)}",
                "chunk_id": chunk_id,
                "bytes_written": 0
            }
    
    def retrieve_chunk(self, chunk_id: str) -> Dict:
        """Retrieve a chunk from the virtual disk"""
        if chunk_id not in self.metadata["chunks"]:
            return {
                "success": False,
                "message": "Chunk not found",
                "data": None,
                "checksum": ""
            }
        
        try:
            chunk_info = self.metadata["chunks"][chunk_id]
            chunk_path = chunk_info["path"]
            
            if not os.path.exists(chunk_path):
                return {
                    "success": False,
                    "message": "Chunk file not found on disk",
                    "data": None,
                    "checksum": ""
                }
            
            with open(chunk_path, 'rb') as f:
                data = f.read()
            
            return {
                "success": True,
                "message": "Chunk retrieved successfully",
                "data": data,
                "checksum": chunk_info["checksum"]
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error retrieving chunk: {str(e)}",
                "data": None,
                "checksum": ""
            }
    
    def delete_chunk(self, chunk_id: str) -> Dict:
        """Delete a chunk from the virtual disk"""
        if chunk_id not in self.metadata["chunks"]:
            return {
                "success": False,
                "message": "Chunk not found"
            }
        
        try:
            chunk_info = self.metadata["chunks"][chunk_id]
            chunk_path = chunk_info["path"]
            chunk_size = chunk_info["size"]
            
            # Delete file if it exists
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
            
            # Remove from metadata
            del self.metadata["chunks"][chunk_id]
            self.used_bytes -= chunk_size
            self._save_metadata()
            
            return {
                "success": True,
                "message": "Chunk deleted successfully"
            }
        
        except Exception as e:
            return {
                "success": False,
                "message": f"Error deleting chunk: {str(e)}"
            }
    
    def get_health(self) -> Dict:
        """Get health status of the virtual disk"""
        return {
            "status": "online",
            "capacity_bytes": self.capacity_bytes,
            "used_bytes": self.used_bytes,
            "available_bytes": self.capacity_bytes - self.used_bytes,
            "chunk_count": len(self.metadata["chunks"]),
            "uptime_seconds": 0  # Would track in production
        }
    
    def list_chunks(self, page: int = 1, page_size: int = 50) -> Dict:
        """List all chunks with pagination"""
        chunks = list(self.metadata["chunks"].items())
        total_count = len(chunks)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        page_chunks = chunks[start_idx:end_idx]
        
        chunk_list = [
            {
                "chunk_id": chunk_id,
                "file_id": info["file_id"],
                "size_bytes": info["size"],
                "checksum": info["checksum"],
                "created_timestamp": info["created_at"]
            }
            for chunk_id, info in page_chunks
        ]
        
        return {
            "chunks": chunk_list,
            "total_count": total_count
        }
