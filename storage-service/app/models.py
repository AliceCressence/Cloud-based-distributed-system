from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, Boolean, Float, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from .database import Base


class UserRole(str, enum.Enum):
    STUDENT_UNDERGRAD = "student_undergrad"
    STUDENT_GRAD = "student_grad"
    FACULTY = "faculty"
    ADMIN = "admin"


class FileStatus(str, enum.Enum):
    UPLOADING = "uploading"
    ACTIVE = "active"
    DELETED = "deleted"


class NodeStatus(str, enum.Enum):
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"


class User(Base):
    """User model - synced from auth-service"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)  # From auth-service
    email = Column(String, unique=True, index=True)
    password_hash = Column(String)  # Hashed password for standalone auth
    role = Column(SQLEnum(UserRole), default=UserRole.STUDENT_UNDERGRAD)
    storage_quota_bytes = Column(BigInteger)  # In bytes
    storage_used_bytes = Column(BigInteger, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    files = relationship("File", back_populates="owner")


class StorageNode(Base):
    """Storage node metadata"""
    __tablename__ = "storage_nodes"

    id = Column(Integer, primary_key=True, index=True)
    node_id = Column(String, unique=True, index=True)
    host = Column(String)
    port = Column(Integer)
    capacity_bytes = Column(BigInteger)  # Total capacity
    used_bytes = Column(BigInteger, default=0)
    status = Column(SQLEnum(NodeStatus), default=NodeStatus.ONLINE)
    last_heartbeat = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chunks = relationship("FileChunk", back_populates="node")


class File(Base):
    """File metadata"""
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(String, unique=True, index=True)
    filename = Column(String, index=True)
    original_size = Column(BigInteger)  # Original file size in bytes
    content_type = Column(String)
    checksum = Column(String)  # SHA-256 hash
    status = Column(SQLEnum(FileStatus), default=FileStatus.UPLOADING)
    
    # Ownership and organization
    user_id = Column(Integer, ForeignKey("users.id"))
    course_id = Column(String, nullable=True)  # From course-service
    folder_path = Column(String, default="/")  # Virtual folder structure
    
    # Metadata
    is_shared = Column(Boolean, default=False)
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    owner = relationship("User", back_populates="files")
    chunks = relationship("FileChunk", back_populates="file", cascade="all, delete-orphan")


class FileChunk(Base):
    """File chunk metadata - maps chunks to storage nodes"""
    __tablename__ = "file_chunks"

    id = Column(Integer, primary_key=True, index=True)
    chunk_id = Column(String, unique=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id"))
    node_id = Column(Integer, ForeignKey("storage_nodes.id"))
    
    chunk_index = Column(Integer)  # Order in the file (0, 1, 2, ...)
    chunk_size = Column(BigInteger)  # Actual chunk size
    checksum = Column(String)  # SHA-256 of this chunk
    is_replica = Column(Boolean, default=False)
    replica_of_chunk_id = Column(String, nullable=True)  # If this is a replica
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    file = relationship("File", back_populates="chunks")
    node = relationship("StorageNode", back_populates="chunks")


class StorageStats(Base):
    """Storage statistics and analytics"""
    __tablename__ = "storage_stats"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # System-wide stats
    total_files = Column(Integer, default=0)
    total_storage_used = Column(BigInteger, default=0)
    total_users = Column(Integer, default=0)
    active_nodes = Column(Integer, default=0)
    
    # Performance metrics
    avg_upload_speed_mbps = Column(Float, default=0.0)
    avg_download_speed_mbps = Column(Float, default=0.0)
    total_uploads_today = Column(Integer, default=0)
    total_downloads_today = Column(Integer, default=0)
