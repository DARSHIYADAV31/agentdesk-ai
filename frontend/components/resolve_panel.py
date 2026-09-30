import streamlit as st

import api_calls
from session import show_errors

HUMAN_STATES = ("escalated", "needs_human")


def resolve_panel(ticket: dict) -> None:
    """Admin or assignee: close a ticket the AI could not solve."""
    if ticket["status"] not in HUMAN_STATES:
        return
    st.subheader("Resolve this ticket")
    with st.form(f"resolve-{ticket['id']}", clear_on_submit=True):
        text = st.text_area("What was done to fix it?", max_chars=2000)
        submitted = st.form_submit_button("Mark resolved", type="primary")
    if submitted and not text.strip():
        st.error("Please describe how it was resolved.")
    elif submitted:
        if show_errors(lambda: api_calls.resolve_ticket(ticket["id"], text)):
            st.rerun()
