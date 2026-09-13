from enum import Enum

from pydantic import BaseModel


class ActionCode(str, Enum):
    MONITOR = "MONITOR"
    REQUEST_CARRIER_UPDATE = "REQUEST_CARRIER_UPDATE"
    ESCALATE_OPERATIONS = "ESCALATE_OPERATIONS"
    ESCALATE_CRITICAL = "ESCALATE_CRITICAL"
    CONTACT_CUSTOMER = "CONTACT_CUSTOMER"


class AIShipmentAnalysis(BaseModel):
    business_impact: str
    root_cause_analysis: str
    action_code: ActionCode
    recommended_action: str
    customer_communication_required: bool