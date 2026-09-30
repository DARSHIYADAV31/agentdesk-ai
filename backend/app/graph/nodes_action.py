from app.agents.action import decide_action
from app.db.ticket_repo import record_action, set_status
from app.graph.state import Deps
from app.schemas.kb_answer import KBAnswer
from app.tools.approval_gate import run_tool
from app.tools.errors import ApprovalRequired


def make_action_node(deps: Deps):
    def node(state):
        ticket_id = state["ticket_id"]
        decision = decide_action(deps.router, ticket_id, state["title"], state["category"],
                                 state["priority"], KBAnswer(**state["kb"]))
        record_action(deps.db, ticket_id, "action", decision.name, decision.reasoning)
        try:
            run_tool(deps.db, deps.backend, ticket_id, decision.name, decision.args)
        except ApprovalRequired as pending:
            set_status(deps.db, ticket_id, "pending_approval")
            return {"outcome": "pending_approval", "approval_id": pending.approval_id}
        return {"outcome": "resolved" if decision.name == "update_ticket" else "escalated"}

    return node
