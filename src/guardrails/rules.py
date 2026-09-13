from src.ai_schema import AIShipmentAnalysis


ALLOWED_ACTIONS = {
    "NORMAL": {
        "MONITOR",
    },
    "MEDIUM": {
        "MONITOR",
        "REQUEST_CARRIER_UPDATE",
    },
    "HIGH": {
        "ESCALATE_OPERATIONS",
        "REQUEST_CARRIER_UPDATE",
        "CONTACT_CUSTOMER",
    },
    "CRITICAL": {
        "ESCALATE_CRITICAL",
        "CONTACT_CUSTOMER",
    },
}


def validate_ai_result(
    ai_result: AIShipmentAnalysis,
    exception_result: dict,
):
    errors = []

    severity = exception_result["severity"]
    action = ai_result.action_code.value

    allowed_actions = ALLOWED_ACTIONS.get(
        severity,
        set(),
    )

    if action not in allowed_actions:
        errors.append(
            f"Action '{action}' is not permitted "
            f"for severity '{severity}'."
        )

    # Critical exceptions must use the critical escalation
    # action rather than relying only on customer communication.
    if severity == "CRITICAL" and action != "ESCALATE_CRITICAL":
        errors.append(
            "CRITICAL shipments must use ESCALATE_CRITICAL."
        )

    return errors