# Data Flow

1. Client uploads file -> API reads bytes -> chunks to `chunk_size_mb`.
2. API selects ONLINE nodes in DB -> assigns chunks round-robin.
3. API calls gRPC store on nodes -> node writes to virtual disk.
4. API writes chunk rows -> updates node used_bytes -> marks file ACTIVE.
5. Download -> API fetches chunk map -> retrieves chunks -> streams to client.

Notes:
- Replication stores each chunk on a secondary node as `{chunk_id}-replica`.
- If primary retrieval fails, API attempts replica.
