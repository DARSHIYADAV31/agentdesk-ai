from app.agents.classifier import classify
from app.agents.knowledge import answer_ticket
from app.db.ticket_repo import record_action, save_classification
from app.graph.state import Deps


def make_classify_node(deps: Deps):
    def node(state):
        ticket_id = state["ticket_id"]
        result = classify(deps.router, state["title"], state["body"], str(ticket_id))
        save_classification(deps.db, ticket_id, result.category, result.priority)
        record_action(deps.db, ticket_id, "classifier",
                      f"{result.category}/{result.priority}", result.reasoning)
        return {"category": result.category, "priority": result.priority}

    return node


def make_kb_node(deps: Deps):
    def node(state):
        ticket_id = state["ticket_id"]
        result = answer_ticket(deps.router, deps.retriever, state["title"],
                               state["body"], str(ticket_id))
        record_action(deps.db, ticket_id, "knowledge",
                      f"sources={result.sources}", f"can_resolve={result.can_resolve}")
        return {"kb": result.model_dump()}

    return node
