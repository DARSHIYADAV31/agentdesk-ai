import streamlit as st

import api_calls
from session import show_errors

NOBODY = "(nobody)"


def admin_fields() -> dict:
    """Extra inputs shown only to the admin, inside the ticket form."""
    users = show_errors(api_calls.list_users) or []
    names = [u["username"] for u in users]
    me = st.session_state.get("user")
    owner = st.selectbox("Ticket is for (employee)", names,
                         index=names.index(me) if me in names else 0)
    assignee = st.selectbox("Assign to (person who will handle it)", [NOBODY] + names)
    skip_ai = st.checkbox("Send straight to the assignee (skip the AI)")
    return {"owner": owner, "assignee": None if assignee == NOBODY else assignee,
            "skip_ai": skip_ai}
