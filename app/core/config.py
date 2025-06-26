from typing import List, Optional
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    project_name: str = "Pool Backend"
    version: str = "0.1.0"
    description: str = "Pool Backend API"
    api_v1_str: str = "/api/v1"
    
    # CORS
    backend_cors_origins: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:5174"]

    @validator("backend_cors_origins", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Database
    database_url: str = "postgresql://pool_user:pool_password@localhost/pool_db"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Environment
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings() 