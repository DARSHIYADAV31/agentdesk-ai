from api_client import request


def login(username: str, password: str) -> dict:
    return request("POST", "/auth/login", json={"username": username, "password": password})


def submit_ticket(title: str, body: str, email: str) -> dict:
    return request("POST", "/tickets",
                   json={"title": title, "body": body, "requester_email": email})


def list_tickets(status: str | None = None, limit: int = 100) -> list:
    params = {"limit": limit, **({"status": status} if status else {})}
    return request("GET", "/tickets", params=params)


def ticket_detail(ticket_id: int) -> dict:
    return request("GET", f"/tickets/{ticket_id}")


def list_approvals(status: str = "pending") -> list:
    return request("GET", "/approvals", params={"status": status})


def decide_approval(approval_id: int, approve: bool) -> dict:
    return request("POST", f"/approvals/{approval_id}/decision", json={"approve": approve})


def list_audit(ticket_id: int | None = None, limit: int = 200) -> list:
    params = {"limit": limit, **({"ticket_id": ticket_id} if ticket_id else {})}
    return request("GET", "/audit", params=params)


def register(username: str, password: str) -> dict:
    return request("POST", "/auth/register", json={"username": username, "password": password})


def me() -> dict:
    return request("GET", "/auth/me")


def list_users() -> list:
    return request("GET", "/users")


def assign_ticket(ticket_id: int, assignee: str | None) -> dict:
    return request("POST", f"/tickets/{ticket_id}/assign", json={"assignee": assignee})


def add_note(ticket_id: int, text: str) -> dict:
    return request("POST", f"/tickets/{ticket_id}/notes", json={"text": text})


def resolve_ticket(ticket_id: int, resolution: str) -> dict:
    return request("POST", f"/tickets/{ticket_id}/resolve", json={"resolution": resolution})


def admin_create_ticket(title: str, body: str, email: str, owner: str | None,
                        assignee: str | None, skip_ai: bool) -> dict:
    payload = {"title": title, "body": body, "requester_email": email,
               "owner": owner, "assignee": assignee, "skip_ai": skip_ai}
    return request("POST", "/admin/tickets", json=payload)
