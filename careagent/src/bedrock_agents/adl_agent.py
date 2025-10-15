from .base import DomainAgent

ADL_PROMPT = """
Role: ADL Agent (bathing, incontinence care, bowel chart, repositioning, food/fluid intake).
- If voice says full bath vs incontinence clean, emit `activity_type` and `confidence`.
- Output JSON with keys: activity_type, timestamp, observations, next_actions.
"""

class ADLAgent(DomainAgent):
    def __init__(self, llm):
        super().__init__(llm, ADL_PROMPT)