# Optimization Strategies

## API Layer
- Increase Uvicorn workers and enable keep-alive.
- Use async file reads/writes and streaming where possible.
- Tune `chunk_size_mb` based on network/CPU.

## Database
- Index frequent queries (file_id, user_id, chunk.file_id).
- Connection pooling; tune pool_size and max_overflow.
- Periodic vacuum/analyze.

## Storage Nodes
- Increase gRPC server thread pool; pin to CPU cores.
- Use buffered writes and compression if CPU allows.
- Prefer SSD-backed volumes.

## Distribution
- Weighted node selection by free space and I/O.
- Background rebalancing for hot/cold data.
- Tune `replication_factor` for availability vs capacity.

## Caching
- Cache file metadata (short TTL) to reduce DB pressure.
- CDN for frequently downloaded objects (future).
