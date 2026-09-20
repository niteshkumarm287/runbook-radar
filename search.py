from pathlib import Path

from sklearn.feature_extraction.text import (
    ENGLISH_STOP_WORDS,
    TfidfVectorizer,
)
from sklearn.metrics.pairwise import cosine_similarity

import os
import re

PROJECT_ROOT = Path(__file__).resolve().parent
RUNBOOKS_DIRECTORY = Path(
    os.environ.get(
        "RUNBOOK_RADAR_RUNBOOKS_DIR",
        PROJECT_ROOT / "runbooks",
    )
)

MINIMUM_SIMILARITY = 0.30
MINIMUM_FILENAME_TERM_MATCHES = 2

GENERIC_ALERT_TERMS = {
    "500",
    "502",
    "503",
    "504",
    "5xx",
    "alert",
    "api",
    "critical",
    "error",
    "errors",
    "failed",
    "failure",
    "failures",
    "high",
    "low",
    "production",
    "unavailable",
    "warning",
}


def extract_terms(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def load_runbooks(directory):
    runbooks = []

    for runbook_path in sorted(directory.rglob("*.md")):
        runbook_text = runbook_path.read_text(encoding="utf-8")

        relative_name = runbook_path.relative_to(directory).with_suffix("")

        normalized_name = " ".join(
            re.findall(
                r"[a-z0-9]+",
                str(relative_name).lower(),
            )
        )

        runbooks.append(
            {
                "name": str(relative_name),
                "path": runbook_path,
                "text": runbook_text,
                "normalized_name": normalized_name,
            }
        )

    return runbooks


def search_runbooks(
    query,
    runbooks,
    limit=3,
    minimum_similarity=MINIMUM_SIMILARITY,
):
    if limit < 0:
        raise ValueError("limit must be non-negative")
    if not 0 <= minimum_similarity <= 1:
        raise ValueError("minimum_similarity must be between 0 and 1")
    if not runbooks or not query.strip() or limit == 0:
        return []

    query_terms = extract_terms(query)

    distinctive_query_terms = (
        query_terms - GENERIC_ALERT_TERMS - set(ENGLISH_STOP_WORDS)
    )

    runbook_texts = [runbook["text"] for runbook in runbooks]

    runbook_names = [runbook["normalized_name"] for runbook in runbooks]

    body_vectorizer = TfidfVectorizer(stop_words="english")

    try:
        body_vectors = body_vectorizer.fit_transform(runbook_texts)
    except ValueError as error:
        if "empty vocabulary" not in str(error):
            raise
        body_scores = [0.0] * len(runbooks)
    else:
        query_body_vector = body_vectorizer.transform([query])
        body_scores = cosine_similarity(query_body_vector, body_vectors).flatten()

    filename_vectorizer = TfidfVectorizer(
        analyzer="char_wb",
        ngram_range=(3, 5),
    )

    try:
        filename_vectors = filename_vectorizer.fit_transform(runbook_names)
    except ValueError as error:
        if "empty vocabulary" not in str(error):
            raise
        filename_scores = [0.0] * len(runbooks)
    else:
        query_filename_vector = filename_vectorizer.transform([query])
        filename_scores = cosine_similarity(
            query_filename_vector, filename_vectors
        ).flatten()

    effective_filename_scores = []
    match_scores = []

    for index, runbook in enumerate(runbooks):
        filename_terms = extract_terms(runbook["normalized_name"])

        filename_term_matches = distinctive_query_terms & filename_terms

        raw_filename_score = float(filename_scores[index])

        if len(filename_term_matches) >= MINIMUM_FILENAME_TERM_MATCHES:
            effective_filename_score = raw_filename_score
        else:
            effective_filename_score = 0.0

        effective_filename_scores.append(effective_filename_score)

        match_scores.append(
            max(
                float(body_scores[index]),
                effective_filename_score,
            )
        )

    ranked_indices = sorted(
        range(len(runbooks)),
        key=lambda index: match_scores[index],
        reverse=True,
    )

    results = []

    for index in ranked_indices:
        score = match_scores[index]

        if score < minimum_similarity:
            break

        runbook_terms = extract_terms(
            runbooks[index]["normalized_name"] + " " + runbooks[index]["text"]
        )

        distinctive_matches = distinctive_query_terms & runbook_terms

        if distinctive_query_terms and not distinctive_matches:
            continue

        results.append(
            {
                "name": runbooks[index]["name"],
                "path": runbooks[index]["path"],
                "score": score,
                "body_score": float(body_scores[index]),
                "filename_score": effective_filename_scores[index],
            }
        )

        if len(results) == limit:
            break

    return results


if __name__ == "__main__":
    if not RUNBOOKS_DIRECTORY.is_dir():
        print(
            "Runbook directory does not exist:",
            RUNBOOKS_DIRECTORY,
        )
        raise SystemExit(1)

    runbooks = load_runbooks(RUNBOOKS_DIRECTORY)

    if not runbooks:
        print(
            "No Markdown runbooks found in:",
            RUNBOOKS_DIRECTORY,
        )
        raise SystemExit(1)

    query = input("Enter alert name: ").strip()

    if not query:
        print("Alert text cannot be empty.")
        raise SystemExit(1)

    results = search_runbooks(query, runbooks)

    print("Alert:", query)
    print()

    if not results:
        print("No reliable runbook match found.")
    else:
        for rank, result in enumerate(results, start=1):
            print(f"{rank}. {result['name']} (match score: {result['score']:.1%})")
