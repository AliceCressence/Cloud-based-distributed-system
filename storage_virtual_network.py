from typing import Dict, List, Optional, Tuple
import hashlib
import time
from storage_virtual_node import StorageVirtualNode, FileTransfer, TransferStatus, FileChunk
from collections import defaultdict
import socket
import json
import threading
from dataclasses import dataclass

@dataclass
class NodeInfo:
    node_id: str
    cpu_capacity: int
    memory_capacity: int
    storage_capacity: int
    bandwidth: int  # Mbps
    ip_address: str
    mac_address: str
    host: str
    port: int

class StorageVirtualNetwork:
    def __init__(self):
        self.nodes: Dict[str, NodeInfo] = {}
        self.transfer_operations: Dict[str, Dict[str, FileTransfer]] = defaultdict(dict)
        self.next_ip = 1
        self.next_mac = 0
        self.server_socket: Optional[socket.socket] = None

    def start_server(self, host='0.0.0.0', port=5000):
        """Start the cloud's socket server for node joins."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen(5)
        print(f"Cloud listening on port {port}")
        threading.Thread(target=self._server_loop, daemon=True).start()

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
            if msg['type'] == 'JOIN':
                data = msg['data']
                ip = self._generate_ip()
                mac = self._generate_mac()
                node_info = NodeInfo(
                    node_id=data['node_id'],
                    cpu_capacity=data['cpu'],
                    memory_capacity=data['mem'],
                    storage_capacity=data['storage'],
                    bandwidth=data['bw'],
                    ip_address=ip,
                    mac_address=mac,
                    host=addr[0],  # Use actual host from connection
                    port=data['listen_port']
                )
                self.nodes[data['node_id']] = node_info
                print(f"Node {data['node_id']} joined from {addr[0]}:{addr[1]}")
                resp = {"type": "ASSIGN", "data": {"ip": ip, "mac": mac}}
            client.send(json.dumps(resp).encode('utf-8'))
        except Exception as e:
            print(f"Error handling client in cloud: {e}")
        finally:
            client.close()

    def _generate_ip(self) -> str:
        ip = f"192.168.1.{self.next_ip}"
        self.next_ip += 1
        return ip

    def _generate_mac(self) -> str:
        mac = f"00:11:22:33:44:{self.next_mac:02x}"
        self.next_mac += 1
        return mac

    def _send_to_node(self, node_id: str, msg: Dict) -> Optional[Dict]:
        if node_id not in self.nodes:
            raise ValueError(f"Node {node_id} not found")
        node = self.nodes[node_id]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((node.host, node.port))
        s.send(json.dumps(msg).encode('utf-8'))
        resp_data = s.recv(4096).decode('utf-8')
        s.close()
        if resp_data:
            return json.loads(resp_data)
        return None

    def _call_on_node(self, node_id: str, method: str, args: List) -> any:
        msg = {"type": "CALL", "method": method, "args": args}
        resp_msg = self._send_to_node(node_id, msg)
        if resp_msg and resp_msg["type"] == "RESULT":
            return resp_msg["data"]
        elif resp_msg and resp_msg["type"] == "ERROR":
            raise ValueError(resp_msg["message"])
        else:
            raise ValueError("No response from node")

    def connect_nodes(self, node1_id: str, node2_id: str, bandwidth: int):
        """Connect two nodes with specified bandwidth via RPC"""
        if node1_id not in self.nodes or node2_id not in self.nodes:
            return False
        msg = {"type": "ADD_CONNECTION", "data": {"other_node_id": node2_id, "bandwidth": bandwidth}}
        self._send_to_node(node1_id, msg)
        msg["data"]["other_node_id"] = node1_id
        self._send_to_node(node2_id, msg)
        return True

    def initiate_file_transfer(
        self,
        source_node_id: str,
        target_node_id: str,
        file_name: str,
        file_size: int
    ) -> Optional[FileTransfer]:
        """Initiate a file transfer between nodes via RPC"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes:
            return None
        file_id = hashlib.md5(f"{file_name}-{time.time()}".encode()).hexdigest()
        result = self._call_on_node(target_node_id, "initiate_file_transfer", [file_id, file_name, file_size, source_node_id])
        if result:
            transfer = FileTransfer.from_dict(result)
            self.transfer_operations[source_node_id][file_id] = transfer
            return transfer
        return None

    def process_file_transfer(
        self,
        source_node_id: str,
        target_node_id: str,
        file_id: str,
        chunks_per_step: int = 1
    ) -> Tuple[int, bool]:
        """Process a file transfer in chunks via RPC"""
        if source_node_id not in self.nodes or target_node_id not in self.nodes or file_id not in self.transfer_operations[source_node_id]:
            return (0, False)
        transfer_dict = self._call_on_node(target_node_id, "get_active_transfer", [file_id])
        if not transfer_dict:
            if file_id in self.transfer_operations[source_node_id]:
                del self.transfer_operations[source_node_id][file_id]
            return (0, True)
        transfer = FileTransfer.from_dict(transfer_dict)
        chunks_transferred = 0
        for chunk in transfer.chunks:
            if chunk.status != TransferStatus.COMPLETED and chunks_transferred < chunks_per_step:
                success = self._call_on_node(target_node_id, "process_chunk_transfer", [file_id, chunk.chunk_id, source_node_id])
                if success:
                    chunks_transferred += 1
                else:
                    return (chunks_transferred, False)
        transfer_dict = self._call_on_node(target_node_id, "get_active_transfer", [file_id])
        completed = transfer_dict is None
        if completed:
            if source_node_id in self.transfer_operations and file_id in self.transfer_operations[source_node_id]:
                del self.transfer_operations[source_node_id][file_id]
        return (chunks_transferred, completed)

    def get_network_stats(self) -> Dict[str, float]:
        """Get overall network statistics via RPC aggregation"""
        if not self.nodes:
            return {
                "total_nodes": 0,
                "total_bandwidth_bps": 0.0,
                "used_bandwidth_bps": 0.0,
                "bandwidth_utilization": 0.0,
                "total_storage_bytes": 0.0,
                "used_storage_bytes": 0.0,
                "storage_utilization": 0.0,
                "active_transfers": 0
            }
        total_bandwidth_bps = sum(n.bandwidth * 1000000 for n in self.nodes.values())
        used_bandwidth_bps = sum(self._call_on_node(node_id, "get_network_utilization", [])["current_utilization_bps"] for node_id in self.nodes)
        total_storage_bytes = sum(n.storage_capacity * 1024**3 for n in self.nodes.values())
        used_storage_bytes = sum(self._call_on_node(node_id, "get_storage_utilization", [])["used_bytes"] for node_id in self.nodes)
        active_transfers = sum(self._call_on_node(node_id, "get_performance_metrics", [])["current_active_transfers"] for node_id in self.nodes)
        bandwidth_utilization = (used_bandwidth_bps / total_bandwidth_bps * 100) if total_bandwidth_bps > 0 else 0.0
        storage_utilization = (used_storage_bytes / total_storage_bytes * 100) if total_storage_bytes > 0 else 0.0
        return {
            "total_nodes": len(self.nodes),
            "total_bandwidth_bps": total_bandwidth_bps,
            "used_bandwidth_bps": used_bandwidth_bps,
            "bandwidth_utilization": bandwidth_utilization,
            "total_storage_bytes": total_storage_bytes,
            "used_storage_bytes": used_storage_bytes,
            "storage_utilization": storage_utilization,
            "active_transfers": active_transfers
        }