"""
Authentication Service
Handles all authentication and authorization logic
"""
from typing import Optional, Tuple
from datetime import datetime
from db.database import Database
from utils import (
    Logger,
    PasswordHasher,
    SessionManager,
    InputValidator,
    AuthenticationException,
    AuthorizationException,
    ValidationException,
    RateLimitException,
    log_audit,
    log_security_event
)

logger = Logger.get_logger(__name__)


class AuthService:
    """Authentication and authorization service"""
    
    def __init__(self, db: Database):
        self.db = db
        self.password_hasher = PasswordHasher()
        self.session_manager = SessionManager()
        self.validator = InputValidator()
    
    def authenticate_admin(self, username: str, password: str) -> Tuple[bool, Optional[dict], str]:
        """
        Authenticate admin user
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            Tuple of (success: bool, user_data: Optional[dict], message: str)
        """
        try:
            # Check if account is locked
            is_locked, minutes_remaining = self.session_manager.is_account_locked(username)
            if is_locked:
                log_security_event("login_attempt_locked", {"username": username})
                raise RateLimitException(
                    f"Account locked. Try again in {minutes_remaining} minutes."
                )
            
            # Validate input
            if not username or not password:
                raise ValidationException("Username and password are required")
            
            # Get admin from database
            admin = self.db.execute_query(
                "SELECT * FROM admins WHERE username = ? AND is_active = 1",
                (username,),
                fetch_one=True
            )
            
            if not admin:
                self.session_manager.record_login_attempt(username, False)
                remaining = self.session_manager.get_remaining_attempts(username)
                log_security_event("admin_login_failed", {
                    "username": username,
                    "reason": "invalid_credentials"
                })
                return False, None, f"Invalid credentials. {remaining} attempts remaining."
            
            # Verify password
            if not self.password_hasher.verify_password(password, admin['password_hash']):
                self.session_manager.record_login_attempt(username, False)
                remaining = self.session_manager.get_remaining_attempts(username)
                log_security_event("admin_login_failed", {
                    "username": username,
                    "reason": "wrong_password"
                })
                return False, None, f"Invalid credentials. {remaining} attempts remaining."
            
            # Update last login
            self.db.execute_query(
                "UPDATE admins SET last_login = ? WHERE admin_id = ?",
                (datetime.now(), admin['admin_id'])
            )
            
            # Record successful login
            self.session_manager.record_login_attempt(username, True)
            
            # Log audit
            log_audit("admin_login", admin['admin_id'], {"username": username})
            
            # Return user data
            user_data = {
                'user_id': admin['admin_id'],
                'username': admin['username'],
                'name': admin['name'],
                'email': admin['email'],
                'user_type': 'admin'
            }
            
            return True, user_data, "Login successful"
            
        except (RateLimitException, ValidationException) as e:
            raise
        except Exception as e:
            logger.error(f"Admin authentication error: {e}")
            raise AuthenticationException("Authentication failed", {"error": str(e)})
    
    def authenticate_renter(self, phone: str) -> Tuple[bool, Optional[dict], str]:
        """
        Authenticate renter user
        
        Args:
            phone: Renter phone number
            
        Returns:
            Tuple of (success: bool, user_data: Optional[dict], message: str)
        """
        try:
            # Check if account is locked
            is_locked, minutes_remaining = self.session_manager.is_account_locked(phone)
            if is_locked:
                log_security_event("login_attempt_locked", {"phone": phone})
                raise RateLimitException(
                    f"Account locked. Try again in {minutes_remaining} minutes."
                )
            
            # Validate phone number
            if not self.validator.validate_phone(phone):
                raise ValidationException("Invalid phone number format")
            
            # Get renter from database
            renter = self.db.execute_query(
                "SELECT * FROM renters WHERE phone = ? AND is_active = 1",
                (phone,),
                fetch_one=True
            )
            
            if not renter:
                self.session_manager.record_login_attempt(phone, False)
                remaining = self.session_manager.get_remaining_attempts(phone)
                log_security_event("renter_login_failed", {
                    "phone": phone,
                    "reason": "not_found"
                })
                return False, None, f"Phone number not found or account inactive. {remaining} attempts remaining."
            
            # Record successful login
            self.session_manager.record_login_attempt(phone, True)
            
            # Log audit
            log_audit("renter_login", renter['renter_id'], {"phone": phone})
            
            # Return user data
            user_data = {
                'user_id': renter['renter_id'],
                'name': renter['name'],
                'phone': renter['phone'],
                'email': renter['email'],
                'user_type': 'renter'
            }
            
            return True, user_data, "Login successful"
            
        except (RateLimitException, ValidationException) as e:
            raise
        except Exception as e:
            logger.error(f"Renter authentication error: {e}")
            raise AuthenticationException("Authentication failed", {"error": str(e)})
    
    def register_renter(
        self,
        name: str,
        phone: str,
        email: Optional[str],
        join_date: str
    ) -> Tuple[bool, str]:
        """
        Register a new renter
        
        Args:
            name: Renter name
            phone: Renter phone number
            email: Renter email (optional)
            join_date: Join date
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate inputs
            if not name or len(name) < 2:
                raise ValidationException("Name must be at least 2 characters")
            
            if not self.validator.validate_phone(phone):
                raise ValidationException("Invalid phone number format (must be 10 digits)")
            
            if email and not self.validator.validate_email(email):
                raise ValidationException("Invalid email format")
            
            # Sanitize inputs
            name = self.validator.sanitize_string(name)
            
            # Insert renter
            renter_id = self.db.execute_query(
                '''INSERT INTO renters (name, phone, email, join_date)
                   VALUES (?, ?, ?, ?)''',
                (name, phone, email, join_date)
            )
            
            # Create notification for admin
            self.db.execute_query(
                '''INSERT INTO notifications (notification_type, message, renter_id, created_date)
                   VALUES (?, ?, ?, ?)''',
                ('Registration', f'New renter registered: {name}', renter_id, datetime.now())
            )
            
            # Log audit
            log_audit("renter_registration", renter_id, {
                "name": name,
                "phone": phone
            })
            
            return True, "Registration successful! Please wait for admin approval."
            
        except ValidationException as e:
            raise
        except Exception as e:
            logger.error(f"Renter registration error: {e}")
            if "UNIQUE constraint failed" in str(e):
                return False, "Phone number already registered"
            raise AuthenticationException("Registration failed", {"error": str(e)})
    
    def change_admin_password(
        self,
        admin_id: int,
        old_password: str,
        new_password: str
    ) -> Tuple[bool, str]:
        """
        Change admin password
        
        Args:
            admin_id: Admin ID
            old_password: Current password
            new_password: New password
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Validate new password strength
            is_valid, message = self.validator.validate_password_strength(new_password)
            if not is_valid:
                raise ValidationException(message)
            
            # Get current admin
            admin = self.db.execute_query(
                "SELECT password_hash FROM admins WHERE admin_id = ?",
                (admin_id,),
                fetch_one=True
            )
            
            if not admin:
                raise AuthorizationException("Admin not found")
            
            # Verify old password
            if not self.password_hasher.verify_password(old_password, admin['password_hash']):
                log_security_event("password_change_failed", {
                    "admin_id": admin_id,
                    "reason": "wrong_old_password"
                })
                return False, "Current password is incorrect"
            
            # Hash new password
            new_hash = self.password_hasher.hash_password(new_password)
            
            # Update password
            self.db.execute_query(
                "UPDATE admins SET password_hash = ?, updated_at = ? WHERE admin_id = ?",
                (new_hash, datetime.now(), admin_id)
            )
            
            # Log audit
            log_audit("password_change", admin_id, {"success": True})
            log_security_event("password_changed", {"admin_id": admin_id})
            
            return True, "Password changed successfully"
            
        except (ValidationException, AuthorizationException) as e:
            raise
        except Exception as e:
            logger.error(f"Password change error: {e}")
            raise AuthenticationException("Password change failed", {"error": str(e)})
    
    def require_admin(self, user_type: str, user_id: Optional[int]) -> None:
        """
        Require admin authorization
        
        Args:
            user_type: Type of user
            user_id: User ID
            
        Raises:
            AuthorizationException: If user is not admin
        """
        if user_type != 'admin' or not user_id:
            log_security_event("unauthorized_access_attempt", {
                "user_type": user_type,
                "user_id": user_id,
                "required": "admin"
            })
            raise AuthorizationException("Admin access required")
    
    def require_renter(self, user_type: str, user_id: Optional[int]) -> None:
        """
        Require renter authorization
        
        Args:
            user_type: Type of user
            user_id: User ID
            
        Raises:
            AuthorizationException: If user is not renter
        """
        if user_type != 'renter' or not user_id:
            log_security_event("unauthorized_access_attempt", {
                "user_type": user_type,
                "user_id": user_id,
                "required": "renter"
            })
            raise AuthorizationException("Renter access required")