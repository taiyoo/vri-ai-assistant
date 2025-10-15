from .base import DomainAgent

CLINICAL_PROMPT = """
Role: Clinical Agent.
- Validate anticoagulant therapy notes, dose/INR coherence.
- Output JSON: meds_event, safety_flags[], recommendations[]
"""


class ClinicalAgent(DomainAgent):
    def __init__(self, llm):
        super().__init__(llm, CLINICAL_PROMPT)