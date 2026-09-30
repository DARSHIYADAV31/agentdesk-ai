import re

import streamlit as st

import api_calls
from components.admin_fields import admin_fields
from session import logout_button, require_login, show_errors

require_login()
logout_button()
st.title("Submit a ticket")

EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
is_admin = st.session_state.get("role") == "admin"


def problems(title: str, body: str, email: str, extras: dict) -> list[str]:
    found = []
    if not 5 <= len(title.strip()) <= 200:
        found.append("Title must be 5-200 characters.")
    if not 10 <= len(body.strip()) <= 5000:
        found.append("Description must be 10-5000 characters.")
    if not EMAIL.match(email.strip()):
        found.append("Enter a valid email address.")
    if extras.get("skip_ai") and not extras.get("assignee"):
        found.append("Choose who to assign it to, or untick 'skip the AI'.")
    return found


def send(title: str, body: str, email: str, extras: dict):
    if is_admin:
        return api_calls.admin_create_ticket(title, body, email, **extras)
    return api_calls.submit_ticket(title, body, email)


with st.form("ticket", clear_on_submit=True):
    title = st.text_input("Title", max_chars=200)
    body = st.text_area("Description", max_chars=5000, height=200)
    email = st.text_input("Your email" if not is_admin else "Employee email")
    extras = admin_fields() if is_admin else {}
    submitted = st.form_submit_button("Submit ticket")

if submitted:
    errors = problems(title, body, email, extras)
    for message in errors:
        st.error(message)
    if not errors:
        ticket = show_errors(lambda: send(title, body, email, extras))
        if ticket:
            st.success(f"Ticket #{ticket['id']} created (status: {ticket['status']}).")
