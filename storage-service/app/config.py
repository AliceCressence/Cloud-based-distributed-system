from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://storage_user:storage_pass@localhost:5432/ictnexus_storage"
    db_pool_size: int = 10
    db_max_overflow: int = 20
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800
    db_pool_pre_ping: bool = True
    
    # JWT Settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    jwt_private_key_path: Optional[str] = None
    jwt_public_key_path: Optional[str] = None
    
    # Storage Configuration
    chunk_size_mb: int = 2
    default_student_quota_gb: int = 10
    default_grad_quota_gb: int = 20
    default_faculty_quota_gb: int = 50
    replication_factor: int = 2
    storage_nodes: str = "localhost:50051,localhost:50052,localhost:50053"
    allowed_origins: str = "*"
    
    # Service URLs
    auth_service_url: str = "http://localhost:5000"
    student_service_url: str = "http://localhost:5001"
    course_service_url: str = "http://localhost:5002"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    
    # Email/SMTP Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""  # Gmail App Password
    smtp_from_email: str = "noreply@ictnexus.edu"
    smtp_from_name: str = "ICTNexus Storage"
    smtp_enabled: bool = False  # Set to True to enable email sending
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
