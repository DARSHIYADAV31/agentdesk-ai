import streamlit as st

import api_calls
from api_errors import ApiError

st.set_page_config(page_title="AgentDesk AI", page_icon="🎫", layout="wide")

DASHBOARD = st.Page("views/dashboard.py", title="Dashboard", icon="📊", default=True)
SUBMIT = st.Page("views/submit_ticket.py", title="Submit Ticket", icon="📝")
QUEUE = st.Page("views/ticket_queue.py", title="Ticket Queue", icon="📋")
APPROVALS = st.Page("views/approvals.py", title="Approvals", icon="✅")
AUDIT = st.Page("views/audit_trail.py", title="Audit Trail", icon="🧾")
LOGIN = [st.Page("views/login.py", title="Log in", icon="🔐", default=True)]


def ensure_role() -> None:
    """Look up the role once per session; an invalid session is signed out."""
    if "role" in st.session_state:
        return
    try:
        st.session_state["role"] = api_calls.me()["role"]
    except ApiError:
        st.session_state.clear()


if st.session_state.get("access"):
    ensure_role()

# Only the login page exists until a session is started, so nothing else is reachable.
if not st.session_state.get("access"):
    pages = LOGIN
else:
    admin_only = [APPROVALS] if st.session_state.get("role") == "admin" else []
    pages = [DASHBOARD, SUBMIT, QUEUE, *admin_only, AUDIT]
st.navigation(pages).run()
