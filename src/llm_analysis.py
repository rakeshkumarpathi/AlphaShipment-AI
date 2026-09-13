import os

from dotenv import load_dotenv
from openai import OpenAI

from src.ai_schema import AIShipmentAnalysis


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("OPENAI_API_KEY is not configured.")

client = OpenAI(api_key=api_key)


def analyze_shipment_with_ai(
    shipment,
    exception_result,
    retrieved_context
):

    context = "\n\n".join(
        f"""
Source: {item["source"]}

{item["content"]}
"""
        for item in retrieved_context
    )

    severity = exception_result["severity"]

    prompt = f"""
You are an AI logistics operations analyst.

Analyze the following shipment exception and provide
a concise operational assessment.

Shipment:
- Shipment ID: {shipment["shipment_id"]}
- Origin: {shipment["origin"]}
- Destination: {shipment["destination"]}
- Carrier: {shipment["carrier"]}
- Status: {shipment["status"]}
- Priority: {shipment["priority"]}
- Delay: {shipment["delay_hours"]} hours
- Reason: {shipment.get("reason", "Not provided")}

Deterministic analysis:
- Exception: {exception_result["exception"]}
- Exception type: {exception_result["exception_type"]}
- Severity: {severity}

Retrieved operational knowledge:
{context}

Allowed action codes by deterministic severity:

NORMAL:
- MONITOR

MEDIUM:
- MONITOR
- REQUEST_CARRIER_UPDATE

HIGH:
- ESCALATE_OPERATIONS
- REQUEST_CARRIER_UPDATE
- CONTACT_CUSTOMER

CRITICAL:
- ESCALATE_CRITICAL
- CONTACT_CUSTOMER

Select exactly one action_code from the allowed actions
for the deterministic severity.

Determine:

1. The business impact of the exception.
2. The most likely root cause based only on the supplied
   shipment information and retrieved operational evidence.
3. The appropriate action_code.
4. A human-readable recommended operational action.
5. Whether customer communication is required.

Important rules:

Important rules:

- Never change the deterministic severity.
- Do not invent shipment facts.
- Do not treat general policy information as proof of
  the actual root cause.
- Prefer recorded shipment information over assumptions.
- Use retrieved policies to guide operational recommendations.
- Recommended actions must be supported by the retrieved
  operational knowledge or the deterministic exception policy.
- Do not introduce operational procedures or contingency
  actions that are not supported by the supplied evidence.
- For CRITICAL shipments, action_code must be ESCALATE_CRITICAL.
- For CRITICAL shipments, customer_communication_required must be true.
"""

    response = client.responses.parse(
        model="gpt-5-mini",
        input=prompt,
        text_format=AIShipmentAnalysis
    )

    return response.output_parsed