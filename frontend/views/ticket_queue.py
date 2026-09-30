import pandas as pd
import streamlit as st

import api_calls
from components.assign_panel import assign_panel
from components.notes_panel import notes_panel
from components.resolve_panel import resolve_panel
from session import logout_button, require_login, show_errors

require_login()
logout_button()
st.title("Ticket queue")

STATUSES = ["", "new", "pending_approval", "resolved", "escalated", "needs_human"]
status = st.selectbox("Status filter", STATUSES, format_func=lambda s: s or "all")
tickets = show_errors(lambda: api_calls.list_tickets(status or None)) or []

if not tickets:
    st.info("No tickets yet.")
    st.stop()

columns = ["id", "title", "owner", "assignee", "category", "priority", "status", "resolved_by", "cost_usd"]
st.dataframe(pd.DataFrame(tickets)[columns], hide_index=True, width="stretch")
ticket_id = st.selectbox("Open ticket", [t["id"] for t in tickets])
detail = show_errors(lambda: api_calls.ticket_detail(ticket_id))
if not detail:
    st.stop()

st.write(f"**Status:** {detail['status']}  |  **Assigned to:** {detail['assignee'] or 'nobody'}")
resolved_by = f" (by {detail['resolved_by']})" if detail["resolved_by"] else ""
st.write(f"**Resolution:** {detail['resolution'] or '-'}{resolved_by}")
if detail["actions"]:
    st.table(pd.DataFrame(detail["actions"])[["agent", "decision", "reasoning"]])
else:
    st.info("No agent decisions yet (the ticket has not been processed).")

is_admin = st.session_state.get("role") == "admin"
if is_admin:
    assign_panel(detail)
if is_admin or detail["assignee"] == st.session_state.get("user"):
    resolve_panel(detail)
    notes_panel(detail)
