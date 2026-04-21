import os
import json

def load_ground_truth():
    path = os.path.join(os.path.dirname(__file__), "ground_truth_dataset.json")
    with open(path, "r") as f:
        data = json.load(f)
    return data["questions"]

def evaluate_sql_result(result, question_id):
    if "error" in result:
        return False, f"Error: {result['error']}"
    if "results" not in result or result["results"] is None:
        return False, "No results returned"
    return True, f"Returned {len(result['results'])} row(s)"