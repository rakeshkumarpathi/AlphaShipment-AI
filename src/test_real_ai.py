from validation import load_shipments
from exception_detection import detect_exception
from llm_analysis import analyze_shipment_with_ai


df = load_shipments()

shipment = df.iloc[16].to_dict()

exception_result = detect_exception(shipment)

print("\nDeterministic Analysis:")
print(exception_result)

print("\nCalling real LLM...")

ai_result = analyze_shipment_with_ai(
    shipment,
    exception_result
)

print("\nAI Analysis:")
print(ai_result)