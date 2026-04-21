import os
import json

def load_ground_truth():
    path = os.path.join(os.path.dirname(__file__), "ground_truth_dataset.json")
    with open(path, "r") as f:
        data = json.load(f)
    return data["questions"]

