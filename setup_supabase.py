"""
Supabase setup helper.
Verifies tables exist, or prints the SQL to create them.
Usage:
    python setup_supabase.py          # check if tables exist
    python setup_supabase.py --sql    # print the CREATE TABLE SQL
"""

import requests
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

HEADERS = {
    "apikey": SUPABASE_SERVICE_KEY,
    "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
}

REST_URL = f"{SUPABASE_URL}/rest/v1"

TABLES = ["raw_data", "clustered_data", "cluster_summary", "outlier_counts", "data_stats", "correlation_data", "elbow_data", "tsne_data"]

SQL = """
-- Run this in Supabase SQL Editor (https://supabase.com/dashboard)

CREATE TABLE IF NOT EXISTS raw_data (
    id BIGSERIAL PRIMARY KEY,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    network_usage FLOAT,
    disk_io FLOAT,
    energy_consumption FLOAT,
    service_latency FLOAT,
    task_priority INT,
    workload_type_low INT,
    workload_type_medium INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS clustered_data (
    id BIGSERIAL PRIMARY KEY,
    cpu_usage FLOAT,
    memory_usage FLOAT,
    network_usage FLOAT,
    disk_io FLOAT,
    energy_consumption FLOAT,
    service_latency FLOAT,
    task_priority INT,
    workload_type_low INT,
    workload_type_medium INT,
    cluster_id INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cluster_summary (
    id BIGSERIAL PRIMARY KEY,
    cluster_id INT UNIQUE,
    cpu_usage_mean FLOAT,
    memory_usage_mean FLOAT,
    network_usage_mean FLOAT,
    disk_io_mean FLOAT,
    energy_consumption_mean FLOAT,
    service_latency_mean FLOAT,
    record_count INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS outlier_counts (
    id BIGSERIAL PRIMARY KEY,
    feature_name TEXT UNIQUE,
    outlier_count INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_stats (
    id BIGSERIAL PRIMARY KEY,
    feature_name TEXT UNIQUE,
    mean_val FLOAT,
    std_val FLOAT,
    min_val FLOAT,
    max_val FLOAT,
    median_val FLOAT,
    row_count INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS correlation_data (
    id BIGSERIAL PRIMARY KEY,
    columns_list TEXT,
    matrix_data TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS elbow_data (
    id BIGSERIAL PRIMARY KEY,
    k INT,
    inertia FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS tsne_data (
    id BIGSERIAL PRIMARY KEY,
    x FLOAT,
    y FLOAT,
    cluster_id INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Enable RLS on all tables
ALTER TABLE raw_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE clustered_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE cluster_summary ENABLE ROW LEVEL SECURITY;
ALTER TABLE outlier_counts ENABLE ROW LEVEL SECURITY;
ALTER TABLE data_stats ENABLE ROW LEVEL SECURITY;
ALTER TABLE correlation_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE elbow_data ENABLE ROW LEVEL SECURITY;
ALTER TABLE tsne_data ENABLE ROW LEVEL SECURITY;

-- Anon read policies (frontend reads with anon key)
CREATE POLICY anon_read_raw_data ON raw_data FOR SELECT TO anon USING (true);
CREATE POLICY anon_read_clustered_data ON clustered_data FOR SELECT TO anon USING (true);
CREATE POLICY anon_read_cluster_summary ON cluster_summary FOR SELECT TO anon USING (true);
CREATE POLICY anon_read_outlier_counts ON outlier_counts FOR SELECT TO anon USING (true);
CREATE POLICY anon_read_data_stats ON data_stats FOR SELECT TO anon USING (true);
CREATE POLICY anon_read_correlation_data ON correlation_data FOR SELECT TO anon USING (true);
CREATE POLICY anon_read_elbow_data ON elbow_data FOR SELECT TO anon USING (true);
CREATE POLICY anon_read_tsne_data ON tsne_data FOR SELECT TO anon USING (true);

-- Service role full access (process.py writes with service key)
CREATE POLICY service_all_raw_data ON raw_data FOR ALL TO service_role USING (true);
CREATE POLICY service_all_clustered_data ON clustered_data FOR ALL TO service_role USING (true);
CREATE POLICY service_all_cluster_summary ON cluster_summary FOR ALL TO service_role USING (true);
CREATE POLICY service_all_outlier_counts ON outlier_counts FOR ALL TO service_role USING (true);
CREATE POLICY service_all_data_stats ON data_stats FOR ALL TO service_role USING (true);
CREATE POLICY service_all_correlation_data ON correlation_data FOR ALL TO service_role USING (true);
CREATE POLICY service_all_elbow_data ON elbow_data FOR ALL TO service_role USING (true);
CREATE POLICY service_all_tsne_data ON tsne_data FOR ALL TO service_role USING (true);
"""


def table_exists(name: str) -> bool:
    resp = requests.get(f"{REST_URL}/{name}?limit=0", headers=HEADERS)
    return resp.status_code == 200


def verify():
    print("Checking tables in Supabase...\n")
    all_ok = True
    for t in TABLES:
        ok = table_exists(t)
        if not ok:
            all_ok = False
        print(f"  {t}: {'OK' if ok else 'MISSING'}")
    if not all_ok:
        print("\nSome tables are missing. Copy the SQL below into Supabase SQL Editor:")
        print(SQL)
    else:
        print("\nAll tables exist.")


if __name__ == "__main__":
    import sys
    if "--sql" in sys.argv:
        print(SQL)
    else:
        verify()
