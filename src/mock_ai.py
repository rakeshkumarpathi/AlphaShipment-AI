from ai_schema import AIShipmentAnalysis


def mock_ai_analysis(shipment, exception_result, carrier_context=None):

    carrier_context = carrier_context or {}

    carrier = shipment.get("carrier", "Unknown")
    delay_hours = float(shipment.get("delay_hours", 0))
    priority = shipment.get("priority", "Normal")
    reason = shipment.get("reason", "Unknown")
    shipment_id = shipment.get("shipment_id", "Unknown")

    carrier_delay_rate = carrier_context.get("delay_rate", 0)
    carrier_avg_delay = carrier_context.get("average_delay_hours", 0)

    if exception_result["severity"] == "CRITICAL":

        return AIShipmentAnalysis(
            business_impact=(
                f"High-priority shipment {shipment_id} has a "
                f"{delay_hours:.0f}-hour delay, creating a significant "
                f"risk of customer impact."
            ),

            root_cause_analysis=(
                f"The recorded reason is {reason}. "
                f"{carrier} currently has a "
                f"{carrier_delay_rate:.1f}% delay rate with an "
                f"average delay of {carrier_avg_delay:.1f} hours, "
                f"indicating potential carrier-level operational risk."
            ),

            recommended_action=(
                "Escalate to the operations team, request an updated "
                "recovery ETA from the carrier, and prioritize proactive "
                "customer communication."
            ),

            customer_communication_required=True
        )

    if exception_result["severity"] == "HIGH":

        return AIShipmentAnalysis(
            business_impact=(
                f"Shipment {shipment_id} has a significant delay "
                f"of {delay_hours:.0f} hours."
            ),

            root_cause_analysis=(
                f"The recorded delay reason is {reason}."
            ),

            recommended_action=(
                "Monitor the shipment closely and request an updated ETA "
                "from the carrier."
            ),

            customer_communication_required=priority in ["High", "Critical"]
        )

    if exception_result["severity"] == "MEDIUM":

        return AIShipmentAnalysis(
            business_impact=(
                f"Shipment {shipment_id} has a minor operational delay."
            ),

            root_cause_analysis=(
                f"The recorded delay reason is {reason}."
            ),

            recommended_action=(
                "Continue monitoring and review the shipment if the delay "
                "increases."
            ),

            customer_communication_required=False
        )

    return AIShipmentAnalysis(
        business_impact="No significant operational impact identified.",
        root_cause_analysis="No major exception identified.",
        recommended_action="Continue normal monitoring.",
        customer_communication_required=False
    )