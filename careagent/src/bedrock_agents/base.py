from typing import Any, Dict, Optional
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage


SYSTEM_BASIS = """
You are a domain-specific agent in an aged-care voice system.
Ground outputs in provided context (EHR snippets, care plan, prior notes).
Return a concise JSON object under key `result` with fields that the router can consume.
"""


class DomainAgent:
    def __init__(self, llm: BaseChatModel, system_prompt: str | None = None):
        self.llm = llm
        self.system_prompt = system_prompt or SYSTEM_BASIS


    async def run(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        messages = [
            SystemMessage(content=self.system_prompt),
            HumanMessage(content=f"Context:\n{payload.get('context')}\n\nTask:\n{payload.get('task')}")
        ]
        resp = await self.llm.ainvoke(messages)
        # naive parse; ensure downstream agent hardens parsing
        return {"result": resp.content}