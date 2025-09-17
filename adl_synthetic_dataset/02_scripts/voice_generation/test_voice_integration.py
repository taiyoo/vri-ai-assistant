#!/usr/bin/env python3
"""
Quick test script for Deepgram TTS integration
"""

import os
import asyncio
from voice_generation_system import DeepgramVoiceSystem

async def test_deepgram_integration():
    """Test the Deepgram TTS integration with a simple example"""
    
    # Check for API key
    api_key = os.getenv('DEEPGRAM_API_KEY')
    if not api_key:
        print("❌ DEEPGRAM_API_KEY environment variable not set")
        print("To set it: export DEEPGRAM_API_KEY='your_api_key_here'")
        return False
    
    print("✅ API key found")
    
    try:
        # Initialize system
        print("🔧 Initializing Deepgram Voice System...")
        vgs = DeepgramVoiceSystem(
            scenarios_file="synthetic_adl_scenarios_enhanced.json",
            output_dir="test_output",
            api_key=api_key
        )
        
        print("✅ System initialized successfully")
        
        # Test with first available scenario
        if vgs.scenarios_data:
            print(f"📊 Found {len(vgs.scenarios_data)} scenarios")
            print("🎯 Testing with first scenario that has dialogue...")
            
            # Find first scenario with dialogue
            test_scenario = None
            for scenario in vgs.scenarios_data:
                if scenario.get('dialogue') and len(scenario['dialogue']) > 0:
                    test_scenario = scenario
                    break
                    
            if test_scenario:
                print(f"🎤 Testing with scenario: {test_scenario.get('scenario_id', 'unknown')}")
                
                # Process just the first scenario
                result = await vgs.process_scenario(test_scenario)
                
                print("✅ Test completed successfully!")
                print(f"Generated {len(result['generated_files'])} audio files")
                print(f"Failed {len(result['failed_turns'])} turns")
                print(f"Processing time: {result['processing_time']:.2f} seconds")
                
                if result['generated_files']:
                    print(f"Sample file: {result['generated_files'][0]['file_path']}")
                    
                return True
            else:
                print("⚠️ No scenarios with dialogue found for testing")
                return False
        else:
            print("❌ No scenarios loaded")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def main():
    print("🎤 Deepgram TTS Integration Test")
    print("=" * 40)
    
    success = asyncio.run(test_deepgram_integration())
    
    if success:
        print("\n🎉 Integration test passed!")
        print("Ready to generate voices for all scenarios")
    else:
        print("\n❌ Integration test failed")
        print("Please check your setup and API key")

if __name__ == "__main__":
    main()
