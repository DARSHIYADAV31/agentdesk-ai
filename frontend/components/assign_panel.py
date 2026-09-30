import streamlit as st

import api_calls
from session import show_errors

NOBODY = "(unassigned)"


def assign_panel(ticket: dict) -> None:
    """Admin-only: pick the person who will handle this ticket."""
    users = show_errors(api_calls.list_users) or []
    names = [NOBODY] + [u["username"] for u in users]
    current = ticket["assignee"] or NOBODY
    choice = st.selectbox("Assign to", names, key=f"assign-{ticket['id']}",
                          index=names.index(current) if current in names else 0)
    if st.button("Save assignment", key=f"save-{ticket['id']}"):
        assignee = None if choice == NOBODY else choice
        if show_errors(lambda: api_calls.assign_ticket(ticket["id"], assignee)):
            st.rerun()
