#!/usr/bin/env python3
"""
Storage Node - gRPC Server
Handles storage operations for file chunks using virtual disks
"""
import argparse
import time
import logging
from concurrent import futures
import grpc

# Note: In production, these would be imported from compiled proto files
# from protos import storage_pb2, storage_pb2_grpc

from virtual_disk import VirtualDisk

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StorageNodeServicer:
    """gRPC servicer for storage node operations"""
    
    def __init__(self, node_id: str, capacity_gb: int = 5):
        self.node_id = node_id
        self.virtual_disk = VirtualDisk(node_id, capacity_gb)
        self.start_time = time.time()
        logger.info(f"Node {node_id} initialized with {capacity_gb}GB capacity")
    
    def StoreChunk(self, request, context):
        """Store a file chunk"""
        logger.info(f"Storing chunk {request.chunk_id} from file {request.file_id}")
        
        result = self.virtual_disk.store_chunk(
            chunk_id=request.chunk_id,
            data=request.data,
            checksum=request.checksum,
            file_id=request.file_id,
            chunk_index=request.chunk_index
        )
        
        # In production, return actual protobuf message
        # return storage_pb2.StoreChunkResponse(**result)
        logger.info(f"Chunk {request.chunk_id}: {result['message']}")
        return MockStoreChunkResponse(**result)
    
    def RetrieveChunk(self, request, context):
        """Retrieve a file chunk"""
        logger.info(f"Retrieving chunk {request.chunk_id}")
        
        result = self.virtual_disk.retrieve_chunk(request.chunk_id)
        
        # return storage_pb2.RetrieveChunkResponse(**result)
        logger.info(f"Chunk {request.chunk_id}: {result['message']}")
        return MockRetrieveChunkResponse(**result)
    
    def DeleteChunk(self, request, context):
        """Delete a file chunk"""
        logger.info(f"Deleting chunk {request.chunk_id}")
        
        result = self.virtual_disk.delete_chunk(request.chunk_id)
        
        # return storage_pb2.DeleteChunkResponse(**result)
        logger.info(f"Chunk {request.chunk_id}: {result['message']}")
        return MockDeleteChunkResponse(**result)
    
    def GetHealth(self, request, context):
        """Get node health status"""
        logger.info("Health check requested")
        
        health = self.virtual_disk.get_health()
        health["uptime_seconds"] = time.time() - self.start_time
        
        # return storage_pb2.HealthResponse(**health)
        return MockHealthResponse(**health)
    
    def ListChunks(self, request, context):
        """List all chunks on this node"""
        logger.info(f"Listing chunks (page {request.page}, size {request.page_size})")
        
        result = self.virtual_disk.list_chunks(request.page, request.page_size)
        
        # return storage_pb2.ListChunksResponse(**result)
        return MockListChunksResponse(**result)


# Mock response classes for development
# In production, these would be generated from proto files
class MockStoreChunkResponse:
    def __init__(self, success, message, chunk_id, bytes_written):
        self.success = success
        self.message = message
        self.chunk_id = chunk_id
        self.bytes_written = bytes_written


class MockRetrieveChunkResponse:
    def __init__(self, success, message, data, checksum):
        self.success = success
        self.message = message
        self.data = data or b""
        self.checksum = checksum


class MockDeleteChunkResponse:
    def __init__(self, success, message):
        self.success = success
        self.message = message


class MockHealthResponse:
    def __init__(self, status, capacity_bytes, used_bytes, available_bytes, chunk_count, uptime_seconds):
        self.status = status
        self.capacity_bytes = capacity_bytes
        self.used_bytes = used_bytes
        self.available_bytes = available_bytes
        self.chunk_count = chunk_count
        self.uptime_seconds = uptime_seconds


class MockListChunksResponse:
    def __init__(self, chunks, total_count):
        self.chunks = chunks
        self.total_count = total_count


def serve(node_id: str, port: int, capacity_gb: int):
    """Start the gRPC server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # In production, use:
    # storage_pb2_grpc.add_StorageNodeServiceServicer_to_server(
    #     StorageNodeServicer(node_id, capacity_gb), server
    # )
    
    servicer = StorageNodeServicer(node_id, capacity_gb)
    
    # Mock server setup for development
    # The actual gRPC server would be registered here
    
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    
    logger.info(f"Storage Node {node_id} listening on port {port}")
    logger.info(f"Capacity: {capacity_gb}GB")
    logger.info(f"Node is ready to accept chunk storage requests")
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info(f"Shutting down node {node_id}...")
        server.stop(0)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Storage Node Server")
    parser.add_argument("--node-id", type=str, required=True, help="Node ID (e.g., node1)")
    parser.add_argument("--port", type=int, required=True, help="gRPC server port")
    parser.add_argument("--capacity-gb", type=int, default=5, help="Node capacity in GB (default: 5)")
    
    args = parser.parse_args()
    
    serve(args.node_id, args.port, args.capacity_gb)
