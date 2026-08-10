import pandas as pd

from validation import load_shipments
from mock_ai import mock_ai_analysis
from exception_detection import detect_exception

df = pd.read_csv("data/shipments.csv")

shipment = df.iloc[16].to_dict()
exception_result = detect_exception(shipment)
carrier_df = pd.read_csv("data/shipments.csv")

carrier_data = carrier_df[carrier_df["carrier"] == shipment["carrier"]]

carrier_context = {
    "delay_rate": (
        (carrier_data["status"] == "Delayed").mean() * 100
    ),
    "average_delay_hours": carrier_data["delay_hours"].mean()
}

print("Deterministic Analysis:")
print(exception_result)

ai_result = mock_ai_analysis(
    shipment,
    exception_result,
    carrier_context
)

print("\nAI Analysis:")
print(ai_result)


