# ICTNexus Storage Service - Complete Guide

**Author:** NZEKUI NZOUDJIO ALICE CRESSENCE  
**Project:** Distributed Cloud Storage Microservice for University Management  
**Date:** December 2, 2025

---

## 🎯 What Makes This Project Unique

While other students built basic cloud storage systems, Alice's innovation is integrating distributed storage into a **complete university management ecosystem** with:

- ✅ **Student-centric design**: Storage quotas tied to enrollment status
- ✅ **Course integration**: Files organized by courses and semesters
- ✅ **Academic workflows**: Assignment submission tracking
- ✅ **Department management**: Faculty-level storage pools
- ✅ **Distributed architecture**: HDFS-like chunking with fault tolerance

---

## 📁 Project Structure

```
storage-service/           # Backend API (FastAPI + PostgreSQL)
├── app/
│   ├── main.py           # FastAPI application
│   ├── models.py         # Database models
│   ├── schemas.py        # Pydantic schemas
│   ├── auth.py           # JWT authentication
│   ├── routers/          # API endpoints
│   └── services/         # Business logic
├── database/
│   └── init.sql          # PostgreSQL schema
└── requirements.txt

storage-nodes/            # gRPC Storage Nodes (Python)
├── node.py              # gRPC server
├── virtual_disk.py      # Virtual disk manager
├── protos/
│   └── storage.proto    # gRPC protocol
└── requirements.txt

storage-client-portal/   # Student Interface (React + TypeScript)
├── src/
│   ├── pages/          # Login, Dashboard
│   ├── context/        # Auth context
│   ├── lib/            # API client
│   └── main.tsx
└── package.json

storage-admin-portal/    # Admin Interface (React + TypeScript)
└── (Similar structure for admin dashboard)

docker-compose.storage.yml  # Docker orchestration
```

---

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Navigate to project root
cd c:\Users\noble\Downloads\dsc\Cressencia

# Start all services
docker-compose -f docker-compose.storage.yml up --build

# Services will be available at:
# - Storage API: http://localhost:8085
# - Client Portal: http://localhost:5175
# - Admin Portal: http://localhost:5176
# - Storage Nodes: localhost:50051, 50052, 50053
# - PostgreSQL: localhost:5434
```

### Option 2: Manual Setup

#### 1. Database Setup
```bash
# Install PostgreSQL 15
# Create database
createdb ictnexus_storage

# Run init script
psql -U postgres -d ictnexus_storage -f storage-service/database/init.sql
```

#### 2. Backend API
```bash
cd storage-service
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your database credentials
python -m app.main
```

#### 3. Storage Nodes
```bash
cd storage-nodes

# Generate gRPC code from proto file
python generate_protos.py

# Start 3 nodes in separate terminals
python node.py --node-id node1 --port 50051 --capacity-gb 5
python node.py --node-id node2 --port 50052 --capacity-gb 5
python node.py --node-id node3 --port 50053 --capacity-gb 5
```

#### 4. Client Portal
```bash
cd storage-client-portal
npm install
npm run dev
# Access at http://localhost:5173
```

#### 5. Admin Portal
```bash
cd storage-admin-portal
npm install
npm run dev
# Access at http://localhost:5173 (use different port in vite.config.ts)
```

---

## 🔑 Default Credentials

- **Admin User**: admin@ictnexus.edu / admin
- **Storage Quota**: 
  - Undergrad Students: 2GB
  - Graduate Students: 5GB
  - Faculty: 10GB
  - Admin: 100GB

---

## 🏗️ System Architecture

### Flow Diagram
```
User (Browser)
    ↓
Client Portal (React)
    ↓ HTTP/REST + JWT
Storage API (FastAPI)
    ↓ gRPC
┌─────────┬─────────┬─────────┐
│ Node 1  │ Node 2  │ Node 3  │
│ 50051   │ 50052   │ 50053   │
│ 5GB     │ 5GB     │ 5GB     │
└─────────┴─────────┴─────────┘
    ↓
Virtual Disks (.vdisk files)
```

### Key Features

**1. File Chunking**
- Files split into 2MB chunks
- Distributed across nodes using round-robin
- Each chunk replicated 2x for fault tolerance

**2. Load Balancing**
- Round-robin distribution
- Automatic node selection
- Health monitoring

**3. Storage Quota Management**
- Role-based quotas
- Real-time usage tracking
- Quota enforcement on upload

**4. Fault Tolerance**
- Chunk replication
- Automatic failover to replicas
- Node health checks

---

## 📊 API Endpoints

### Authentication
```
POST /api/v1/auth/register   # Create account
POST /api/v1/auth/login      # Login (get JWT)
GET  /api/v1/auth/me         # Get current user
```

### Files
```
POST   /api/v1/files/upload        # Upload file
GET    /api/v1/files               # List files
GET    /api/v1/files/{id}          # Get file info
GET    /api/v1/files/{id}/download # Download file
DELETE /api/v1/files/{id}          # Delete file
GET    /api/v1/files/{id}/chunks   # Get chunk map
```

### Admin - Nodes
```
POST   /api/v1/nodes              # Create node
GET    /api/v1/nodes              # List nodes
GET    /api/v1/nodes/{id}         # Get node
GET    /api/v1/nodes/health       # Check all nodes
GET    /api/v1/nodes/overview     # System overview
DELETE /api/v1/nodes/{id}         # Delete node
```

### Admin - Users
```
GET /api/v1/admin/users              # List users
GET /api/v1/admin/users/{id}         # Get user
PUT /api/v1/admin/users/{id}/quota   # Update quota
PUT /api/v1/admin/users/{id}/role    # Update role
```

---

## 🧪 Testing

### Test File Upload
```bash
# Login and get token
curl -X POST http://localhost:8085/api/v1/auth/login \
  -F "username=admin@ictnexus.edu" \
  -F "password=admin"

# Upload file
curl -X POST http://localhost:8085/api/v1/files/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@test.pdf"

# List files
curl http://localhost:8085/api/v1/files \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check Node Health
```bash
curl http://localhost:8085/api/v1/nodes/health \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 🎓 Academic Integration Ideas

### Phase 1: Current Features
- ✅ File upload/download
- ✅ Storage quotas
- ✅ User authentication
- ✅ Node management

### Phase 2: University Integration
- 📚 Course-based folders (auto-created from course-service)
- 📝 Assignment submission deadlines
- 👥 Shared group project folders
- 📊 Department storage analytics
- 🔔 Quota warning notifications

### Phase 3: Advanced Features
- 🔄 File versioning
- 🔍 Full-text search
- 📱 Mobile app
- 🌐 CDN integration for faster downloads
- 📈 Usage analytics dashboard

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Backend** | Python 3.11, FastAPI | REST API server |
| **Database** | PostgreSQL 15 | Metadata storage |
| **Storage** | gRPC, Protocol Buffers | Node communication |
| **Frontend** | React 18, TypeScript | User interfaces |
| **Styling** | TailwindCSS, shadcn/ui | Modern UI |
| **Auth** | JWT, bcrypt | Security |
| **Containers** | Docker, Docker Compose | Deployment |

---

## 📝 Database Schema

### Users
- user_id, email, role
- storage_quota_bytes, storage_used_bytes
- Tracks individual user storage

### Files
- file_id, filename, original_size
- user_id, course_id, folder_path
- status, checksum, version

### File Chunks
- chunk_id, chunk_index, chunk_size
- file_id, node_id
- is_replica, replica_of_chunk_id

### Storage Nodes
- node_id, host, port
- capacity_bytes, used_bytes, status
- last_heartbeat

---

## 🚨 Troubleshooting

### Port Already in Use
```bash
# Check what's using the port
netstat -ano | findstr :8085

# Kill the process
taskkill /PID <process_id> /F
```

### Database Connection Failed
```bash
# Check PostgreSQL is running
pg_isready

# Verify credentials in .env file
# Ensure DATABASE_URL matches your PostgreSQL setup
```

### Node Won't Start
```bash
# Check if gRPC proto files are compiled
cd storage-nodes
python generate_protos.py

# Verify port isn't in use
netstat -ano | findstr :50051
```

---

## 📊 Performance Metrics

### Expected Performance
- **Upload Speed**: 10-50 MB/s (local network)
- **Download Speed**: 20-100 MB/s (local network)
- **Chunk Distribution**: <100ms per chunk
- **File Listing**: <50ms for 1000 files
- **Concurrent Users**: 100+ (with load balancing)

### Scalability
- **Horizontal**: Add more storage nodes
- **Vertical**: Increase node capacity
- **Database**: PostgreSQL replication
- **Caching**: Redis for file metadata

---

## 🎯 Demonstration Points

1. **Show distributed storage**
   - Upload large file (>4MB)
   - Show chunks distributed across nodes
   - Demonstrate chunk replication

2. **Show fault tolerance**
   - Stop one node
   - Download file using replica chunks

3. **Show quota management**
   - Upload files until quota exceeded
   - Show error message
   - Admin increases quota

4. **Show admin dashboard**
   - Node statistics
   - System overview
   - User management

---

## 📧 Contact & Support

**Developer**: NZEKUI NZOUDJIO ALICE CRESSENCE  
**Email**: nzekuinzoudjio.alice@ictu.edu.cm  
**Course**: CS 4122 – Distributed Systems  
**Instructor**: Daniel Moune

---

## 🏆 Project Highlights

This project demonstrates:
- ✅ Microservices architecture
- ✅ Distributed systems concepts (chunking, replication, load balancing)
- ✅ RESTful API design
- ✅ gRPC for inter-service communication
- ✅ Modern frontend development
- ✅ Containerization with Docker
- ✅ Database design & optimization
- ✅ Security best practices (JWT, bcrypt)

**Total Lines of Code**: ~3,500+  
**Services**: 6 (API, 3 nodes, 2 frontends)  
**Technologies**: 10+
