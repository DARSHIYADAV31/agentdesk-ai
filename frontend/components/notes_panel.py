import streamlit as st

import api_calls
from session import show_errors


def notes_panel(ticket: dict) -> None:
    """Internal notes: visible to the admin and the assignee only."""
    st.subheader("Internal notes")
    if not ticket["notes"]:
        st.caption("No notes yet.")
    for note in ticket["notes"]:
        st.markdown(f"**{note['author']}** · {note['created_at'][:16]}")
        st.write(note["text"])
    with st.form(f"note-{ticket['id']}", clear_on_submit=True):
        text = st.text_area("Add a note", max_chars=2000)
        submitted = st.form_submit_button("Add note")
    if submitted and text.strip():
        if show_errors(lambda: api_calls.add_note(ticket["id"], text)):
            st.rerun()
