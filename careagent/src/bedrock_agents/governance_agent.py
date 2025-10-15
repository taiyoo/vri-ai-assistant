from .base import DomainAgent

GOV_PROMPT = """
Role: Care Governance Agent (compliance and discrepancy).
- Compare expected vs recorded care; detect conflicts (e.g., shower vs incont. clean).
- Check ACQS/policy compliance for the event.
- Output JSON: issues[], severity, required_actions[], notify_roles[]
"""

class GovernanceAgent(DomainAgent):
    def __init__(self, llm):
        super().__init__(llm, GOV_PROMPT)