from sqlalchemy import select

from app.db.audit_model import AuditLog
from tests.unit.test_api_assign import assign, auth, setup


def note(client, ticket_id, headers, text="Called the user, checking the router."):
    return client.post(f"/tickets/{ticket_id}/notes", json={"text": text}, headers=headers)


def test_admin_and_assignee_can_add_notes_and_both_see_them(client):
    _, sam, ticket_id = setup(client)
    root = auth(client, "root")
    assign(client, ticket_id, "sam", root)
    assert note(client, ticket_id, root, "Assigned to Sam").status_code == 201
    assert note(client, ticket_id, sam, "On it").status_code == 201
    for headers in (root, sam):
        notes = client.get(f"/tickets/{ticket_id}", headers=headers).json()["notes"]
        assert [n["author"] for n in notes] == ["root", "sam"]


def test_requester_cannot_write_or_read_internal_notes(client):
    alice, _, ticket_id = setup(client)
    note(client, ticket_id, auth(client, "root"))
    assert note(client, ticket_id, alice).status_code == 403
    assert client.get(f"/tickets/{ticket_id}", headers=alice).json()["notes"] == []


def test_unrelated_user_gets_404_and_empty_note_is_rejected(client):
    _, sam, ticket_id = setup(client)
    assert note(client, ticket_id, sam).status_code == 404
    assert note(client, ticket_id, auth(client, "root"), "   ").status_code == 422


def test_note_is_audited_without_its_text(client, db):
    _, _, ticket_id = setup(client)
    note(client, ticket_id, auth(client, "root"), "secret customer detail")
    row = db.scalars(select(AuditLog).where(AuditLog.action == "note:add")).one()
    assert row.status == "succeeded" and "secret" not in row.detail
