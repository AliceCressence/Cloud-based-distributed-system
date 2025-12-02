#!/usr/bin/env python3
"""
Generate Python code from proto files
Run this to compile the .proto file into Python gRPC code
"""
import subprocess
import sys
import os

def generate():
    """Generate Python code from proto files"""
    proto_file = "protos/storage.proto"
    
    if not os.path.exists(proto_file):
        print(f"Error: {proto_file} not found")
        sys.exit(1)
    
    print("Generating Python gRPC code from proto files...")
    
    try:
        subprocess.run([
            "python", "-m", "grpc_tools.protoc",
            f"--proto_path=.",
            f"--python_out=.",
            f"--grpc_python_out=.",
            proto_file
        ], check=True)
        
        print("✓ Proto files compiled successfully!")
        print("Generated files:")
        print("  - protos/storage_pb2.py")
        print("  - protos/storage_pb2_grpc.py")
        
    except subprocess.CalledProcessError as e:
        print(f"Error generating proto files: {e}")
        sys.exit(1)


if __name__ == "__main__":
    generate()
