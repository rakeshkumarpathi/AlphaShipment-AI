import pandas as pd

from src.ai_schema import AIShipmentAnalysis, ActionCode
from src.workflow.graph import workflow


def test_workflow_exception_shipment(monkeypatch):
    df = pd.read_csv("data/shipments.csv")

    # Select the first real exception shipment
    shipment = df[df["delay_hours"] > 0].iloc[0].to_dict()

    def mock_ai_analysis(
        shipment,
        exception_result,
        retrieved_context,
    ):
        if exception_result["severity"] == "CRITICAL":
            action = ActionCode.ESCALATE_CRITICAL
        elif exception_result["severity"] == "HIGH":
            action = ActionCode.ESCALATE_OPERATIONS
        elif exception_result["severity"] == "MEDIUM":
            action = ActionCode.REQUEST_CARRIER_UPDATE
        else:
            action = ActionCode.MONITOR

        return AIShipmentAnalysis(
            business_impact="Test business impact",
            root_cause_analysis="Test root cause",
            action_code=action,
            recommended_action="Test recommended action",
            customer_communication_required=False,
        )

    monkeypatch.setattr(
        "src.workflow.graph.analyze_shipment_with_ai",
        mock_ai_analysis,
    )

    result = workflow.invoke(
        {
            "shipment": shipment
        }
    )

    assert "deterministic" in result
    assert result["deterministic"]["exception"] is True

    assert "retrieved_context" in result
    assert len(result["retrieved_context"]) > 0

    assert "ai_result" in result
    assert result["ai_result"] is not None

    assert "guardrail_errors" in result
    assert result["guardrail_errors"] == []