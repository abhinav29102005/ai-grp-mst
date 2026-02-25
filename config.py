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