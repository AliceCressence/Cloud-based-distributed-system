from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from .models import UserRole, FileStatus, NodeStatus


# User Schemas
class UserBase(BaseModel):
    email: str
    role: UserRole = UserRole.STUDENT_UNDERGRAD


class UserCreate(UserBase):
    user_id: str
    password: str


class UserResponse(UserBase):
    id: int
    user_id: str
    storage_quota_bytes: int
    storage_used_bytes: int
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# File Schemas
class FileUploadRequest(BaseModel):
    filename: str
    content_type: str
    file_size: int
    course_id: Optional[str] = None
    folder_path: str = "/"


class FileMetadata(BaseModel):
    id: int
    file_id: str
    filename: str
    original_size: int
    content_type: str
    status: FileStatus
    course_id: Optional[str]
    folder_path: str
    is_shared: bool
    version: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class FileListResponse(BaseModel):
    files: List[FileMetadata]
    total: int
    storage_used: int
    storage_quota: int


# Storage Node Schemas
class NodeCreate(BaseModel):
    node_id: str
    host: str
    port: int
    capacity_bytes: int = Field(default=5 * 1024 * 1024 * 1024)  # 5GB default


class NodeResponse(BaseModel):
    id: int
    node_id: str
    host: str
    port: int
    capacity_bytes: int
    used_bytes: int
    status: NodeStatus
    last_heartbeat: datetime
    created_at: datetime

    class Config:
        from_attributes = True


class NodeHealthResponse(BaseModel):
    node_id: str
    status: NodeStatus
    capacity_bytes: int
    used_bytes: int
    available_bytes: int
    utilization_percent: float


# Chunk Schemas
class ChunkMetadata(BaseModel):
    chunk_id: str
    chunk_index: int
    chunk_size: int
    node_id: str
    checksum: str


class FileChunkMap(BaseModel):
    file_id: str
    total_chunks: int
    chunks: List[ChunkMetadata]


# Upload/Download Schemas
class UploadInitResponse(BaseModel):
    file_id: str
    chunk_size: int
    total_chunks: int
    upload_urls: List[str]  # URLs for chunk upload


class ChunkUploadResponse(BaseModel):
    chunk_id: str
    chunk_index: int
    node_id: str
    success: bool
    message: str


class DownloadURLResponse(BaseModel):
    file_id: str
    filename: str
    download_url: str
    expires_at: datetime


# Statistics Schemas
class StorageStatistics(BaseModel):
    total_files: int
    total_storage_used: int
    total_users: int
    active_nodes: int
    avg_upload_speed_mbps: float
    avg_download_speed_mbps: float
    total_uploads_today: int
    total_downloads_today: int
    timestamp: datetime


class UserQuotaInfo(BaseModel):
    user_id: str
    email: str
    role: UserRole
    storage_quota_bytes: int
    storage_used_bytes: int
    available_bytes: int
    utilization_percent: float
    file_count: int


# Admin Schemas
class SystemOverview(BaseModel):
    total_nodes: int
    online_nodes: int
    total_capacity_bytes: int
    total_used_bytes: int
    total_available_bytes: int
    system_utilization_percent: float
    total_users: int
    total_files: int


class NodeStatistics(BaseModel):
    node_id: str
    status: NodeStatus
    capacity_bytes: int
    used_bytes: int
    file_count: int
    chunk_count: int
    avg_chunk_size: float
    uptime_percent: float
