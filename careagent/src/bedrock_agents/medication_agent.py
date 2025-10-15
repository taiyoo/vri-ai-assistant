from .base import DomainAgent

MEDICATION_PROMPT = """
Role: Medication Agent (medication administration, side effects, clinical observations).
- Record medication given to residents, dosages, timing, and any observed effects
- Track medication compliance and any side effects or reactions
- Handle clinical observations related to medications
- Output JSON with keys: medication_name, dosage, timestamp, administration_route, observations, side_effects, next_due.

Examples:
- "Gave John 5mg of medication X at 2pm" 
- "Patient complained of nausea after morning medication"
- "Blood pressure elevated, may need medication adjustment"
"""

class MedicationAgent(DomainAgent):
    def __init__(self, llm):
        super().__init__(llm, MEDICATION_PROMPT)
