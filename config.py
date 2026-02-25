"""
Configuration for the Cloud Resource Allocation project.
Reads configuration from Streamlit secrets.
"""
import streamlit as st
import os

# Read from Streamlit secrets or environment variables
# For local development, add secrets to .streamlit/secrets.toml
try:
    SUPABASE_URL = st.secrets.get("SUPABASE_URL") or os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = st.secrets.get("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = st.secrets.get("SUPABASE_SERVICE_KEY") or os.getenv("SUPABASE_SERVICE_KEY")
except Exception as e:
    # Fallback to environment variables only
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
    SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# Validate required secrets are present
if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_KEY:
    raise ValueError(
        "Missing required Supabase configuration. "
        "Please set SUPABASE_URL, SUPABASE_ANON_KEY, and SUPABASE_SERVICE_KEY "
        "in .streamlit/secrets.toml for local development or in Streamlit Cloud secrets."
    )

# Supabase table names
TABLE_RAW_DATA = "raw_data"
TABLE_CLUSTERED_DATA = "clustered_data"
TABLE_CLUSTER_SUMMARY = "cluster_summary"
TABLE_OUTLIER_COUNTS = "outlier_counts"