from app.db.ticket_repo import save_cost, set_status
from app.graph.state import Deps


def make_final_node(deps: Deps):
    def node(state):
        ticket_id = state["ticket_id"]
        if state.get("error"):
            set_status(deps.db, ticket_id, "needs_human")
        summary = deps.router.tracker.summarize(str(ticket_id))
        save_cost(deps.db, ticket_id, summary["cost_usd"])
        return {"outcome": "needs_human"} if state.get("error") else {}

    return node
