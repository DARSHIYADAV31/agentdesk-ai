import json
from pathlib import Path

from app.agents.classifier import classify
from app.llm.errors import LLMUnavailableError

DATASET = Path(__file__).parent / "dataset.jsonl"


def load_dataset(path: Path = DATASET) -> list[dict]:
    lines = path.read_text(encoding="utf-8").splitlines()
    return [json.loads(line) for line in lines if line.strip()]


def evaluate(router, rows: list[dict]) -> list[dict]:
    results = []
    for index, row in enumerate(rows):
        try:
            predicted = classify(router, row["title"], row["body"], f"eval-{index}").category
        except LLMUnavailableError:
            predicted = "error"  # counted as wrong, never skipped
        results.append({"title": row["title"], "expected": row["expected_category"],
                        "predicted": predicted})
    return results
