# Shipment Escalation Policy

## Severity Levels

### NORMAL

No operational exception requiring escalation.

Recommended action:
MONITOR

### MEDIUM

A moderate shipment issue requiring additional monitoring or a carrier update.

Permitted actions:
- REQUEST_CARRIER_UPDATE
- MONITOR

### HIGH

A significant shipment exception requiring operational attention.

Permitted actions:
- ESCALATE_OPERATIONS
- REQUEST_CARRIER_UPDATE
- CONTACT_CUSTOMER

### CRITICAL

A severe shipment exception requiring immediate escalation.

Permitted actions:
- ESCALATE_CRITICAL
- CONTACT_CUSTOMER

For critical exceptions, the preferred operational action is ESCALATE_CRITICAL.