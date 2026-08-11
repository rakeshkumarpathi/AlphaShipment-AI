from fastapi import FastAPI
from pydantic import BaseModel

from src.exception_detection import detect_exception
from src.llm_analysis import analyze_shipment_with_ai


app = FastAPI(
    title="AlphaShipment AI",
    description="AI-Powered Shipment Exception & Operations Automation Platform",
    version="1.0.0"
)


class Shipment(BaseModel):
    shipment_id: str
    origin: str
    destination: str
    carrier: str
    shipment_date: str
    expected_delivery: str
    status: str
    priority: str
    delay_hours: float
    reason: str | None = None


@app.get("/")
def root():
    return {
        "message": "AlphaShipment AI API is running"
    }


@app.post("/analyze-shipment")
def analyze_shipment(shipment: Shipment):

    shipment_data = shipment.model_dump()

    result = detect_exception(shipment_data)

    return {
        "shipment_id": shipment.shipment_id,
        **result
    }


@app.post("/ai-analyze")
def ai_analyze_shipment(shipment: Shipment):

    shipment_data = shipment.model_dump()

    exception_result = detect_exception(shipment_data)

    ai_result = analyze_shipment_with_ai(
        shipment_data,
        exception_result
    )

    return ai_result