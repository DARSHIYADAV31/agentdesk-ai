from collections import Counter


def accuracy(results: list[dict]) -> float:
    if not results:
        return 0.0
    return sum(r["expected"] == r["predicted"] for r in results) / len(results)


def confusion(results: list[dict]) -> dict:
    """Counts of (expected -> predicted) for the misclassified rows only."""
    wrong = Counter((r["expected"], r["predicted"]) for r in results
                    if r["expected"] != r["predicted"])
    return {f"{expected} -> {predicted}": n for (expected, predicted), n in wrong.items()}
