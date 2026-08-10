import os

from dotenv import load_dotenv
from openai import OpenAI

from ai_schema import AIShipmentAnalysis


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not configured.")

client = OpenAI(api_key=api_key)


def analyze_shipment_with_ai(shipment, exception_result):

    prompt = f"""
You are an AI logistics operations analyst.

Analyze this shipment exception.

Shipment:
- Shipment ID: {shipment["shipment_id"]}
- Origin: {shipment["origin"]}
- Destination: {shipment["destination"]}
- Carrier: {shipment["carrier"]}
- Status: {shipment["status"]}
- Priority: {shipment["priority"]}
- Delay: {shipment["delay_hours"]} hours
- Reason: {shipment["reason"]}

Deterministic analysis:
- Exception: {exception_result["exception"]}
- Exception type: {exception_result["exception_type"]}
- Severity: {exception_result["severity"]}

Provide an operational analysis.

Do not invent facts that are not present in the supplied information.
"""

    response = client.responses.parse(
        model="gpt-5-mini",
        input=prompt,
        text_format=AIShipmentAnalysis
    )

    return response.output_parsed