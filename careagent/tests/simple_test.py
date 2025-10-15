#!/usr/bin/env python3
"""
Simple Testing Framework for Multi-Agent Platform

This script provides basic testing capabilities that work without complex dependencies.
It focuses on testing the core functionality and provides metrics analysis.
"""

import asyncio
import json
import time
import random
import argparse
from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class TestResult:
    """Simple test result structure"""
    test_id: str
    success: bool
    response_time: float
    intent: str
    utterance: str
    error: Optional[str] = None

@dataclass
class TestSummary:
    """Summary of test execution"""
    total_tests: int
    successful_tests: int
    failed_tests: int
    avg_response_time: float
    success_rate: float
    intent_distribution: Dict[str, int]
    errors: List[str]

class SimpleTestFramework:
    """Simple testing framework for the multi-agent platform"""
    
    SAMPLE_DATA = {
        "record_adl": [
            "I need to record that Mrs. Johnson had a shower this morning",
            "Patient completed her breakfast and took her medications",
            "Resident needed assistance with toileting at 2 PM"
        ],
        "medication": [
            "What's the dosage for warfarin for this patient?",
            "Patient missed her morning medications",
            "Need to check medication interactions"
        ],
        "behavior": [
            "Patient was agitated during care this morning",
            "Resident seems confused and doesn't recognize staff",
            "Mr. Brown was very cooperative during personal care"
        ],
        "governance_check": [
            "Need to verify all ADL documentation is complete",
            "Check if medication administration was properly recorded",
            "Audit required for compliance with care standards"
        ]
    }
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.start_time = time.time()
    
    async def mock_agent_call(self, intent: str, utterance: str) -> Dict[str, Any]:
        """Mock an agent call with realistic delay and response"""
        # Simulate processing time
        delay = random.uniform(0.1, 0.5)
        await asyncio.sleep(delay)
        
        # Simulate different success rates based on intent
        success_rates = {
            "record_adl": 0.95,
            "medication": 0.90,
            "behavior": 0.88,
            "governance_check": 0.92
        }
        
        success_rate = success_rates.get(intent, 0.85)
        success = random.random() < success_rate
        
        if success:
            return {
                "status": "success",
                "intent": intent,
                "response": f"Mock response for {intent}: {utterance[:50]}...",
                "confidence": random.uniform(0.8, 0.99),
                "processing_time": delay
            }
        else:
            error_messages = [
                "Service temporarily unavailable",
                "Rate limit exceeded", 
                "Invalid input format",
                "Timeout error"
            ]
            return {
                "status": "error",
                "error": random.choice(error_messages),
                "processing_time": delay
            }
    
    async def run_single_test(self, intent: str, utterance: str, test_id: str) -> TestResult:
        """Run a single test"""
        start_time = time.time()
        
        try:
            response = await self.mock_agent_call(intent, utterance)
            end_time = time.time()
            
            success = response.get("status") == "success"
            error = response.get("error") if not success else None
            
            return TestResult(
                test_id=test_id,
                success=success,
                response_time=end_time - start_time,
                intent=intent,
                utterance=utterance,
                error=error
            )
            
        except Exception as e:
            end_time = time.time()
            return TestResult(
                test_id=test_id,
                success=False,
                response_time=end_time - start_time,
                intent=intent,
                utterance=utterance,
                error=str(e)
            )
    
    async def run_concurrent_tests(self, num_agents: int, requests_per_agent: int) -> TestSummary:
        """Run tests with multiple concurrent agents"""
        print(f"Running {num_agents} agents with {requests_per_agent} requests each...")
        
        tasks = []
        test_counter = 0
        
        for agent_id in range(num_agents):
            for request_id in range(requests_per_agent):
                # Select random intent and utterance
                intent = random.choice(list(self.SAMPLE_DATA.keys()))
                utterance = random.choice(self.SAMPLE_DATA[intent])
                test_id = f"agent_{agent_id}_req_{request_id}"
                
                task = self.run_single_test(intent, utterance, test_id)
                tasks.append(task)
                test_counter += 1
        
        # Execute all tasks concurrently
        results = await asyncio.gather(*tasks)
        self.results.extend(results)
        
        # Calculate summary
        successful_tests = sum(1 for r in results if r.success)
        failed_tests = len(results) - successful_tests
        avg_response_time = sum(r.response_time for r in results) / len(results)
        success_rate = successful_tests / len(results)
        
        # Intent distribution
        intent_distribution = {}
        for result in results:
            intent_distribution[result.intent] = intent_distribution.get(result.intent, 0) + 1
        
        # Collect errors
        errors = [r.error for r in results if r.error]
        
        return TestSummary(
            total_tests=len(results),
            successful_tests=successful_tests,
            failed_tests=failed_tests,
            avg_response_time=avg_response_time,
            success_rate=success_rate,
            intent_distribution=intent_distribution,
            errors=errors
        )
    
    def analyze_synthetic_data(self, data_path: str) -> Dict[str, Any]:
        """Analyze synthetic ADL dataset"""
        try:
            with open(data_path, 'r') as f:
                data = json.load(f)
            
            analysis = {
                "total_scenarios": len(data),
                "adl_categories": {},
                "environments": {},
                "times_of_day": {},
                "caregiver_roles": {},
                "sample_utterances": []
            }
            
            for scenario in data[:50]:  # Analyze first 50 scenarios
                context = scenario.get("context", {})
                
                # Count ADL categories
                adl_cat = context.get("adl_category", "unknown")
                analysis["adl_categories"][adl_cat] = analysis["adl_categories"].get(adl_cat, 0) + 1
                
                # Count environments
                env = context.get("environment", "unknown")
                analysis["environments"][env] = analysis["environments"].get(env, 0) + 1
                
                # Count times of day
                time_of_day = context.get("time_of_day", "unknown")
                analysis["times_of_day"][time_of_day] = analysis["times_of_day"].get(time_of_day, 0) + 1
                
                # Count caregiver roles
                role = context.get("caregiver_role", "unknown")
                analysis["caregiver_roles"][role] = analysis["caregiver_roles"].get(role, 0) + 1
                
                # Extract sample utterances
                for turn in scenario.get("dialogue", [])[:2]:  # First 2 turns
                    if turn.get("speaker") == "Personal Care Assistant":
                        utterance = turn.get("utterance", "")
                        if utterance and len(utterance) > 10:
                            analysis["sample_utterances"].append(utterance[:100])
            
            return analysis
            
        except Exception as e:
            return {"error": f"Failed to analyze data: {e}"}
    
    def test_routing_logic(self) -> Dict[str, Any]:
        """Test simple routing logic"""
        print("Testing routing logic...")
        
        routing_tests = [
            ("I need to record a shower for Mrs. Smith", "record_adl"),
            ("Patient missed his medication dose", "medication"),
            ("Resident was agitated this morning", "behavior"),
            ("Check compliance documentation", "governance_check"),
            ("Hello, how are you?", "general")
        ]
        
        correct_routes = 0
        total_routes = len(routing_tests)
        
        for utterance, expected_intent in routing_tests:
            # Simple keyword-based routing
            predicted_intent = self._classify_intent(utterance)
            
            if predicted_intent == expected_intent:
                correct_routes += 1
                print(f"✓ '{utterance[:30]}...' -> {predicted_intent}")
            else:
                print(f"✗ '{utterance[:30]}...' -> {predicted_intent} (expected {expected_intent})")
        
        accuracy = correct_routes / total_routes
        return {
            "accuracy": accuracy,
            "correct_routes": correct_routes,
            "total_routes": total_routes
        }
    
    def _classify_intent(self, utterance: str) -> str:
        """Simple intent classification"""
        utterance_lower = utterance.lower()
        
        if any(word in utterance_lower for word in ["medication", "dose", "pill", "medicine"]):
            return "medication"
        elif any(word in utterance_lower for word in ["agitated", "confused", "mood", "behavior"]):
            return "behavior"
        elif any(word in utterance_lower for word in ["check", "verify", "compliance", "audit"]):
            return "governance_check"
        elif any(word in utterance_lower for word in ["record", "shower", "feeding", "toileting", "adl"]):
            return "record_adl"
        else:
            return "general"
    
    def simulate_discrepancy_detection(self) -> Dict[str, Any]:
        """Simulate discrepancy detection"""
        print("Simulating discrepancy detection...")
        
        # Mock discrepancies
        discrepancies = []
        
        for i in range(random.randint(2, 8)):
            discrepancy = {
                "id": f"DISC_{i+1:03d}",
                "type": random.choice(["documentation_mismatch", "timeline_inconsistency", "missing_signature"]),
                "severity": random.choice(["low", "medium", "high"]),
                "description": f"Mock discrepancy #{i+1} detected in care documentation",
                "detected_at": datetime.now().isoformat(),
                "resolved": random.choice([True, False])
            }
            discrepancies.append(discrepancy)
        
        stats = {
            "total_discrepancies": len(discrepancies),
            "resolved": sum(1 for d in discrepancies if d["resolved"]),
            "by_severity": {},
            "by_type": {}
        }
        
        for disc in discrepancies:
            # Count by severity
            severity = disc["severity"]
            stats["by_severity"][severity] = stats["by_severity"].get(severity, 0) + 1
            
            # Count by type
            disc_type = disc["type"]
            stats["by_type"][disc_type] = stats["by_type"].get(disc_type, 0) + 1
        
        return {
            "stats": stats,
            "discrepancies": discrepancies
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive test report"""
        total_time = time.time() - self.start_time
        
        if self.results:
            successful_results = [r for r in self.results if r.success]
            failed_results = [r for r in self.results if not r.success]
            
            avg_response_time = sum(r.response_time for r in self.results) / len(self.results)
            success_rate = len(successful_results) / len(self.results)
            
            intent_dist = {}
            for result in self.results:
                intent_dist[result.intent] = intent_dist.get(result.intent, 0) + 1
        else:
            avg_response_time = 0
            success_rate = 0
            intent_dist = {}
            failed_results = []
        
        return {
            "execution_summary": {
                "total_time": total_time,
                "total_requests": len(self.results),
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "requests_per_second": len(self.results) / total_time if total_time > 0 else 0
            },
            "intent_distribution": intent_dist,
            "error_summary": {
                "total_errors": len(failed_results),
                "error_types": list(set(r.error for r in failed_results if r.error))
            },
            "recommendations": self._generate_recommendations(success_rate, avg_response_time)
        }
    
    def _generate_recommendations(self, success_rate: float, avg_response_time: float) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        if success_rate < 0.9:
            recommendations.append("Consider improving error handling and retry mechanisms")
        
        if avg_response_time > 1.0:
            recommendations.append("Response times are high - investigate performance bottlenecks")
        
        if success_rate > 0.95 and avg_response_time < 0.5:
            recommendations.append("Excellent performance - system is ready for production")
        
        return recommendations
    
    def save_report(self, filename: Optional[str] = None):
        """Save test report"""
        if filename is None:
            filename = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report = self.generate_report()
        
        # Add detailed results
        report["detailed_results"] = [asdict(r) for r in self.results]
        
        with open(filename, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"Report saved to {filename}")

async def main():
    """Main testing function"""
    parser = argparse.ArgumentParser(description="Test the multi-agent platform")
    parser.add_argument("--agents", type=int, default=2, help="Number of concurrent agents")
    parser.add_argument("--requests", type=int, default=10, help="Requests per agent")
    parser.add_argument("--data-path", type=str, help="Path to synthetic ADL data")
    
    args = parser.parse_args()
    
    print("="*60)
    print("MULTI-AGENT PLATFORM TESTING FRAMEWORK")
    print("="*60)
    
    framework = SimpleTestFramework()
    
    # Test 1: Routing Logic
    print("\n1. Testing Routing Logic...")
    routing_results = framework.test_routing_logic()
    print(f"Routing Accuracy: {routing_results['accuracy']:.2%}")
    
    # Test 2: Single Agent Performance
    print("\n2. Testing Single Agent Performance...")
    single_summary = await framework.run_concurrent_tests(1, args.requests)
    print(f"Single Agent - Success Rate: {single_summary.success_rate:.2%}")
    print(f"Single Agent - Avg Response Time: {single_summary.avg_response_time:.3f}s")
    
    # Test 3: Multi-Agent Concurrency (if requested)
    if args.agents > 1:
        print(f"\n3. Testing {args.agents}-Agent Concurrency...")
        multi_summary = await framework.run_concurrent_tests(args.agents, args.requests)
        print(f"Multi-Agent - Success Rate: {multi_summary.success_rate:.2%}")
        print(f"Multi-Agent - Avg Response Time: {multi_summary.avg_response_time:.3f}s")
        
        # Compare performance
        throughput_ratio = (
            (multi_summary.total_tests / multi_summary.avg_response_time) / 
            (single_summary.total_tests / single_summary.avg_response_time)
        )
        print(f"Throughput Improvement: {throughput_ratio:.2f}x")
    
    # Test 4: Discrepancy Detection
    print("\n4. Testing Discrepancy Detection...")
    discrepancy_results = framework.simulate_discrepancy_detection()
    disc_stats = discrepancy_results["stats"]
    print(f"Discrepancies Detected: {disc_stats['total_discrepancies']}")
    print(f"Resolved: {disc_stats['resolved']}")
    
    # Test 5: Synthetic Data Analysis (if path provided)
    if args.data_path:
        print(f"\n5. Analyzing Synthetic Data from {args.data_path}...")
        data_analysis = framework.analyze_synthetic_data(args.data_path)
        if "error" not in data_analysis:
            print(f"Total Scenarios: {data_analysis['total_scenarios']}")
            print(f"ADL Categories: {list(data_analysis['adl_categories'].keys())}")
        else:
            print(f"Error: {data_analysis['error']}")
    
    # Generate final report
    print("\n" + "="*60)
    print("GENERATING FINAL REPORT")
    print("="*60)
    
    final_report = framework.generate_report()
    execution = final_report["execution_summary"]
    
    print(f"Total Execution Time: {execution['total_time']:.2f}s")
    print(f"Total Requests: {execution['total_requests']}")
    print(f"Overall Success Rate: {execution['success_rate']:.2%}")
    print(f"Average Response Time: {execution['avg_response_time']:.3f}s")
    print(f"Requests Per Second: {execution['requests_per_second']:.1f}")
    
    if final_report["recommendations"]:
        print(f"\nRecommendations:")
        for rec in final_report["recommendations"]:
            print(f"• {rec}")
    
    # Save report
    framework.save_report()
    
    print(f"\n✅ Testing completed successfully!")

if __name__ == "__main__":
    asyncio.run(main())
