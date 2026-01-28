from langgraph.graph import StateGraph, START, END
from app.graph.state import ReviewInputState, ReviewOutputState, ReviewState
from app.graph.nodes import retriever, searcher, reviewer

graph_builder = StateGraph(state_schema=ReviewState, input_schema=ReviewInputState, output_schema=ReviewOutputState, output_schema=ReviewOutputState)

graph_builder.add_node("retriever", retriever)
graph_builder.add_node("searcher", searcher)
graph_builder.add_node("reviewer", reviewer)

# 1. 시작 -> 로컬 리트리버
graph_builder.add_edge(START, "retriever")

# 2. 리트리버 결과 확인
graph_builder.add_conditional_edges(
    "retriever",
    lambda state: "search" if state.get("solution") is None else "review",
    {
        "search": "searcher",
        "review": "reviewer"
    }
)
graph_builder.add_edge("searcher", "reviewer")
graph_builder.add_edge("reviewer", END)

graph = graph_builder.compile()