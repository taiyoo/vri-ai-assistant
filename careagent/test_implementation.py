#!/usr/bin/env python
"""
Test script for intent classification and agent routing
Run this to verify the implementation without LiveKit
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.intent_classifier import IntentClassifier
from src.router import AgentRouter
from src.config import settings

async def test_intent_classification():
    """Test intent classification with various utterances"""
    print("Testing Intent Classification...")
    
    classifier = IntentClassifier()
    
    test_utterances = [
        "Mrs Smith had breakfast and ate about half of it",
        "John needs help with bathing this morning", 
        "Patient has a fever of 38.5 degrees",
        "Mary seems confused and agitated today",
        "Check if the care plan is up to date",
        "Hello, how are you?",
        "What's the weather like?",
        "Patient took medication at 2pm",
        "Blood pressure is elevated at 160/95"
    ]
    
    for utterance in test_utterances:
        try:
            result = await classifier.classify_with_fallback(utterance)
            intent = result.get("intent")
            confidence = result.get("confidence")
            entities = result.get("entities", {})
            
            print(f"\nUtterance: '{utterance}'")
            print(f"Intent: {intent} (confidence: {confidence:.2f})")
            if entities:
                print(f"Entities: {entities}")
                
        except Exception as e:
            print(f"Error classifying '{utterance}': {e}")

async def test_agent_routing():
    """Test agent routing with classified intents"""
    print("\n\nTesting Agent Routing...")
    
    router = AgentRouter()
    
    test_cases = [
        {
            "intent": "record_adl",
            "payload": {
                "utterance": "Mrs Smith had lunch",
                "context": "Meal recording",
                "task": "Record meal intake for Mrs Smith"
            }
        },
        {
            "intent": "clinical", 
            "payload": {
                "utterance": "Patient has fever",
                "context": "Clinical observation",
                "task": "Record fever observation"
            }
        },
        {
            "intent": "general",
            "payload": {
                "utterance": "Hello",
                "context": "General greeting",
                "task": "Respond to greeting"
            }
        }
    ]
    
    for test_case in test_cases:
        try:
            intent = test_case["intent"]
            payload = test_case["payload"]
            
            print(f"\nTesting intent: {intent}")
            result = await router.route(intent, payload)
            print(f"Response: {result}")
            
        except Exception as e:
            print(f"Error routing {intent}: {e}")

async def test_end_to_end():
    """Test end-to-end flow: classification → routing → response"""
    print("\n\nTesting End-to-End Flow...")
    
    classifier = IntentClassifier()
    router = AgentRouter()
    
    utterances = [
        "Mrs Johnson ate half her breakfast this morning",
        "Patient complained of chest pain",
        "How much water did Mr Brown drink today?"
    ]
    
    for utterance in utterances:
        try:
            print(f"\n--- Processing: '{utterance}' ---")
            
            # Step 1: Classify intent
            classification = await classifier.classify_with_fallback(utterance)
            intent = classification.get("intent")
            confidence = classification.get("confidence")
            
            print(f"1. Classification: {intent} (confidence: {confidence:.2f})")
            
            # Step 2: Prepare payload
            payload = {
                "utterance": utterance,
                "context": f"Voice input processed",
                "task": utterance,
                "entities": classification.get("entities", {}),
                "classification": classification
            }
            
            # Step 3: Route to agent
            response = await router.route(intent, payload)
            print(f"2. Agent Response: {response}")
            
        except Exception as e:
            print(f"Error in end-to-end test for '{utterance}': {e}")

async def main():
    """Run all tests"""
    print("=== CareAgent Implementation Tests ===\n")
    
    # Check configuration
    print("Configuration:")
    print(f"- AWS Region: {settings.aws_region}")
    print(f"- ADL Model: {settings.bedrock_adl_model_id}")
    print(f"- Governance Model: {settings.bedrock_gov_model_id}")
    print()
    
    try:
        await test_intent_classification()
        await test_agent_routing() 
        await test_end_to_end()
        
        print("\n=== All Tests Completed ===")
        
    except Exception as e:
        print(f"Test execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
