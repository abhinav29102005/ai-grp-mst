# Cloud Resource Allocation - Clustering Dashboard

Streamlit dashboard with Supabase backend. ML results are pre-computed locally and stored in Supabase.

## Architecture

```
process.py (local)             Supabase (PostgreSQL)
  - preprocess CSV                    |
  - KMeans clustering          stores all results
  - t-SNE, elbow, outliers           |
  - push to Supabase          dashboard.py (Streamlit Cloud)
                                 - reads via anon key
                                 - Plotly charts
                                 - 7 pages
```

## Project Structure

```
dashboard.py            Streamlit dashboard
.streamlit/config.toml  Streamlit theme

process.py              local CLI: CSV -> ML -> Supabase
ml_pipeline.py          ML functions (KMeans, t-SNE, etc.)
config.py               Supabase credentials
supabase_client.py      lightweight REST client (httpx)
setup_supabase.py       table creation SQL
requirements.txt        Python deps
```

## Setup

### 1. Create Supabase tables

```bash
python setup_supabase.py --sql
```

Copy the output into the Supabase SQL Editor and run it.

### 2. Process data

```bash
python process.py cloud_resource_allocation_dataset.csv
```

### 3. Run locally

```bash
streamlit run dashboard.py
```

### 4. Deploy to Streamlit Community Cloud

1. Push repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io/)
3. New app -> select repo -> main file: `dashboard.py` -> Deploy

## Supabase Tables

| Table | Purpose |
|-------|---------|
| raw_data | Preprocessed dataset rows |
| data_stats | Per-feature statistics |
| outlier_counts | IQR outlier counts per feature |
| correlation_data | Correlation matrix (JSON) |
| elbow_data | Inertia values for K=1..10 |
| cluster_summary | Mean values per cluster |
| clustered_data | All rows with cluster_id |
| tsne_data | 2D t-SNE coordinates |

Group 23 - AIML Project
| tsne_data | 2D t-SNE coordinates with cluster labels |

Group 23 - AIML Project
