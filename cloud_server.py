import sys
import threading
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import FileTransfer

if __name__ == "__main__":
    network = StorageVirtualNetwork()
    threading.Thread(target=network.start_server, daemon=True).start()
    
    print("Cloud server started. Use commands: list, connect <node1> <node2> <bw>, transfer <source> <target> <file_name> <file_size_bytes>, exit")
    
    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue
        if cmd == "exit":
            sys.exit(0)
        elif cmd == "list":
            if not network.nodes:
                print("No nodes connected")
            for node_id, info in network.nodes.items():
                print(f"{node_id}: IP={info.ip_address}, MAC={info.mac_address}, Port={info.port}")
        elif cmd.startswith("connect "):
            parts = cmd.split()
            if len(parts) == 4:
                node1, node2, bw = parts[1], parts[2], int(parts[3])
                if network.connect_nodes(node1, node2, bw):
                    print(f"Connected {node1} and {node2} with {bw} Mbps")
                else:
                    print("Connection failed (nodes not found?)")
            else:
                print("Usage: connect <node1> <node2> <bw>")
        elif cmd.startswith("transfer "):
            parts = cmd.split()
            if len(parts) == 5:
                source = parts[1]
                target = parts[2]
                file_name = parts[3]
                file_size = int(parts[4])
                transfer = network.initiate_file_transfer(source, target, file_name, file_size)
                if transfer:
                    print(f"Transfer initiated: {transfer.file_id}")
                    while True:
                        chunks_done, completed = network.process_file_transfer(source, target, transfer.file_id, chunks_per_step=3)
                        print(f"Transferred {chunks_done} chunks, completed: {completed}")
                        if completed:
                            print("Transfer completed successfully!")
                            break
                        stats = network.get_network_stats()
                        print(f"Network utilization: {stats['bandwidth_utilization']:.2f}%")
                        util = network._call_on_node(target, "get_storage_utilization", [])
                        print(f"Storage utilization on {target}: {util['utilization_percent']:.2f}%")
                else:
                    print("Transfer initiation failed (storage full?)")
            else:
                print("Usage: transfer <source> <target> <file_name> <file_size_bytes>")
        else:
            print("Unknown command")