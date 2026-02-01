"""
Tests for Authentication Service
"""
import pytest
import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db.database import Database, DatabaseInitializer
from services.auth_service import AuthService
from utils import (
    AuthenticationException,
    ValidationException,
    RateLimitException,
    PasswordHasher
)


@pytest.fixture
def test_db():
    """Create a test database"""
    db_path = "test_pg.db"
    db = Database(db_path)
    initializer = DatabaseInitializer(db)
    initializer.initialize_schema()
    
    yield db
    
    # Cleanup
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def auth_service(test_db):
    """Create auth service with test database"""
    return AuthService(test_db)


class TestAdminAuthentication:
    """Test admin authentication"""
    
    def test_authenticate_admin_success(self, auth_service, test_db):
        """Test successful admin authentication"""
        # Create test admin
        password_hash = PasswordHasher.hash_password("testpass123")
        test_db.execute_query(
            "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
            ("testadmin", password_hash, "Test Admin")
        )
        
        # Authenticate
        success, user_data, message = auth_service.authenticate_admin("testadmin", "testpass123")
        
        assert success is True
        assert user_data is not None
        assert user_data['username'] == "testadmin"
        assert user_data['user_type'] == "admin"
        assert "successful" in message.lower()
    
    def test_authenticate_admin_wrong_password(self, auth_service, test_db):
        """Test admin authentication with wrong password"""
        # Create test admin
        password_hash = PasswordHasher.hash_password("testpass123")
        test_db.execute_query(
            "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
            ("testadmin", password_hash, "Test Admin")
        )
        
        # Try to authenticate with wrong password
        success, user_data, message = auth_service.authenticate_admin("testadmin", "wrongpass")
        
        assert success is False
        assert user_data is None
        assert "invalid" in message.lower()
    
    def test_authenticate_admin_nonexistent(self, auth_service):
        """Test admin authentication with nonexistent user"""
        success, user_data, message = auth_service.authenticate_admin("nonexistent", "password")
        
        assert success is False
        assert user_data is None
        assert "invalid" in message.lower()
    
    def test_authenticate_admin_empty_credentials(self, auth_service):
        """Test admin authentication with empty credentials"""
        with pytest.raises(ValidationException):
            auth_service.authenticate_admin("", "")


class TestRenterAuthentication:
    """Test renter authentication"""
    
    def test_authenticate_renter_success(self, auth_service, test_db):
        """Test successful renter authentication"""
        # Create test renter
        test_db.execute_query(
            "INSERT INTO renters (name, phone, join_date) VALUES (?, ?, ?)",
            ("Test Renter", "9876543210", "2024-01-01")
        )
        
        # Authenticate
        success, user_data, message = auth_service.authenticate_renter("9876543210")
        
        assert success is True
        assert user_data is not None
        assert user_data['phone'] == "9876543210"
        assert user_data['user_type'] == "renter"
    
    def test_authenticate_renter_invalid_phone(self, auth_service):
        """Test renter authentication with invalid phone"""
        with pytest.raises(ValidationException):
            auth_service.authenticate_renter("invalid")
    
    def test_authenticate_renter_nonexistent(self, auth_service):
        """Test renter authentication with nonexistent phone"""
        success, user_data, message = auth_service.authenticate_renter("9999999999")
        
        assert success is False
        assert user_data is None


class TestRenterRegistration:
    """Test renter registration"""
    
    def test_register_renter_success(self, auth_service):
        """Test successful renter registration"""
        success, message = auth_service.register_renter(
            "New Renter",
            "9876543210",
            "test@example.com",
            "2024-01-01"
        )
        
        assert success is True
        assert "successful" in message.lower()
    
    def test_register_renter_duplicate_phone(self, auth_service, test_db):
        """Test renter registration with duplicate phone"""
        # Create first renter
        test_db.execute_query(
            "INSERT INTO renters (name, phone, join_date) VALUES (?, ?, ?)",
            ("First Renter", "9876543210", "2024-01-01")
        )
        
        # Try to register with same phone
        success, message = auth_service.register_renter(
            "Second Renter",
            "9876543210",
            "test@example.com",
            "2024-01-01"
        )
        
        assert success is False
        assert "already registered" in message.lower()
    
    def test_register_renter_invalid_phone(self, auth_service):
        """Test renter registration with invalid phone"""
        with pytest.raises(ValidationException):
            auth_service.register_renter(
                "Test Renter",
                "invalid",
                "test@example.com",
                "2024-01-01"
            )
    
    def test_register_renter_invalid_email(self, auth_service):
        """Test renter registration with invalid email"""
        with pytest.raises(ValidationException):
            auth_service.register_renter(
                "Test Renter",
                "9876543210",
                "invalid-email",
                "2024-01-01"
            )
    
    def test_register_renter_short_name(self, auth_service):
        """Test renter registration with short name"""
        with pytest.raises(ValidationException):
            auth_service.register_renter(
                "A",
                "9876543210",
                "test@example.com",
                "2024-01-01"
            )


class TestPasswordChange:
    """Test password change functionality"""
    
    def test_change_password_success(self, auth_service, test_db):
        """Test successful password change"""
        # Create test admin
        old_hash = PasswordHasher.hash_password("OldPass123")
        admin_id = test_db.execute_query(
            "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
            ("testadmin", old_hash, "Test Admin")
        )
        
        # Change password
        success, message = auth_service.change_admin_password(
            admin_id,
            "OldPass123",
            "NewPass123"
        )
        
        assert success is True
        assert "successful" in message.lower()
    
    def test_change_password_wrong_old_password(self, auth_service, test_db):
        """Test password change with wrong old password"""
        # Create test admin
        old_hash = PasswordHasher.hash_password("OldPass123")
        admin_id = test_db.execute_query(
            "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
            ("testadmin", old_hash, "Test Admin")
        )
        
        # Try to change with wrong old password
        success, message = auth_service.change_admin_password(
            admin_id,
            "WrongPass",
            "NewPass123"
        )
        
        assert success is False
        assert "incorrect" in message.lower()
    
    def test_change_password_weak_new_password(self, auth_service, test_db):
        """Test password change with weak new password"""
        # Create test admin
        old_hash = PasswordHasher.hash_password("OldPass123")
        admin_id = test_db.execute_query(
            "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
            ("testadmin", old_hash, "Test Admin")
        )
        
        # Try to change to weak password
        with pytest.raises(ValidationException):
            auth_service.change_admin_password(
                admin_id,
                "OldPass123",
                "weak"
            )


class TestRateLimiting:
    """Test rate limiting functionality"""
    
    def test_account_lockout_after_max_attempts(self, auth_service, test_db):
        """Test account lockout after max failed attempts"""
        # Create test admin
        password_hash = PasswordHasher.hash_password("testpass123")
        test_db.execute_query(
            "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
            ("testadmin", password_hash, "Test Admin")
        )
        
        # Make multiple failed attempts
        for _ in range(5):
            try:
                auth_service.authenticate_admin("testadmin", "wrongpass")
            except:
                pass
        
        # Next attempt should raise RateLimitException
        with pytest.raises(RateLimitException):
            auth_service.authenticate_admin("testadmin", "wrongpass")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])