#!/usr/bin/env python3
"""
Create personalized voice configurations for the top 5 most common resident profiles
"""

import json
from collections import defaultdict

def get_top_resident_profiles():
    with open('synthetic_adl_scenarios_enhanced.json', 'r') as f:
        data = json.load(f)
    
    profile_counts = defaultdict(int)
    profile_data = {}
    
    for scenario in data:
        profile = scenario['resident_profile']
        key = (profile['age'], profile['gender'], tuple(sorted(profile['health_conditions'])))
        
        if key not in profile_data:
            profile_data[key] = profile
        profile_counts[key] += 1
    
    # Sort by frequency and take top 5
    top_profiles = sorted(profile_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    print("🎤 TOP 5 RESIDENT PROFILES FOR VOICE CONFIGURATION")
    print("=" * 60)
    
    voice_configs = []
    
    for i, ((age, gender, health_conditions), count) in enumerate(top_profiles, 1):
        profile = profile_data[(age, gender, health_conditions)]
        
        print(f"\n👤 Resident Profile {i} ({count} scenarios):")
        print(f"  Age: {age}")
        print(f"  Gender: {gender}")
        print(f"  Health Conditions: {list(health_conditions)}")
        
        # Create voice configuration based on profile
        voice_config = create_voice_config(i, age, gender, list(health_conditions))
        voice_configs.append(voice_config)
        
        print(f"  🎵 Voice Model: {voice_config['voice_model']}")
        print(f"  🎛️  Speech Rate: {voice_config['speech_rate']}")
        print(f"  📢 Characteristics: {voice_config['characteristics']}")
    
    return voice_configs

def create_voice_config(profile_id, age, gender, health_conditions):
    """Create personalized voice configuration based on resident profile"""
    
    # Base voice selection based on gender and age
    if gender.lower() == 'female':
        if age >= 90:
            voice_model = "aura-2-athena-en"  # Mature, calm, professional
            characteristics = "Calm, mature, gentle"
        elif age >= 85:
            voice_model = "aura-2-vesta-en"   # Natural, empathetic, patient
            characteristics = "Natural, empathetic, patient"
        else:
            voice_model = "aura-2-luna-en"    # Friendly, natural, engaging
            characteristics = "Friendly, natural, engaging"
    else:  # Male
        if age >= 90:
            voice_model = "aura-2-orpheus-en" # Professional, clear, trustworthy
            characteristics = "Professional, clear, trustworthy"
        elif age >= 85:
            voice_model = "aura-2-mars-en"    # Smooth, patient, trustworthy
            characteristics = "Smooth, patient, trustworthy"
        else:
            voice_model = "aura-2-orion-en"   # Approachable, comfortable, calm
            characteristics = "Approachable, comfortable, calm"
    
    # Adjust speech rate based on health conditions
    speech_rate = 1.0
    
    # Health condition adjustments
    if any('hearing' in condition.lower() for condition in health_conditions):
        speech_rate = 0.8  # Slower for hearing impaired
        characteristics += ", clear enunciation"
    
    if any('dementia' in condition.lower() for condition in health_conditions):
        speech_rate = 0.7  # Much slower for dementia
        characteristics += ", very clear speech"
    
    if any('parkinson' in condition.lower() for condition in health_conditions):
        speech_rate = 0.75  # Slower for Parkinson's
        characteristics += ", steady pace"
    
    if any('cognitive' in condition.lower() for condition in health_conditions):
        speech_rate = 0.8   # Slower for cognitive impairment
        characteristics += ", gentle delivery"
    
    return {
        "profile_id": profile_id,
        "age": age,
        "gender": gender,
        "health_conditions": health_conditions,
        "voice_model": voice_model,
        "speech_rate": speech_rate,
        "characteristics": characteristics
    }

if __name__ == "__main__":
    voice_configs = get_top_resident_profiles()
    
    print("\n" + "=" * 60)
    print("🎉 VOICE CONFIGURATIONS READY FOR IMPLEMENTATION")
    print("=" * 60)
