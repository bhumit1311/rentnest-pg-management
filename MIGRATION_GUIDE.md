# Migration Guide: Legacy to Refactored Architecture

## Overview

This guide helps you migrate from the old PG Management System to the new, secure, and properly architected version.

## 🔴 CRITICAL CHANGES

### 1. Password Security
**OLD:** Passwords stored in plaintext
**NEW:** Passwords hashed with bcrypt

**Action Required:**
- All admin passwords must be reset
- Default admin password is still `admin123` but will be hashed
- Users should change passwords immediately after first login

### 2. Database Schema
**OLD:** No foreign keys, no constraints
**NEW:** Full referential integrity with foreign keys and constraints

**Action Required:**
- Database will be recreated with new schema
- Old data needs migration (see Data Migration section)

### 3. File Structure
**OLD:** Flat structure with mixed concerns
**NEW:** Layered architecture

```
OLD:
├── auth.py (mixed UI + logic)
├── admin_panel.py (mixed UI + logic)
├── simple_database.py (no transactions)

NEW:
├── config.py (configuration)
├── db/
│   └── database.py (database layer)
├── services/
│   └── auth_service.py (business logic)
├── utils/
│   ├── logger.py (logging)
│   ├── security.py (security utilities)
│   └── exceptions.py (error handling)
├── ui/ (to be created - UI layer)
└── tests/ (comprehensive tests)
```

## 📋 Migration Steps

### Step 1: Backup Current Data

```bash
# Backup your current database
cp pg_simple.db pg_simple_backup.db

# Backup any uploaded files
cp -r uploads uploads_backup
```

### Step 2: Install New Dependencies

```bash
# Install updated requirements
pip install -r requirements.txt
```

### Step 3: Set Up Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and set your values
# IMPORTANT: Change SECRET_KEY in production!
```

### Step 4: Initialize New Database

```python
# Run this script to initialize the new database
from db.database import Database, DatabaseInitializer

db = Database()
initializer = DatabaseInitializer(db)
initializer.initialize_schema()
initializer.create_default_admin()
```

### Step 5: Migrate Data (Optional)

If you have existing data, use the migration script:

```python
# migration_script.py (to be created)
from db.database import Database
from utils import PasswordHasher
import sqlite3

# Connect to old database
old_conn = sqlite3.connect('pg_simple_backup.db')
old_cursor = old_conn.cursor()

# Connect to new database
new_db = Database()

# Migrate admins (with password hashing)
old_cursor.execute("SELECT username, password, name FROM admins")
for username, password, name in old_cursor.fetchall():
    password_hash = PasswordHasher.hash_password(password)
    new_db.execute_query(
        "INSERT INTO admins (username, password_hash, name) VALUES (?, ?, ?)",
        (username, password_hash, name)
    )

# Migrate renters
old_cursor.execute("SELECT name, phone, email, join_date FROM renters")
for name, phone, email, join_date in old_cursor.fetchall():
    new_db.execute_query(
        "INSERT INTO renters (name, phone, email, join_date) VALUES (?, ?, ?, ?)",
        (name, phone, email, join_date)
    )

# Continue for other tables...
```

## 🔧 Code Changes Required

### Authentication

**OLD:**
```python
from simple_database import SimplePGDatabase

db = SimplePGDatabase()
admin = db.authenticate_admin(username, password)
```

**NEW:**
```python
from db.database import Database
from services.auth_service import AuthService

db = Database()
auth_service = AuthService(db)
success, user_data, message = auth_service.authenticate_admin(username, password)
```

### Error Handling

**OLD:**
```python
try:
    # some operation
except Exception as e:
    st.error(str(e))
```

**NEW:**
```python
from utils import handle_exception, DatabaseException

try:
    # some operation
except DatabaseException as e:
    success, message = handle_exception(e)
    st.error(message)
```

### Logging

**OLD:**
```python
print(f"User logged in: {username}")
```

**NEW:**
```python
from utils import Logger, log_audit

logger = Logger.get_logger(__name__)
logger.info(f"User logged in: {username}")
log_audit("user_login", user_id, {"username": username})
```

## 🔒 Security Improvements

### 1. Password Hashing
- All passwords now use bcrypt with configurable salt rounds
- Minimum password strength requirements enforced

### 2. Rate Limiting
- Login attempts are tracked
- Accounts lock after 5 failed attempts
- 15-minute lockout period

### 3. Input Validation
- Phone numbers validated (10 digits)
- Email format validated
- SQL injection prevention through parameterized queries
- XSS prevention through input sanitization

### 4. Session Management
- Session timeout after 30 minutes of inactivity
- Secure session token generation

### 5. Audit Logging
- All important actions logged
- Security events tracked
- Audit trail for compliance

## 📊 Database Changes

### New Tables
- `audit_log`: Track all important actions

### Modified Tables
All tables now have:
- `created_at` timestamp
- `updated_at` timestamp
- Proper foreign key constraints
- Check constraints for data validation
- Indexes for performance

### Foreign Keys
Now enforced with CASCADE and SET NULL options:
- Deleting a room cascades to beds
- Deleting a renter sets bed.renter_id to NULL
- Deleting a renter cascades to payments and complaints

## 🚀 Performance Improvements

### 1. Database Indexes
- Indexes on frequently queried columns
- Composite indexes for common queries

### 2. Connection Pooling
- Context managers for automatic cleanup
- Transaction management

### 3. Caching (Future)
- Streamlit caching for expensive operations
- Query result caching

## 🧪 Testing

### Run Tests
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=. --cov-report=html

# Run specific test file
pytest tests/test_auth_service.py -v
```

### Test Coverage
- Authentication: ✅ Comprehensive
- Database: ✅ Basic coverage
- Services: ⏳ In progress
- UI: ⏳ To be added

## 📝 Configuration

### Environment Variables
```bash
# .env file
ENVIRONMENT=production
DB_NAME=pg_management.db
SECRET_KEY=your-secret-key-here
PASSWORD_SALT_ROUNDS=12
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=30
MAX_LOGIN_ATTEMPTS=5
LOGIN_LOCKOUT_MINUTES=15
```

### Production Checklist
- [ ] Change SECRET_KEY from default
- [ ] Set ENVIRONMENT=production
- [ ] Configure proper logging
- [ ] Set up automated backups
- [ ] Enable HTTPS
- [ ] Configure firewall rules
- [ ] Set up monitoring
- [ ] Review and test all security settings

## 🐛 Troubleshooting

### Issue: "Module not found" errors
**Solution:** Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Database locked
**Solution:** Close all connections and restart:
```python
# Ensure proper connection cleanup
with db.get_connection() as conn:
    # your code here
    pass  # connection auto-closes
```

### Issue: Password verification fails
**Solution:** Ensure passwords were migrated with hashing:
```python
# Re-hash passwords if needed
from utils import PasswordHasher
new_hash = PasswordHasher.hash_password("password")
```

## 📞 Support

For issues or questions:
1. Check the logs in `logs/` directory
2. Review error messages in `logs/error_*.log`
3. Check the audit log in database
4. Consult the main README.md

## 🎯 Next Steps

After migration:
1. Test all functionality thoroughly
2. Update UI components (admin_panel.py, renter_panel.py)
3. Implement remaining service layers
4. Add comprehensive UI tests
5. Set up CI/CD pipeline
6. Configure production deployment

## ⚠️ Breaking Changes

1. **API Changes**: All database methods now return tuples (success, data/message)
2. **Exception Handling**: Custom exceptions replace generic Exception
3. **Password Format**: Old plaintext passwords won't work
4. **Database Schema**: Incompatible with old schema
5. **Configuration**: Now uses .env instead of hardcoded values

## 📚 Additional Resources

- [README.md](README.md) - Main documentation
- [FINAL_IMPROVEMENTS_TODO.md](FINAL_IMPROVEMENTS_TODO.md) - Remaining tasks
- [config.py](config.py) - Configuration options
- [tests/](tests/) - Test examples