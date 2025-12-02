import time
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Union
from enum import Enum, auto
import hashlib
import socket
import json
import threading

class TransferStatus(Enum):
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()

@dataclass
class FileChunk:
    chunk_id: int
    size: int  # in bytes
    checksum: str
    status: TransferStatus = TransferStatus.PENDING
    stored_node: Optional[str] = None

    def to_dict(self):
        return {
            "chunk_id": self.chunk_id,
            "size": self.size,
            "checksum": self.checksum,
            "status": self.status.name,
            "stored_node": self.stored_node
        }

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(
            chunk_id=d["chunk_id"],
            size=d["size"],
            checksum=d["checksum"],
            status=TransferStatus[d["status"]],
            stored_node=d["stored_node"]
        )

@dataclass
class FileTransfer:
    file_id: str
    file_name: str
    total_size: int  # in bytes
    chunks: List[FileChunk]
    status: TransferStatus = TransferStatus.PENDING
    created_at: float = time.time()
    completed_at: Optional[float] = None

    def to_dict(self):
        return {
            "file_id": self.file_id,
            "file_name": self.file_name,
            "total_size": self.total_size,
            "chunks": [c.to_dict() for c in self.chunks],
            "status": self.status.name,
            "created_at": self.created_at,
            "completed_at": self.completed_at
        }

    @classmethod
    def from_dict(cls, d: Dict):
        return cls(
            file_id=d["file_id"],
            file_name=d["file_name"],
            total_size=d["total_size"],
            chunks=[FileChunk.from_dict(c) for c in d["chunks"]],
            status=TransferStatus[d["status"]],
            created_at=d["created_at"],
            completed_at=d["completed_at"]
        )

class StorageVirtualNode:
    def __init__(
        self,
        node_id: str,
        cpu_capacity: int,  # in vCPUs
        memory_capacity: int,  # in GB
        storage_capacity: int,  # in GB
        bandwidth: int  # in Mbps
    ):
        self.node_id = node_id
        self.cpu_capacity = cpu_capacity
        self.memory_capacity = memory_capacity
        self.total_storage = storage_capacity * 1024 * 1024 * 1024  # Convert GB to bytes
        self.bandwidth = bandwidth * 1000000  # Convert Mbps to bits per second
        
        # Current utilization
        self.used_storage = 0
        self.active_transfers: Dict[str, FileTransfer] = {}
        self.stored_files: Dict[str, FileTransfer] = {}
        self.network_utilization = 0  # Current bandwidth usage
        
        # Performance metrics
        self.total_requests_processed = 0
        self.total_data_transferred = 0  # in bytes
        self.failed_transfers = 0
        
        # Network connections (node_id: bandwidth_available in bps)
        self.connections: Dict[str, int] = {}
        
        # Distributed extensions
        self.ip_address: Optional[str] = None
        self.mac_address: Optional[str] = None
        self.listen_port: Optional[int] = None
        self.server_socket: Optional[socket.socket] = None

    def start_server(self, host='0.0.0.0', port=0):
        """Start the node's socket server for RPC calls."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.listen_port = self.server_socket.getsockname()[1]
        self.server_socket.listen(5)
        threading.Thread(target=self._server_loop, daemon=True).start()
        print(f"Node {self.node_id} listening on port {self.listen_port}")

    def _server_loop(self):
        while True:
            client, addr = self.server_socket.accept()
            threading.Thread(target=self._handle_client, args=(client,), daemon=True).start()

    def _handle_client(self, client):
        try:
            data = client.recv(4096).decode('utf-8')
            if not data:
                return
            msg = json.loads(data)
            resp = {"type": "ERROR", "message": "Unknown type"}
            if msg['type'] == 'CALL':
                method_name = msg.get('method')
                args = msg.get('args', [])
                if hasattr(self, method_name):
                    method = getattr(self, method_name)
                    result = method(*args)
                    if isinstance(result, FileTransfer):
                        result = result.to_dict()
                    resp = {"type": "RESULT", "data": result}
                else:
                    resp = {"type": "ERROR", "message": f"No method {method_name}"}
            elif msg['type'] == 'ADD_CONNECTION':
                data = msg['data']
                self.add_connection(data['other_node_id'], data['bandwidth'])
                resp = {"type": "OK"}
            client.send(json.dumps(resp).encode('utf-8'))
        except Exception as e:
            print(f"Error handling client in node {self.node_id}: {e}")
        finally:
            client.close()

    def add_connection(self, node_id: str, bandwidth: int):
        """Add a network connection to another node"""
        self.connections[node_id] = bandwidth * 1000000  # Mbps to bps

    def _calculate_chunk_size(self, file_size: int) -> int:
        """Determine optimal chunk size based on file size"""
        if file_size < 10 * 1024 * 1024:  # < 10MB
            return 512 * 1024  # 512KB chunks
        elif file_size < 100 * 1024 * 1024:  # < 100MB
            return 2 * 1024 * 1024  # 2MB chunks
        else:
            return 10 * 1024 * 1024  # 10MB chunks

    def _generate_chunks(self, file_id: str, file_size: int) -> List[FileChunk]:
        """Break file into chunks for transfer"""
        chunk_size = self._calculate_chunk_size(file_size)
        num_chunks = math.ceil(file_size / chunk_size)
        
        chunks = []
        for i in range(num_chunks):
            fake_checksum = hashlib.md5(f"{file_id}-{i}".encode()).hexdigest()
            actual_chunk_size = min(chunk_size, file_size - i * chunk_size)
            chunks.append(FileChunk(
                chunk_id=i,
                size=actual_chunk_size,
                checksum=fake_checksum
            ))
        
        return chunks

    def initiate_file_transfer(
        self,
        file_id: str,
        file_name: str,
        file_size: int,
        source_node: Optional[str] = None
    ) -> Optional[FileTransfer]:
        """Initiate a file storage request to this node"""
        if self.used_storage + file_size > self.total_storage:
            return None
        
        chunks = self._generate_chunks(file_id, file_size)
        transfer = FileTransfer(
            file_id=file_id,
            file_name=file_name,
            total_size=file_size,
            chunks=chunks
        )
        
        self.active_transfers[file_id] = transfer
        return transfer

    def process_chunk_transfer(
        self,
        file_id: str,
        chunk_id: int,
        source_node: str
    ) -> bool:
        """Process an incoming file chunk"""
        if file_id not in self.active_transfers:
            return False
        
        transfer = self.active_transfers[file_id]
        
        try:
            chunk = next(c for c in transfer.chunks if c.chunk_id == chunk_id)
        except StopIteration:
            return False
        
        chunk_size_bits = chunk.size * 8
        available_bandwidth = min(
            self.bandwidth - self.network_utilization,
            self.connections.get(source_node, 0)
        )
        
        if available_bandwidth <= 0:
            return False
        
        transfer_time = chunk_size_bits / available_bandwidth
        time.sleep(transfer_time)
        
        chunk.status = TransferStatus.COMPLETED
        chunk.stored_node = self.node_id
        
        self.network_utilization += available_bandwidth * 0.8
        self.total_data_transferred += chunk.size
        
        if all(c.status == TransferStatus.COMPLETED for c in transfer.chunks):
            transfer.status = TransferStatus.COMPLETED
            transfer.completed_at = time.time()
            self.used_storage += transfer.total_size
            self.stored_files[file_id] = transfer
            del self.active_transfers[file_id]
            self.total_requests_processed += 1
        
        return True

    def retrieve_file(
        self,
        file_id: str,
        destination_node: str
    ) -> Optional[FileTransfer]:
        """Initiate file retrieval to another node"""
        if file_id not in self.stored_files:
            return None
        
        file_transfer = self.stored_files[file_id]
        
        new_transfer = FileTransfer(
            file_id=f"retr-{file_id}-{time.time()}",
            file_name=file_transfer.file_name,
            total_size=file_transfer.total_size,
            chunks=[
                FileChunk(
                    chunk_id=c.chunk_id,
                    size=c.size,
                    checksum=c.checksum,
                    stored_node=destination_node
                )
                for c in file_transfer.chunks
            ]
        )
        
        return new_transfer

    def get_storage_utilization(self) -> Dict[str, Union[int, float]]:
        """Get current storage utilization metrics"""
        return {
            "used_bytes": self.used_storage,
            "total_bytes": self.total_storage,
            "utilization_percent": (self.used_storage / self.total_storage) * 100 if self.total_storage > 0 else 0,
            "files_stored": len(self.stored_files),
            "active_transfers": len(self.active_transfers)
        }

    def get_network_utilization(self) -> Dict[str, Union[int, float, List[str]]]:
        """Get current network utilization metrics"""
        total_bandwidth_bps = self.bandwidth
        return {
            "current_utilization_bps": self.network_utilization,
            "max_bandwidth_bps": total_bandwidth_bps,
            "utilization_percent": (self.network_utilization / total_bandwidth_bps) * 100 if total_bandwidth_bps > 0 else 0,
            "connections": list(self.connections.keys())
        }

    def get_performance_metrics(self) -> Dict[str, int]:
        """Get node performance metrics"""
        return {
            "total_requests_processed": self.total_requests_processed,
            "total_data_transferred_bytes": self.total_data_transferred,
            "failed_transfers": self.failed_transfers,
            "current_active_transfers": len(self.active_transfers)
        }

    def get_active_transfer(self, file_id: str) -> Optional[Dict]:
        """Get active transfer details for RPC"""
        transfer = self.active_transfers.get(file_id)
        if transfer:
            return transfer.to_dict()
        return None