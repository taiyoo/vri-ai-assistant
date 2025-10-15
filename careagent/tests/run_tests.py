#!/usr/bin/env python3
"""
Test Runner for Multi-Agent Orchestration Platform

This script coordinates all testing activities:
1. Mock voice inputs from synthetic dataset
2. High concurrency testing
3. Metrics collection and analysis
4. Report generation

Usage:
    python run_tests.py --full  # Run complete test suite
    python run_tests.py --quick  # Run quick validation tests
    python run_tests.py --load --agents 2 --requests 20  # Load testing only
"""

import asyncio
import argparse
import sys
from pathlib import Path
import subprocess
import json
from datetime import datetime

def check_dependencies():
    """Check if required dependencies are available"""
    required_files = [
        "../src/router.py",
        "../src/config.py", 
        "../src/utils/logging.py",
        "../../../adl_synthetic_dataset/01_data/processed/synthetic_adl_scenarios_enhanced.json"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print("⚠️  Warning: Missing required files:")
        for file in missing_files:
            print(f"   - {file}")
        print("Some tests may not work correctly.")
        return False
    
    return True

def run_simple_tests(args):
    """Run the simple testing framework"""
    print("Running Simple Test Framework...")
    
    cmd = ["python", "simple_test.py"]
    
    if hasattr(args, 'agents'):
        cmd.extend(["--agents", str(args.agents)])
    if hasattr(args, 'requests'):
        cmd.extend(["--requests", str(args.requests)])
    
    # Add synthetic data path if it exists
    data_path = "../../../adl_synthetic_dataset/01_data/processed/synthetic_adl_scenarios_enhanced.json"
    if Path(data_path).exists():
        cmd.extend(["--data-path", data_path])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running simple tests: {e}")
        return False

def run_load_tests(args):
    """Run load testing (if available)"""
    if not Path("load_test.py").exists():
        print("Load test script not found, skipping load tests")
        return True
    
    print("Running Load Tests...")
    
    cmd = ["python", "load_test.py"]
    cmd.extend(["--agents", str(getattr(args, 'agents', 2))])
    cmd.extend(["--requests", str(getattr(args, 'requests', 20))])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Error running load tests: {e}")
        return False

def run_simulation_tests(args):
    """Run simulation tests (if available)"""
    if not Path("test_simulation.py").exists():
        print("Simulation test script not found, skipping simulation tests")
        return True
    
    print("Running Simulation Tests...")
    
    try:
        # Try to run pytest if available
        result = subprocess.run(["python", "-m", "pytest", "test_simulation.py", "-v"], 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Pytest not available, trying direct execution: {e}")
        
        try:
            result = subprocess.run(["python", "test_simulation.py"], 
                                  capture_output=True, text=True)
            print(result.stdout)
            if result.stderr:
                print("Errors:", result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"Error running simulation tests: {e}")
            return False

def analyze_synthetic_data():
    """Analyze the synthetic ADL dataset"""
    data_path = "../../../adl_synthetic_dataset/01_data/processed/synthetic_adl_scenarios_enhanced.json"
    
    if not Path(data_path).exists():
        print("⚠️  Synthetic data not found at expected location")
        return {}
    
    try:
        with open(data_path, 'r') as f:
            data = json.load(f)
        
        print(f"📊 Synthetic Dataset Analysis:")
        print(f"   Total scenarios: {len(data)}")
        
        # Analyze first 100 scenarios for performance
        sample_data = data[:100] if len(data) > 100 else data
        
        adl_categories = {}
        environments = {}
        caregiver_roles = {}
        
        for scenario in sample_data:
            context = scenario.get("context", {})
            
            adl_cat = context.get("adl_category", "unknown")
            adl_categories[adl_cat] = adl_categories.get(adl_cat, 0) + 1
            
            env = context.get("environment", "unknown") 
            environments[env] = environments.get(env, 0) + 1
            
            role = context.get("caregiver_role", "unknown")
            caregiver_roles[role] = caregiver_roles.get(role, 0) + 1
        
        print(f"   ADL Categories: {list(adl_categories.keys())}")
        print(f"   Environments: {list(environments.keys())}")
        print(f"   Caregiver Roles: {list(caregiver_roles.keys())}")
        
        return {
            "total_scenarios": len(data),
            "adl_categories": adl_categories,
            "environments": environments,
            "caregiver_roles": caregiver_roles
        }
        
    except Exception as e:
        print(f"Error analyzing synthetic data: {e}")
        return {}

def generate_summary_report(test_results):
    """Generate a summary report of all test executions"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_file = f"test_execution_summary_{timestamp}.json"
    
    summary = {
        "execution_timestamp": datetime.now().isoformat(),
        "test_results": test_results,
        "synthetic_data_analysis": analyze_synthetic_data(),
        "recommendations": []
    }
    
    # Generate recommendations based on results
    if all(test_results.values()):
        summary["recommendations"].append("All tests passed - system appears ready for further development")
    else:
        failed_tests = [test for test, passed in test_results.items() if not passed]
        summary["recommendations"].append(f"Failed tests: {', '.join(failed_tests)} - investigate and fix issues")
    
    with open(report_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"📄 Summary report saved to {report_file}")
    return report_file

def main():
    """Main test execution function"""
    parser = argparse.ArgumentParser(description="Run comprehensive tests for multi-agent platform")
    parser.add_argument("--full", action="store_true", help="Run complete test suite")
    parser.add_argument("--quick", action="store_true", help="Run quick validation tests only")
    parser.add_argument("--load", action="store_true", help="Run load tests only")
    parser.add_argument("--agents", type=int, default=2, help="Number of concurrent agents for load testing")
    parser.add_argument("--requests", type=int, default=20, help="Number of requests for testing")
    
    args = parser.parse_args()
    
    print("="*80)
    print("MULTI-AGENT ORCHESTRATION PLATFORM - TEST EXECUTION")
    print("="*80)
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check dependencies
    print("\n🔍 Checking Dependencies...")
    deps_ok = check_dependencies()
    
    # Analyze synthetic data
    print("\n📊 Analyzing Synthetic Dataset...")
    analyze_synthetic_data()
    
    test_results = {}
    
    if args.load:
        # Load testing only
        print(f"\n🚀 Load Testing Mode (Agents: {args.agents}, Requests: {args.requests})")
        test_results["load_tests"] = run_load_tests(args)
    
    elif args.quick:
        # Quick tests only
        print("\n⚡ Quick Test Mode")
        test_results["simple_tests"] = run_simple_tests(args)
    
    else:
        # Full test suite (default)
        print("\n🧪 Full Test Suite Mode")
        
        print("\n" + "-"*50)
        print("1. SIMPLE FRAMEWORK TESTS")
        print("-"*50)
        test_results["simple_tests"] = run_simple_tests(args)
        
        print("\n" + "-"*50)
        print("2. LOAD TESTS")
        print("-"*50)
        test_results["load_tests"] = run_load_tests(args)
        
        print("\n" + "-"*50)
        print("3. SIMULATION TESTS")
        print("-"*50)
        test_results["simulation_tests"] = run_simulation_tests(args)
    
    # Generate summary
    print("\n" + "="*80)
    print("TEST EXECUTION SUMMARY")
    print("="*80)
    
    passed_tests = sum(1 for passed in test_results.values() if passed)
    total_tests = len(test_results)
    
    print(f"Tests Passed: {passed_tests}/{total_tests}")
    
    for test_name, passed in test_results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
    
    # Generate detailed report
    report_file = generate_summary_report(test_results)
    
    if all(test_results.values()):
        print(f"\n🎉 All tests completed successfully!")
        return 0
    else:
        print(f"\n⚠️  Some tests failed. Check the reports for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
