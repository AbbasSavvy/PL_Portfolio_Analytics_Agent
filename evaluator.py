import os
import json
from database import setup_database
import time
from agent import create_client, answer_question

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

def evaluate_exposure_result(result, question_id):
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

        print(f"Q{question_id} [{difficulty}] {question_text}")

        try:
            result = answer_question(question_text, conn, client)

            if question_type == "exposure_calculator":
                success, message = evaluate_exposure_result(result, question_id)
            else:
                success, message = evaluate_sql_result(result, question_id)

            if success:
                print(f"  PASS - {message}")
                passed += 1
            else:
                print(f"  FAIL - {message}")
                failed += 1

        except Exception as e:
            print(f"  FAIL - Exception: {e}")
            failed += 1

        # time.sleep(15)
        print()

    print("-" * 60)
    print(f"Results: {passed}/{len(questions)} passed ({(passed / len(questions)) * 100:.0f}%)")


if __name__ == "__main__":
    run_evaluation()