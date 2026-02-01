"""
Security Utilities
Password hashing, session management, and security helpers
"""
import hashlib
import secrets
import bcrypt
from datetime import datetime, timedelta
from typing import Optional, Tuple
from config import get_config
from utils.logger import Logger, log_security_event
from utils.exceptions import AuthenticationException, RateLimitException

config = get_config()
logger = Logger.get_logger(__name__)


class PasswordHasher:
    """Secure password hashing using bcrypt"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt(rounds=config.PASSWORD_SALT_ROUNDS)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash
        
        Args:
            password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        try:
            return bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False


class SessionManager:
    """Manage user sessions and login attempts"""
    
    # In-memory storage for login attempts (in production, use Redis or database)
    _login_attempts = {}
    _locked_accounts = {}
    
    @classmethod
    def record_login_attempt(cls, identifier: str, success: bool) -> None:
        """
        Record a login attempt
        
        Args:
            identifier: Username or phone number
            success: Whether the login was successful
        """
        if success:
            # Clear attempts on successful login
            cls._login_attempts.pop(identifier, None)
            cls._locked_accounts.pop(identifier, None)
            log_security_event("login_success", {"identifier": identifier})
        else:
            # Increment failed attempts
            if identifier not in cls._login_attempts:
                cls._login_attempts[identifier] = []
            
            cls._login_attempts[identifier].append(datetime.now())
            
            # Remove attempts older than lockout period
            cutoff = datetime.now() - timedelta(minutes=config.LOGIN_LOCKOUT_MINUTES)
            cls._login_attempts[identifier] = [
                attempt for attempt in cls._login_attempts[identifier]
                if attempt > cutoff
            ]
            
            # Check if account should be locked
            if len(cls._login_attempts[identifier]) >= config.MAX_LOGIN_ATTEMPTS:
                cls._locked_accounts[identifier] = datetime.now()
                log_security_event("account_locked", {
                    "identifier": identifier,
                    "attempts": len(cls._login_attempts[identifier])
                })
            else:
                log_security_event("login_failed", {
                    "identifier": identifier,
                    "attempts": len(cls._login_attempts[identifier])
                })
    
    @classmethod
    def is_account_locked(cls, identifier: str) -> Tuple[bool, Optional[int]]:
        """
        Check if an account is locked
        
        Args:
            identifier: Username or phone number
            
        Returns:
            Tuple of (is_locked: bool, minutes_remaining: Optional[int])
        """
        if identifier not in cls._locked_accounts:
            return False, None
        
        locked_time = cls._locked_accounts[identifier]
        unlock_time = locked_time + timedelta(minutes=config.LOGIN_LOCKOUT_MINUTES)
        
        if datetime.now() >= unlock_time:
            # Unlock the account
            cls._locked_accounts.pop(identifier, None)
            cls._login_attempts.pop(identifier, None)
            return False, None
        
        minutes_remaining = int((unlock_time - datetime.now()).total_seconds() / 60) + 1
        return True, minutes_remaining
    
    @classmethod
    def get_remaining_attempts(cls, identifier: str) -> int:
        """
        Get remaining login attempts before lockout
        
        Args:
            identifier: Username or phone number
            
        Returns:
            Number of remaining attempts
        """
        attempts = len(cls._login_attempts.get(identifier, []))
        return max(0, config.MAX_LOGIN_ATTEMPTS - attempts)


class TokenGenerator:
    """Generate secure tokens for various purposes"""
    
    @staticmethod
    def generate_session_token() -> str:
        """Generate a secure session token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_reset_token() -> str:
        """Generate a password reset token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_api_key() -> str:
        """Generate an API key"""
        return secrets.token_urlsafe(48)


class InputValidator:
    """Validate and sanitize user inputs"""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove spaces and dashes
        phone = phone.replace(" ", "").replace("-", "")
        
        # Check if it's 10 digits
        return phone.isdigit() and len(phone) == 10
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format
        
        Args:
            email: Email to validate
            
        Returns:
            True if valid, False otherwise
        """
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def sanitize_string(text: str) -> str:
        """
        Sanitize string input to prevent injection attacks
        
        Args:
            text: Text to sanitize
            
        Returns:
            Sanitized text
        """
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '\\', ';', '--']
        for char in dangerous_chars:
            text = text.replace(char, '')
        return text.strip()
    
    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        Validate password strength
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        return True, "Password is strong"