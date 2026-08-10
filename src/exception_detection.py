import pandas as pd


def detect_exception(row):
    delay_hours = float(row["delay_hours"])
    priority = row["priority"]
    status = row["status"]

    # Critical delay
    if delay_hours >= 24:
        return {
            "exception": True,
            "exception_type": "DELIVERY_DELAY",
            "severity": "CRITICAL"
        }

    # High-priority delay
    if delay_hours > 0 and priority in ["High", "Critical"]:
        return {
            "exception": True,
            "exception_type": "PRIORITY_DELAY",
            "severity": "HIGH"
        }

    # Explicit exception status
    if status == "Exception":
        return {
            "exception": True,
            "exception_type": "SHIPMENT_EXCEPTION",
            "severity": "HIGH"
        }

    # Normal delay
    if delay_hours > 0:
        return {
            "exception": True,
            "exception_type": "DELIVERY_DELAY",
            "severity": "MEDIUM"
        }

    return {
        "exception": False,
        "exception_type": "NONE",
        "severity": "NORMAL"
    }


def analyze_dataset():
    df = pd.read_csv("data/shipments.csv")

    results = []

    for _, row in df.iterrows():
        result = detect_exception(row)

        results.append({
            "shipment_id": row["shipment_id"],
            "status": row["status"],
            "priority": row["priority"],
            "delay_hours": row["delay_hours"],
            **result
        })

    result_df = pd.DataFrame(results)

    print("\n===== EXCEPTION ANALYSIS =====")
    print(f"Total shipments: {len(result_df)}")
    print(f"Exceptions detected: {result_df['exception'].sum()}")
    print(
        f"Exception rate: "
        f"{result_df['exception'].mean() * 100:.2f}%"
    )

    print("\nException types:")
    print(
        result_df[result_df["exception"]]
        ["exception_type"]
        .value_counts()
    )

    print("\nSeverity:")
    print(
        result_df[result_df["exception"]]
        ["severity"]
        .value_counts()
    )

    return result_df


if __name__ == "__main__":
    analyze_dataset()