# Streamlit Cloud Deployment Guide

## Prerequisites
✅ Your code is already pushed to GitHub: https://github.com/abhinav29102005/ai-grp-mst

## Step-by-Step Deployment Instructions

### 1. Go to Streamlit Community Cloud
Visit: **https://share.streamlit.io/**

### 2. Sign In with GitHub
- Click "Sign in with GitHub"
- Authorize Streamlit to access your GitHub repositories

### 3. Deploy New App
- Click the **"New app"** button
- Fill in the deployment form:
  - **Repository**: `abhinav29102005/ai-grp-mst`
  - **Branch**: `main`
  - **Main file path**: `dashboard.py`
  - **App URL**: Choose a custom URL (e.g., `ai-grp-mst` or `cloud-resource-allocation`)

### 4. Configure Secrets (IMPORTANT!)
Before clicking "Deploy", click on **"Advanced settings"** and add your Supabase secrets:

```toml
SUPABASE_URL = "https://ltgghjqptfokkidbiaif.supabase.co"
SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0Z2doanFwdGZva2tpZGJpYWlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjM2ODgsImV4cCI6MjA4NzQ5OTY4OH0.VUVXG33fT8rlBdHwuyzqsCKnQeK21Bd92namuMdRWFY"
SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0Z2doanFwdGZva2tpZGJpYWlmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTkyMzY4OCwiZXhwIjoyMDg3NDk5Njg4fQ.gUEP_TCabl9tvGlYBQMl1n8G5jx8NEV-ufJv5I0NiTs"
```

### 5. Deploy!
- Click **"Deploy"** button
- Wait 2-3 minutes for the app to build and deploy
- Your app will be live at: `https://[your-app-name].streamlit.app`

## Update config.py for Streamlit Cloud

You need to modify `config.py` to read from Streamlit secrets in production:

```python
"""
Configuration for the Cloud Resource Allocation project.
"""
import streamlit as st

# Try to read from Streamlit secrets first (for cloud deployment)
# Fall back to hardcoded values for local development
try:
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://ltgghjqptfokkidbiaif.supabase.co")
    SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0Z2doanFwdGZva2tpZGJpYWlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjM2ODgsImV4cCI6MjA4NzQ5OTY4OH0.VUVXG33fT8rlBdHwuyzqsCKnQeK21Bd92namuMdRWFY")
    SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0Z2doanFwdGZva2tpZGJpYWlmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTkyMzY4OCwiZXhwIjoyMDg3NDk5Njg4fQ.gUEP_TCabl9tvGlYBQMl1n8G5jx8NEV-ufJv5I0NiTs")
except:
    # Fallback for local development
    SUPABASE_URL = "https://ltgghjqptfokkidbiaif.supabase.co"
    SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0Z2doanFwdGZva2tpZGJpYWlmIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzE5MjM2ODgsImV4cCI6MjA4NzQ5OTY4OH0.VUVXG33fT8rlBdHwuyzqsCKnQeK21Bd92namuMdRWFY"
    SUPABASE_SERVICE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx0Z2doanFwdGZva2tpZGJpYWlmIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3MTkyMzY4OCwiZXhwIjoyMDg3NDk5Njg4fQ.gUEP_TCabl9tvGlYBQMl1n8G5jx8NEV-ufJv5I0NiTs"

# Supabase table names
TABLE_RAW_DATA = "raw_data"
TABLE_CLUSTERED_DATA = "clustered_data"
TABLE_CLUSTER_SUMMARY = "cluster_summary"
TABLE_OUTLIER_COUNTS = "outlier_counts"
```

## After Deployment

### Managing Your App
- **Dashboard**: https://share.streamlit.io/
- **View logs**: Click on your app → "Manage app" → "Logs"
- **Update secrets**: "Manage app" → "Settings" → "Secrets"
- **Reboot app**: "Manage app" → "⋮" menu → "Reboot app"

### Automatic Updates
Any push to the `main` branch will automatically redeploy your app!

## Troubleshooting

**Issue**: App shows "Unable to connect to Supabase"
- **Fix**: Check that secrets are properly configured in Streamlit Cloud settings

**Issue**: Import errors
- **Fix**: Ensure all packages are in `requirements.txt` with proper versions

**Issue**: App crashes on startup
- **Fix**: Check logs in Streamlit dashboard for specific error messages

## Resources
- 📚 Streamlit Docs: https://docs.streamlit.io/
- 💬 Community Forum: https://discuss.streamlit.io/
- 🐛 Report Issues: https://github.com/streamlit/streamlit/issues
