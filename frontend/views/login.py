import re

import streamlit as st

import api_calls
from session import show_errors

# Signed-out users see no navigation at all.
st.markdown("<style>[data-testid='stSidebar'], [data-testid='stSidebarCollapsedControl']"
            "{display:none}</style>", unsafe_allow_html=True)

USERNAME = re.compile(r"^[A-Za-z0-9_.-]{3,50}$")


def start_session(tokens: dict, username: str) -> None:
    st.session_state.update(access=tokens["access_token"],
                            refresh=tokens["refresh_token"], user=username)
    st.rerun()


def signup_problems(username: str, password: str, confirm: str) -> list[str]:
    found = []
    if not USERNAME.match(username.strip()):
        found.append("Username: 3-50 letters, numbers, dot, dash or underscore.")
    if len(password) < 8:
        found.append("Password must be at least 8 characters.")
    if password != confirm:
        found.append("Passwords do not match.")
    return found


def login_tab() -> None:
    with st.form("login"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Log in", type="primary")
    if submitted:
        tokens = show_errors(lambda: api_calls.login(username, password))
        if tokens:
            start_session(tokens, username)


def signup_tab() -> None:
    with st.form("signup"):
        username = st.text_input("Choose a username")
        password = st.text_input("Choose a password", type="password")
        confirm = st.text_input("Confirm password", type="password")
        submitted = st.form_submit_button("Create account", type="primary")
    if not submitted:
        return
    problems = signup_problems(username, password, confirm)
    for message in problems:
        st.error(message)
    if not problems:
        tokens = show_errors(lambda: api_calls.register(username.strip(), password))
        if tokens:
            start_session(tokens, username.strip())


st.title("AgentDesk AI")
st.caption("Sign in to triage and resolve support tickets.")
login, signup = st.tabs(["Log in", "Sign up"])
with login:
    login_tab()
with signup:
    signup_tab()
