import sqlite3
import pandas as pd
import os

CSV_LOAD_ORDER = [
    ("sectors", "data/sectors.csv"),
    ("benchmarks", "data/benchmarks.csv"),
    ("portfolios", "data/portfolios.csv"),
    ("securities", "data/securities.csv"),
    ("holdings", "data/holdings.csv"),
    ("transactions", "data/transactions.csv"),
    ("historical_prices", "data/historical_prices.csv"),
    ("portfolio_performance", "data/portfolio_performance.csv"),
    ("risk_metrics", "data/risk_metrics.csv"),
]


def create_connection():
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def load_schema(conn):
    schema_path = os.path.join(os.path.dirname(__file__), "database_schema.sql")
    try:
        with open(schema_path, "r") as f:
            schema = f.read()
        conn.executescript(schema)
        print("Schema loaded - all tables created")
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")
    except sqlite3.Error as e:
        raise RuntimeError(f"Failed to execute schema: {e}")


def load_csv_data(conn):
    base_dir = os.path.dirname(__file__)
    for table_name, csv_path in CSV_LOAD_ORDER:
        full_path = os.path.join(base_dir, csv_path)
        try:
            if not os.path.exists(full_path):
                print(f"Missing: {csv_path} - skipping")
                continue
            df = pd.read_csv(full_path)
            df.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"Loaded {len(df)} rows into '{table_name}'")
        except Exception as e:
            print(f"Failed to load '{table_name}': {e}")