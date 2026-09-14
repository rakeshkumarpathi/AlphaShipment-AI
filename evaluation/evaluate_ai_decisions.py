import json
from pathlib import Path

import pandas as pd

from src.workflow.graph import workflow
from src.ai_schema import ActionCode
from src.guardrails.rules import ALLOWED_ACTIONS


DATA_PATH = Path("data/shipments.csv")
RESULT_PATH = Path("evaluation/ai_results.json")


def expected_severity(row):
    delay_hours = float(row["delay_hours"])
    priority = row["priority"]
    status = row["status"]

    if delay_hours >= 24:
        return "CRITICAL"

    if delay_hours > 0 and priority in ["High", "Critical"]:
        return "HIGH"

    if status == "Exception":
        return "HIGH"

    if delay_hours > 0:
        return "MEDIUM"

    return "NORMAL"


def main():

    df = pd.read_csv(DATA_PATH)

    # Evaluate a representative sample:
    # normal + medium + high + critical shipments.
    selected_rows = []

    normal = df[df["delay_hours"] == 0]
    medium = df[
        (df["delay_hours"] > 0)
        & (df["delay_hours"] < 24)
        & (~df["priority"].isin(["High", "Critical"]))
    ]
    high = df[
        (df["delay_hours"] > 0)
        & (df["delay_hours"] < 24)
        & (df["priority"].isin(["High", "Critical"]))
    ]
    critical = df[df["delay_hours"] >= 24]

    for group in [normal, medium, high, critical]:
        if not group.empty:
            selected_rows.append(group.iloc[0])

    results = []

    severity_correct = 0
    action_valid = 0
    guardrails_passed = 0
    structured_output_valid = 0

    for row in selected_rows:

        shipment = row.to_dict()

        result = workflow.invoke(
            {
                "shipment": shipment
            }
        )

        deterministic = result["deterministic"]

        expected = expected_severity(shipment)

        actual = deterministic["severity"]

        severity_match = actual == expected

        if severity_match:
            severity_correct += 1

        ai_result = result.get("ai_result")

        if ai_result is None:

            action_valid_result = (
                not deterministic["exception"]
            )

            structured_valid_result = True

            action = None

        else:

            action = ai_result.action_code.value

            allowed = ALLOWED_ACTIONS.get(
                actual,
                set()
            )

            action_valid_result = (
                action in allowed
            )

            structured_valid_result = True

        if action_valid_result:
            action_valid += 1

        if structured_valid_result:
            structured_output_valid += 1

        guardrail_errors = result.get(
            "guardrail_errors",
            []
        )

        guardrail_pass = (
            len(guardrail_errors) == 0
        )

        if guardrail_pass:
            guardrails_passed += 1

        results.append(
            {
                "shipment_id":
                    shipment["shipment_id"],

                "expected_severity":
                    expected,

                "actual_severity":
                    actual,

                "severity_match":
                    severity_match,

                "action_code":
                    action,

                "action_valid_for_severity":
                    action_valid_result,

                "guardrails_passed":
                    guardrail_pass,

                "guardrail_errors":
                    guardrail_errors,

                "structured_output_valid":
                    structured_valid_result
            }
        )

        print("\n========================================")
        print(
            "Shipment:",
            shipment["shipment_id"]
        )

        print(
            "Expected severity:",
            expected
        )

        print(
            "Actual severity:",
            actual
        )

        print(
            "Severity correct:",
            severity_match
        )

        print(
            "Action code:",
            action
        )

        print(
            "Action valid:",
            action_valid_result
        )

        print(
            "Guardrails passed:",
            guardrail_pass
        )

    total = len(results)

    summary = {
        "shipments_evaluated": total,
        "severity_accuracy":
            severity_correct / total
            if total else 0,
        "action_validity":
            action_valid / total
            if total else 0,
        "guardrail_pass_rate":
            guardrails_passed / total
            if total else 0,
        "structured_output_validity":
            structured_output_valid / total
            if total else 0,
        "results": results
    }

    with open(
        RESULT_PATH,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            summary,
            file,
            indent=2
        )

    print("\n========================================")
    print("AI DECISION EVALUATION")
    print("========================================")

    print(
        f"Shipments evaluated: {total}"
    )

    print(
        f"Severity accuracy: "
        f"{summary['severity_accuracy']:.2%}"
    )

    print(
        f"Action validity: "
        f"{summary['action_validity']:.2%}"
    )

    print(
        f"Guardrail pass rate: "
        f"{summary['guardrail_pass_rate']:.2%}"
    )

    print(
        f"Structured output validity: "
        f"{summary['structured_output_validity']:.2%}"
    )

    print(
        f"\nResults saved to: "
        f"{RESULT_PATH}"
    )


if __name__ == "__main__":
    main()