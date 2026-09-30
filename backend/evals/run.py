import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

from app.config import get_settings
from app.llm.gemini import build_gemini
from app.llm.mistral import build_mistral
from app.llm.router import LLMRouter
from evals.metrics import accuracy, confusion
from evals.runner import evaluate, load_dataset

RESULTS_DIR = Path(__file__).parent / "results"


def save_report(report: dict) -> Path:
    RESULTS_DIR.mkdir(exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    path = RESULTS_DIR / f"eval-{stamp}.json"
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return path


def main() -> int:
    settings = get_settings()
    router = LLMRouter(build_gemini(settings), build_mistral(settings),
                       attempts=settings.llm_max_attempts)
    results = evaluate(router, load_dataset())
    score = accuracy(results)
    report = {"accuracy": score, "total": len(results), "errors": confusion(results),
              "results": results}
    path = save_report(report)
    threshold = float(os.getenv("EVAL_MIN_ACCURACY", "0.85"))
    print(f"Accuracy {score:.1%} over {len(results)} tickets (min {threshold:.0%}) -> {path}")
    return 0 if score >= threshold else 1


if __name__ == "__main__":
    sys.exit(main())
