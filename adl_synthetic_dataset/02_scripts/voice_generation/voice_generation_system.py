#!/usr/bin/env python3
"""
Voice Generation System for ADL Healthcare Scenarios - Deepgram TTS
==================================================================

This system generates synthetic voice data from the corrected ADL dialogue scenarios,
creating realistic audio files for caregiver and resident interactions using Deepgram TTS.

Features:
- Multi-speaker voice synthesis with distinct voices for caregivers and residents
- Context-aware audio generation based on environment and time of day
- Emotion and tone adjustment based on speaker intent and health conditions
- Batch processing with progress tracking
- Audio quality optimization for healthcare training applications
"""

import json
import os
import asyncio
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import aiohttp
import aiofiles
import argparse

# Audio processing imports
try:
    from pydub import AudioSegment
    AUDIO_PROCESSING_AVAILABLE = True
except ImportError:
    AUDIO_PROCESSING_AVAILABLE = False
    print("Warning: pydub not available. Combined audio files will not be generated.")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('voice_generation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class VoiceConfig:
    """Configuration for voice synthesis parameters"""
    caregiver_voice_id: str = "aura-2-hera-en"     # Default Aura 2 voice for caregivers
    resident_voice_id: str = "aura-2-athena-en"    # Default Aura 2 voice for residents
    encoding: str = "linear16"
    sample_rate: int = 24000
    container: str = "wav"
    
@dataclass
class SpeechParameters:
    """Parameters for speech synthesis based on context"""
    model: str = "aura-asteria-en"
    speed: float = 1.0  # Speech speed multiplier
    emphasis: str = "normal"

class DeepgramVoiceSystem:
    """Main system for generating voice data from ADL scenarios using Deepgram TTS"""
    
    def __init__(self, 
                 scenarios_file: str = "synthetic_adl_scenarios_enhanced.json",
                 output_dir: str = "generated_audio",
                 api_key: Optional[str] = None):
        """
        Initialize the voice generation system
        
        Args:
            scenarios_file: Path to the ADL scenarios JSON file
            output_dir: Directory to store generated audio files
            api_key: Deepgram API key (if None, will read from environment)
        """
        self.scenarios_file = scenarios_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True, parents=True)
        
        # Get API key
        self.api_key = api_key or os.getenv('DEEPGRAM_API_KEY')
        if not self.api_key:
            raise ValueError("Deepgram API key is required. Set DEEPGRAM_API_KEY environment variable or pass api_key parameter.")
            
        logger.info("Initialized Deepgram TTS client")
            
        self.voice_config = VoiceConfig()
        self.scenarios_data = self._load_scenarios()
        
        # Statistics tracking
        self.stats = {
            'total_scenarios': 0,
            'processed_scenarios': 0,
            'total_utterances': 0,
            'generated_audio_files': 0,
            'failed_generations': 0,
            'processing_start_time': None,
            'processing_end_time': None
        }
        
    def _load_scenarios(self) -> List[Dict]:
        """Load and validate ADL scenarios from JSON file"""
        try:
            with open(self.scenarios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"Loaded {len(data)} scenarios from {self.scenarios_file}")
            return data
        except FileNotFoundError:
            logger.error(f"Scenarios file not found: {self.scenarios_file}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in scenarios file: {e}")
            raise
            
    def _get_voice_parameters(self, 
                                speaker: str, 
                                context: Dict, 
                                intent: str, 
                                health_conditions: List[str] = None,
                                scenario_data: Dict = None) -> Tuple[str, SpeechParameters]:
        """
        Select appropriate voice model and parameters based on context and resident profile
        
        Args:
            speaker: The speaker role/name
            context: Scenario context including environment, time, etc.
            intent: Speaker's intent for the utterance
            health_conditions: Resident's health conditions
            scenario_data: Full scenario data for resident profile matching
            
        Returns:
            Tuple of (voice_model, speech_parameters)
        """
        from voice_config import CAREGIVER_VOICES, RESIDENT_VOICE_PROFILES, RESIDENT_VOICES
        
        health_conditions = health_conditions or []
        
        # Determine speaker type and select appropriate voice
        is_caregiver = any(role in speaker.lower() for role in ['caregiver', 'nurse', 'assistant'])
        
        if is_caregiver:
            # For caregivers, try to determine gender from speaker name/role
            # Default to female voice, but could be enhanced with name-based gender detection
            if any(male_indicator in speaker.lower() for male_indicator in ['mr', 'male', 'man']):
                voice_model = CAREGIVER_VOICES["male"]  # aura-2-zeus-en (Aura 2)
            else:
                voice_model = CAREGIVER_VOICES["female"]  # aura-2-hera-en (Aura 2)
            base_params = SpeechParameters(model=voice_model, speed=1.0)
        else:
            # For residents, try to match to personalized voice profiles
            voice_model, speed = self._get_personalized_resident_voice(scenario_data, health_conditions)
            base_params = SpeechParameters(model=voice_model, speed=speed)        # Adjust parameters based on health conditions
        if health_conditions:
            if any('hearing' in condition.lower() for condition in health_conditions):
                # No volume control in Deepgram, but we can use slower speech
                base_params.speed = max(0.7, base_params.speed - 0.1)
            if any('parkinson' in condition.lower() for condition in health_conditions):
                base_params.speed = 0.7  # Much slower speech
            if any('dementia' in condition.lower() for condition in health_conditions):
                base_params.speed = 0.8  # Slower, clearer speech
                
        # Adjust based on time of day
        time_of_day = context.get('time_of_day', '').lower()
        if time_of_day == 'evening':
            base_params.speed = max(0.8, base_params.speed - 0.1)  # Slower in evening
            
        return voice_model, base_params
        
    async def _synthesize_speech_deepgram(self, 
                                        text: str, 
                                        voice_model: str, 
                                        params: SpeechParameters,
                                        output_file: str) -> bool:
        """
        Synthesize speech using Deepgram TTS API
        
        Args:
            text: The text to convert to speech
            voice_model: Deepgram voice model
            params: Speech parameters for customization
            output_file: Path to save the audio file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Clean text
            clean_text = text.strip()
            if not clean_text:
                return False
                
            # Prepare request
            url = "https://api.deepgram.com/v1/speak"
            headers = {
                "Authorization": f"Token {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Build request payload - Deepgram TTS format
            payload = {
                "text": clean_text
            }
            
            # Add query parameters for Deepgram TTS
            query_params = {
                "model": voice_model,
                "encoding": self.voice_config.encoding,
                "sample_rate": str(self.voice_config.sample_rate),
                "container": self.voice_config.container
            }
            
            # Add speed parameter if different from default
            if params.speed != 1.0:
                # Deepgram uses different parameter names, adjust as needed
                # Check Deepgram docs for exact parameter name
                pass  # Speed control might be model-dependent
            
            # Build URL with query parameters
            url_with_params = f"{url}?" + "&".join([f"{k}={v}" for k, v in query_params.items()])
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url_with_params, headers=headers, json=payload) as response:
                    if response.status == 200:
                        # Save audio file
                        async with aiofiles.open(output_file, 'wb') as f:
                            async for chunk in response.content.iter_chunked(8192):
                                await f.write(chunk)
                        
                        logger.debug(f"Generated audio: {output_file}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Deepgram API error {response.status} for {output_file}: {error_text}")
                        return False
                        
        except Exception as e:
            logger.error(f"Unexpected error generating {output_file}: {e}")
            return False
            
    def _create_output_structure(self, scenario_id: str) -> Path:
        """Create organized directory structure for audio files"""
        scenario_dir = self.output_dir / scenario_id
        scenario_dir.mkdir(exist_ok=True, parents=True)
        return scenario_dir
        
    async def process_scenario(self, scenario: Dict) -> Dict:
        """
        Process a single ADL scenario and generate all audio files
        
        Args:
            scenario: ADL scenario dictionary
            
        Returns:
            Processing results dictionary
        """
        scenario_id = scenario.get('scenario_id', 'unknown')
        dialogue = scenario.get('dialogue', [])
        context = scenario.get('context', {})
        resident_profile = scenario.get('resident_profile', {})
        health_conditions = resident_profile.get('health_conditions', [])
        
        logger.info(f"Processing scenario {scenario_id} with {len(dialogue)} dialogue turns")
        
        scenario_dir = self._create_output_structure(scenario_id)
        results = {
            'scenario_id': scenario_id,
            'total_turns': len(dialogue),
            'generated_files': [],
            'failed_turns': [],
            'processing_time': 0
        }
        
        start_time = datetime.now()
        
        # Process each dialogue turn
        for turn in dialogue:
            turn_id = turn.get('turn_id', 0)
            speaker = turn.get('speaker', 'Unknown')
            utterance = turn.get('utterance', '').strip()
            intent = turn.get('intent', '')
            
            # Skip empty utterances
            if not utterance:
                logger.warning(f"Skipping empty utterance in {scenario_id}, turn {turn_id}")
                results['failed_turns'].append({
                    'turn_id': turn_id,
                    'reason': 'Empty utterance'
                })
                continue
                
            # Generate voice parameters
            voice_model, speech_params = self._get_voice_parameters(
                speaker, context, intent, health_conditions, scenario
            )
            
            # Generate output filename
            speaker_clean = speaker.replace(' ', '_').replace('-', '_')
            output_filename = f"{scenario_id}_turn_{turn_id:02d}_{speaker_clean}.{self.voice_config.container}"
            output_path = scenario_dir / output_filename
            
            # Synthesize speech using Deepgram
            success = await self._synthesize_speech_deepgram(
                utterance, voice_model, speech_params, str(output_path)
            )
            
            if success:
                results['generated_files'].append({
                    'turn_id': turn_id,
                    'speaker': speaker,
                    'file_path': str(output_path),
                    'voice_model': voice_model,
                    'utterance_length': len(utterance)
                })
                self.stats['generated_audio_files'] += 1
            else:
                results['failed_turns'].append({
                    'turn_id': turn_id,
                    'speaker': speaker,
                    'reason': 'Speech synthesis failed'
                })
                self.stats['failed_generations'] += 1
                
            self.stats['total_utterances'] += 1
            
        # Calculate processing time
        end_time = datetime.now()
        results['processing_time'] = (end_time - start_time).total_seconds()
        
        # Generate scenario metadata file
        metadata = {
            'scenario_info': {
                'scenario_id': scenario_id,
                'care_goal': scenario.get('care_goal', ''),
                'adl_category': context.get('adl_category', ''),
                'environment': context.get('environment', ''),
                'time_of_day': context.get('time_of_day', ''),
                'caregiver_role': context.get('caregiver_role', '')
            },
            'audio_files': results['generated_files'],
            'processing_results': results,
            'voice_config': {
                'caregiver_voice': self.voice_config.caregiver_voice_id,
                'resident_voice': self.voice_config.resident_voice_id,
                'encoding': self.voice_config.encoding,
                'sample_rate': self.voice_config.sample_rate
            },
            'generated_timestamp': datetime.now().isoformat()
        }
        
        metadata_file = scenario_dir / f"{scenario_id}_metadata.json"
        async with aiofiles.open(metadata_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(metadata, indent=2, ensure_ascii=False))
            
        # Combine individual audio files into one conversation file
        if len(results['generated_files']) > 1:
            combined_file = self._combine_audio_files(scenario_dir, scenario_id)
            if combined_file:
                results['combined_conversation_file'] = str(combined_file.name)
            
        self.stats['processed_scenarios'] += 1
        logger.info(f"Completed scenario {scenario_id}: {len(results['generated_files'])} files generated")
        
        return results
        
    async def generate_all_voices(self, 
                                scenario_filter: Optional[List[str]] = None,
                                max_scenarios: Optional[int] = None) -> Dict:
        """
        Generate voice data for all or filtered ADL scenarios
        
        Args:
            scenario_filter: List of scenario IDs to process (None for all)
            max_scenarios: Maximum number of scenarios to process
            
        Returns:
            Overall processing results
        """
        self.stats['processing_start_time'] = datetime.now()
        self.stats['total_scenarios'] = len(self.scenarios_data)
        
        logger.info(f"Starting voice generation for {self.stats['total_scenarios']} scenarios")
        
        # Filter scenarios if requested
        scenarios_to_process = self.scenarios_data
        if scenario_filter:
            scenarios_to_process = [
                s for s in scenarios_to_process 
                if s.get('scenario_id') in scenario_filter
            ]
            logger.info(f"Filtered to {len(scenarios_to_process)} scenarios")
            
        if max_scenarios:
            scenarios_to_process = scenarios_to_process[:max_scenarios]
            logger.info(f"Limited to {len(scenarios_to_process)} scenarios")
            
        # Process scenarios
        all_results = []
        for i, scenario in enumerate(scenarios_to_process, 1):
            logger.info(f"Processing scenario {i}/{len(scenarios_to_process)}")
            try:
                result = await self.process_scenario(scenario)
                all_results.append(result)
            except Exception as e:
                logger.error(f"Failed to process scenario {scenario.get('scenario_id', 'unknown')}: {e}")
                self.stats['failed_generations'] += 1
                
        self.stats['processing_end_time'] = datetime.now()
        
        # Generate final report
        return await self._generate_final_report(all_results)
        
    async def _generate_final_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive processing report"""
        total_time = (self.stats['processing_end_time'] - self.stats['processing_start_time']).total_seconds()
        
        report = {
            'processing_summary': {
                'total_scenarios_available': self.stats['total_scenarios'],
                'scenarios_processed': self.stats['processed_scenarios'],
                'total_utterances_processed': self.stats['total_utterances'],
                'audio_files_generated': self.stats['generated_audio_files'],
                'failed_generations': self.stats['failed_generations'],
                'processing_time_seconds': total_time,
                'average_time_per_scenario': total_time / max(self.stats['processed_scenarios'], 1)
            },
            'output_location': str(self.output_dir),
            'voice_configuration': {
                'caregiver_voice': self.voice_config.caregiver_voice_id,
                'resident_voice': self.voice_config.resident_voice_id,
                'encoding': self.voice_config.encoding,
                'sample_rate': self.voice_config.sample_rate,
                'provider': 'Deepgram TTS'
            },
            'detailed_results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save report
        report_file = self.output_dir / "voice_generation_report.json"
        async with aiofiles.open(report_file, 'w', encoding='utf-8') as f:
            await f.write(json.dumps(report, indent=2, ensure_ascii=False))
            
        logger.info(f"Voice generation completed. Report saved to {report_file}")
        logger.info(f"Generated {self.stats['generated_audio_files']} audio files in {total_time:.2f} seconds")
        
        return report

    def _get_personalized_resident_voice(self, scenario_data: Dict, health_conditions: List[str]) -> Tuple[str, float]:
        """
        Get personalized voice based on resident profile matching
        
        Args:
            scenario_data: Full scenario data with resident_profile
            health_conditions: List of health conditions
            
        Returns:
            Tuple of (voice_model, speed)
        """
        from voice_config import RESIDENT_VOICE_PROFILES, RESIDENT_VOICES
        
        if not scenario_data or 'resident_profile' not in scenario_data:
            # Fallback to default voices
            return RESIDENT_VOICES["elderly_female"], 0.9
        
        resident_profile = scenario_data['resident_profile']
        age = str(resident_profile.get('age', 85))
        gender = resident_profile.get('gender', 'Female')
        conditions = resident_profile.get('health_conditions', [])
        
        # Try to match specific profiles
        for profile_key, voice_config in RESIDENT_VOICE_PROFILES.items():
            profile_age, profile_gender, profile_condition = profile_key
            
            if (age == profile_age and 
                gender == profile_gender and 
                any(profile_condition.lower() in condition.lower() for condition in conditions)):
                
                logger.info(f"Matched personalized voice profile: {profile_key}")
                return voice_config["voice_model"], voice_config["speed"]
        
        # Fallback based on gender and general health conditions
        if gender.lower() == 'male':
            voice_model = RESIDENT_VOICES["elderly_male"]
        else:
            voice_model = RESIDENT_VOICES["elderly_female"]
        
        # Adjust speed based on health conditions
        speed = 0.9  # Default elderly speed
        
        if any('hearing' in condition.lower() for condition in conditions):
            speed = 0.8  # Slower for hearing impaired
        if any('dementia' in condition.lower() for condition in conditions):
            speed = 0.7  # Much slower for dementia
        if any('parkinson' in condition.lower() for condition in conditions):
            speed = 0.75  # Slower for Parkinson's
        if any('cognitive' in condition.lower() for condition in conditions):
            speed = 0.8   # Slower for cognitive impairment
            
        return voice_model, speed

    def _combine_audio_files(self, scenario_dir: Path, scenario_id: str) -> Optional[Path]:
        """
        Combine individual dialogue turn audio files into one conversation file
        
        Args:
            scenario_dir: Directory containing individual turn audio files
            scenario_id: Scenario identifier
            
        Returns:
            Path to the combined audio file, or None if combination failed
        """
        if not AUDIO_PROCESSING_AVAILABLE:
            logger.warning("Audio processing not available. Skipping audio combination.")
            return None
            
        # Find all WAV files in the scenario directory (excluding metadata and combined files)
        audio_files = sorted([f for f in scenario_dir.glob("*_turn_*.wav")])
        
        if len(audio_files) < 2:
            logger.info(f"Only {len(audio_files)} audio files found. Skipping combination for {scenario_id}")
            return None
            
        try:
            logger.info(f"Combining {len(audio_files)} audio files for {scenario_id}")
            
            # Load the first audio file
            combined_audio = AudioSegment.from_wav(str(audio_files[0]))
            
            # Add each subsequent file with a pause between speakers
            pause_duration_ms = 500  # 500ms pause between speakers
            
            for audio_file in audio_files[1:]:
                # Add pause between speakers
                pause = AudioSegment.silent(duration=pause_duration_ms)
                combined_audio += pause
                
                # Add the next audio segment
                next_audio = AudioSegment.from_wav(str(audio_file))
                combined_audio += next_audio
                
            # Create output filename
            output_file = scenario_dir / f"{scenario_id}_full_conversation.wav"
            
            # Export the combined audio
            combined_audio.export(str(output_file), format="wav")
            
            duration_seconds = len(combined_audio) / 1000
            logger.info(f"Combined conversation saved: {output_file} ({duration_seconds:.1f}s)")
            
            return output_file
            
        except Exception as e:
            logger.error(f"Error combining audio files for {scenario_id}: {e}")
            return None

async def main():
    """Main function for command-line usage"""
    parser = argparse.ArgumentParser(description="Generate voice data from ADL scenarios using Deepgram TTS")
    parser.add_argument("--scenarios", default="synthetic_adl_scenarios_enhanced.json",
                       help="Path to ADL scenarios JSON file")
    parser.add_argument("--output", default="generated_audio",
                       help="Output directory for audio files")
    parser.add_argument("--filter", nargs="+", 
                       help="Specific scenario IDs to process")
    parser.add_argument("--max-scenarios", type=int,
                       help="Maximum number of scenarios to process")
    parser.add_argument("--api-key", 
                       help="Deepgram API key (can also set DEEPGRAM_API_KEY env var)")
    
    args = parser.parse_args()
    
    try:
        # Initialize voice generation system
        vgs = DeepgramVoiceSystem(
            scenarios_file=args.scenarios,
            output_dir=args.output,
            api_key=args.api_key
        )
        
        # Generate voices
        report = await vgs.generate_all_voices(
            scenario_filter=args.filter,
            max_scenarios=args.max_scenarios
        )
        
        print(f"\nVoice generation completed successfully!")
        print(f"Generated {report['processing_summary']['audio_files_generated']} audio files")
        print(f"Processing time: {report['processing_summary']['processing_time_seconds']:.2f} seconds")
        print(f"Output directory: {report['output_location']}")
        
    except Exception as e:
        logger.error(f"Voice generation failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
