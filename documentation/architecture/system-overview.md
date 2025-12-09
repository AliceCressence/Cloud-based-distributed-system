# System Overview

## Services
- Storage Service (FastAPI)
- PostgreSQL (metadata)
- Storage Nodes (gRPC) x3
- Client Portal (React)
- Admin Portal (React)

## High-Level Diagram
```mermaid
flowchart LR
  A[Client Portal] -->|HTTP| S((Storage Service))
  B[Admin Portal] -->|HTTP| S
  S -->|SQL| DB[(PostgreSQL)]
  S -->|gRPC| N1[Node 1]
  S -->|gRPC| N2[Node 2]
  S -->|gRPC| N3[Node 3]
```

## Key Properties
- Chunked storage with optional replication
- Role-based access control
- Node health and overview APIs
- Docker Compose orchestration
