import pandas as pd

from validation import load_shipments, validate_shipments
from shipment_analysis import analyze_shipments
from carrier_analysis import analyze_carriers


def run_pipeline():
    df = load_shipments()

    errors = validate_shipments(df)

    if errors:
        print("\nValidation Errors:")

        for error in errors:
            print(f"✗ {error}")

        return

    print("\nValidation Results:")
    print("✓ All validation checks passed.")

    analyzed_df = analyze_shipments(df)

    print("\nException Analysis:")

    print(
        analyzed_df[
            [
                "shipment_id",
                "carrier",
                "priority",
                "delay_hours",
                "exception",
                "exception_type",
                "severity"
            ]
        ].to_string(index=False)
    )

    carrier_analysis = analyze_carriers(analyzed_df)

    print("\nCarrier Performance Analysis:")

    print(
        carrier_analysis.to_string(index=False)
    )


if __name__ == "__main__":
    run_pipeline()