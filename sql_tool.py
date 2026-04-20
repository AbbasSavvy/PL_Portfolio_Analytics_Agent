import os
import re
import sqlite3

def get_schema_for_prompt():
    schema_path = os.path.join(os.path.dirname(__file__), "database_schema.sql")
    try:
        with open(schema_path, "r") as f:
            schema = f.read()
        table_blocks = re.findall(r"CREATE TABLE.*?;", schema, re.DOTALL | re.IGNORECASE)
        return "\n\n".join(table_blocks)
    except FileNotFoundError:
        raise FileNotFoundError(f"Schema file not found at: {schema_path}")


def generate_sql(question, client):
    schema = get_schema_for_prompt()
    prompt = f"""You are a SQL expert working with a SQLite database.

Given this schema:
{schema}

Write a SQL query to answer this question: "{question}"

Rules:
- Return only the SQL query, no explanation or markdown
- Do not wrap the query in backticks or code blocks
- Use only tables and columns that exist in the schema above
"""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    return response.text.strip()



def execute_sql(query, conn):
    try:
        cursor = conn.execute(query)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except sqlite3.Error as e:
        raise RuntimeError(f"SQL execution failed: {e}\nQuery: {query}")