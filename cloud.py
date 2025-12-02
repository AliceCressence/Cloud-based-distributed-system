import bcrypt
import grpc
from concurrent import futures
import cloudsecurity_pb2
import cloudsecurity_pb2_grpc
import smtplib
from email.mime.text import MIMEText
import random
from storage_virtual_network import StorageVirtualNetwork
from storage_virtual_node import StorageVirtualNode

# In-memory OTP store for simplicity (email -> otp)
otp_store = {}

def send_otp(email):
    otp = str(random.randint(100000, 999999))
    otp_store[email] = otp
    # Real email sending
    try:
        msg = MIMEText(f"Your OTP is {otp}. Valid for 5 minutes.")
        msg['Subject'] = 'Your Cloud Service OTP'
        msg['From'] = 'yourgmail@gmail.com'  # Replace with your email
        msg['To'] = email

        server = smtplib.SMTP('smtp.gmail.com', 587)  # Gmail example
        server.starttls()
        server.login('yourgmail@gmail.com', 'your-app-password')  # Replace with creds
        server.sendmail('yourgmail@gmail.com', email, msg.as_string())
        server.quit()
        return f"OTP sent to {email}"
    except Exception as e:
        return f"Failed to send OTP: {str(e)}"
    
    # Simulate for demo (uncomment if needed):
    # print(f"[SIMULATED] OTP for {email}: {otp}")
    # return f"OTP sent to {email} (check console)"

class UserServiceSkeleton(cloudsecurity_pb2_grpc.UserServiceServicer):
    def __init__(self):
        self.network = StorageVirtualNetwork()

    def login(self, request, context) -> cloudsecurity_pb2.Response:
        print(f'New login request: {request}')
        result = self.check_credentials(request.login, request.password)
        return cloudsecurity_pb2.Response(result=result)

    def check_credentials(self, username, pwd):
        credentials = {}
        emails = {}
        file_path = 'credentials'
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if line.strip():
                        user, email, hash_pwd = line.strip().split(',')
                        credentials[user] = hash_pwd
                        emails[user] = email
        except FileNotFoundError:
            return "Credentials file not found"
        
        if username in credentials and bcrypt.checkpw(pwd.encode('utf-8'), credentials[username].encode('utf-8')):
            return send_otp(emails[username])
        return "Unauthorized"

    def Enroll(self, request, context) -> cloudsecurity_pb2.Response:
        file_path = 'credentials'
        username = request.username
        email = request.email
        password = request.password
        
        credentials = {}
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    if line.strip():
                        user, _, _ = line.strip().split(',')
                        credentials[user] = True
        except FileNotFoundError:
            pass
        
        if username in credentials:
            return cloudsecurity_pb2.Response(result="User exists")
        
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        with open(file_path, 'a') as file:
            file.write(f"{username},{email},{hashed}\n")
        
        return cloudsecurity_pb2.Response(result="Enrolled successfully")

    def VerifyOTP(self, request, context) -> cloudsecurity_pb2.Response:
        email = request.email
        otp = request.otp
        if otp_store.get(email) == otp:
            del otp_store[email]  # Clear after verify
            return cloudsecurity_pb2.Response(result="OTP verified")
        return cloudsecurity_pb2.Response(result="Invalid OTP")

    # Storage methods
    def AddNode(self, request, context):
        node = StorageVirtualNode(
            request.node_id, 
            request.cpu_capacity, 
            request.memory_capacity, 
            request.storage_capacity, 
            request.bandwidth
        )
        self.network.add_node(node)
        return cloudsecurity_pb2.Response(result=f"Added node {request.node_id}")

    def ConnectNodes(self, request, context):
        success = self.network.connect_nodes(request.node1_id, request.node2_id, request.bandwidth)
        result = "Connected" if success else "Failed to connect"
        return cloudsecurity_pb2.Response(result=result)

    def InitiateFileTransfer(self, request, context):
        transfer = self.network.initiate_file_transfer(
            request.source_node_id,
            request.target_node_id,
            request.file_name,
            request.file_size
        )
        if transfer:
            return cloudsecurity_pb2.Response(result=transfer.file_id)
        return cloudsecurity_pb2.Response(result="Initiate failed")

    def ProcessFileTransfer(self, request, context):
        chunks, done = self.network.process_file_transfer(
            request.source_node_id,
            request.target_node_id,
            request.file_id,
            request.chunks_per_step
        )
        result = f"Chunks: {chunks}, Done: {done}"
        return cloudsecurity_pb2.Response(result=result)

    def GetNetworkStats(self, request, context):
        stats = self.network.get_network_stats()
        return cloudsecurity_pb2.Response(result=str(stats))

def run():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    cloudsecurity_pb2_grpc.add_UserServiceServicer_to_server(UserServiceSkeleton(), server)
    server.add_insecure_port('[::]:51234')
    print('Server starting on 51234...', end='')
    server.start()
    print(' [OK]')
    server.wait_for_termination()

if __name__ == '__main__':
    run()