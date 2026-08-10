import pandas as pd

DATA_PATH = "data/shipments.csv"


def analyze_carriers():
    df = pd.read_csv(DATA_PATH)

    carrier_summary = (
        df.groupby("carrier")
        .agg(
            total_shipments=("shipment_id", "count"),
            delayed_shipments=(
                "status",
                lambda x: (x == "Delayed").sum()
            ),
            exceptions=(
                "status",
                lambda x: (x == "Exception").sum()
            ),
            average_delay_hours=("delay_hours", "mean"),
            max_delay_hours=("delay_hours", "max")
        )
        .reset_index()
    )

    carrier_summary["delay_rate"] = (
        carrier_summary["delayed_shipments"]
        / carrier_summary["total_shipments"]
        * 100
    )

    carrier_summary["exception_rate"] = (
        carrier_summary["exceptions"]
        / carrier_summary["total_shipments"]
        * 100
    )

    carrier_summary = carrier_summary.sort_values(
        "delay_rate",
        ascending=False
    )

    print("\n===== CARRIER ANALYSIS =====")
    print(carrier_summary.to_string(index=False))

    print("\n===== HIGHEST DELAY RATE =====")

    worst_carrier = carrier_summary.iloc[0]

    print(
        f"Carrier: {worst_carrier['carrier']}"
    )
    print(
        f"Delay Rate: {worst_carrier['delay_rate']:.2f}%"
    )
    print(
        f"Average Delay: "
        f"{worst_carrier['average_delay_hours']:.2f} hours"
    )

    return carrier_summary


if __name__ == "__main__":
    analyze_carriers()