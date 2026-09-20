import json
from pathlib import Path
from search import (RUNBOOKS_DIRECTORY, load_runbooks, search_runbooks)

PROJECT_ROOT = Path(__file__).resolve().parent
CASES_FILE = PROJECT_ROOT / "data/cases.json"

with CASES_FILE.open(encoding="utf-8") as file:
    cases = json.load(file)

runbooks = load_runbooks(RUNBOOKS_DIRECTORY)

top_1_correct = 0
top_3_correct = 0

print(f"Loaded {len(cases)} evaluation case(s)")
print(f"Loaded {len(runbooks)} runbook(s)")

for case in cases:
    results = search_runbooks(case["alert"], runbooks)

    predicted_names = [
        result["name"]
        for result in results
    ]

    if predicted_names:
        top_prediction = predicted_names[0]
    else:
        top_prediction = None

    expected = case["expected_runbook"]

    top_1_passed = top_prediction == expected

    if expected is None:
        top_3_passed = len(predicted_names) == 0
    else:
        top_3_passed = expected in predicted_names

    if top_1_passed:
        top_1_correct += 1

    if top_3_passed:
        top_3_correct += 1

    status = "PASS" if top_1_passed else "FAIL"
    candidate_details = [
        (
            f"{result['name']} "
            f"(match={result['score']:.1%}, "
            f"body={result['body_score']:.1%}, "
            f"filename={result['filename_score']:.1%})"
        )
        for result in results
    ]

    candidates = ", ".join(candidate_details) or "no match"
    
    print()
    print(f"[{status}] {case['id']}")
    print(f"    Expected: {expected or 'no match'}")
    print(f"    Predicted: {top_prediction or 'no match'}")
    print(f"    Candidates: {candidates}")

case_count = len(cases)

top_1_accuracy = top_1_correct / case_count * 100
top_3_accuracy = top_3_correct / case_count * 100

print()
print("Evaluation summary")
print("------------------")
print(f"Top-1 correct: {top_1_correct}/{case_count}")
print(f"Top-1 accuracy: {top_1_accuracy:.1f}%")
print(f"Top-3 correct: {top_3_correct}/{case_count}")
print(f"Top-3 accuracy: {top_3_accuracy:.1f}%")

if top_1_correct < case_count:
    raise SystemExit(1)