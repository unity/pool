"""
Logging configuration for the Pool Backend application
"""

import logging
import logging.config
import sys
from pathlib import Path
from typing import Dict, Any

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure logging for the application based on settings
    """
    
    # Create logs directory if logging to file
    if settings.log_to_file:
        log_path = Path(settings.log_file_path)
        log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Define logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "format": settings.log_format,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
            "detailed": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "default",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            # Root logger
            "": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # App-specific loggers
            "app": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "app.agents": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            "app.api": {
                "level": settings.log_level,
                "handlers": ["console"],
                "propagate": False,
            },
            # Uvicorn loggers
            "uvicorn": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.access": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
            # FastAPI logger
            "fastapi": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False,
            },
        },
    }
    
    # Add file handler if enabled
    if settings.log_to_file:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": settings.log_level,
            "formatter": "detailed",
            "filename": settings.log_file_path,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        }
        
        # Add file handler to all loggers
        for logger_config in logging_config["loggers"].values():
            if "handlers" in logger_config:
                logger_config["handlers"].append("file")
    
    # Apply the configuration
    logging.config.dictConfig(logging_config)
    
    # Log startup message
    logger = logging.getLogger("app.core.logging_config")
    logger.info(f"Logging configured - Level: {settings.log_level}, File logging: {settings.log_to_file}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the specified name
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


# Convenience function for getting module-specific loggers
def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module with consistent naming
    
    Args:
        module_name: Module name (e.g., 'agents.letta', 'api.endpoints')
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(f"app.{module_name}") 