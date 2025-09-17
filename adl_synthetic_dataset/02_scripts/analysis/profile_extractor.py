#!/usr/bin/env python3
"""
Extract unique resident profiles from the ADL dataset
"""

import json
from collections import defaultdict

def extract_resident_profiles():
    with open('synthetic_adl_scenarios_enhanced.json', 'r') as f:
        data = json.load(f)
    
    profiles = {}
    profile_counts = defaultdict(int)
    
    for scenario in data:
        profile = scenario['resident_profile']
        key = (profile['age'], profile['gender'], tuple(sorted(profile['health_conditions'])))
        
        if key not in profiles:
            profiles[key] = profile
        profile_counts[key] += 1
    
    print("🏥 UNIQUE RESIDENT PROFILES IN DATASET")
    print("=" * 50)
    
    for i, (key, profile) in enumerate(profiles.items(), 1):
        age, gender, health_conditions = key
        count = profile_counts[key]
        
        print(f"\n👤 Resident {i}:")
        print(f"  Age: {age}")
        print(f"  Gender: {gender}")
        print(f"  Health Conditions: {list(health_conditions)}")
        print(f"  Scenarios: {count}")
    
    print(f"\n📊 Total unique profiles: {len(profiles)}")
    print(f"📊 Total scenarios: {len(data)}")
    
    return list(profiles.values())

if __name__ == "__main__":
    extract_resident_profiles()
