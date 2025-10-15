#!/usr/bin/env python3
"""
Testing & Simulation for Multi-Agent Orchestration Platform

This module implements:
1. Mock voice inputs from synthetic ADL dataset
2. High concurrency testing with multiple agents
3. Metrics collection and verification of routing, Bedrock agent calls, and discrepancy detection
"""

import asyncio
import json
import time
import logging
import random
from typing import List, Dict, Any, Optional, cast
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
try:
    import pytest
except ImportError:
    pytest = None
import numpy as np

# Import our modules
import sys
sys.path.append('..')
from src.router import AgentRouter, Intent
from src.intent_classifier import IntentClassifier
from src.utils.logging import get_logger

logger = get_logger("test_simulation")

@dataclass
class TestMetrics:
    """Metrics collected during testing"""
    test_id: str
    timestamp: datetime
    agent_count: int
    total_requests: int
    successful_requests: int
    failed_requests: int
    avg_response_time: float
    routing_decisions: Dict[str, int]
    bedrock_calls: Dict[str, int]
    discrepancies_detected: int
    errors: List[str]

@dataclass
class MockVoiceInput:
    """Represents a mock voice input from synthetic data"""
    scenario_id: str
    utterance: str
    expected_intent: Intent
    context: Dict[str, Any]
    metadata: Dict[str, Any]

class SyntheticDataLoader:
    """Loads and processes synthetic ADL scenarios for testing"""
    
    def __init__(self, data_path: str = "../../../adl_synthetic_dataset/01_data/processed/synthetic_adl_scenarios_enhanced.json"):
        self.data_path = Path(data_path)
        self.scenarios: List[Dict[str, Any]] = []
        self.mock_inputs: List[MockVoiceInput] = []
        
    def load_data(self) -> None:
        """Load synthetic scenarios from JSON file"""
        try:
            with open(self.data_path, 'r') as f:
                self.scenarios = json.load(f)
            logger.info(f"Loaded {len(self.scenarios)} synthetic scenarios")
        except FileNotFoundError:
            logger.error(f"Synthetic data file not found: {self.data_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {e}")
            raise
    
    def create_mock_inputs(self, count: Optional[int] = None) -> List[MockVoiceInput]:
        """Convert scenarios to mock voice inputs"""
        if not self.scenarios:
            self.load_data()
        
        selected_scenarios = self.scenarios[:count] if count else self.scenarios
        mock_inputs = []
        
        for scenario in selected_scenarios:
            # Extract utterances from dialogue
            for turn in scenario.get("dialogue", []):
                if turn.get("speaker") == "Personal Care Assistant":
                    # Determine expected intent based on context
                    expected_intent = self._classify_intent(
                        turn.get("utterance", ""),
                        scenario.get("context", {})
                    )
                    
                    mock_input = MockVoiceInput(
                        scenario_id=scenario.get("scenario_id", "unknown"),
                        utterance=turn.get("utterance", ""),
                        expected_intent=expected_intent,
                        context=scenario.get("context", {}),
                        metadata={
                            "resident_profile": scenario.get("resident_profile", {}),
                            "care_goal": scenario.get("care_goal", ""),
                            "risk_flags": scenario.get("risk_flags", []),
                            "turn_id": turn.get("turn_id", 0)
                        }
                    )
                    mock_inputs.append(mock_input)
        
        self.mock_inputs = mock_inputs
        logger.info(f"Created {len(mock_inputs)} mock voice inputs")
        return mock_inputs
    
    def _classify_intent(self, utterance: str, context: Dict[str, Any]) -> Intent:
        """Classify intent based on utterance and context"""
        utterance_lower = utterance.lower()
        adl_category = context.get("adl_category", "").lower()
        
        # Simple rule-based classification for testing
        if any(word in utterance_lower for word in ["medication", "dose", "pill", "medicine"]):
            return "medication"
        elif any(word in utterance_lower for word in ["behavior", "mood", "angry", "confused", "agitated"]):
            return "behavior"
        elif any(word in utterance_lower for word in ["check", "verify", "compliance", "documentation"]):
            return "governance_check"
        elif adl_category in ["hygiene", "mobility", "feeding", "toileting"]:
            return "record_adl"
        else:
            return "general"

class AgentSimulator:
    """Simulates multiple agents for concurrency testing"""
    
    def __init__(self, router: AgentRouter):
        self.router = router
        self.metrics: List[TestMetrics] = []
        
    async def simulate_single_request(self, mock_input: MockVoiceInput) -> Dict[str, Any]:
        """Simulate a single agent request"""
        start_time = time.time()
        
        try:
            # Prepare payload for router
            payload = {
                "utterance": mock_input.utterance,
                "context": mock_input.context,
                "metadata": mock_input.metadata,
                "timestamp": datetime.now().isoformat()
            }
            
            # Route the request
            response = await self.router.route(mock_input.expected_intent, payload)
            
            end_time = time.time()
            response_time = end_time - start_time
            
            return {
                "success": True,
                "response": response,
                "response_time": response_time,
                "mock_input": mock_input,
                "error": None
            }
            
        except Exception as e:
            end_time = time.time()
            response_time = end_time - start_time
            
            logger.error(f"Error in simulation: {e}")
            return {
                "success": False,
                "response": None,
                "response_time": response_time,
                "mock_input": mock_input,
                "error": str(e)
            }
    
    async def simulate_concurrent_agents(
        self,
        mock_inputs: List[MockVoiceInput],
        agent_count: int = 1,
        delay_between_requests: float = 0.1
    ) -> TestMetrics:
        """Simulate multiple concurrent agents"""
        test_id = f"concurrent_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        logger.info(f"Starting concurrent simulation: {test_id} with {agent_count} agents")
        
        start_time = time.time()
        
        # Create tasks for concurrent execution
        tasks = []
        for i in range(agent_count):
            # Select subset of inputs for this agent
            agent_inputs = mock_inputs[i::agent_count]  # Distribute inputs across agents
            
            for mock_input in agent_inputs:
                task = self.simulate_single_request(mock_input)
                tasks.append(task)
                
                # Add small delay between requests to simulate realistic timing
                if delay_between_requests > 0:
                    await asyncio.sleep(delay_between_requests)
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Process results and collect metrics
        successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
        failed_requests = len(results) - successful_requests
        
        response_times = [
            r.get("response_time", 0) for r in results 
            if isinstance(r, dict) and "response_time" in r
        ]
        avg_response_time = float(np.mean(response_times)) if response_times else 0.0
        
        # Count routing decisions
        routing_decisions = {}
        bedrock_calls = {}
        errors = []
        
        for result in results:
            if isinstance(result, dict):
                if result.get("success"):
                    intent = result["mock_input"].expected_intent
                    routing_decisions[intent] = routing_decisions.get(intent, 0) + 1
                    
                    # Count Bedrock calls (simplified)
                    bedrock_calls[intent] = bedrock_calls.get(intent, 0) + 1
                
                if result.get("error"):
                    errors.append(result["error"])
            elif isinstance(result, Exception):
                errors.append(str(result))
        
        metrics = TestMetrics(
            test_id=test_id,
            timestamp=datetime.now(),
            agent_count=agent_count,
            total_requests=len(results),
            successful_requests=successful_requests,
            failed_requests=failed_requests,
            avg_response_time=avg_response_time,
            routing_decisions=routing_decisions,
            bedrock_calls=bedrock_calls,
            discrepancies_detected=0,  # TODO: Implement discrepancy detection
            errors=errors
        )
        
        self.metrics.append(metrics)
        
        logger.info(f"Simulation completed in {total_time:.2f}s")
        logger.info(f"Success rate: {successful_requests}/{len(results)} ({100*successful_requests/len(results):.1f}%)")
        logger.info(f"Average response time: {avg_response_time:.3f}s")
        
        return metrics

class TestSuite:
    """Main test suite for the multi-agent platform"""
    
    def __init__(self):
        self.data_loader = SyntheticDataLoader()
        self.router = AgentRouter()
        self.simulator = AgentSimulator(self.router)
        self.results: List[TestMetrics] = []
    
    async def setup(self):
        """Setup test environment"""
        logger.info("Setting up test environment...")
        self.data_loader.load_data()
        
    async def test_routing_accuracy(self, sample_size: int = 50):
        """Test routing accuracy with sample inputs"""
        logger.info(f"Testing routing accuracy with {sample_size} samples")
        
        mock_inputs = self.data_loader.create_mock_inputs(sample_size)
        
        correct_routes = 0
        total_routes = 0
        
        for mock_input in mock_inputs:
            try:
                # Use intent classifier to determine actual intent
                classifier = IntentClassifier()
                predicted_intent = await classifier.classify(mock_input.utterance)
                
                # Compare with expected intent
                if predicted_intent == mock_input.expected_intent:
                    correct_routes += 1
                
                total_routes += 1
                
            except Exception as e:
                logger.error(f"Error in routing test: {e}")
        
        accuracy = correct_routes / total_routes if total_routes > 0 else 0
        logger.info(f"Routing accuracy: {correct_routes}/{total_routes} ({100*accuracy:.1f}%)")
        
        return accuracy
    
    async def test_single_agent_performance(self, sample_size: int = 20):
        """Test performance with single agent"""
        logger.info("Testing single agent performance...")
        
        mock_inputs = self.data_loader.create_mock_inputs(sample_size)
        metrics = await self.simulator.simulate_concurrent_agents(
            mock_inputs=mock_inputs,
            agent_count=1,
            delay_between_requests=0.1
        )
        
        self.results.append(metrics)
        return metrics
    
    async def test_dual_agent_concurrency(self, sample_size: int = 40):
        """Test performance with two concurrent agents"""
        logger.info("Testing dual agent concurrency...")
        
        mock_inputs = self.data_loader.create_mock_inputs(sample_size)
        metrics = await self.simulator.simulate_concurrent_agents(
            mock_inputs=mock_inputs,
            agent_count=2,
            delay_between_requests=0.05
        )
        
        self.results.append(metrics)
        return metrics
    
    async def test_bedrock_agent_calls(self, sample_size: int = 10):
        """Test that Bedrock agents are called correctly"""
        logger.info("Testing Bedrock agent calls...")
        
        # Test each intent type
        intents_to_test: List[Intent] = ["record_adl", "medication", "behavior", "governance_check"]
        
        for intent in intents_to_test:
            mock_input = MockVoiceInput(
                scenario_id=f"test_{intent}",
                utterance=f"Test utterance for {intent}",
                expected_intent=intent,
                context={"test": True},
                metadata={"test_case": intent}
            )
            
            try:
                result = await self.simulator.simulate_single_request(mock_input)
                
                if result["success"]:
                    logger.info(f"✓ {intent} agent call successful")
                else:
                    logger.error(f"✗ {intent} agent call failed: {result['error']}")
                    
            except Exception as e:
                logger.error(f"✗ {intent} agent call error: {e}")
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        if not self.results:
            return {"error": "No test results available"}
        
        # Aggregate metrics
        total_requests = sum(m.total_requests for m in self.results)
        total_successful = sum(m.successful_requests for m in self.results)
        total_failed = sum(m.failed_requests for m in self.results)
        
        avg_response_times = [m.avg_response_time for m in self.results]
        overall_avg_response_time = np.mean(avg_response_times)
        
        # Aggregate routing decisions
        all_routing_decisions = {}
        for metrics in self.results:
            for intent, count in metrics.routing_decisions.items():
                all_routing_decisions[intent] = all_routing_decisions.get(intent, 0) + count
        
        # Performance comparison
        single_agent_metrics = next((m for m in self.results if m.agent_count == 1), None)
        dual_agent_metrics = next((m for m in self.results if m.agent_count == 2), None)
        
        report = {
            "summary": {
                "total_tests": len(self.results),
                "total_requests": total_requests,
                "success_rate": total_successful / total_requests if total_requests > 0 else 0,
                "overall_avg_response_time": overall_avg_response_time,
                "routing_decisions": all_routing_decisions
            },
            "performance_comparison": {},
            "test_details": [asdict(m) for m in self.results],
            "recommendations": []
        }
        
        # Add performance comparison
        if single_agent_metrics and dual_agent_metrics:
            throughput_improvement = (
                dual_agent_metrics.total_requests / dual_agent_metrics.avg_response_time
            ) / (
                single_agent_metrics.total_requests / single_agent_metrics.avg_response_time
            ) if single_agent_metrics.avg_response_time > 0 else 0
            
            report["performance_comparison"] = {
                "single_agent_avg_response_time": single_agent_metrics.avg_response_time,
                "dual_agent_avg_response_time": dual_agent_metrics.avg_response_time,
                "throughput_improvement": throughput_improvement,
                "concurrency_efficiency": throughput_improvement / 2  # Ideal would be 1.0
            }
        
        # Add recommendations
        if report["summary"]["success_rate"] < 0.95:
            report["recommendations"].append("Consider improving error handling and retry mechanisms")
        
        if overall_avg_response_time > 2.0:
            report["recommendations"].append("Response times are high - consider optimizing Bedrock calls")
        
        if dual_agent_metrics and single_agent_metrics and dual_agent_metrics.avg_response_time > single_agent_metrics.avg_response_time * 1.5:
            report["recommendations"].append("Concurrency overhead detected - investigate resource bottlenecks")
        
        return report
    
    def save_report(self, report: Dict[str, Any], filename: Optional[str] = None):
        """Save test report to file"""
        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        filepath = Path(__file__).parent / "reports" / filename
        filepath.parent.mkdir(exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Test report saved to {filepath}")

# Pytest test functions (only if pytest is available)
if pytest is not None:
    @pytest.mark.asyncio
    async def test_mock_voice_inputs():
        """Test that mock voice inputs are created correctly"""
        data_loader = SyntheticDataLoader()
        data_loader.load_data()
        
        mock_inputs = data_loader.create_mock_inputs(10)
        
        assert len(mock_inputs) > 0
        assert all(isinstance(mi, MockVoiceInput) for mi in mock_inputs)
        assert all(mi.utterance for mi in mock_inputs)
        assert all(mi.expected_intent in ["record_adl", "medication", "behavior", "governance_check", "general"] for mi in mock_inputs)

    @pytest.mark.asyncio
    async def test_single_agent_simulation():
        """Test single agent simulation"""
        test_suite = TestSuite()
        await test_suite.setup()
        
        metrics = await test_suite.test_single_agent_performance(sample_size=5)
        
        assert metrics.agent_count == 1
        assert metrics.total_requests == 5
        assert metrics.successful_requests >= 0
        assert metrics.avg_response_time >= 0

    @pytest.mark.asyncio
    async def test_dual_agent_simulation():
        """Test dual agent simulation"""
        test_suite = TestSuite()
        await test_suite.setup()
        
        metrics = await test_suite.test_dual_agent_concurrency(sample_size=10)
        
        assert metrics.agent_count == 2
        assert metrics.total_requests == 10
        assert metrics.successful_requests >= 0
        assert metrics.avg_response_time >= 0

if __name__ == "__main__":
    # Run comprehensive test suite
    async def run_full_test_suite():
        test_suite = TestSuite()
        await test_suite.setup()
        
        print("\n=== Multi-Agent Orchestration Platform Test Suite ===\n")
        
        # Test routing accuracy
        accuracy = await test_suite.test_routing_accuracy(sample_size=30)
        print(f"Routing Accuracy: {accuracy:.2%}")
        
        # Test single agent performance
        print("\n--- Single Agent Performance Test ---")
        await test_suite.test_single_agent_performance(sample_size=20)
        
        # Test dual agent concurrency
        print("\n--- Dual Agent Concurrency Test ---")
        await test_suite.test_dual_agent_concurrency(sample_size=40)
        
        # Test Bedrock agent calls
        print("\n--- Bedrock Agent Call Verification ---")
        await test_suite.test_bedrock_agent_calls()
        
        # Generate and save report
        print("\n--- Generating Test Report ---")
        report = test_suite.generate_report()
        test_suite.save_report(report)
        
        print("\n=== Test Summary ===")
        print(f"Total Tests: {report['summary']['total_tests']}")
        print(f"Total Requests: {report['summary']['total_requests']}")
        print(f"Success Rate: {report['summary']['success_rate']:.2%}")
        print(f"Average Response Time: {report['summary']['overall_avg_response_time']:.3f}s")
        
        if report['recommendations']:
            print("\n--- Recommendations ---")
            for rec in report['recommendations']:
                print(f"• {rec}")
        
        return report
    
    # Run the test suite
    asyncio.run(run_full_test_suite())
