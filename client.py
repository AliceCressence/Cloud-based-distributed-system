import sys
import grpc
import cloudsecurity_pb2
import cloudsecurity_pb2_grpc

def run(request_type, **kwargs):
    with grpc.insecure_channel('localhost:51234') as channel:
        stub = cloudsecurity_pb2_grpc.UserServiceStub(channel)
        
        if request_type == "login":
            response = stub.login(cloudsecurity_pb2.Request(login=kwargs['login'], password=kwargs['password']))
        elif request_type == "enroll":
            response = stub.Enroll(cloudsecurity_pb2.EnrollRequest(
                username=kwargs['username'], email=kwargs['email'], password=kwargs['password']
            ))
        elif request_type == "verify_otp":
            response = stub.VerifyOTP(cloudsecurity_pb2.VerifyOTPRequest(
                email=kwargs['email'], otp=kwargs['otp']
            ))
        elif request_type == "add_node":
            response = stub.AddNode(cloudsecurity_pb2.AddNodeRequest(
                node_id=kwargs['node_id'], cpu_capacity=kwargs.get('cpu', 4),
                memory_capacity=kwargs.get('memory', 16), storage_capacity=kwargs.get('storage', 500),
                bandwidth=kwargs.get('bandwidth', 1000)
            ))
        elif request_type == "connect_nodes":
            response = stub.ConnectNodes(cloudsecurity_pb2.ConnectNodesRequest(
                node1_id=kwargs['node1'], node2_id=kwargs['node2'], bandwidth=kwargs.get('bandwidth', 1000)
            ))
        elif request_type == "initiate_transfer":
            response = stub.InitiateFileTransfer(cloudsecurity_pb2.FileTransferRequest(
                source_node_id=kwargs['source'], target_node_id=kwargs['target'],
                file_name=kwargs['file_name'], file_size=kwargs['file_size']
            ))
        elif request_type == "process_transfer":
            response = stub.ProcessFileTransfer(cloudsecurity_pb2.ProcessTransferRequest(
                source_node_id=kwargs['source'], target_node_id=kwargs['target'],
                file_id=kwargs['file_id'], chunks_per_step=kwargs.get('chunks', 3)
            ))
        elif request_type == "get_stats":
            response = stub.GetNetworkStats(cloudsecurity_pb2.Empty())
        else:
            print("Invalid request")
            return
        
        print(f"Result: {response.result}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python client.py <request> [args]")
        sys.exit(1)
    
    request = sys.argv[1]
    args = {}
    for arg in sys.argv[2:]:
        if '=' in arg:
            key, value = arg.split('=', 1)
            args[key] = value
        else:
            print("Args must be key=value")
            sys.exit(1)
    
    run(request, **args)