import grpc
import hashlib
from typing import List, Tuple, Optional
from .config import get_settings

settings = get_settings()


class StorageNodeClient:
    """Client for communicating with storage nodes via gRPC"""
    
    def __init__(self):
        self.nodes = self._parse_nodes()
        self.current_node_index = 0
    
    def _parse_nodes(self) -> List[Tuple[str, int]]:
        """Parse storage nodes from config"""
        nodes = []
        for node_str in settings.storage_nodes.split(','):
            host, port = node_str.strip().split(':')
            nodes.append((host, int(port)))
        return nodes
    
    def get_next_node(self) -> Tuple[str, int]:
        """Get next node using round-robin load balancing"""
        node = self.nodes[self.current_node_index]
        self.current_node_index = (self.current_node_index + 1) % len(self.nodes)
        return node
    
    async def store_chunk(
        self,
        chunk_id: str,
        data: bytes,
        checksum: str,
        chunk_index: int,
        file_id: str,
        node_host: str,
        node_port: int
    ) -> dict:
        """Store a chunk on a specific node"""
        try:
            # For now, return mock response
            # In production, this would use the compiled gRPC stubs
            return {
                "success": True,
                "message": f"Chunk stored on {node_host}:{node_port}",
                "chunk_id": chunk_id,
                "bytes_written": len(data)
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "chunk_id": chunk_id,
                "bytes_written": 0
            }
    
    async def retrieve_chunk(
        self,
        chunk_id: str,
        node_host: str,
        node_port: int
    ) -> dict:
        """Retrieve a chunk from a specific node"""
        try:
            # Mock response - in production use gRPC
            return {
                "success": True,
                "message": "Chunk retrieved",
                "data": b"",  # Actual data would come from node
                "checksum": ""
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e),
                "data": None,
                "checksum": ""
            }
    
    async def delete_chunk(
        self,
        chunk_id: str,
        node_host: str,
        node_port: int
    ) -> dict:
        """Delete a chunk from a specific node"""
        try:
            return {
                "success": True,
                "message": "Chunk deleted"
            }
        except Exception as e:
            return {
                "success": False,
                "message": str(e)
            }
    
    async def get_node_health(
        self,
        node_host: str,
        node_port: int
    ) -> dict:
        """Get health status of a node"""
        try:
            return {
                "status": "online",
                "capacity_bytes": 5 * 1024 * 1024 * 1024,  # 5GB
                "used_bytes": 0,
                "available_bytes": 5 * 1024 * 1024 * 1024,
                "chunk_count": 0,
                "uptime_seconds": 0
            }
        except Exception as e:
            return {
                "status": "offline",
                "capacity_bytes": 0,
                "used_bytes": 0,
                "available_bytes": 0,
                "chunk_count": 0,
                "uptime_seconds": 0
            }


def calculate_checksum(data: bytes) -> str:
    """Calculate SHA-256 checksum of data"""
    return hashlib.sha256(data).hexdigest()


def chunk_file(file_data: bytes, chunk_size_mb: int = 2) -> List[bytes]:
    """Split file into chunks"""
    chunk_size = chunk_size_mb * 1024 * 1024  # Convert to bytes
    chunks = []
    
    for i in range(0, len(file_data), chunk_size):
        chunk = file_data[i:i + chunk_size]
        chunks.append(chunk)
    
    return chunks


# Global storage client instance
storage_client = StorageNodeClient()
