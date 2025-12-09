# gRPC Protocol (Storage Nodes)

Current: Mocked gRPC service class in `storage-nodes/node.py` without generated protobufs.

Planned:
- Define proto for StoreChunk, RetrieveChunk, DeleteChunk, Health, ListChunks.
- Generate stubs; enable TLS/mTLS between API and nodes.
- Add per-RPC deadlines and retries.
