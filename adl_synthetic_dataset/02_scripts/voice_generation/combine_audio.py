#!/usr/bin/env python3
"""
Audio File Combiner for ADL Scenarios
====================================

Combines individual dialogue turn WAV files into a single conversation file.
"""

import os
import asyncio
from pathlib import Path
from pydub import AudioSegment
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AudioCombiner:
    """Combines individual audio files into conversation files"""
    
    def __init__(self, pause_duration_ms: int = 500):
        """
        Initialize the audio combiner
        
        Args:
            pause_duration_ms: Duration of pause between speakers in milliseconds
        """
        self.pause_duration_ms = pause_duration_ms
        
    def combine_scenario_audio(self, scenario_dir: Path) -> Path:
        """
        Combine all audio files in a scenario directory into one conversation file
        
        Args:
            scenario_dir: Directory containing individual turn audio files
            
        Returns:
            Path to the combined audio file
        """
        # Find all WAV files in the scenario directory
        audio_files = sorted(scenario_dir.glob("*_turn_*.wav"))
        
        if not audio_files:
            logger.warning(f"No audio files found in {scenario_dir}")
            return None
            
        logger.info(f"Combining {len(audio_files)} audio files from {scenario_dir.name}")
        
        # Load the first audio file
        combined_audio = AudioSegment.from_wav(str(audio_files[0]))
        
        # Add each subsequent file with a pause
        for audio_file in audio_files[1:]:
            # Add pause between speakers
            pause = AudioSegment.silent(duration=self.pause_duration_ms)
            combined_audio += pause
            
            # Add the next audio segment
            next_audio = AudioSegment.from_wav(str(audio_file))
            combined_audio += next_audio
            
        # Create output filename
        scenario_id = scenario_dir.name
        output_file = scenario_dir / f"{scenario_id}_full_conversation.wav"
        
        # Export the combined audio
        combined_audio.export(str(output_file), format="wav")
        
        logger.info(f"Combined conversation saved: {output_file}")
        
        # Log statistics
        duration_seconds = len(combined_audio) / 1000
        logger.info(f"Total conversation duration: {duration_seconds:.1f} seconds")
        
        return output_file
        
    def combine_all_scenarios(self, base_dir: Path) -> dict:
        """
        Combine audio files for all scenarios in the base directory
        
        Args:
            base_dir: Base directory containing scenario folders
            
        Returns:
            Dictionary with results for each scenario
        """
        results = {}
        
        # Find all scenario directories
        scenario_dirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name.startswith('ADL_')]
        
        logger.info(f"Found {len(scenario_dirs)} scenario directories")
        
        for scenario_dir in scenario_dirs:
            try:
                combined_file = self.combine_scenario_audio(scenario_dir)
                results[scenario_dir.name] = {
                    'success': True,
                    'combined_file': str(combined_file) if combined_file else None,
                    'error': None
                }
            except Exception as e:
                logger.error(f"Error combining {scenario_dir.name}: {e}")
                results[scenario_dir.name] = {
                    'success': False,
                    'combined_file': None,
                    'error': str(e)
                }
                
        return results

def main():
    """Main function to combine audio files"""
    
    # Configuration
    base_dir = Path("generated_audio")
    pause_duration = 500  # 500ms pause between speakers
    
    if not base_dir.exists():
        logger.error(f"Directory {base_dir} does not exist")
        return
        
    # Create combiner
    combiner = AudioCombiner(pause_duration_ms=pause_duration)
    
    # Combine all scenarios
    results = combiner.combine_all_scenarios(base_dir)
    
    # Print summary
    print("\n🎵 AUDIO COMBINATION SUMMARY")
    print("=" * 40)
    
    successful = sum(1 for r in results.values() if r['success'])
    total = len(results)
    
    print(f"Successfully combined: {successful}/{total} scenarios")
    print(f"Pause between speakers: {pause_duration}ms")
    
    for scenario_id, result in results.items():
        if result['success']:
            print(f"✅ {scenario_id}: {result['combined_file']}")
        else:
            print(f"❌ {scenario_id}: {result['error']}")

if __name__ == "__main__":
    main()
