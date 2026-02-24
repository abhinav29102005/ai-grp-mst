"""
main.py -- Entry point for the Cloud Resource Allocation project.

Usage:
    python main.py                          # launch Streamlit dashboard
    python main.py process <csv_file>       # run ML pipeline then launch dashboard
    python main.py process <csv_file> -k 4  # run ML pipeline with 4 clusters
    python main.py sql                      # print table creation SQL
"""

import sys
import subprocess
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def run_process(csv_path, n_clusters=3):
    cmd = [sys.executable, os.path.join(ROOT, "process.py"), csv_path, "--clusters", str(n_clusters)]
    print(f"Running ML pipeline: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode != 0:
        print("\nPipeline failed. Fix errors above and retry.")
        sys.exit(1)
    print()


def run_dashboard():
    cmd = [sys.executable, "-m", "streamlit", "run", os.path.join(ROOT, "dashboard.py")]
    print("Starting Streamlit dashboard ...\n")
    subprocess.run(cmd, cwd=ROOT)


def print_sql():
    cmd = [sys.executable, os.path.join(ROOT, "setup_supabase.py"), "--sql"]
    subprocess.run(cmd, cwd=ROOT)


def main():
    args = sys.argv[1:]

    if not args:
        run_dashboard()
        return

    command = args[0]

    if command == "sql":
        print_sql()

    elif command == "process":
        if len(args) < 2:
            print("Usage: python main.py process <csv_file> [-k N]")
            sys.exit(1)
        csv_path = args[1]
        n_clusters = 3
        if "-k" in args:
            n_clusters = int(args[args.index("-k") + 1])
        run_process(csv_path, n_clusters)
        run_dashboard()

    else:
        print("Usage:")
        print("  python main.py                          Launch dashboard")
        print("  python main.py process <csv> [-k N]     Run ML pipeline + dashboard")
        print("  python main.py sql                      Print table creation SQL")
        sys.exit(1)


if __name__ == "__main__":
    main()
