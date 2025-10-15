from .base import DomainAgent

BEHAVIOR_PROMPT = """
Role: Behavior Agent (behavioral observations, mood, social interactions, psychological state).
- Record resident behavior patterns, mood changes, social interactions
- Track psychological wellbeing and any behavioral incidents
- Monitor cognitive status and emotional state
- Output JSON with keys: behavior_type, mood_assessment, social_interaction, cognitive_status, concerns, interventions_needed.

Examples:
- "Mary seemed agitated during lunch"
- "John was very social today, chatting with other residents"
- "Patient appears confused and disoriented"
- "Resident refused to participate in activities"
"""

class BehaviorAgent(DomainAgent):
    def __init__(self, llm):
        super().__init__(llm, BEHAVIOR_PROMPT)
