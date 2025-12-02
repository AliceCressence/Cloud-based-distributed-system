from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://storage_user:storage_pass@localhost:5432/ictnexus_storage"
    
    # JWT Settings
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Storage Configuration
    chunk_size_mb: int = 2
    default_student_quota_gb: int = 2
    default_grad_quota_gb: int = 5
    default_faculty_quota_gb: int = 10
    replication_factor: int = 2
    storage_nodes: str = "localhost:50051,localhost:50052,localhost:50053"
    
    # Service URLs
    auth_service_url: str = "http://localhost:5000"
    student_service_url: str = "http://localhost:5001"
    course_service_url: str = "http://localhost:5002"
    
    # RabbitMQ
    rabbitmq_url: str = "amqp://guest:guest@localhost:5672/"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings():
    return Settings()
