# Scaling Guide

## Horizontal Scale
- Add more storage nodes: start new node container and register via `/api/v1/nodes`.
- Increase Uvicorn workers for API.

## Replication
- Raise `replication_factor` to improve availability (capacity trade-off).

## Future: Queue Workers
- Introduce RabbitMQ and workers to decouple uploads and heavy jobs.
- Auto-scale workers by queue depth.

## Observability
- Track node health, used_bytes, and chunk counts.
- Alert on low free capacity and node failures.
