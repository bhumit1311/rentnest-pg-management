"""
Custom Exceptions
Centralized exception handling for the application
"""


class PGManagementException(Exception):
    """Base exception for PG Management System"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseException(PGManagementException):
    """Database-related exceptions"""
    pass


class AuthenticationException(PGManagementException):
    """Authentication-related exceptions"""
    pass


class AuthorizationException(PGManagementException):
    """Authorization-related exceptions"""
    pass


class ValidationException(PGManagementException):
    """Data validation exceptions"""
    pass


class ResourceNotFoundException(PGManagementException):
    """Resource not found exceptions"""
    pass


class DuplicateResourceException(PGManagementException):
    """Duplicate resource exceptions"""
    pass


class FileUploadException(PGManagementException):
    """File upload-related exceptions"""
    pass


class ConfigurationException(PGManagementException):
    """Configuration-related exceptions"""
    pass


class RateLimitException(PGManagementException):
    """Rate limiting exceptions"""
    pass


def handle_exception(exception: Exception) -> tuple[bool, str]:
    """
    Handle exceptions and return user-friendly messages
    
    Args:
        exception: The exception to handle
        
    Returns:
        Tuple of (success: bool, message: str)
    """
    if isinstance(exception, ValidationException):
        return False, f"Validation Error: {exception.message}"
    
    elif isinstance(exception, AuthenticationException):
        return False, "Authentication failed. Please check your credentials."
    
    elif isinstance(exception, AuthorizationException):
        return False, "You don't have permission to perform this action."
    
    elif isinstance(exception, ResourceNotFoundException):
        return False, f"Resource not found: {exception.message}"
    
    elif isinstance(exception, DuplicateResourceException):
        return False, f"Duplicate entry: {exception.message}"
    
    elif isinstance(exception, FileUploadException):
        return False, f"File upload error: {exception.message}"
    
    elif isinstance(exception, RateLimitException):
        return False, "Too many attempts. Please try again later."
    
    elif isinstance(exception, DatabaseException):
        return False, "Database error occurred. Please try again."
    
    else:
        return False, "An unexpected error occurred. Please contact support."