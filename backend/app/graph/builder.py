from langgraph.graph import END, StateGraph

from app.graph.guard import guarded
from app.graph.node_final import make_final_node
from app.graph.nodes_action import make_action_node
from app.graph.nodes_analyze import make_classify_node, make_kb_node
from app.graph.state import Deps, PipelineState


def _next_or_final(next_node: str):
    return lambda state: "final" if state.get("error") else next_node


def build_graph(deps: Deps):
    graph = StateGraph(PipelineState)
    graph.add_node("classify", guarded(deps, "classify", make_classify_node(deps)))
    graph.add_node("kb", guarded(deps, "kb", make_kb_node(deps)))
    graph.add_node("action", guarded(deps, "action", make_action_node(deps)))
    graph.add_node("final", make_final_node(deps))
    graph.set_entry_point("classify")
    graph.add_conditional_edges("classify", _next_or_final("kb"), ["kb", "final"])
    graph.add_conditional_edges("kb", _next_or_final("action"), ["action", "final"])
    graph.add_edge("action", "final")
    graph.add_edge("final", END)
    return graph.compile()
