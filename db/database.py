"""
Database Layer
Centralized database access with transactions, constraints, and proper error handling
"""
import sqlite3
from contextlib import contextmanager
from typing import Optional, List, Tuple, Any
from datetime import datetime
from config import get_config
from utils import (
    Logger,
    DatabaseException,
    DuplicateResourceException,
    ResourceNotFoundException,
    log_audit
)

config = get_config()
logger = Logger.get_logger(__name__)


class Database:
    """Database connection and transaction management"""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize database connection
        
        Args:
            db_path: Path to database file (uses config default if not provided)
        """
        self.db_path = db_path or str(config.DB_PATH)
        self._ensure_database_exists()
    
    def _ensure_database_exists(self):
        """Ensure database file and tables exist"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                # Enable foreign keys
                cursor.execute("PRAGMA foreign_keys = ON")
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to ensure database exists: {e}")
            raise DatabaseException("Failed to initialize database", {"error": str(e)})
    
    @contextmanager
    def get_connection(self):
        """
        Get database connection with automatic cleanup
        
        Yields:
            sqlite3.Connection: Database connection
        """
        conn = None
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            yield conn
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {e}")
            raise DatabaseException("Database connection failed", {"error": str(e)})
        finally:
            if conn:
                conn.close()
    
    @contextmanager
    def transaction(self):
        """
        Context manager for database transactions
        
        Yields:
            sqlite3.Connection: Database connection with transaction
        """
        with self.get_connection() as conn:
            try:
                yield conn
                conn.commit()
            except Exception as e:
                conn.rollback()
                logger.error(f"Transaction failed, rolled back: {e}")
                raise
    
    def execute_query(
        self,
        query: str,
        params: Tuple = (),
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Optional[Any]:
        """
        Execute a database query
        
        Args:
            query: SQL query to execute
            params: Query parameters
            fetch_one: Whether to fetch one result
            fetch_all: Whether to fetch all results
            
        Returns:
            Query results or None
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(query, params)
                
                if fetch_one:
                    return cursor.fetchone()
                elif fetch_all:
                    return cursor.fetchall()
                
                conn.commit()
                return cursor.lastrowid
        except sqlite3.IntegrityError as e:
            logger.warning(f"Integrity constraint violation: {e}")
            raise DuplicateResourceException(str(e))
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {e}")
            raise DatabaseException("Query execution failed", {"error": str(e)})
    
    def execute_many(self, query: str, params_list: List[Tuple]) -> int:
        """
        Execute a query with multiple parameter sets
        
        Args:
            query: SQL query to execute
            params_list: List of parameter tuples
            
        Returns:
            Number of rows affected
        """
        try:
            with self.transaction() as conn:
                cursor = conn.cursor()
                cursor.executemany(query, params_list)
                return cursor.rowcount
        except sqlite3.IntegrityError as e:
            logger.warning(f"Integrity constraint violation in batch: {e}")
            raise DuplicateResourceException(str(e))
        except sqlite3.Error as e:
            logger.error(f"Batch execution failed: {e}")
            raise DatabaseException("Batch execution failed", {"error": str(e)})


class DatabaseInitializer:
    """Initialize database schema"""
    
    def __init__(self, db: Database):
        self.db = db
    
    def initialize_schema(self):
        """Create all database tables with proper constraints"""
        logger.info("Initializing database schema")
        
        with self.db.transaction() as conn:
            cursor = conn.cursor()
            
            # Enable foreign keys
            cursor.execute("PRAGMA foreign_keys = ON")
            
            # 1. ADMINS TABLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS admins (
                    admin_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME,
                    CHECK (length(username) >= 3),
                    CHECK (length(password_hash) > 0)
                )
            ''')
            
            # 2. RENTERS TABLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS renters (
                    renter_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    email TEXT,
                    join_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CHECK (length(name) >= 2),
                    CHECK (length(phone) = 10)
                )
            ''')
            
            # 3. ROOMS TABLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS rooms (
                    room_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_number TEXT UNIQUE NOT NULL,
                    room_type TEXT NOT NULL,
                    sharing_type INTEGER NOT NULL,
                    monthly_rent REAL NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CHECK (room_type IN ('AC', 'Non-AC')),
                    CHECK (sharing_type > 0),
                    CHECK (monthly_rent >= 0)
                )
            ''')
            
            # 4. BEDS TABLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS beds (
                    bed_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id INTEGER NOT NULL,
                    bed_number INTEGER NOT NULL,
                    renter_id INTEGER,
                    is_occupied BOOLEAN DEFAULT 0,
                    occupied_since DATE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (room_id) REFERENCES rooms (room_id) ON DELETE CASCADE,
                    FOREIGN KEY (renter_id) REFERENCES renters (renter_id) ON DELETE SET NULL,
                    UNIQUE(room_id, bed_number),
                    CHECK (bed_number > 0)
                )
            ''')
            
            # 5. PAYMENTS TABLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS payments (
                    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    renter_id INTEGER NOT NULL,
                    month_year TEXT NOT NULL,
                    amount REAL NOT NULL,
                    payment_date DATE NOT NULL,
                    payment_method TEXT DEFAULT 'Cash',
                    transaction_id TEXT,
                    notes TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_by INTEGER,
                    FOREIGN KEY (renter_id) REFERENCES renters (renter_id) ON DELETE CASCADE,
                    FOREIGN KEY (created_by) REFERENCES admins (admin_id),
                    UNIQUE(renter_id, month_year),
                    CHECK (amount > 0),
                    CHECK (payment_method IN ('Cash', 'UPI', 'Bank Transfer', 'Card'))
                )
            ''')
            
            # 6. COMPLAINTS TABLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS complaints (
                    complaint_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    renter_id INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT DEFAULT 'Medium',
                    status TEXT DEFAULT 'Open',
                    created_date DATETIME NOT NULL,
                    resolved_date DATETIME,
                    admin_response TEXT,
                    resolved_by INTEGER,
                    FOREIGN KEY (renter_id) REFERENCES renters (renter_id) ON DELETE CASCADE,
                    FOREIGN KEY (resolved_by) REFERENCES admins (admin_id),
                    CHECK (category IN ('Maintenance', 'Cleanliness', 'Facilities', 'Other')),
                    CHECK (priority IN ('Low', 'Medium', 'High', 'Critical')),
                    CHECK (status IN ('Open', 'In Progress', 'Resolved', 'Closed'))
                )
            ''')
            
            # 7. NOTIFICATIONS TABLE
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    notification_type TEXT NOT NULL,
                    message TEXT NOT NULL,
                    renter_id INTEGER,
                    created_date DATETIME NOT NULL,
                    is_read BOOLEAN DEFAULT 0,
                    read_at DATETIME,
                    FOREIGN KEY (renter_id) REFERENCES renters (renter_id) ON DELETE CASCADE,
                    CHECK (notification_type IN ('Payment', 'Complaint', 'Registration', 'General'))
                )
            ''')
            
            # 8. AUDIT_LOG TABLE (for tracking important actions)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS audit_log (
                    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_type TEXT NOT NULL,
                    user_id INTEGER NOT NULL,
                    action TEXT NOT NULL,
                    table_name TEXT,
                    record_id INTEGER,
                    old_values TEXT,
                    new_values TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    ip_address TEXT,
                    CHECK (user_type IN ('admin', 'renter'))
                )
            ''')
            
            # Create indexes for better performance
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_renters_phone ON renters(phone)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_renters_active ON renters(is_active)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_beds_room ON beds(room_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_beds_renter ON beds(renter_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_payments_renter ON payments(renter_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_renter ON complaints(renter_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_read ON notifications(is_read)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_audit_timestamp ON audit_log(timestamp)')
            
        logger.info("Database schema initialized successfully")
    
    def create_default_admin(self):
        """Create default admin account if none exists"""
        from utils import PasswordHasher
        
        try:
            # Check if any admin exists
            result = self.db.execute_query(
                "SELECT COUNT(*) as count FROM admins",
                fetch_one=True
            )
            
            if result and result['count'] == 0:
                # Create default admin
                password_hash = PasswordHasher.hash_password("admin123")
                
                self.db.execute_query(
                    '''INSERT INTO admins (username, password_hash, name, email)
                       VALUES (?, ?, ?, ?)''',
                    ("admin", password_hash, "Administrator", "admin@pgmanagement.com")
                )
                
                logger.info("Default admin account created")
                log_audit("create_default_admin", None, {"username": "admin"})
        except Exception as e:
            logger.error(f"Failed to create default admin: {e}")
            raise DatabaseException("Failed to create default admin", {"error": str(e)})