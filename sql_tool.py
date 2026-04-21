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
- String values are case-sensitive, use exact casing as stored in the database
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


FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "TRUNCATE", "ALTER", "INSERT", "UPDATE"]

def validate_sql(query):
    """Block any SQL that modifies or destroys data."""
    query_upper = query.upper()
    for keyword in FORBIDDEN_KEYWORDS:
        if keyword in query_upper:
            raise ValueError(f"Query contains forbidden keyword: {keyword}. Only SELECT queries are allowed.")


def run_sql_tool(question, conn, client):
    try:
        sql_query = generate_sql(question, client)
        print(f"Generated SQL: {sql_query}")
        validate_sql(sql_query)
        results = execute_sql(sql_query, conn)
        return {"sql": sql_query, "results": results}
    except Exception as e:
        return {"error": str(e)}