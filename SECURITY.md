# Security Notice

## ⚠️ Important: Secrets Management

This repository uses Supabase for data storage. **Never commit API keys or secrets to version control.**

### For Local Development

1. Copy your credentials to `.streamlit/secrets.toml` (already in `.gitignore`)
2. This file will NOT be committed to Git

### For Streamlit Cloud Deployment

1. Go to your app settings in Streamlit Cloud
2. Navigate to "Secrets" section
3. Add your Supabase credentials there

### If You Accidentally Exposed Secrets

If you've already pushed secrets to GitHub:

1. **Rotate/Reset your keys immediately** in Supabase dashboard
2. Update the new keys in `.streamlit/secrets.toml` locally
3. Update the new keys in Streamlit Cloud secrets
4. Clear Git history (if needed): https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository

### GitGuardian Alert

If you received a GitGuardian alert about exposed secrets:
1. Click "Fix This Secret Leak" 
2. Follow the steps to rotate your Supabase Service Role Key
3. Update your keys in the appropriate locations (NOT in code)
