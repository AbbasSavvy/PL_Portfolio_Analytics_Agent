import os
import re


def get_schema_for_prompt():
    schema_path = os.path.join(os.path.dirname(__file__), "database_schema.sql")
    try:
        with open(schema_path, "r") as f:
            schema = f.read()
        table_blocks = re.findall(r"CREATE TABLE.*?;", schema, re.DOTALL | re.IGNORECASE)
        return "\n\n".join(table_blocks)
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")