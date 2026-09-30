from evals.metrics import accuracy, confusion
from evals.runner import evaluate, load_dataset
from app.llm.errors import LLMUnavailableError


class PerfectRouter:
    """Answers with whatever category the dataset expects, keyed by title."""

    def __init__(self, rows):
        self.by_title = {r["title"]: r["expected_category"] for r in rows}

    def invoke(self, messages, ticket_id="-"):
        title = messages[1][1].split("\n")[0].removeprefix("Title: ")
        content = f'{{"category":"{self.by_title[title]}","priority":"low"}}'
        return type("R", (), {"content": content})(), None


class DownRouter:
    def invoke(self, messages, ticket_id="-"):
        raise LLMUnavailableError("down")


def test_dataset_is_labeled_and_covers_every_category():
    rows = load_dataset()
    assert len(rows) >= 20
    assert {r["expected_category"] for r in rows} >= {
        "hardware", "software", "network", "access", "account", "billing", "other"}


def test_perfect_classifier_scores_100_percent():
    rows = load_dataset()
    assert accuracy(evaluate(PerfectRouter(rows), rows)) == 1.0


def test_llm_outage_counts_as_wrong_not_skipped():
    rows = load_dataset()
    results = evaluate(DownRouter(), rows)
    assert len(results) == len(rows) and accuracy(results) == 0.0


def test_confusion_lists_only_mistakes():
    results = [{"expected": "network", "predicted": "network"},
               {"expected": "network", "predicted": "access"}]
    assert confusion(results) == {"network -> access": 1}
