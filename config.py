"""
Configuration module for GeoNode-GeoServer integration tests.

This module provides centralized configuration management with environment
variable support, validation, and default values.
"""

import os
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse
from pathlib import Path


class Config:
    """Configuration class for test suite settings."""
    
    def __init__(self):
        """Initialize configuration with environment variables and defaults."""
        self._load_config()
        self._validate_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables with defaults."""
        
        # Service URLs
        self.GEONODE_URL = os.getenv("GEONODE_URL", "http://localhost:8000")
        self.GEOSERVER_URL = os.getenv("GEOSERVER_URL", "http://localhost:8080/geoserver")
        
        # Authentication
        self.USERNAME = os.getenv("GEONODE_USERNAME", "admin")
        self.PASSWORD = os.getenv("GEONODE_PASSWORD", "geoserver")
        
        # Test data paths
        self.SAMPLE_SHAPEFILE_PATH = os.getenv("SAMPLE_SHAPEFILE_PATH", "./data/sample_vector.shp")
        self.SAMPLE_RASTER_PATH = os.getenv("SAMPLE_RASTER_PATH", "./data/sample_raster.tif")
        
        # Timeout and retry settings
        self.DEFAULT_TIMEOUT = int(os.getenv("DEFAULT_TIMEOUT", "30"))
        self.UPLOAD_TIMEOUT = int(os.getenv("UPLOAD_TIMEOUT", "180"))
        self.MAX_RETRY_ATTEMPTS = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
        
        # File size limits
        self.MAX_FILE_SIZE_MB = int(os.getenv("MAX_FILE_SIZE_MB", "100"))
        
        # Workspace settings
        self.DEFAULT_WORKSPACE = os.getenv("DEFAULT_WORKSPACE", "geonode")
        
        # Test configuration
        self.ENABLE_CLEANUP = os.getenv("ENABLE_CLEANUP", "false").lower() == "true"
        self.VERBOSE_LOGGING = os.getenv("VERBOSE_LOGGING", "false").lower() == "true"
        self.TEST_ENVIRONMENT = os.getenv("TEST_ENVIRONMENT", "development")
        
        # Optional settings
        self.NOTIFICATION_WEBHOOK = os.getenv("NOTIFICATION_WEBHOOK", "")
        self.OUTPUT_DIR = os.getenv("OUTPUT_DIR", "./output")
        
        # SSL/TLS settings
        self.VERIFY_SSL = os.getenv("VERIFY_SSL", "true").lower() == "true"
        self.SSL_CERT_PATH = os.getenv("SSL_CERT_PATH", "")
        
        # Logging configuration
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
        self.LOG_FILE = os.getenv("LOG_FILE", "")
        
    def _validate_config(self) -> None:
        """Validate configuration values."""
        errors = []
        
        # Validate URLs
        if not self._is_valid_url(self.GEONODE_URL):
            errors.append(f"Invalid GEONODE_URL: {self.GEONODE_URL}")
        
        if not self._is_valid_url(self.GEOSERVER_URL):
            errors.append(f"Invalid GEOSERVER_URL: {self.GEOSERVER_URL}")
        
        # Validate credentials
        if not self.USERNAME or not self.PASSWORD:
            errors.append("USERNAME and PASSWORD must be provided")
        
        # Validate file paths
        if not Path(self.SAMPLE_SHAPEFILE_PATH).exists():
            errors.append(f"Sample shapefile not found: {self.SAMPLE_SHAPEFILE_PATH}")
        
        if not Path(self.SAMPLE_RASTER_PATH).exists():
            errors.append(f"Sample raster not found: {self.SAMPLE_RASTER_PATH}")
        
        # Validate numeric values
        if self.DEFAULT_TIMEOUT <= 0:
            errors.append("DEFAULT_TIMEOUT must be positive")
        
        if self.MAX_RETRY_ATTEMPTS < 0:
            errors.append("MAX_RETRY_ATTEMPTS must be non-negative")
        
        if self.MAX_FILE_SIZE_MB <= 0:
            errors.append("MAX_FILE_SIZE_MB must be positive")
        
        # Validate log level
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.LOG_LEVEL not in valid_log_levels:
            errors.append(f"Invalid LOG_LEVEL: {self.LOG_LEVEL}. Must be one of {valid_log_levels}")
        
        if errors:
            raise ValueError(f"Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate if a URL is properly formatted."""
        try:
            parsed = urlparse(url)
            return parsed.scheme in ['http', 'https'] and bool(parsed.netloc)
        except Exception:
            return False
    
    def get_logging_config(self) -> Dict[str, Any]:
        """Get logging configuration dictionary."""
        config = {
            'level': getattr(logging, self.LOG_LEVEL),
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            'datefmt': '%Y-%m-%d %H:%M:%S'
        }
        
        if self.LOG_FILE:
            config['filename'] = self.LOG_FILE
            config['filemode'] = 'a'
        
        return config
    
    def get_session_config(self) -> Dict[str, Any]:
        """Get session configuration for requests."""
        return {
            'timeout': self.DEFAULT_TIMEOUT,
            'verify': self.VERIFY_SSL,
            'cert': self.SSL_CERT_PATH if self.SSL_CERT_PATH else None
        }
    
    def get_test_data_paths(self) -> Dict[str, str]:
        """Get test data file paths."""
        return {
            'shapefile': self.SAMPLE_SHAPEFILE_PATH,
            'raster': self.SAMPLE_RASTER_PATH
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary (excluding sensitive data)."""
        return {
            'geonode_url': self.GEONODE_URL,
            'geoserver_url': self.GEOSERVER_URL,
            'username': self.USERNAME,
            'password': '***REDACTED***',
            'default_timeout': self.DEFAULT_TIMEOUT,
            'upload_timeout': self.UPLOAD_TIMEOUT,
            'max_retry_attempts': self.MAX_RETRY_ATTEMPTS,
            'max_file_size_mb': self.MAX_FILE_SIZE_MB,
            'default_workspace': self.DEFAULT_WORKSPACE,
            'enable_cleanup': self.ENABLE_CLEANUP,
            'verbose_logging': self.VERBOSE_LOGGING,
            'test_environment': self.TEST_ENVIRONMENT,
            'verify_ssl': self.VERIFY_SSL,
            'log_level': self.LOG_LEVEL
        }
    
    def __str__(self) -> str:
        """String representation of configuration."""
        config_dict = self.to_dict()
        return "\n".join(f"{key}: {value}" for key, value in config_dict.items())


# Global configuration instance
config = Config()


def get_config() -> Config:
    """Get the global configuration instance."""
    return config


def reload_config() -> Config:
    """Reload configuration from environment variables."""
    global config
    config = Config()
    return config


# Environment-specific configurations
class DevelopmentConfig(Config):
    """Development environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.VERBOSE_LOGGING = True
        self.ENABLE_CLEANUP = False


class ProductionConfig(Config):
    """Production environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.VERBOSE_LOGGING = False
        self.ENABLE_CLEANUP = True
        self.VERIFY_SSL = True


class TestingConfig(Config):
    """Testing environment configuration."""
    
    def __init__(self):
        super().__init__()
        self.DEFAULT_TIMEOUT = 10
        self.MAX_RETRY_ATTEMPTS = 1
        self.ENABLE_CLEANUP = True


def get_config_for_environment(environment: str) -> Config:
    """Get configuration for specific environment."""
    environment = environment.lower()
    
    if environment == "development":
        return DevelopmentConfig()
    elif environment == "production":
        return ProductionConfig()
    elif environment == "testing":
        return TestingConfig()
    else:
        return Config()


if __name__ == "__main__":
    # Print current configuration for debugging
    print("Current Configuration:")
    print("=" * 50)
    print(config)
