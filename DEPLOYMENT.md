# 🚀 Deployment Guide

## Deploy to Streamlit Community Cloud (Recommended - FREE)

### Prerequisites
- GitHub account
- Repository: https://github.com/bhumit1311/rentnest-pg-management

### Step 1: Access Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Click "Sign in with GitHub"
3. Authorize Streamlit to access your repositories

### Step 2: Deploy Your App
1. Click "New app" button
2. Fill in the deployment form:
   - **Repository:** `bhumit1311/rentnest-pg-management`
   - **Branch:** `main`
   - **Main file path:** `main.py`
   - **App URL:** Choose your custom subdomain (e.g., `rentnest-pg`)
3. Click "Deploy!"

### Step 3: Configure Secrets (Important!)
1. After deployment, go to your app settings
2. Click on "Secrets" in the left sidebar
3. Add your environment variables:
```toml
# Database Configuration
DB_PATH = "pg_management.db"

# Security
SECRET_KEY = "your-secret-key-here"

# Admin Credentials (Change these!)
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "your-secure-password"
```

### Step 4: Your App is Live! 🎉
Your app will be available at:
`https://[your-app-name].streamlit.app`

---

## Alternative Deployment Options

### Option 2: Heroku
```bash
# Install Heroku CLI
# Create Procfile (already included)
heroku login
heroku create your-app-name
git push heroku main
```

### Option 3: Railway
1. Go to https://railway.app/
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose `bhumit1311/rentnest-pg-management`
5. Railway will auto-detect and deploy

### Option 4: Render
1. Go to https://render.com/
2. Click "New +"
3. Select "Web Service"
4. Connect your GitHub repository
5. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `streamlit run main.py --server.port=$PORT --server.address=0.0.0.0`

---

## 🔧 Configuration Files

### Files for Deployment:
- ✅ `requirements.txt` - Python dependencies
- ✅ `runtime.txt` - Python version
- ✅ `packages.txt` - System packages (if needed)
- ✅ `.streamlit/config.toml` - Streamlit configuration
- ✅ `.env.example` - Environment variables template

### Important Notes:
1. **Never commit `.env` file** - It's in `.gitignore`
2. **Database:** SQLite database will be created automatically
3. **Uploads:** Create `uploads/` directory on first run
4. **Secrets:** Always use Streamlit Cloud secrets for production

---

## 📊 Post-Deployment Checklist

- [ ] App is accessible via URL
- [ ] Admin login works
- [ ] Database is initialized
- [ ] File uploads work
- [ ] All features functional
- [ ] No errors in logs
- [ ] Environment variables configured
- [ ] Custom domain (optional)

---

## 🆘 Troubleshooting

### App won't start?
- Check logs in Streamlit Cloud dashboard
- Verify `requirements.txt` has all dependencies
- Ensure `main.py` is in root directory

### Database errors?
- Database will be created automatically
- Check file permissions
- Verify `DB_PATH` in secrets

### Import errors?
- Update `requirements.txt`
- Redeploy the app

---

## 🎯 Next Steps

1. **Custom Domain:** Configure in Streamlit Cloud settings (paid feature)
2. **Analytics:** Enable in Streamlit Cloud dashboard
3. **Monitoring:** Set up error tracking
4. **Backups:** Schedule database backups
5. **Updates:** Push to GitHub, auto-deploys to Streamlit Cloud

---

**Your app is ready for production! 🚀**