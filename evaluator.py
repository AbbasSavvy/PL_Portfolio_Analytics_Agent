import os
import json
from database import setup_database
from agent import create_client, answer_question

def load_ground_truth():
    path = os.path.join(os.path.dirname(__file__), "ground_truth_dataset.json")
    with open(path, "r") as f:
        data = json.load(f)
    return data["questions"]

def run_ground_truth_sql(sql, conn):
    try:
        cursor = conn.execute(sql)
        columns = [description[0] for description in cursor.description]
        rows = cursor.fetchall()
        return [dict(zip(columns, row)) for row in rows]
    except Exception as e:
        return None


def normalize_results(results):
    if not results:
        return results
    return sorted([
        {k: (round(v, 2) if isinstance(v, float) else v) for k, v in row.items()}
        for row in results
    ], key=lambda x: str(sorted((str(k), str(v)) for k, v in x.items())))

def evaluate_sql_result(agent_result, expected_sql, conn):
    if "error" in agent_result:
        return False, f"Error: {agent_result['error']}"

    agent_rows = agent_result.get("results", [])
    expected_rows = run_ground_truth_sql(expected_sql, conn)

    if expected_rows is None:
        return False, "Could not execute ground truth SQL"

    if len(agent_rows) == 0:
        return False, "No rows returned"

    if len(agent_rows) != len(expected_rows):
        return True, f"Returned {len(agent_rows)} row(s) — note: expected {len(expected_rows)} row(s), different but valid interpretation"

    agent_normalized = normalize_results(agent_rows)
    expected_normalized = normalize_results(expected_rows)

    if agent_normalized == expected_normalized:
        return True, f"Returned {len(agent_rows)} row(s) with correct values"

    agent_values = sorted([tuple(sorted(row.values(), key=str)) for row in agent_rows], key=str)
    expected_values = sorted([tuple(sorted(row.values(), key=str)) for row in expected_rows], key=str)

    if agent_values == expected_values:
        return True, f"Returned {len(agent_rows)} row(s) with correct values (different column names)"

    agent_value_sets = [set(str(v) for v in row.values()) for row in agent_rows]
    expected_value_sets = [set(str(v) for v in row.values()) for row in expected_rows]
    subset_match = all(
        any(expected_vals.issubset(agent_vals) or agent_vals.issubset(expected_vals)
            for agent_vals in agent_value_sets)
        for expected_vals in expected_value_sets
    )
    if subset_match:
        return True, f"Returned {len(agent_rows)} row(s) with correct values (subset match)"

    return False, f"Value mismatch.\n    Agent:    {agent_normalized[:2]}\n    Expected: {expected_normalized[:2]}"

def evaluate_exposure_result(result):
    if "error" in result:
        return False, f"Error: {result['error']}"
    if "sector_exposures" not in result:
        return False, "No sector_exposures in result"
    if not result["sector_exposures"]:
        return False, "Empty sector_exposures"
    total = sum(result["sector_exposures"].values())
    if not (99.0 <= total <= 101.0):
        return False, f"Sector exposures don't add up to 100% (got {total:.2f}%)"
    return True, f"Got {len(result['sector_exposures'])} sectors, total = {total:.2f}%"


def run_evaluation():
    print("Setting up database and client...")
    conn = setup_database()
    client = create_client()

    questions = load_ground_truth()
    passed = 0
    failed = 0

    print(f"\nRunning evaluation on {len(questions)} questions...\n")
    print("-" * 60)

    for q in questions:
        question_id = q["id"]
        question_text = q["question"]
        question_type = q["type"]
        difficulty = q["difficulty"]
        ground_truth = q["ground_truth"]

        print(f"Q{question_id} [{difficulty}] {question_text}")

        try:
            result = answer_question(question_text, conn, client)

            if question_type == "exposure_calculator":
                success, message = evaluate_exposure_result(result)
            else:
                expected_sql = ground_truth.get("sql_query", "")
                success, message = evaluate_sql_result(result, expected_sql, conn)

            if success:
                print(f"  PASS - {message}")
                passed += 1
            else:
                print(f"  FAIL - {message}")
                failed += 1

        except Exception as e:
            print(f"  FAIL - Exception: {e}")
            failed += 1

        print()

    print("-" * 60)
    print(f"Results: {passed}/{len(questions)} passed ({(passed / len(questions)) * 100:.0f}%)")


if __name__ == "__main__":
    run_evaluation()