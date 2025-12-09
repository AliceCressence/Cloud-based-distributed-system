# Storage Distribution Design

## Current Implementation
- Files are chunked to size `chunk_size_mb` (config).
- Chunks are distributed round-robin across ONLINE nodes from the database.
- Optional replication: `replication_factor > 1` stores a replica on the next node.
- Node usage counters are updated per chunk; system overview aggregates capacity and usage.

## Node Selection
- Round-robin by chunk index across `StorageNode` rows marked ONLINE.
- Simple and fair under even node capacities.

## Pros
- Even distribution without central coordinator.
- Simple to implement and reason about.

## Cons
- Ignores available capacity and load per node.
- No data rebalancing when nodes join/leave.

## Planned Improvements
- Weighted selection by free capacity and recent I/O.
- Consistent hashing to minimize data movement on topology change.
- Background rebalancer to move cold data.
- Rack/zone awareness for replicas.

## Verification Tests
- Upload N files and query `/api/v1/nodes/overview` to confirm even chunk spread.
- Kill one node; verify reads succeed using replica chunks.
- Increase `replication_factor` and confirm duplicate chunk records in DB.
