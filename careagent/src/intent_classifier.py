"""
Intent Classification Module using Langchain
Classifies user utterances into predefined intents for aged care scenarios
"""
from typing import Dict, Any, Optional
import json
import boto3
from langchain_community.chat_models import BedrockChat
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from src.config import settings
from src.utils.logging import get_logger

logger = get_logger("intent_classifier")

# Define intent classification prompt
INTENT_CLASSIFICATION_PROMPT = """
You are an intent classifier for an aged care voice assistant system. Your job is to classify user utterances into one of the following intents:

**Intent Categories:**
1. **record_adl** - Activities of Daily Living
   - Examples: "Mrs Smith had breakfast", "John needs help with bathing", "Patient ate half their lunch", "Mary drank 200ml water", "Toileting assistance needed"
   
2. **clinical** - Medical/Clinical observations  
   - Examples: "Patient has a fever", "Blood pressure is elevated", "Wound dressing needs changing", "Pain level is 7/10", "Medication side effects observed"
   
3. **governance_check** - Compliance and safety checks
   - Examples: "Check if care plan is up to date", "Verify medication schedule", "Safety assessment needed", "Review incident report"

4. **general** - General questions or conversation
   - Examples: "How are you today?", "What's the weather like?", "Thank you", "Hello"

**Instructions:**
- Analyze the user's utterance carefully
- Consider the context of aged care settings
- Return ONLY a JSON object with the following structure:
{
  "intent": "intent_name",
  "confidence": 0.85,
  "entities": {
    "resident_name": "extracted_name_if_any",
    "activity": "extracted_activity_if_any",
    "measurement": "extracted_measurement_if_any"
  }
}

**Rules:**
- Confidence should be between 0.0 and 1.0
- If unsure, default to "general" intent with lower confidence
- Extract relevant entities when possible
- Be consistent with intent classification

User utterance: {utterance}
"""

class IntentClassifier:
    def __init__(self):
        """Initialize the intent classifier with Bedrock LLM"""
        session = boto3.Session(region_name=settings.aws_region)
        # Use the governance model for intent classification as it's likely more general purpose
        self.llm = BedrockChat(
            client=session.client("bedrock-runtime"), 
            model_id=settings.bedrock_gov_model_id,
            model_kwargs={
                "temperature": 0.1,  # Low temperature for consistent classification
                "max_tokens": 200,   # Short responses for classification
            }
        )
        
        self.prompt_template = ChatPromptTemplate.from_template(INTENT_CLASSIFICATION_PROMPT)
        logger.info("Intent classifier initialized")

    async def classify(self, utterance: str) -> Dict[str, Any]:
        """
        Classify user utterance into intent
        
        Args:
            utterance: The user's spoken text
            
        Returns:
            Dict containing intent, confidence, and extracted entities
        """
        try:
            logger.info(f"Classifying utterance: {utterance[:100]}...")
            
            # Create the classification prompt
            messages = [
                SystemMessage(content="You are an expert intent classifier for aged care voice systems."),
                HumanMessage(content=self.prompt_template.format(utterance=utterance))
            ]
            
            # Get LLM response
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            try:
                result = json.loads(response.content.strip())
                logger.info(f"Classified intent: {result.get('intent')} (confidence: {result.get('confidence')})")
                return result
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse LLM response as JSON: {e}")
                logger.error(f"Raw response: {response.content}")
                
                # Fallback classification
                return {
                    "intent": "general",
                    "confidence": 0.5,
                    "entities": {}
                }
                
        except Exception as e:
            logger.error(f"Error in intent classification: {e}")
            return {
                "intent": "general",
                "confidence": 0.3,
                "entities": {},
                "error": str(e)
            }

    def validate_intent(self, intent: str) -> bool:
        """Validate if intent is one of the supported types"""
        valid_intents = ["record_adl", "clinical", "governance_check", "general"]
        return intent in valid_intents

    async def classify_with_fallback(self, utterance: str, min_confidence: float = 0.7) -> Dict[str, Any]:
        """
        Classify utterance with fallback to general intent if confidence is low
        
        Args:
            utterance: The user's spoken text
            min_confidence: Minimum confidence threshold
            
        Returns:
            Classification result with fallback handling
        """
        result = await self.classify(utterance)
        
        # Apply confidence threshold
        if result.get("confidence", 0) < min_confidence:
            logger.warning(f"Low confidence {result.get('confidence')} for intent {result.get('intent')}, falling back to general")
            result["intent"] = "general"
            result["confidence"] = 0.5
            result["fallback_applied"] = True
            
        # Validate intent
        if not self.validate_intent(result.get("intent", "")):
            logger.warning(f"Invalid intent {result.get('intent')}, falling back to general")
            result["intent"] = "general"
            result["confidence"] = 0.5
            result["validation_failed"] = True
            
        return result
