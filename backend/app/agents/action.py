import logging

from app.agents.policy import ActionDecision, apply_policy
from app.agents.prompts import ACTION_SYSTEM
from app.logging_setup import log_event
from app.schemas.kb_answer import KBAnswer
from app.tools.schemas import TOOL_SCHEMAS

logger = logging.getLogger("agent.action")


def first_tool_call(response):
    calls = getattr(response, "tool_calls", None) or []
    if not calls:
        return None
    return ActionDecision(calls[0]["name"], dict(calls[0]["args"]), "model tool call")


def decide_action(router, ticket_id: int, title: str, category: str, priority: str,
                  kb: KBAnswer) -> ActionDecision:
    summary = (f"Ticket {ticket_id}: {title}\nCategory: {category}, priority: {priority}\n"
               f"KB can_resolve: {kb.can_resolve}\nKB answer: {kb.answer}")
    response, _ = router.invoke([("system", ACTION_SYSTEM), ("human", summary)],
                                str(ticket_id), tools=TOOL_SCHEMAS)
    decision = apply_policy(first_tool_call(response), kb, ticket_id)
    log_event(logger, logging.INFO, "action_decided", ticket_id=ticket_id, tool=decision.name)
    return decision
