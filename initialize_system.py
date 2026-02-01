"""
System Initialization Script
Sets up the new database and optionally migrates data from old system
"""
import os
import sys
from pathlib import Path
from datetime import datetime

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

from db.database import Database, DatabaseInitializer
from utils import Logger, PasswordHasher, log_audit
from config import get_config

logger = Logger.get_logger(__name__)
config = get_config()


def initialize_new_system():
    """Initialize the new system from scratch"""
    print("=" * 60)
    print("PG Management System - Initialization")
    print("=" * 60)
    print()
    
    # Check if database already exists
    if config.DB_PATH.exists():
        response = input(f"Database '{config.DB_PATH}' already exists. Overwrite? (yes/no): ")
        if response.lower() != 'yes':
            print("Initialization cancelled.")
            return False
        
        # Backup existing database
        backup_path = config.DB_PATH.with_suffix('.backup.db')
        print(f"Backing up existing database to {backup_path}")
        import shutil
        shutil.copy2(config.DB_PATH, backup_path)
        
        # Remove old database
        config.DB_PATH.unlink()
    
    print("\n1. Creating directories...")
    config.init_directories()
    print(f"   ✓ Created: {config.UPLOAD_DIR}")
    print(f"   ✓ Created: {config.BACKUP_DIR}")
    print(f"   ✓ Created: {config.LOG_DIR}")
    
    print("\n2. Initializing database...")
    db = Database()
    initializer = DatabaseInitializer(db)
    
    print("   - Creating tables...")
    initializer.initialize_schema()
    print("   ✓ Database schema created")
    
    print("   - Creating default admin...")
    initializer.create_default_admin()
    print("   ✓ Default admin created")
    
    print("\n3. Verifying installation...")
    # Verify tables exist
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = [
        'admins', 'renters', 'rooms', 'beds', 
        'payments', 'complaints', 'notifications', 'audit_log'
    ]
    
    missing_tables = set(expected_tables) - set(tables)
    if missing_tables:
        print(f"   ✗ Missing tables: {missing_tables}")
        return False
    
    print(f"   ✓ All {len(expected_tables)} tables created successfully")
    
    print("\n4. Configuration summary:")
    print(f"   - Environment: {config.ENVIRONMENT}")
    print(f"   - Database: {config.DB_PATH}")
    print(f"   - Log Level: {config.LOG_LEVEL}")
    print(f"   - Session Timeout: {config.SESSION_TIMEOUT_MINUTES} minutes")
    print(f"   - Max Login Attempts: {config.MAX_LOGIN_ATTEMPTS}")
    
    # Check for configuration warnings
    warnings = config.validate()
    if warnings:
        print("\n⚠️  Configuration Warnings:")
        for warning in warnings:
            print(f"   - {warning}")
    
    print("\n" + "=" * 60)
    print("✅ Initialization Complete!")
    print("=" * 60)
    print("\nDefault Admin Credentials:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n⚠️  IMPORTANT: Change the default password immediately!")
    print("\nTo start the application:")
    print("   streamlit run main.py")
    print("=" * 60)
    
    return True


def migrate_from_old_system():
    """Migrate data from old database to new system"""
    print("=" * 60)
    print("Data Migration from Old System")
    print("=" * 60)
    print()
    
    old_db_path = input("Enter path to old database (e.g., pg_simple.db): ").strip()
    
    if not os.path.exists(old_db_path):
        print(f"Error: Database '{old_db_path}' not found!")
        return False
    
    print(f"\nMigrating data from: {old_db_path}")
    print(f"To new database: {config.DB_PATH}")
    print()
    
    response = input("Continue with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return False
    
    import sqlite3
    
    # Connect to old database
    old_conn = sqlite3.connect(old_db_path)
    old_conn.row_factory = sqlite3.Row
    old_cursor = old_conn.cursor()
    
    # Connect to new database
    new_db = Database()
    
    print("\n1. Migrating admins...")
    try:
        old_cursor.execute("SELECT username, password, name FROM admins")
        admin_count = 0
        for row in old_cursor.fetchall():
            # Hash the old plaintext password
            password_hash = PasswordHasher.hash_password(row['password'])
            
            try:
                new_db.execute_query(
                    "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
                    (row['username'], password_hash, row['name'])
                )
                admin_count += 1
            except Exception as e:
                print(f"   ⚠️  Skipped admin '{row['username']}': {e}")
        
        print(f"   ✓ Migrated {admin_count} admins")
    except Exception as e:
        print(f"   ✗ Error migrating admins: {e}")
    
    print("\n2. Migrating renters...")
    try:
        old_cursor.execute("SELECT name, phone, email, join_date, is_active FROM renters")
        renter_count = 0
        renter_map = {}  # Map old IDs to new IDs
        
        for row in old_cursor.fetchall():
            try:
                new_id = new_db.execute_query(
                    "INSERT INTO renters (name, phone, email, join_date, is_active) VALUES (?, ?, ?, ?, ?)",
                    (row['name'], row['phone'], row['email'], row['join_date'], row['is_active'])
                )
                renter_map[row['phone']] = new_id
                renter_count += 1
            except Exception as e:
                print(f"   ⚠️  Skipped renter '{row['name']}': {e}")
        
        print(f"   ✓ Migrated {renter_count} renters")
    except Exception as e:
        print(f"   ✗ Error migrating renters: {e}")
    
    print("\n3. Migrating rooms...")
    try:
        old_cursor.execute("SELECT room_number, room_type, sharing_type, monthly_rent FROM rooms")
        room_count = 0
        room_map = {}  # Map old IDs to new IDs
        
        for row in old_cursor.fetchall():
            try:
                new_id = new_db.execute_query(
                    "INSERT INTO rooms (room_number, room_type, sharing_type, monthly_rent) VALUES (?, ?, ?, ?)",
                    (row['room_number'], row['room_type'], row['sharing_type'], row['monthly_rent'])
                )
                room_map[row['room_number']] = new_id
                room_count += 1
            except Exception as e:
                print(f"   ⚠️  Skipped room '{row['room_number']}': {e}")
        
        print(f"   ✓ Migrated {room_count} rooms")
    except Exception as e:
        print(f"   ✗ Error migrating rooms: {e}")
    
    print("\n4. Migrating beds...")
    try:
        old_cursor.execute("""
            SELECT b.room_id, b.bed_number, b.is_occupied, r.room_number, 
                   renter.phone, b.renter_id
            FROM beds b
            JOIN rooms r ON b.room_id = r.room_id
            LEFT JOIN renters renter ON b.renter_id = renter.renter_id
        """)
        bed_count = 0
        
        for row in old_cursor.fetchall():
            try:
                new_room_id = room_map.get(row['room_number'])
                new_renter_id = renter_map.get(row['phone']) if row['phone'] else None
                
                if new_room_id:
                    new_db.execute_query(
                        "INSERT INTO beds (room_id, bed_number, renter_id, is_occupied) VALUES (?, ?, ?, ?)",
                        (new_room_id, row['bed_number'], new_renter_id, row['is_occupied'])
                    )
                    bed_count += 1
            except Exception as e:
                print(f"   ⚠️  Skipped bed: {e}")
        
        print(f"   ✓ Migrated {bed_count} beds")
    except Exception as e:
        print(f"   ✗ Error migrating beds: {e}")
    
    print("\n5. Migrating payments...")
    try:
        old_cursor.execute("""
            SELECT p.month_year, p.amount, p.payment_date, p.payment_method,
                   r.phone
            FROM payments p
            JOIN renters r ON p.renter_id = r.renter_id
        """)
        payment_count = 0
        
        for row in old_cursor.fetchall():
            try:
                new_renter_id = renter_map.get(row['phone'])
                if new_renter_id:
                    new_db.execute_query(
                        "INSERT INTO payments (renter_id, month_year, amount, payment_date, payment_method) VALUES (?, ?, ?, ?, ?)",
                        (new_renter_id, row['month_year'], row['amount'], row['payment_date'], row['payment_method'])
                    )
                    payment_count += 1
            except Exception as e:
                print(f"   ⚠️  Skipped payment: {e}")
        
        print(f"   ✓ Migrated {payment_count} payments")
    except Exception as e:
        print(f"   ✗ Error migrating payments: {e}")
    
    print("\n6. Migrating complaints...")
    try:
        old_cursor.execute("""
            SELECT c.title, c.description, c.category, c.priority, c.status,
                   c.created_date, c.resolved_date, c.admin_response,
                   r.phone
            FROM complaints c
            JOIN renters r ON c.renter_id = r.renter_id
        """)
        complaint_count = 0
        
        for row in old_cursor.fetchall():
            try:
                new_renter_id = renter_map.get(row['phone'])
                if new_renter_id:
                    new_db.execute_query(
                        """INSERT INTO complaints (renter_id, title, description, category, 
                           priority, status, created_date, resolved_date, admin_response) 
                           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                        (new_renter_id, row['title'], row['description'], row['category'],
                         row['priority'], row['status'], row['created_date'], 
                         row['resolved_date'], row['admin_response'])
                    )
                    complaint_count += 1
            except Exception as e:
                print(f"   ⚠️  Skipped complaint: {e}")
        
        print(f"   ✓ Migrated {complaint_count} complaints")
    except Exception as e:
        print(f"   ✗ Error migrating complaints: {e}")
    
    old_conn.close()
    
    print("\n" + "=" * 60)
    print("✅ Migration Complete!")
    print("=" * 60)
    print("\n⚠️  IMPORTANT:")
    print("1. All passwords have been re-hashed for security")
    print("2. Admins must reset their passwords")
    print("3. Review migrated data for accuracy")
    print("4. Test all functionality before going live")
    print("=" * 60)
    
    return True


def main():
    """Main entry point"""
    print("\nPG Management System - Setup Wizard")
    print("=" * 60)
    print("\nChoose an option:")
    print("1. Initialize new system (fresh install)")
    print("2. Initialize and migrate from old system")
    print("3. Exit")
    print()
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == '1':
        initialize_new_system()
    elif choice == '2':
        if initialize_new_system():
            print("\n")
            migrate_from_old_system()
    elif choice == '3':
        print("Exiting...")
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        logger.error(f"Initialization failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("Check logs for details.")