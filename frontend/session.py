import streamlit as st

from api_errors import ApiError


def require_login() -> None:
    """Stop the page unless the user has signed in on the home page."""
    if not st.session_state.get("access"):
        st.warning("Please sign in on the home page first.")
        st.stop()


def show_errors(action):
    """Run action(); show API errors as messages instead of crashing the page."""
    try:
        return action()
    except ApiError as exc:
        st.error(str(exc))
        return None


def logout_button() -> None:
    if st.sidebar.button("Log out"):
        st.session_state.clear()
        st.rerun()


def require_admin() -> None:
    """Stop the page unless the signed-in user is an admin."""
    if st.session_state.get("role") != "admin":
        st.warning("This page is for admins only.")
        st.stop()
