"""
Streamlit Dashboard -- Cloud Resource Allocation Clustering
Reads pre-computed ML results from Supabase and renders interactive charts.
"""

import json
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from supabase_client import get_anon_client

st.set_page_config(
    page_title="Cloud Resource Allocation",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# -- Custom CSS -----------------------------------------------------------
st.markdown("""
<style>
    .block-container { padding-top: 1rem; }
    div[data-testid="stMetric"] {
        background: #f8f9fa; border-radius: 8px; padding: 12px 16px;
        border-left: 4px solid #0f3460;
    }
    .stTabs [data-baseweb="tab-list"] { gap: 8px; }
    .stTabs [data-baseweb="tab"] {
        background: #f0f2f6; border-radius: 6px 6px 0 0; padding: 8px 20px;
    }
</style>
""", unsafe_allow_html=True)


# -- Data fetching --------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_table(name, limit=10000):
    """Fetch all rows from a Supabase table with pagination."""
    client = get_anon_client()
    rows = []
    page_size = 1000
    offset = 0
    while offset < limit:
        batch = client.table(name).select("*").limit(page_size).execute().data
        if not batch:
            break
        rows.extend(batch)
        if len(batch) < page_size:
            break
        offset += page_size
    return rows


@st.cache_data(ttl=300)
def load_all():
    stats = fetch_table("data_stats")
    outliers = fetch_table("outlier_counts")
    corr = fetch_table("correlation_data")
    elbow = fetch_table("elbow_data")
    summary = fetch_table("cluster_summary")
    clustered = fetch_table("clustered_data")
    tsne = fetch_table("tsne_data")
    return stats, outliers, corr, elbow, summary, clustered, tsne


# -- Sidebar --------------------------------------------------------------
with st.sidebar:
    st.title("Cloud Resource Allocation")
    st.caption("ML Clustering Dashboard")
    st.divider()
    page = st.radio(
        "Navigate",
        ["Overview", "Outliers", "Correlation", "Elbow Method",
         "Clustering", "Cluster Explorer", "t-SNE"],
        label_visibility="collapsed",
    )
    st.divider()
    if st.button("Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    st.caption("Group 23 - AIML Project")


# -- Load data ------------------------------------------------------------
try:
    stats, outliers, corr_raw, elbow, summary, clustered, tsne = load_all()
except Exception as e:
    st.error(f"Failed to load data from Supabase: {e}")
    st.info("Make sure you've run `python process.py <csv>` to populate the database.")
    st.stop()

COLORS = ["#0f3460", "#e94560", "#16c79a", "#f5a623", "#7b68ee", "#00bcd4"]

# -- Pages ----------------------------------------------------------------

if page == "Overview":
    st.header("Dataset Overview")

    if stats:
        df_stats = pd.DataFrame(stats)
        cols = st.columns(3)
        for i, row in df_stats.iterrows():
            with cols[i % 3]:
                st.metric(
                    row["feature_name"].replace("_", " ").title(),
                    f"{row['mean_val']:.2f}",
                    f"Std: {row['std_val']:.2f}",
                )

        st.subheader("Feature Statistics")
        display_df = df_stats[["feature_name", "mean_val", "std_val", "min_val", "max_val", "median_val", "row_count"]].copy()
        display_df.columns = ["Feature", "Mean", "Std", "Min", "Max", "Median", "Rows"]
        st.dataframe(display_df, use_container_width=True, hide_index=True)

        st.subheader("Feature Distributions")
        if clustered:
            df_c = pd.DataFrame(clustered)
            numeric_cols = [c for c in df_c.columns if c not in ("id", "created_at", "cluster_id")]
            selected = st.selectbox("Select feature", numeric_cols)
            fig = px.histogram(df_c, x=selected, nbins=40, color_discrete_sequence=[COLORS[0]])
            fig.update_layout(template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No statistics found. Run process.py first.")


elif page == "Outliers":
    st.header("Outlier Analysis (IQR Method)")

    if outliers:
        df_out = pd.DataFrame(outliers)
        total = df_out["outlier_count"].sum()
        st.metric("Total Outliers", int(total))

        fig = px.bar(
            df_out, x="feature_name", y="outlier_count",
            color="outlier_count", color_continuous_scale="Reds",
            labels={"feature_name": "Feature", "outlier_count": "Outlier Count"},
        )
        fig.update_layout(template="plotly_white", showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_out[["feature_name", "outlier_count"]], use_container_width=True, hide_index=True)
    else:
        st.warning("No outlier data found.")


elif page == "Correlation":
    st.header("Feature Correlation Matrix")

    if corr_raw:
        row = corr_raw[0]
        cols_list = json.loads(row["columns_list"])
        matrix = json.loads(row["matrix_data"])

        fig = go.Figure(data=go.Heatmap(
            z=matrix, x=cols_list, y=cols_list,
            colorscale="RdBu_r", zmin=-1, zmax=1,
            text=[[f"{v:.2f}" for v in r] for r in matrix],
            texttemplate="%{text}",
        ))
        fig.update_layout(template="plotly_white", height=550)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No correlation data found.")


elif page == "Elbow Method":
    st.header("Elbow Method - Optimal K")

    if elbow:
        df_elbow = pd.DataFrame(elbow).sort_values("k")
        fig = px.line(
            df_elbow, x="k", y="inertia",
            markers=True,
            labels={"k": "Number of Clusters (K)", "inertia": "Inertia (WCSS)"},
            color_discrete_sequence=[COLORS[0]],
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        st.dataframe(df_elbow[["k", "inertia"]], use_container_width=True, hide_index=True)
    else:
        st.warning("No elbow data found.")


elif page == "Clustering":
    st.header("KMeans Clustering Results")

    if summary:
        df_summary = pd.DataFrame(summary).sort_values("cluster_id")

        cols = st.columns(len(df_summary))
        for i, (_, row) in enumerate(df_summary.iterrows()):
            with cols[i]:
                st.metric(
                    f"Cluster {int(row['cluster_id'])}",
                    f"{int(row['record_count'])} records",
                )

        st.subheader("Cluster Centroids")
        display_cols = [c for c in df_summary.columns if c not in ("id", "created_at")]
        st.dataframe(df_summary[display_cols], use_container_width=True, hide_index=True)

        st.subheader("Cluster Comparison")
        mean_cols = [c for c in df_summary.columns if c.endswith("_mean")]
        if mean_cols:
            features = [c.replace("_mean", "").replace("_", " ").title() for c in mean_cols]
            fig = go.Figure()
            for _, row in df_summary.iterrows():
                cid = int(row["cluster_id"])
                fig.add_trace(go.Bar(
                    name=f"Cluster {cid}",
                    x=features,
                    y=[row[c] for c in mean_cols],
                    marker_color=COLORS[cid % len(COLORS)],
                ))
            fig.update_layout(barmode="group", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No cluster summary found.")


elif page == "Cluster Explorer":
    st.header("Cluster Data Explorer")

    if clustered:
        df_c = pd.DataFrame(clustered)
        numeric_cols = [c for c in df_c.columns if c not in ("id", "created_at", "cluster_id")]

        col1, col2 = st.columns(2)
        with col1:
            x_col = st.selectbox("X Axis", numeric_cols, index=0)
        with col2:
            y_col = st.selectbox("Y Axis", numeric_cols, index=min(1, len(numeric_cols) - 1))

        df_c["cluster_label"] = "Cluster " + df_c["cluster_id"].astype(str)
        fig = px.scatter(
            df_c, x=x_col, y=y_col, color="cluster_label",
            color_discrete_sequence=COLORS,
            opacity=0.6,
            labels={x_col: x_col.replace("_", " ").title(), y_col: y_col.replace("_", " ").title()},
        )
        fig.update_layout(template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Filtered Data")
        cluster_filter = st.multiselect(
            "Filter by cluster",
            sorted(df_c["cluster_id"].unique()),
            default=sorted(df_c["cluster_id"].unique()),
        )
        filtered = df_c[df_c["cluster_id"].isin(cluster_filter)]
        display_cols = [c for c in filtered.columns if c not in ("id", "created_at", "cluster_label")]
        st.dataframe(filtered[display_cols].head(200), use_container_width=True, hide_index=True)
        st.caption(f"Showing {min(200, len(filtered))} of {len(filtered)} rows")
    else:
        st.warning("No clustered data found.")


elif page == "t-SNE":
    st.header("t-SNE Visualization")

    if tsne:
        df_tsne = pd.DataFrame(tsne)
        df_tsne["cluster_label"] = "Cluster " + df_tsne["cluster_id"].astype(str)

        fig = px.scatter(
            df_tsne, x="x", y="y", color="cluster_label",
            color_discrete_sequence=COLORS,
            opacity=0.7,
            labels={"x": "t-SNE Dimension 1", "y": "t-SNE Dimension 2"},
        )
        fig.update_layout(template="plotly_white", height=600)
        fig.update_traces(marker=dict(size=4))
        st.plotly_chart(fig, use_container_width=True)

        with st.expander("t-SNE Data Sample"):
            st.dataframe(df_tsne[["x", "y", "cluster_id"]].head(100), use_container_width=True, hide_index=True)
    else:
        st.warning("No t-SNE data found.")
