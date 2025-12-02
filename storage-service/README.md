# ICTNexus - Cloud Storage Service

A distributed file storage microservice integrated into the ICTNexus University Management System.

## 🎯 Alice's Innovation

While other students built basic cloud storage systems, Alice's unique contribution is integrating distributed storage into a **university management ecosystem** where:
- Students can store assignments, projects, and coursework
- Faculty can manage course materials and shared resources
- The system integrates with enrollment, grades, and billing services
- Storage quotas are linked to student enrollment status

## 🏗️ Architecture Overview

### Storage Service Components
1. **Storage API** (FastAPI - Port 8085)
   - User authentication via university SSO
   - File chunking service (2MB chunks)
   - Load balancing (round-robin)
   - Node management & monitoring
   - Integration with auth-service and student-service

2. **Storage Nodes** (Python gRPC - Ports 50051+)
   - Virtual disk storage (.vdisk files)
   - gRPC protocol for chunk storage/retrieval
   - Health monitoring
   - 5GB capacity per node

3. **Storage Portal** (React - Port 5175)
   - Student file upload/download
   - Course-based file organization
   - Storage quota tied to enrollment
   - Assignment submission tracking

4. **Storage Admin Dashboard** (React - Port 5176)
   - Node management (create/stop/monitor)
   - University-wide storage analytics
   - Department storage allocation
   - Cost management per faculty

## 🆕 Alice's Unique Features

### Integration with University Services
- **Auth Service**: Single sign-on for all users
- **Student Service**: Storage quota based on enrollment
- **Course Service**: Organized folders per course
- **Finance Service**: Storage billing for exceeding quotas
- **Faculty Service**: Department-level storage pools

### Smart Features
- **Auto-organize**: Files tagged by course and semester
- **Collaboration**: Shared folders for group projects
- **Versioning**: Track assignment revisions
- **Quota Policies**: Different limits for undergrad/grad/faculty
- **Academic Calendar Sync**: Auto-archive at semester end

## 📊 Default Configuration

- **Chunk Size**: 2MB
- **Storage Per Node**: 5GB
- **Student Quota**: 2GB (undergrad), 5GB (grad), 10GB (faculty)
- **Replication Factor**: 2
- **Storage API Port**: 8085
- **Storage Node Ports**: 50051-50053
- **Storage Portal**: 5175
- **Admin Dashboard**: 5176

## 🔗 Service Integration

```
┌─────────────────────────────────────────────────────┐
│         ICTNexus University System                  │
├─────────────────────────────────────────────────────┤
│  Auth (5000) → Student (5001) → Course (5002)      │
│       ↓              ↓                ↓             │
│  [STORAGE SERVICE - Port 8085]                      │
│       ↓              ↓                ↓             │
│  Node-1 (50051) | Node-2 (50052) | Node-3 (50053) │
└─────────────────────────────────────────────────────┘
```

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy
- **Storage**: gRPC, Protocol Buffers
- **Database**: PostgreSQL (shared with other services)
- **Frontend**: React, TypeScript, TailwindCSS, shadcn/ui
- **Message Queue**: RabbitMQ (for service events)
- **Containerization**: Docker, Docker Compose

## 👥 Author

**NZEKUI NZOUDJIO ALICE CRESSENCE**  
Matricule: ICTU20241151  
ICT University - Distributed Systems & Cloud Computing
