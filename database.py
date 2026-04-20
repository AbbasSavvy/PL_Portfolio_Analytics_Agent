import sqlite3
import pandas as pd
import os


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