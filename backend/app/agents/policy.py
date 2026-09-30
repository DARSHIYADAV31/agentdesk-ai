from dataclasses import dataclass

from app.schemas.kb_answer import KBAnswer
from app.tools.registry import TOOL_SPECS


@dataclass
class ActionDecision:
    name: str
    args: dict
    reasoning: str = ""


def escalation(ticket_id: int, reason: str) -> ActionDecision:
    return ActionDecision("escalate", {"ticket_id": ticket_id, "reason": reason}, reason)


def apply_policy(decision, kb: KBAnswer, ticket_id: int) -> ActionDecision:
    """Model output is untrusted: constrain it to what the pipeline may do."""
    if decision is None or decision.name not in TOOL_SPECS:
        return escalation(ticket_id, "no valid tool call")
    spec = TOOL_SPECS[decision.name]
    # The model may not target any ticket other than the one being processed.
    args = {k: v for k, v in decision.args.items() if k in spec.params}
    args["ticket_id"] = ticket_id
    if not all(key in args for key in spec.required):
        return escalation(ticket_id, "tool call missing arguments")
    if decision.name == "lookup_ticket":
        return escalation(ticket_id, "lookup is not a resolution")
    if decision.name == "update_ticket" and not (kb.can_resolve and args["status"] == "resolved"):
        return escalation(ticket_id, "no cited knowledge-base solution")
    return ActionDecision(decision.name, args, decision.reasoning)
