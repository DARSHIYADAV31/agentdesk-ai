from collections import Counter

import streamlit as st

import api_calls
from session import logout_button, require_login, show_errors

require_login()
logout_button()
st.title("Dashboard")
st.caption(f"Signed in as {st.session_state.get('user', '')}")

tickets = show_errors(api_calls.list_tickets) or []
counts = Counter(t["status"] for t in tickets)
cols = st.columns(4)
cols[0].metric("Tickets", len(tickets))
cols[1].metric("Pending approval", counts["pending_approval"])
cols[2].metric("Needs human", counts["needs_human"])
cols[3].metric("LLM cost (USD)", f"{sum(t['cost_usd'] for t in tickets):.4f}")
if counts:
    st.bar_chart(counts)
