from pydantic import BaseModel


class AIShipmentAnalysis(BaseModel):
    business_impact: str
    root_cause_analysis: str
    recommended_action: str
    customer_communication_required: bool