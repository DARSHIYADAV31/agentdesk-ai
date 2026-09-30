import pandas as pd
import streamlit as st

import api_calls
from session import logout_button, require_login, show_errors

require_login()
logout_button()
st.title("Audit trail")

ticket_id = st.number_input("Filter by ticket id (0 = all)", min_value=0, step=1)
rows = show_errors(lambda: api_calls.list_audit(int(ticket_id) or None)) or []

if rows:
    columns = ["created_at", "ticket_id", "actor", "action", "status", "detail"]
    st.dataframe(pd.DataFrame(rows)[columns], hide_index=True, width="stretch")
else:
    st.info("No audit entries.")
