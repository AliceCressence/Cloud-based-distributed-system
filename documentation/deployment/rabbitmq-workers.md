# RabbitMQ + Workers (Proposed Implementation)

This guide describes how to introduce asynchronous processing using RabbitMQ and worker services, so uploads and heavy tasks can be queued and processed reliably at scale.

## Architecture
- RabbitMQ: durable queues, DLQ (dead-letter queue), priorities, TTL.
- Workers: separate service(s) consuming jobs (uploads, rebalancing, virus scan, thumbnailing).
- API: enqueues jobs and returns 202/accepted where appropriate.

## Compose Override (Example)
Create `docker-compose.rmq.yml` alongside the main compose file (example only; do not deploy to prod as-is):

```yaml
version: "3.9"
services:
  rabbitmq:
    image: rabbitmq:3.13-management
    container_name: storage_rabbitmq
    ports:
      - "5672:5672"   # AMQP
      - "15672:15672" # Mgmt UI
    environment:
      RABBITMQ_DEFAULT_USER: guest
      RABBITMQ_DEFAULT_PASS: guest
    networks:
      - ums-net

  storage-worker:
    build: ./storage-service
    container_name: storage_worker
    command: ["python", "-m", "app.worker"]
    environment:
      DATABASE_URL: postgresql://storage_user:storage_pass@storage-db:5432/ictnexus_storage
      RABBITMQ_URL: amqp://guest:guest@rabbitmq:5672/
    depends_on:
      - rabbitmq
      - storage-db
    networks:
      - ums-net

networks:
  ums-net:
    external: true
```

Run with:
```
docker compose -f docker-compose.storage.yml -f docker-compose.rmq.yml up -d --build
```

## Queue Definitions
- Queue: `uploads` (main)
- DLQ: `uploads.dlq`
- Routing keys: `uploads.default`, future keys: `uploads.priority`

## Message Schema (Example)
```json
{
  "id": "uuid",
  "type": "STORAGE_UPLOAD",
  "payload": { "file_id": "...", "user_id": 123, "chunks": ["..."] },
  "attempt": 0,
  "created_at": "2025-12-09T00:00:00Z"
}
```

## API Changes (High-level)
- Current: API reads bytes and stores chunks synchronously.
- Proposed: API writes metadata, enqueues job, returns 202; worker processes chunking and storage.
- Idempotency: include `idempotency_key` and check before reprocessing.

## Worker Responsibilities
- Validate user quota at processing time.
- Chunk file, store to nodes with replication.
- Update DB: chunk rows, node usage, file status.
- Retry with exponential backoff; send to DLQ after max attempts.

## Monitoring
- RabbitMQ management UI (15672) for queue depth and rates.
- Export metrics to Prometheus (optional) and alert on thresholds.

## Security Notes
- Use non-default credentials in production.
- Restrict management UI to admins/VPN.
- TLS for AMQP in production.
