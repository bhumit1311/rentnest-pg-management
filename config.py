"""
Configuration Management
Centralized configuration for the PG Management System
"""
import os
from pathlib import Path
from typing import Optional

class Config:
    """Application configuration"""
    
    # Base paths
    BASE_DIR = Path(__file__).parent
    
    # Database configuration
    DB_NAME: str = os.getenv("DB_NAME", "pg_management.db")
    DB_PATH: Path = BASE_DIR / DB_NAME
    
    # Security configuration
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-in-production")
    PASSWORD_SALT_ROUNDS: int = 12
    SESSION_TIMEOUT_MINUTES: int = 30
    MAX_LOGIN_ATTEMPTS: int = 5
    LOGIN_LOCKOUT_MINUTES: int = 15
    
    # File upload configuration
    UPLOAD_DIR: Path = BASE_DIR / "uploads"
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".pdf", ".doc", ".docx"}
    
    # Backup configuration
    BACKUP_DIR: Path = BASE_DIR / "backups"
    AUTO_BACKUP_ENABLED: bool = True
    BACKUP_RETENTION_DAYS: int = 30
    
    # Logging configuration
    LOG_DIR: Path = BASE_DIR / "logs"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Application configuration
    APP_NAME: str = "RentNest - Smart Living Management"
    APP_VERSION: str = "2.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    
    @classmethod
    def init_directories(cls):
        """Create necessary directories if they don't exist"""
        for directory in [cls.UPLOAD_DIR, cls.BACKUP_DIR, cls.LOG_DIR]:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def validate(cls) -> list[str]:
        """Validate configuration and return list of warnings"""
        warnings = []
        
        if cls.SECRET_KEY == "change-this-in-production" and cls.is_production():
            warnings.append("SECRET_KEY is using default value in production!")
        
        if cls.PASSWORD_SALT_ROUNDS < 10:
            warnings.append("PASSWORD_SALT_ROUNDS is too low for security!")
        
        return warnings


class DevelopmentConfig(Config):
    """Development environment configuration"""
    DEBUG: bool = True
    ENVIRONMENT: str = "development"


class ProductionConfig(Config):
    """Production environment configuration"""
    DEBUG: bool = False
    ENVIRONMENT: str = "production"
    SESSION_TIMEOUT_MINUTES: int = 60
    AUTO_BACKUP_ENABLED: bool = True


class TestConfig(Config):
    """Test environment configuration"""
    DEBUG: bool = True
    ENVIRONMENT: str = "test"
    DB_NAME: str = "test_pg_management.db"
    SESSION_TIMEOUT_MINUTES: int = 5


def get_config() -> Config:
    """Get configuration based on environment"""
    env = os.getenv("ENVIRONMENT", "development").lower()
    
    config_map = {
        "development": DevelopmentConfig,
        "production": ProductionConfig,
        "test": TestConfig
    }
    
    return config_map.get(env, DevelopmentConfig)()