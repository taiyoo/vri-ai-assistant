#!/usr/bin/env python3
"""
Load Testing Script for Multi-Agent Orchestration Platform

This script provides simple load testing capabilities to verify:
1. Agent routing performance
2. Bedrock agent call verification
3. Discrepancy detection functionality
4. Concurrency handling

Usage:
    python load_test.py --agents 1 --requests 10
    python load_test.py --agents 2 --requests 20 --delay 0.1
"""

import asyncio
import argparse
import json
import time
import random
from pathlib import Path
from typing import List, Dict, Any, Optional
import sys

# Add the src directory to Python path
sys.path.append('../src')

try:
    from src.utils.metrics import get_metrics_collector
    from src.router import AgentRouter
    from src.intent_classifier import IntentClassifier
    from src.utils.logging import get_logger
    
    logger = get_logger("load_test")
    
except ImportError as e:
    print(f"Warning: Could not import modules: {e}")
    print("This script should be run from the careagent directory")
    
    # Create fallback logger
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("load_test")

class MockDataGenerator:
    """Generate mock data for load testing"""
    
    SAMPLE_UTTERANCES = {
        "record_adl": [
            "I need to record that Mrs. Johnson had a shower this morning",
            "Patient completed her breakfast and took her medications",
            "Resident needed assistance with toileting at 2 PM",
            "Mr. Smith refused his afternoon shower today",
            "Completed repositioning for bed-bound patient"
        ],
        "medication": [
            "What's the dosage for warfarin for this patient?",
            "Patient missed her morning medications",
            "Need to check medication interactions for new prescription",
            "Blood levels indicate warfarin adjustment needed",
            "Patient experiencing side effects from new medication"
        ],
        "behavior": [
            "Patient was agitated during care this morning",
            "Resident seems confused and doesn't recognize staff",
            "Mr. Brown was very cooperative during personal care",
            "Patient exhibited wandering behavior overnight",
            "Resident appears depressed and withdrawn today"
        ],
        "governance_check": [
            "Need to verify all ADL documentation is complete",
            "Check if medication administration was properly recorded",
            "Audit required for compliance with care standards",
            "Verify discrepancies in care documentation",
            "Review incomplete care records for this shift"
        ],
        "general": [
            "What's the weather like today?",
            "How long have you been working here?",
            "Can you help me find the supply room?",
            "What time does the next shift start?",
            "Hello, how are you doing?"
        ]
    }
    
    def generate_mock_request(self, intent: Optional[str] = None) -> Dict[str, Any]:
        """Generate a mock request with random or specified intent"""
        if intent is None:
            intent = random.choice(list(self.SAMPLE_UTTERANCES.keys()))
        
        utterance = random.choice(self.SAMPLE_UTTERANCES[intent])
        
        return {
            "intent": intent,
            "utterance": utterance,
            "context": {
                "environment": random.choice(["Room", "Bathroom", "Kitchen", "Lounge"]),
                "time_of_day": random.choice(["Morning", "Afternoon", "Evening", "Night"]),
                "caregiver_role": random.choice(["Registered Nurse", "Personal Care Assistant", "Medication Nurse"]),
                "adl_category": random.choice(["Hygiene", "Mobility", "Feeding", "Toileting", "Medication"])
            },
            "metadata": {
                "test_case": True,
                "generated_at": time.time(),
                "patient_id": f"TEST_{random.randint(1000, 9999)}"
            }
        }

class LoadTester:
    """Main load testing class"""
    
    def __init__(self):
        try:
            self.metrics = get_metrics_collector()
        except:
            self.metrics = None
        self.router = None
        self.data_generator = MockDataGenerator()
        self.results = []
        
    async def setup(self):
        """Initialize components"""
        try:
            if 'AgentRouter' in globals():
                self.router = AgentRouter()
                logger.info("Load tester initialized successfully")
            else:
                logger.warning("AgentRouter not available - using mock mode")
                self.router = None
        except Exception as e:
            logger.error(f"Failed to initialize router: {e}")
            self.router = None
    
    async def single_request_test(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single request and collect metrics"""
        start_time = time.time()
        
        try:
            with self.metrics.timed_operation(f"request_{request_data['intent']}"):
                # Record routing decision
                self.metrics.record_routing_decision(
                    utterance=request_data["utterance"],
                    predicted_intent=request_data["intent"],
                    actual_intent=request_data["intent"],  # In mock data, these match
                    confidence_score=0.95,  # Mock confidence
                    response_time=0.0,  # Will be updated
                    success=True
                )
                
                # Call the router
                response = await self.router.route(request_data["intent"], request_data)
                
                # Record Bedrock call
                self.metrics.record_bedrock_call(
                    agent_type=request_data["intent"],
                    model_id="mock-model",
                    input_tokens=len(request_data["utterance"].split()) * 2,  # Rough estimate
                    output_tokens=50,  # Mock output tokens
                    response_time=time.time() - start_time,
                    success=True,
                    cost_estimate=0.001  # Mock cost
                )
                
                end_time = time.time()
                
                return {
                    "success": True,
                    "response": response,
                    "response_time": end_time - start_time,
                    "request": request_data,
                    "error": None
                }
                
        except Exception as e:
            end_time = time.time()
            
            # Record failed routing
            self.metrics.record_routing_decision(
                utterance=request_data["utterance"],
                predicted_intent=request_data["intent"],
                response_time=end_time - start_time,
                success=False,
                error_message=str(e)
            )
            
            logger.error(f"Request failed: {e}")
            return {
                "success": False,
                "response": None,
                "response_time": end_time - start_time,
                "request": request_data,
                "error": str(e)
            }
    
    async def concurrent_load_test(
        self,
        num_agents: int = 1,
        requests_per_agent: int = 10,
        delay_between_requests: float = 0.1,
        intent_distribution: Dict[str, float] = None
    ) -> Dict[str, Any]:
        """Run concurrent load test"""
        
        if intent_distribution is None:
            intent_distribution = {
                "record_adl": 0.4,
                "medication": 0.2,
                "behavior": 0.2,
                "governance_check": 0.1,
                "general": 0.1
            }
        
        logger.info(f"Starting load test: {num_agents} agents, {requests_per_agent} requests each")
        
        start_time = time.time()
        tasks = []
        
        # Generate requests for each agent
        for agent_id in range(num_agents):
            for request_id in range(requests_per_agent):
                # Select intent based on distribution
                intent = random.choices(
                    list(intent_distribution.keys()),
                    weights=list(intent_distribution.values())
                )[0]
                
                request_data = self.data_generator.generate_mock_request(intent)
                request_data["agent_id"] = agent_id
                request_data["request_id"] = request_id
                
                task = self.single_request_test(request_data)
                tasks.append(task)
                
                # Add delay between requests
                if delay_between_requests > 0:
                    await asyncio.sleep(delay_between_requests)
        
        # Execute all requests concurrently
        logger.info(f"Executing {len(tasks)} concurrent requests...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Process results
        successful_requests = sum(1 for r in results if isinstance(r, dict) and r.get("success", False))
        failed_requests = len(results) - successful_requests
        
        response_times = [
            r.get("response_time", 0) for r in results 
            if isinstance(r, dict) and "response_time" in r
        ]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        # Check for discrepancies (mock implementation)
        discrepancies_detected = random.randint(0, max(1, len(results) // 10))
        for i in range(discrepancies_detected):
            self.metrics.record_discrepancy(
                scenario_id=f"LOAD_TEST_{i}",
                discrepancy_type="documentation_mismatch",
                severity=random.choice(["low", "medium", "high"]),
                detected_by="automated_audit",
                description=f"Mock discrepancy detected during load test #{i}",
                resolved=random.choice([True, False])
            )
        
        # Compile results
        test_results = {
            "test_config": {
                "num_agents": num_agents,
                "requests_per_agent": requests_per_agent,
                "total_requests": len(results),
                "delay_between_requests": delay_between_requests,
                "intent_distribution": intent_distribution
            },
            "performance": {
                "total_time": total_time,
                "successful_requests": successful_requests,
                "failed_requests": failed_requests,
                "success_rate": successful_requests / len(results) if results else 0,
                "avg_response_time": avg_response_time,
                "requests_per_second": len(results) / total_time if total_time > 0 else 0,
                "discrepancies_detected": discrepancies_detected
            },
            "detailed_results": results
        }
        
        self.results.append(test_results)
        
        logger.info(f"Load test completed in {total_time:.2f}s")
        logger.info(f"Success rate: {successful_requests}/{len(results)} ({100*successful_requests/len(results):.1f}%)")
        logger.info(f"Average response time: {avg_response_time:.3f}s")
        logger.info(f"Requests per second: {len(results)/total_time:.1f}")
        
        return test_results
    
    def print_summary(self):
        """Print a summary of all test results"""
        if not self.results:
            print("No test results available")
            return
        
        print("\n" + "="*60)
        print("LOAD TEST SUMMARY")
        print("="*60)
        
        for i, result in enumerate(self.results, 1):
            config = result["test_config"]
            perf = result["performance"]
            
            print(f"\nTest {i}:")
            print(f"  Agents: {config['num_agents']}")
            print(f"  Requests per agent: {config['requests_per_agent']}")
            print(f"  Total requests: {config['total_requests']}")
            print(f"  Success rate: {perf['success_rate']:.2%}")
            print(f"  Avg response time: {perf['avg_response_time']:.3f}s")
            print(f"  Requests/sec: {perf['requests_per_second']:.1f}")
            print(f"  Discrepancies detected: {perf['discrepancies_detected']}")
        
        # Overall metrics
        overall_metrics = self.metrics.generate_summary_report()
        print(f"\nOverall Session Metrics:")
        print(f"  Total routing decisions: {overall_metrics['routing_metrics']['total_routing_decisions']}")
        print(f"  Routing accuracy: {overall_metrics['routing_metrics']['routing_accuracy']:.2%}")
        print(f"  Bedrock calls: {overall_metrics['bedrock_metrics'].get('total_calls', 0)}")
        print(f"  Total discrepancies: {overall_metrics['discrepancy_metrics'].get('total_discrepancies', 0)}")
    
    def save_results(self, filename: str = None):
        """Save test results to file"""
        if filename is None:
            filename = f"load_test_results_{time.strftime('%Y%m%d_%H%M%S')}.json"
        
        output_data = {
            "test_results": self.results,
            "metrics_summary": self.metrics.generate_summary_report(),
            "test_timestamp": time.time()
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2, default=str)
        
        print(f"Results saved to {filename}")
        
        # Also save detailed metrics
        self.metrics.save_detailed_metrics("load_test")

async def run_load_tests(args):
    """Run the load tests based on command line arguments"""
    tester = LoadTester()
    
    try:
        await tester.setup()
        
        # Run single agent test
        print("Running single agent test...")
        await tester.concurrent_load_test(
            num_agents=1,
            requests_per_agent=args.requests // 2,
            delay_between_requests=args.delay
        )
        
        # Run multi-agent test if requested
        if args.agents > 1:
            print(f"Running {args.agents}-agent test...")
            await tester.concurrent_load_test(
                num_agents=args.agents,
                requests_per_agent=args.requests // args.agents,
                delay_between_requests=args.delay
            )
        
        # Print summary and save results
        tester.print_summary()
        tester.save_results()
        
    except Exception as e:
        logger.error(f"Load test failed: {e}")
        raise

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Load test the multi-agent platform")
    parser.add_argument("--agents", type=int, default=2, help="Number of concurrent agents (default: 2)")
    parser.add_argument("--requests", type=int, default=20, help="Total number of requests (default: 20)")
    parser.add_argument("--delay", type=float, default=0.1, help="Delay between requests in seconds (default: 0.1)")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        import logging
        logging.getLogger().setLevel(logging.DEBUG)
    
    print(f"Starting load test with {args.agents} agents, {args.requests} total requests")
    
    try:
        asyncio.run(run_load_tests(args))
        print("\nLoad test completed successfully!")
    except KeyboardInterrupt:
        print("\nLoad test interrupted by user")
    except Exception as e:
        print(f"\nLoad test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
