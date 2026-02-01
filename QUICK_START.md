# 🚀 Quick Start Guide - PG Management System v2.0

## ⚡ Get Started in 5 Minutes

### Prerequisites
- Python 3.8 or higher
- pip installed

### Step 1: Install Dependencies (1 minute)
```bash
pip install -r requirements.txt
```

### Step 2: Initialize System (1 minute)
```bash
python initialize_system.py
```
Choose option **1** for fresh installation.

### Step 3: Start Application (30 seconds)
```bash
streamlit run main.py
```

### Step 4: Login (30 seconds)
Open browser at `http://localhost:8501`

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Change password immediately after first login!**

---

## 🔧 Configuration (Optional)

### Set Up Environment Variables
```bash
# Copy template
cp .env.example .env

# Edit .env file
# Change SECRET_KEY for production!
```

### Key Settings
```bash
ENVIRONMENT=development
SECRET_KEY=your-secret-key-here
LOG_LEVEL=INFO
SESSION_TIMEOUT_MINUTES=30
```

---

## 📊 What's New in v2.0

### 🔒 Security
- ✅ Password hashing (bcrypt)
- ✅ Rate limiting (5 attempts)
- ✅ Input validation
- ✅ SQL injection prevention
- ✅ Audit logging

### 🏗️ Architecture
- ✅ Layered design (UI → Services → Database)
- ✅ Proper error handling
- ✅ Centralized logging
- ✅ Configuration management

### 🛡️ Database
- ✅ Foreign key constraints
- ✅ Transaction support
- ✅ Data validation
- ✅ Performance indexes

---

## 🧪 Run Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html
```

---

## 📚 Documentation

- **README.md** - Complete documentation
- **MIGRATION_GUIDE.md** - Upgrade from old version
- **REFACTORING_SUMMARY.md** - What changed
- **IMPLEMENTATION_STATUS.md** - Current status

---

## 🆘 Troubleshooting

### Issue: Module not found
```bash
pip install -r requirements.txt
```

### Issue: Database error
```bash
# Reinitialize database
python initialize_system.py
```

### Issue: Login fails
- Check default credentials: `admin` / `admin123`
- Check logs in `logs/` directory

---

## 📞 Need Help?

1. Check `README.md` for detailed docs
2. Review logs in `logs/` directory
3. Check `MIGRATION_GUIDE.md` for migration help

---

## ✅ Next Steps

After installation:
1. ✅ Change default admin password
2. ✅ Configure `.env` for your environment
3. ✅ Add rooms and renters
4. ✅ Test all features
5. ✅ Review security settings

---

**Ready to go! 🎉**