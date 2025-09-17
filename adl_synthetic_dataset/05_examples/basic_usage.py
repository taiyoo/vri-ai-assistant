#!/usr/bin/env python3
"""
Basic ADL Dataset Usage Example
==============================

This example demonstrates how to load and explore the ADL synthetic dataset.
"""

import json
import sys
from pathlib import Path
from collections import Counter

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

def load_dataset():
    """Load the processed ADL dataset"""
    data_path = project_root / "01_data" / "processed" / "synthetic_adl_scenarios_enhanced.json"
    
    if not data_path.exists():
        print(f"❌ Dataset not found at: {data_path}")
        print("Please ensure the dataset has been processed and is in the correct location.")
        return None
    
    with open(data_path, 'r', encoding='utf-8') as f:
        scenarios = json.load(f)
    
    print(f"✅ Loaded {len(scenarios)} ADL scenarios")
    return scenarios

def explore_dataset(scenarios):
    """Basic dataset exploration"""
    print("\n📊 DATASET OVERVIEW")
    print("=" * 50)
    
    # Basic statistics
    total_scenarios = len(scenarios)
    total_turns = sum(len(scenario['dialogue']) for scenario in scenarios)
    avg_turns = total_turns / total_scenarios if total_scenarios > 0 else 0
    
    print(f"Total Scenarios: {total_scenarios}")
    print(f"Total Dialogue Turns: {total_turns}")
    print(f"Average Turns per Scenario: {avg_turns:.1f}")
    
    # ADL categories
    categories = [scenario['context'].get('adl_category', 'Unknown') for scenario in scenarios]
    category_counts = Counter(categories)
    
    print("\n🎯 TOP ADL CATEGORIES:")
    for category, count in category_counts.most_common(5):
        print(f"  • {category}: {count} scenarios")
    
    # Environments
    environments = [scenario['context'].get('environment', 'Unknown') for scenario in scenarios]
    environment_counts = Counter(environments)
    
    print("\n🏥 CARE ENVIRONMENTS:")
    for environment, count in environment_counts.most_common():
        print(f"  • {environment}: {count} scenarios")
    
    # Resident demographics
    ages = []
    genders = []
    conditions = []
    
    for scenario in scenarios:
        profile = scenario.get('resident_profile', {})
        
        if 'age' in profile:
            ages.append(str(profile['age']))
        if 'gender' in profile:
            genders.append(profile['gender'])
        
        health = profile.get('health_conditions', [])
        conditions.extend(health)
    
    print("\n👥 RESIDENT DEMOGRAPHICS:")
    if ages:
        age_counts = Counter(ages)
        print(f"  Ages: {', '.join(f'{age}({count})' for age, count in age_counts.most_common(3))}")
    
    if genders:
        gender_counts = Counter(genders)
        print(f"  Genders: {', '.join(f'{gender}({count})' for gender, count in gender_counts.items())}")
    
    if conditions:
        condition_counts = Counter(conditions)
        print(f"  Top Conditions: {', '.join(condition_counts.keys())[:3]}")

def show_sample_scenario(scenarios):
    """Show a sample scenario"""
    if not scenarios:
        return
    
    print("\n📝 SAMPLE SCENARIO")
    print("=" * 50)
    
    scenario = scenarios[0]
    
    print(f"Scenario ID: {scenario['scenario_id']}")
    print(f"Environment: {scenario['context'].get('environment', 'Unknown')}")
    print(f"ADL Category: {scenario['context'].get('adl_category', 'Unknown')}")
    print(f"Time: {scenario['context'].get('time_of_day', 'Unknown')}")
    
    # Show resident profile summary
    profile = scenario.get('resident_profile', {})
    if profile:
        age = profile.get('age', 'Unknown')
        gender = profile.get('gender', 'Unknown')
        print(f"Resident: {age} year old {gender}")
        
        conditions = profile.get('health_conditions', [])
        if conditions:
            print(f"Health Conditions: {', '.join(conditions[:3])}")
    
    # Show care goal
    if 'care_goal' in scenario:
        print(f"Care Goal: {scenario['care_goal'][:100]}...")
    
    # Show dialogue sample
    print("\n💬 DIALOGUE SAMPLE:")
    dialogue = scenario.get('dialogue', [])
    for turn in dialogue[:3]:  # Show first 3 turns
        speaker = turn.get('speaker', 'Unknown')
        utterance = turn.get('utterance', '')
        print(f"  {speaker}: {utterance}")
    
    if len(dialogue) > 3:
        print(f"  ... ({len(dialogue) - 3} more turns)")

def main():
    """Main execution function"""
    print("🎯 ADL SYNTHETIC DATASET - BASIC USAGE EXAMPLE")
    print("=" * 60)
    
    # Load dataset
    scenarios = load_dataset()
    if not scenarios:
        return 1
    
    # Explore dataset
    explore_dataset(scenarios)
    
    # Show sample
    show_sample_scenario(scenarios)
    
    print("\n✨ NEXT STEPS:")
    print("  • Try: python3 05_examples/voice_generation_demo.py")
    print("  • Explore: jupyter notebook 05_examples/jupyter_notebooks/")
    print("  • Analyze: python3 02_scripts/analysis/visualizer.py")
    
    return 0

if __name__ == "__main__":
    exit(main())
