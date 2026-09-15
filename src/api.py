from pathlib import Path
from unittest import result

import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.workflow.graph import workflow

import logging
from src.logging_config import setup_logging

setup_logging()
logger = logging.getLogger(__name__)


app = FastAPI(
    title="AlphaShipment AI",
    description="AI-Powered Shipment Exception & Operations Automation Platform",
    version="1.0.0"
)


CSV_PATH = (
    Path(__file__).resolve().parent.parent
    / "data"
    / "shipments.csv"
)

shipments_df = pd.read_csv(CSV_PATH)


class ShipmentRequest(BaseModel):
    shipment_id: str


@app.post("/ai-analyze")
def ai_analyze_shipment(request: ShipmentRequest):

    shipment_id = request.shipment_id

    logger.info("Processing shipment %s", shipment_id)

    shipment = shipments_df[
        shipments_df["shipment_id"] == shipment_id
    ]

    if shipment.empty:
        logger.warning("Shipment %s not found", shipment_id)
        raise HTTPException(
            status_code=404,
            detail=f"Shipment {shipment_id} not found"
        )

    shipment_data = shipment.iloc[0].to_dict()

    shipment_data = {
        key: None if pd.isna(value) else value
        for key, value in shipment_data.items()
    }

    try:
        result = workflow.invoke(
            {
                "shipment": shipment_data
            }
        )

    except ValueError as error:
        logger.error(
            "Workflow validation failed for shipment %s: %s",
            shipment_id,
            error,
        )
        raise HTTPException(
            status_code=422,
            detail=str(error)
        ) from error

    deterministic = result["deterministic"]

    # Normal shipment: graph ends after deterministic analysis.
    if not deterministic["exception"]:
        return {
            "shipment_id": shipment_id,
            "exception_analysis": deterministic,
            "retrieved_context": [],
            "ai_analysis": None,
            "guardrails": {
                "passed": True,
                "errors": []
            }
        }

    guardrail_errors = result.get(
        "guardrail_errors",
        []
    )

    if guardrail_errors:
        logger.warning(
        "Guardrail validation failed for shipment %s | severity=%s | errors=%s",
        shipment_id,
        deterministic["severity"],
        guardrail_errors,
    )
        ai_result = result.get("ai_result")
        raise HTTPException(
            status_code=422,
            detail={
                "message": "AI recommendation failed business guardrails.",
                "errors": guardrail_errors,
                "action_code": (
                    ai_result.action_code.value
                    if ai_result
                    else None
                ),
                "severity": deterministic["severity"],
            }
        )

    logger.info(
        "Shipment %s analyzed successfully | severity=%s | action=%s",
        shipment_id,
        deterministic["severity"],
        result["ai_result"].action_code.value,
    )

    ai_result = result["ai_result"]

    return {
        "shipment_id": shipment_id,
        "exception_analysis": deterministic,
        "retrieved_context": result.get(
            "retrieved_context",
            []
        ),
        "ai_analysis": ai_result.model_dump(),
        "guardrails": {
            "passed": True,
            "errors": []
        }
    }
