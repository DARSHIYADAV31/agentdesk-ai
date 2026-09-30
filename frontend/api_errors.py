import requests


class ApiError(Exception):
    """Message is safe to show to the user."""


def describe(response: requests.Response) -> str:
    try:
        detail = response.json().get("detail")
    except ValueError:
        detail = None
    if isinstance(detail, list):  # FastAPI validation errors
        return "; ".join(f"{'.'.join(map(str, e['loc'][1:]))}: {e['msg']}" for e in detail)
    return detail or f"Request failed ({response.status_code})"
