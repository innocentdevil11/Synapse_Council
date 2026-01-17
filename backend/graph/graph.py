from langgraph.graph import StateGraph, END

from graph.state import SynapseState
from graph.nodes import (
    ethical_node,
    eq_node,
    risk_node,
    red_team_node,
    values_node,
    aggregator_node,
)


def build_synapse_council_graph():
    graph = StateGraph(SynapseState)

    # Register nodes
    graph.add_node("ethical", ethical_node)
    graph.add_node("eq", eq_node)
    graph.add_node("risk", risk_node)
    graph.add_node("red_team", red_team_node)
    graph.add_node("values", values_node)
    graph.add_node("aggregator", aggregator_node)

    # Entry point
    graph.set_entry_point("ethical")

    # Parallel execution fan-out
    graph.add_edge("ethical", "eq")
    graph.add_edge("ethical", "risk")
    graph.add_edge("ethical", "red_team")
    graph.add_edge("ethical", "values")

    # Fan-in to aggregator
    graph.add_edge("eq", "aggregator")
    graph.add_edge("risk", "aggregator")
    graph.add_edge("red_team", "aggregator")
    graph.add_edge("values", "aggregator")

    # End
    graph.add_edge("aggregator", END)

    return graph.compile()
