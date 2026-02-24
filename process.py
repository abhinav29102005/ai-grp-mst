"""
process.py -- Local CLI to run all ML and push results to Supabase.
Run this once with your CSV, and the static frontend will display everything.

Usage:
    python process.py cloud_resource_allocation_dataset.csv
    python process.py cloud_resource_allocation_dataset.csv --clusters 3
"""

import sys
import time
import json
import numpy as np
import pandas as pd

from ml_pipeline import (
    load_and_preprocess,
    compute_outliers,
    run_kmeans,
    compute_elbow,
    compute_tsne,
    compute_correlation,
    NUMERIC_FEATURES,
)
from supabase_client import get_service_client


def batch_insert(table: str, records: list, chunk_size: int = 1000):
    client = get_service_client()
    for i in range(0, len(records), chunk_size):
        client.table(table).insert(records[i : i + chunk_size]).execute()


def clear_table(table: str):
    client = get_service_client()
    client.table(table).delete().gte("id", 0).execute()


INT_COLUMNS = {"task_priority", "workload_type_low", "workload_type_medium", "cluster_id"}


def to_record(row, columns):
    record = {}
    for col in columns:
        val = row[col]
        if pd.isna(val):
            record[col] = None
        elif col in INT_COLUMNS or isinstance(val, (np.integer,)):
            record[col] = int(val)
        elif isinstance(val, (np.floating,)):
            record[col] = float(val)
        else:
            record[col] = val
    return record


def main():
    if len(sys.argv) < 2:
        print("Usage: python process.py <csv_file> [--clusters N]")
        sys.exit(1)

    csv_path = sys.argv[1]
    n_clusters = 3
    if "--clusters" in sys.argv:
        idx = sys.argv.index("--clusters")
        n_clusters = int(sys.argv[idx + 1])

    start = time.time()

    # -- 1. Load and preprocess ------------------------------------------------
    print(f"[1/7] Loading {csv_path} ...")
    df_raw = pd.read_csv(csv_path)
    df = load_and_preprocess(df_raw)
    print(f"       {len(df)} rows, {len(df.columns)} columns after preprocessing")

    # -- 2. Push preprocessed data ---------------------------------------------
    print("[2/7] Uploading preprocessed data to Supabase ...")
    clear_table("raw_data")
    records = [to_record(row, df.columns) for _, row in df.iterrows()]
    batch_insert("raw_data", records)
    print(f"       {len(records)} rows uploaded")

    # -- 3. Compute and push statistics ----------------------------------------
    print("[3/7] Computing feature statistics ...")
    clear_table("data_stats")
    stats_records = []
    for col in NUMERIC_FEATURES:
        if col in df.columns:
            stats_records.append({
                "feature_name": col,
                "mean_val": round(float(df[col].mean()), 4),
                "std_val": round(float(df[col].std()), 4),
                "min_val": round(float(df[col].min()), 4),
                "max_val": round(float(df[col].max()), 4),
                "median_val": round(float(df[col].median()), 4),
                "row_count": len(df),
            })
    batch_insert("data_stats", stats_records)

    # -- 4. Compute and push outliers ------------------------------------------
    print("[4/7] Computing outliers (IQR method) ...")
    clear_table("outlier_counts")
    outliers = compute_outliers(df)
    outlier_records = [{"feature_name": k, "outlier_count": v} for k, v in outliers.items()]
    batch_insert("outlier_counts", outlier_records)
    print(f"       {sum(outliers.values())} total outliers across {len(outliers)} features")

    # -- 5. Compute and push correlation + elbow -------------------------------
    print("[5/7] Computing correlation matrix and elbow data ...")

    clear_table("correlation_data")
    corr = compute_correlation(df)
    batch_insert("correlation_data", [{
        "columns_list": json.dumps(corr["columns"]),
        "matrix_data": json.dumps(corr["matrix"]),
    }])

    clear_table("elbow_data")
    elbow = compute_elbow(df, k_range=range(1, 11))
    batch_insert("elbow_data", elbow)

    # -- 6. Run KMeans and push ------------------------------------------------
    print(f"[6/7] Running KMeans (K={n_clusters}) ...")
    clustered_df, summary_df, scaled_data = run_kmeans(df, n_clusters=n_clusters)

    clear_table("clustered_data")
    cluster_records = [to_record(row, clustered_df.columns) for _, row in clustered_df.iterrows()]
    batch_insert("clustered_data", cluster_records)

    clear_table("cluster_summary")
    summary_records = summary_df.to_dict(orient="records")
    batch_insert("cluster_summary", summary_records)

    counts = clustered_df["cluster_id"].value_counts().sort_index()
    for cid, cnt in counts.items():
        print(f"       Cluster {cid}: {cnt} records")

    # -- 7. Run t-SNE and push -------------------------------------------------
    print("[7/7] Running t-SNE (this may take a moment) ...")
    labels = clustered_df["cluster_id"].values
    tsne_results = compute_tsne(scaled_data, labels, perplexity=30)

    clear_table("tsne_data")
    batch_insert("tsne_data", tsne_results)

    elapsed = round(time.time() - start, 1)
    print(f"\nDone in {elapsed}s. All results are now in Supabase.")
    print("Your static dashboard will read directly from these tables.")


if __name__ == "__main__":
    main()
