"""
Centralized Logging System
Provides structured logging for the entire application
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from config import get_config

config = get_config()


class Logger:
    """Centralized logger for the application"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get or create a logger instance"""
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Remove existing handlers to avoid duplicates
        logger.handlers.clear()
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(name)s - %(message)s'
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        # File handler
        config.init_directories()
        log_file = config.LOG_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(config.LOG_FORMAT)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Error file handler
        error_log_file = config.LOG_DIR / f"error_{datetime.now().strftime('%Y-%m-%d')}.log"
        error_handler = logging.FileHandler(error_log_file, encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(file_formatter)
        logger.addHandler(error_handler)
        
        cls._loggers[name] = logger
        return logger


def log_function_call(func):
    """Decorator to log function calls"""
    logger = Logger.get_logger(func.__module__)
    
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"{func.__name__} failed with error: {str(e)}", exc_info=True)
            raise
    
    return wrapper


def log_error(logger: logging.Logger, error: Exception, context: Optional[dict] = None):
    """Log an error with context"""
    error_msg = f"Error: {str(error)}"
    if context:
        error_msg += f" | Context: {context}"
    logger.error(error_msg, exc_info=True)


def log_security_event(event_type: str, details: dict):
    """Log security-related events"""
    logger = Logger.get_logger("security")
    logger.warning(f"Security Event: {event_type} | Details: {details}")


def log_audit(action: str, user_id: Optional[int], details: dict):
    """Log audit trail for important actions"""
    logger = Logger.get_logger("audit")
    logger.info(f"Audit: {action} | User: {user_id} | Details: {details}")