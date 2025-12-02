-- ICTNexus Storage Service Database Schema
-- PostgreSQL initialization script
-- Database 'ictnexus_storage' and user 'storage_user' are already created by Docker

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    user_id VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'student_undergrad',
    storage_quota_bytes BIGINT NOT NULL,
    storage_used_bytes BIGINT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_user_id ON users(user_id);
CREATE INDEX IF NOT EXISTS idx_email ON users(email);

-- Storage nodes table
CREATE TABLE IF NOT EXISTS storage_nodes (
    id SERIAL PRIMARY KEY,
    node_id VARCHAR(255) UNIQUE NOT NULL,
    host VARCHAR(255) NOT NULL,
    port INTEGER NOT NULL,
    capacity_bytes BIGINT NOT NULL,
    used_bytes BIGINT DEFAULT 0,
    status VARCHAR(50) DEFAULT 'online',
    last_heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_node_id ON storage_nodes(node_id);
CREATE INDEX IF NOT EXISTS idx_status ON storage_nodes(status);

-- Files table
CREATE TABLE IF NOT EXISTS files (
    id SERIAL PRIMARY KEY,
    file_id VARCHAR(255) UNIQUE NOT NULL,
    filename VARCHAR(500) NOT NULL,
    original_size BIGINT NOT NULL,
    content_type VARCHAR(255),
    checksum VARCHAR(64) NOT NULL,
    status VARCHAR(50) DEFAULT 'uploading',
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    course_id VARCHAR(255),
    folder_path VARCHAR(1000) DEFAULT '/',
    is_shared BOOLEAN DEFAULT FALSE,
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_file_id ON files(file_id);
CREATE INDEX IF NOT EXISTS idx_user_id_files ON files(user_id);
CREATE INDEX IF NOT EXISTS idx_course_id ON files(course_id);
CREATE INDEX IF NOT EXISTS idx_file_status ON files(status);

-- File chunks table
CREATE TABLE IF NOT EXISTS file_chunks (
    id SERIAL PRIMARY KEY,
    chunk_id VARCHAR(255) UNIQUE NOT NULL,
    file_id INTEGER REFERENCES files(id) ON DELETE CASCADE,
    node_id INTEGER REFERENCES storage_nodes(id) ON DELETE RESTRICT,
    chunk_index INTEGER NOT NULL,
    chunk_size BIGINT NOT NULL,
    checksum VARCHAR(64) NOT NULL,
    is_replica BOOLEAN DEFAULT FALSE,
    replica_of_chunk_id VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_chunk_id ON file_chunks(chunk_id);
CREATE INDEX IF NOT EXISTS idx_file_id_chunks ON file_chunks(file_id);
CREATE INDEX IF NOT EXISTS idx_node_id_chunks ON file_chunks(node_id);

-- Storage statistics table
CREATE TABLE IF NOT EXISTS storage_stats (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_files INTEGER DEFAULT 0,
    total_storage_used BIGINT DEFAULT 0,
    total_users INTEGER DEFAULT 0,
    active_nodes INTEGER DEFAULT 0,
    avg_upload_speed_mbps FLOAT DEFAULT 0.0,
    avg_download_speed_mbps FLOAT DEFAULT 0.0,
    total_uploads_today INTEGER DEFAULT 0,
    total_downloads_today INTEGER DEFAULT 0
);

CREATE INDEX IF NOT EXISTS idx_timestamp ON storage_stats(timestamp);

-- Create admin user (password: admin)
-- Password hash is bcrypt hash of "admin"
-- Quota: 2GB (2147483648 bytes)
INSERT INTO users (user_id, email, password_hash, role, storage_quota_bytes, storage_used_bytes, is_active)
VALUES ('admin', 'admin@ictnexus.edu', '$2b$12$OkUAx2ma1IN8GIvw367lu.yNpLyReys15FczyE.2R0bkhW9MgYIoW', 'ADMIN', 2147483648, 0, TRUE)
ON CONFLICT (user_id) DO NOTHING;

-- Sample storage nodes (for testing)
INSERT INTO storage_nodes (node_id, host, port, capacity_bytes, used_bytes, status)
VALUES 
    ('node1', 'localhost', 50051, 5368709120, 0, 'online'),
    ('node2', 'localhost', 50052, 5368709120, 0, 'online'),
    ('node3', 'localhost', 50053, 5368709120, 0, 'online')
ON CONFLICT (node_id) DO NOTHING;
