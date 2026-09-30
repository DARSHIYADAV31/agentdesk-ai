import os

import requests
import streamlit as st

from api_errors import ApiError, describe

BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
TIMEOUT_SECONDS = 15


def _send(method: str, path: str, **kwargs) -> requests.Response:
    headers = {"Authorization": f"Bearer {st.session_state.get('access', '')}"}
    try:
        return requests.request(method, BASE_URL + path, headers=headers,
                                timeout=TIMEOUT_SECONDS, **kwargs)
    except requests.RequestException:
        raise ApiError("Cannot reach the API. Is the backend running?")


def _refresh() -> bool:
    token = st.session_state.get("refresh")
    if not token:
        return False
    response = _send("POST", "/auth/refresh", json={"refresh_token": token})
    if not response.ok:
        return False
    st.session_state.update(access=response.json()["access_token"],
                            refresh=response.json()["refresh_token"])
    return True


def request(method: str, path: str, **kwargs):
    response = _send(method, path, **kwargs)
    if response.status_code == 401 and _refresh():
        response = _send(method, path, **kwargs)
    if not response.ok:
        raise ApiError(describe(response))
    return response.json()
