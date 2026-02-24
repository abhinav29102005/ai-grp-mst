"""
ML Pipeline module.
Handles data preprocessing, clustering, outlier detection, and t-SNE.
All heavy computation lives here, results are cached in Supabase.
"""

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
from typing import Tuple, Dict, List
import io
import base64
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns


# Column name mapping from raw CSV to clean names
COLUMN_MAP = {
    "CPU_Usage (%)": "cpu_usage",
    "Memory_Usage (MB)": "memory_usage",
    "Network_Usage (MBps)": "network_usage",
    "Disk_IO (MBps)": "disk_io",
    "Energy_Consumption (Watts)": "energy_consumption",
    "Service_Latency (ms)": "service_latency",
}

NUMERIC_FEATURES = [
    "cpu_usage",
    "memory_usage",
    "network_usage",
    "disk_io",
    "energy_consumption",
    "service_latency",
]


def load_and_preprocess(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw dataset:
    - Drop target column
    - Fill missing values
    - One-hot encode categoricals
    - Convert booleans to int
    - Drop Predicted_Workload
    """
    df = df_raw.copy()

    # Drop target if present
    if "Optimized_Resource_Allocation" in df.columns:
        df.drop(columns=["Optimized_Resource_Allocation"], inplace=True)

    # Fill missing values
    numerical_cols = df.select_dtypes(include=["float64", "int64"]).columns
    categorical_cols = df.select_dtypes(include=["object"]).columns

    for col in numerical_cols:
        df[col].fillna(df[col].mean(), inplace=True)
    for col in categorical_cols:
        df[col].fillna(df[col].mode()[0], inplace=True)

    # One-hot encode
    df = pd.get_dummies(df, drop_first=True)

    # Convert bools to int
    bool_columns = df.select_dtypes(include="bool").columns
    df[bool_columns] = df[bool_columns].astype(int)

    # Drop predicted workload if present
    if "Predicted_Workload (%)" in df.columns:
        df.drop(columns=["Predicted_Workload (%)"], inplace=True)

    # Rename columns to clean names
    rename_map = {}
    for old_name, new_name in COLUMN_MAP.items():
        if old_name in df.columns:
            rename_map[old_name] = new_name
    df.rename(columns=rename_map, inplace=True)

    # Normalize all column names: lowercase, no spaces/parens/percent
    df.columns = [
        c.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("%", "pct")
        for c in df.columns
    ]

    return df


def compute_outliers(df: pd.DataFrame) -> Dict[str, int]:
    """Count outliers per numeric column using IQR method."""
    outlier_counts = {}
    for col in df.select_dtypes(include=[np.number]).columns:
        q1 = df[col].quantile(0.25)
        q3 = df[col].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        count = int(((df[col] < lower) | (df[col] > upper)).sum())
        outlier_counts[col] = count
    return outlier_counts


def run_kmeans(df: pd.DataFrame, n_clusters: int = 3) -> Tuple[pd.DataFrame, pd.DataFrame, np.ndarray]:
    """
    Run KMeans clustering on the dataframe.
    Returns: (clustered_df, cluster_summary, scaled_data)
    """
    # Scale
    scaler = StandardScaler()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    scaled_data = scaler.fit_transform(df[numeric_cols])

    # Cluster
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(scaled_data)

    clustered_df = df.copy()
    clustered_df["cluster_id"] = labels

    # Summary
    summary_rows = []
    for cid in range(n_clusters):
        mask = clustered_df["cluster_id"] == cid
        subset = clustered_df.loc[mask, numeric_cols]
        row = {
            "cluster_id": cid,
            "record_count": int(mask.sum()),
        }
        for feat in NUMERIC_FEATURES:
            if feat in subset.columns:
                row[f"{feat}_mean"] = round(float(subset[feat].mean()), 4)
        summary_rows.append(row)

    summary_df = pd.DataFrame(summary_rows)
    return clustered_df, summary_df, scaled_data


def compute_elbow(df: pd.DataFrame, k_range: range = range(1, 11)) -> List[Dict]:
    """Compute inertia for a range of k values."""
    scaler = StandardScaler()
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    scaled = scaler.fit_transform(df[numeric_cols])

    results = []
    for k in k_range:
        km = KMeans(n_clusters=k, random_state=42, n_init=10)
        km.fit(scaled)
        results.append({"k": k, "inertia": round(float(km.inertia_), 2)})
    return results


def compute_tsne(scaled_data: np.ndarray, labels: np.ndarray, perplexity: int = 30) -> List[Dict]:
    """Run t-SNE and return 2D coordinates with cluster labels."""
    tsne = TSNE(n_components=2, perplexity=perplexity, random_state=42)
    coords = tsne.fit_transform(scaled_data)
    results = []
    for i in range(len(coords)):
        results.append({
            "x": round(float(coords[i, 0]), 4),
            "y": round(float(coords[i, 1]), 4),
            "cluster_id": int(labels[i]),
        })
    return results


def compute_correlation(df: pd.DataFrame) -> Dict:
    """Compute correlation matrix for numeric columns."""
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Remove cluster_id if present
    numeric_cols = [c for c in numeric_cols if c != "cluster_id"]
    corr = df[numeric_cols].corr()
    return {
        "columns": numeric_cols,
        "matrix": corr.values.tolist(),
    }


def generate_plot_base64(plot_func, **kwargs) -> str:
    """Generate a matplotlib plot and return as base64 PNG."""
    fig, ax = plt.subplots(figsize=kwargs.get("figsize", (10, 6)))
    plot_func(ax=ax, **{k: v for k, v in kwargs.items() if k != "figsize"})
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=100, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("utf-8")
