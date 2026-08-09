from langgraph.graph import StateGraph, START, END

from graph_nodes import (
    GraphState,
    classify_intent,
    retrieve_and_answer,
    direct_answer,
)
from schemas import AskResponse


def _route_intent(state: GraphState) -> str:
    intent = state["intent"]
    return intent if intent in ("policy_question", "general_question") else "general_question"


def build_graph():
    workflow = StateGraph(GraphState)

    workflow.add_node("classify_intent", classify_intent)
    workflow.add_node("retrieve_and_answer", retrieve_and_answer)
    workflow.add_node("direct_answer", direct_answer)

    workflow.add_edge(START, "classify_intent")

    workflow.add_conditional_edges(
        "classify_intent",
        _route_intent,
        {
            "policy_question": "retrieve_and_answer",
            "general_question": "direct_answer"
        }
    )

    workflow.add_edge("retrieve_and_answer", END)
    workflow.add_edge("direct_answer", END)

    return workflow.compile()


graph = build_graph()


def run_graph(query: str) -> AskResponse:
    state = graph.invoke({
        "query": query,
        "intent": "",
        "retrieved_context": [],
        "answer": "",
        "sources": [],
        "confidence": 0.0
    })

    return AskResponse(
        answer=state["answer"],
        sources=state["sources"],
        confidence=state["confidence"]
    )


if __name__ == "__main__":
    for test_query in [
        "What is the Zepto's refund policy?",
        "What's the weather like today?"
    ]:
        response = run_graph(test_query)
        print(f"\nQuery: {test_query}")
        print(response.model_dump_json(indent=2))
