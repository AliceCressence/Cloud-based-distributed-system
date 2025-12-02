import sys
import socket
import json
from storage_virtual_node import StorageVirtualNode

if __name__ == "__main__":
    if len(sys.argv) < 6:
        print("Usage: python node_client.py <node_id> <cpu_vCPUs> <memory_GB> <storage_GB> <bandwidth_Mbps> [cloud_host=localhost] [cloud_port=5000]")
        sys.exit(1)
    
    node_id = sys.argv[1]
    cpu = int(sys.argv[2])
    mem = int(sys.argv[3])
    storage = int(sys.argv[4])
    bw = int(sys.argv[5])
    cloud_host = sys.argv[6] if len(sys.argv) > 6 else 'localhost'
    cloud_port = int(sys.argv[7]) if len(sys.argv) > 7 else 5000
    
    node = StorageVirtualNode(node_id, cpu, mem, storage, bw)
    node.start_server()  # Starts on random port
    
    # Send join notification to cloud
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((cloud_host, cloud_port))
    msg = {
        "type": "JOIN",
        "data": {
            "node_id": node_id,
            "cpu": cpu,
            "mem": mem,
            "storage": storage,
            "bw": bw,
            "listen_port": node.listen_port
        }
    }
    s.send(json.dumps(msg).encode('utf-8'))
    resp_data = s.recv(4096).decode('utf-8')
    s.close()
    
    if resp_data:
        resp = json.loads(resp_data)
        if resp["type"] == "ASSIGN":
            node.ip_address = resp["data"]["ip"]
            node.mac_address = resp["data"]["mac"]
            print(f"Node {node_id} assigned IP: {node.ip_address}, MAC: {node.mac_address}")
        else:
            print("Failed to join cloud")
    else:
        print("No response from cloud")
    
    # Keep node running (server active)
    input("Press Enter to exit node...")