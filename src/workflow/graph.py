from typing import Any, TypedDict

from langgraph.graph import END, START, StateGraph

from src.exception_detection import detect_exception
from src.guardrails.rules import validate_ai_result
from src.llm_analysis import analyze_shipment_with_ai
from src.rag.retriever import retrieve_for_shipment


class ShipmentState(TypedDict, total=False):
    shipment: dict
    deterministic: dict
    retrieved_context: list[dict]
    ai_result: Any
    guardrail_errors: list[str]


def validate_node(state: ShipmentState):
    required_fields = [
        "shipment_id",
        "origin",
        "destination",
        "carrier",
        "status",
        "priority",
        "delay_hours",
    ]

    missing = [
        field
        for field in required_fields
        if field not in state["shipment"]
    ]

    if missing:
        raise ValueError(
            f"Missing required shipment fields: {missing}"
        )

    return {}


def exception_detection_node(state: ShipmentState):
    result = detect_exception(
        state["shipment"]
    )

    return {
        "deterministic": result
    }


def route_after_exception(state: ShipmentState):
    if not state["deterministic"]["exception"]:
        return "end"

    return "retrieve"


def retrieve_node(state: ShipmentState):
    context = retrieve_for_shipment(
        state["shipment"],
        state["deterministic"],
    )

    return {
        "retrieved_context": context
    }


def llm_analysis_node(state: ShipmentState):
    result = analyze_shipment_with_ai(
        state["shipment"],
        state["deterministic"],
        state["retrieved_context"],
    )

    return {
        "ai_result": result
    }


def guardrail_node(state: ShipmentState):
    errors = validate_ai_result(
        state["ai_result"],
        state["deterministic"],
    )

    return {
        "guardrail_errors": errors
    }


def build_graph():
    graph = StateGraph(ShipmentState)

    graph.add_node(
        "validate",
        validate_node,
    )

    graph.add_node(
        "exception_detection",
        exception_detection_node,
    )

    graph.add_node(
        "retrieve",
        retrieve_node,
    )

    graph.add_node(
        "llm_analysis",
        llm_analysis_node,
    )

    graph.add_node(
        "guardrails",
        guardrail_node,
    )

    graph.add_edge(
        START,
        "validate",
    )

    graph.add_edge(
        "validate",
        "exception_detection",
    )

    graph.add_conditional_edges(
        "exception_detection",
        route_after_exception,
        {
            "retrieve": "retrieve",
            "end": END,
        },
    )

    graph.add_edge(
        "retrieve",
        "llm_analysis",
    )

    graph.add_edge(
        "llm_analysis",
        "guardrails",
    )

    graph.add_edge(
        "guardrails",
        END,
    )

    return graph.compile()


workflow = build_graph()