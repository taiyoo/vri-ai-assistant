from __future__ import annotations
from typing import Dict, Any, Literal
import boto3
from langchain_community.chat_models import BedrockChat
from src.config import settings
from src.bedrock_agents.adl_agent import ADLAgent
from src.bedrock_agents.medication_agent import MedicationAgent
from src.bedrock_agents.behavior_agent import BehaviorAgent
from src.bedrock_agents.governance_agent import GovernanceAgent
from src.utils.logging import get_logger


logger = get_logger("router")

Intent = Literal[
    "record_adl",
    "clinical", 
    "behavior",
    "medication",
    "governance_check",
    "general",
]

class AgentRouter:
    def __init__(self) -> None:
        session = boto3.Session(region_name=settings.aws_region)
        self.adl_llm = BedrockChat(client=session.client("bedrock-runtime"), model_id=settings.bedrock_adl_model_id)
        self.med_llm = BedrockChat(client=session.client("bedrock-runtime"), model_id=settings.bedrock_med_model_id)
        self.beh_llm = BedrockChat(client=session.client("bedrock-runtime"), model_id=settings.bedrock_beh_model_id)
        self.gov_llm = BedrockChat(client=session.client("bedrock-runtime"), model_id=settings.bedrock_gov_model_id)

        self.adl = ADLAgent(self.adl_llm)
        self.med = MedicationAgent(self.med_llm)
        self.beh = BehaviorAgent(self.beh_llm)
        self.gov = GovernanceAgent(self.gov_llm)


    async def route(self, intent: Intent, payload: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Routing intent={intent}")
        if intent == "record_adl":
            return await self.adl.run(payload)
        if intent == "medication":
            return await self.med.run(payload)
        if intent == "clinical":
            return await self.med.run(payload)  # Use medication agent for clinical queries
        if intent == "behavior":
            return await self.beh.run(payload)
        if intent == "governance_check":
            return await self.gov.run(payload)
        if intent == "general":
            # Handle general conversation with a default response
            return {
                "result": "I'm here to help with aged care activities. You can tell me about meals, medication, daily activities, or ask questions about resident care.",
                "intent": "general"
            }
        return {"error": "unknown_intent"}