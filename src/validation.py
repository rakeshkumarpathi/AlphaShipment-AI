import pandas as pd

DATA_PATH = "data/shipments.csv"
VALID_STATUSES = {"Delivered", "Delayed", "Exception"}
VALID_PRIORITIES = {"Normal", "High", "Low", "Critical"}

REQUIRED_COLUMNS = [
    "shipment_id",
    "origin",
    "destination",
    "carrier",
    "shipment_date",
    "expected_delivery",
    "status",
    "priority",
    "delay_hours",
]


def load_shipments():
    df = pd.read_csv(DATA_PATH)

    print("Shipment data loaded successfully.")
    print(f"Total shipments: {len(df)}")

    # Check required columns
    missing_columns = [
        col for col in REQUIRED_COLUMNS
        if col not in df.columns
    ]

    if missing_columns:
        print("❌ Missing columns:", missing_columns)
        return False

    # Check missing values
    missing_values = df[REQUIRED_COLUMNS].isnull().sum()

    print("\nMissing values:")
    print(missing_values)

    # Check duplicate shipment IDs
    duplicates = df["shipment_id"].duplicated().sum()
    print(f"\nDuplicate shipment IDs: {duplicates}")

    # Check status values
    invalid_status = ~df["status"].isin(VALID_STATUSES)
    print(f"Invalid status records: {invalid_status.sum()}")

    # Check priority values
    invalid_priority = ~df["priority"].isin(VALID_PRIORITIES)
    print(f"Invalid priority records: {invalid_priority.sum()}")

    # Delay statistics
    print("\nDelay statistics:")
    print(df["delay_hours"].describe())

    # Distribution
    print("\nShipment status distribution:")
    print(df["status"].value_counts())

    print("\nPriority distribution:")
    print(df["priority"].value_counts())

    print("\n✅ Dataset validation completed.")

    return True


if __name__ == "__main__":
    load_shipments()