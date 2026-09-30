import json
import re


def extract_json(text: str) -> dict:
    """Pull the first JSON object out of a reply, tolerating code fences."""
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError("no JSON object in model output")
    return json.loads(match.group(0))
