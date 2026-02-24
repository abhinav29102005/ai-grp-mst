# Cloud Resource Allocation - Clustering Dashboard

Streamlit dashboard with Supabase backend. All ML results are pre-computed locally and stored in Supabase. The dashboard reads directly from Supabase.

Live: [aigrp23-2026.bigboyaks.me](http://aigrp23-2026.bigboyaks.me/)

## Architecture

```
process.py (run locally)          Supabase (PostgreSQL)
  - preprocess CSV                     |
  - KMeans clustering          stores all results
  - t-SNE, elbow, outliers            |
  - push to Supabase           dashboard.py (Streamlit Cloud)
                                  - reads via anon key
                                  - Plotly charts
                                  - 7 dashboard pages

                                frontend/ (CF Pages backup)
                                  - static HTML/JS version
```

## Project Structure

```
dashboard.py            Streamlit dashboard (deployed on Streamlit Cloud)
.streamlit/config.toml  Streamlit theme config

frontend/               static backup deployed to Cloudflare Pages
  index.html            main dashboard page
  css/style.css         styles
  js/app.js             reads Supabase, renders Plotly charts

process.py              run locally: CSV -> ML -> Supabase
ml_pipeline.py          ML functions (KMeans, t-SNE, etc.)
config.py               Supabase URL and keys
supabase_client.py      lightweight REST client (httpx)
setup_supabase.py       verify/print table creation SQL
requirements.txt        Python deps
```

## Setup

### 1. Create Supabase tables

```bash
source venv/bin/activate
python setup_supabase.py --sql
```

Copy the printed SQL into the Supabase SQL Editor and run it.

### 2. Process data

```bash
source venv/bin/activate
python process.py cloud_resource_allocation_dataset.csv
```

This runs all ML (preprocessing, outliers, correlation, elbow, KMeans, t-SNE) and pushes every result to Supabase.

### 3. Run locally

```bash
source venv/bin/activate
streamlit run dashboard.py
```

### 4. Deploy to Streamlit Community Cloud

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. Click "New app" -> select this repo
4. Set main file: `dashboard.py`
5. Deploy
6. Add custom domain `aigrp23-2026.bigboyaks.me` in settings

### 5. (Optional) Deploy static frontend to Cloudflare Pages

1. Go to [Cloudflare Dashboard](https://dash.cloudflare.com/) -> Pages
2. Connect your GitHub repo
3. Set build output directory: `frontend`
4. Deploy

## Supabase Tables

| Table | Purpose |
|-------|---------|
| raw_data | Preprocessed dataset rows |
| data_stats | Per-feature statistics (mean, std, min, max, median) |
| outlier_counts | IQR outlier counts per feature |
| correlation_data | Correlation matrix (JSON) |
| elbow_data | Inertia values for K=1..10 |
| cluster_summary | Mean values per cluster |
| clustered_data | All rows with cluster_id |
| tsne_data | 2D t-SNE coordinates with cluster labels |

Group 23 - AIML Project
