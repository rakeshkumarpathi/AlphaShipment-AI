from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.exception_detection import detect_exception
from src.llm_analysis import analyze_shipment_with_ai
from src.rag.retriever import retrieve_for_shipment
from src.guardrails.rules import validate_ai_result


app = FastAPI(
    title="AlphaShipment AI",
    description="AI-Powered Shipment Exception & Operations Automation Platform",
    version="1.0.0"
)


CSV_PATH = Path(__file__).resolve().parent.parent / "data" / "shipments.csv"

shipments_df = pd.read_csv(CSV_PATH)


class ShipmentRequest(BaseModel):
    shipment_id: str


@app.post("/ai-analyze")
def ai_analyze_shipment(request: ShipmentRequest):

    shipment_id = request.shipment_id

    # Find shipment in CSV
    shipment = shipments_df[
        shipments_df["shipment_id"] == shipment_id
    ]

    if shipment.empty:
        raise HTTPException(
            status_code=404,
            detail=f"Shipment {shipment_id} not found"
        )

    # Convert matching row to dictionary
    shipment_data = shipment.iloc[0].to_dict()

    # Handle NaN values
    shipment_data = {
        key: None if pd.isna(value) else value
        for key, value in shipment_data.items()
    }

    # Deterministic exception analysis
    exception_result = detect_exception(shipment_data)

    if not exception_result["exception"]:
        return {
            "shipment_id": shipment_id,
            "exception_analysis": exception_result,
            "retrieved_context": [],
            "ai_analysis": None,
            "guardrails": {
                "passed": True,
                "errors": []
            }
        }

    # RAG retrieval
    retrieved_context = retrieve_for_shipment(
        shipment_data,
        exception_result
    )

    # Generative AI analysis
    ai_result = analyze_shipment_with_ai(
        shipment_data,
        exception_result,
        retrieved_context
    )

    # Business guardrails
    guardrail_errors = validate_ai_result(
        ai_result,
        exception_result
    )

    if guardrail_errors:
        raise HTTPException(
            status_code=422,
            detail={
                "message": "AI recommendation failed business guardrails.",
                "errors": guardrail_errors,
                "action_code": ai_result.action_code.value,
                "severity": exception_result["severity"],
            }
        )

    return {
        "shipment_id": shipment_id,
        "exception_analysis": exception_result,
        "retrieved_context": retrieved_context,
        "ai_analysis": ai_result.model_dump(),
        "guardrails": {
            "passed": True,
            "errors": []
        }
    }