import streamlit as st

import api_calls
from session import logout_button, require_admin, require_login, show_errors

require_login()
require_admin()
logout_button()
st.title("Pending approvals")
st.caption("Destructive actions run only after an admin approves them here.")

pending = show_errors(api_calls.list_approvals) or []
if not pending:
    st.info("Nothing is waiting for approval.")

for item in pending:
    with st.container(border=True):
        st.write(f"**#{item['id']}** ticket {item['ticket_id']}: `{item['tool']}` {item['args']}")
        approve, reject = st.columns(2)
        if approve.button("Approve", key=f"a{item['id']}"):
            if show_errors(lambda: api_calls.decide_approval(item["id"], True)):
                st.rerun()
        if reject.button("Reject", key=f"r{item['id']}"):
            if show_errors(lambda: api_calls.decide_approval(item["id"], False)):
                st.rerun()
