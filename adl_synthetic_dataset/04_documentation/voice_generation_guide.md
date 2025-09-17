# Voice Generation System for ADL Healthcare Scenarios - Deepgram TTS

This system generates synthetic voice data from your corrected ADL dialogue scenarios, creating realistic audio files for caregiver and resident interactions using Deepgram's advanced text-to-speech technology.

## Features

- **Multi-speaker voice synthesis** with distinct Deepgram Aura voices for caregivers and residents
- **Context-aware audio generation** based on environment and time of day
- **Health condition adjustments** - voice parameters adapt to resident conditions
- **High-quality neural voices** - Deepgram's Aura models for natural speech
- **Batch processing** with progress tracking and detailed reporting
- **Audio quality optimization** for healthcare training applications

## Files Overview

### Core System Files
- `voice_generation_system.py` - Main voice generation system (requires Deepgram API)
- `voice_generation_demo.py` - Demo version that works without API credentials
- `voice_config.py` - Configuration settings for voices and parameters
- `requirements_voice.txt` - Python package requirements
- `setup_voice_generation.sh` - Setup script

### Input Data
- `synthetic_adl_scenarios_enhanced.json` - Your corrected ADL scenarios with improved dialogue structure

## Quick Start

### Option 1: Demo Mode (No API Required)
```bash
# Run setup
chmod +x setup_voice_generation.sh
./setup_voice_generation.sh

# Activate environment
source venv_voice/bin/activate

# Run demo
python3 voice_generation_demo.py
```

### Option 2: Full System (Deepgram API Required)
```bash
# Setup (same as above)
./setup_voice_generation.sh
source venv_voice/bin/activate

# Set your Deepgram API key
export DEEPGRAM_API_KEY="your_api_key_here"

# Test API access (optional)
python3 -c "import os; print('API Key set:', bool(os.getenv('DEEPGRAM_API_KEY')))"

# Run full voice generation
python3 voice_generation_system.py --max-scenarios 5
```

## Voice Configuration

The system uses Deepgram's Aura voices for natural, human-like speech:

### Caregiver Voices
- **aura-asteria-en** (Female) - Professional, warm, caring tone
- **aura-orion-en** (Male) - Professional, calm, authoritative tone

### Resident Voices  
- **aura-luna-en** (Female) - Gentle, softer, elderly-appropriate voice
- **aura-orpheus-en** (Male) - Gentle, mature, elderly-appropriate voice

### Dynamic Adjustments

The system automatically adjusts voice parameters based on:

- **Health Conditions**: Slower speech for Parkinson's, clearer for hearing impaired
- **Environment**: Softer in bathrooms, clearer in dining areas
- **Time of Day**: Gentle in morning, calm in evening
- **Speaker Intent**: Reassuring, instructional, responsive tones

## Output Structure

```
generated_audio/
├── ADL_001/
│   ├── ADL_001_turn_01_Personal_Care_Assistant.mp3
│   ├── ADL_001_turn_02_Resident.mp3
│   ├── ADL_001_turn_03_Personal_Care_Assistant.mp3
│   └── ADL_001_metadata.json
├── ADL_002/
│   └── ...
└── voice_generation_report.json
```

## Command Line Options

```bash
# Process specific scenarios
python3 voice_generation_system.py --filter ADL_001 ADL_002 ADL_003

# Limit number of scenarios
python3 voice_generation_system.py --max-scenarios 10

# Custom output directory
python3 voice_generation_system.py --output /path/to/audio/files

# Provide API key directly (alternative to environment variable)
python3 voice_generation_system.py --api-key your_deepgram_api_key

# Help
python3 voice_generation_system.py --help
```

## Quality Metrics

The system tracks and reports:
- Total scenarios processed
- Audio files generated successfully
- Failed generations and reasons
- Processing time and performance
- Dialogue quality analysis
- Voice parameter effectiveness

## Sample Usage Scenarios

### Healthcare Training
Generate complete audio datasets for:
- Caregiver training simulations
- Communication skills development
- Patient interaction modeling
- Scenario-based learning modules

### Voice AI Development
Create training data for:
- Healthcare chatbots
- Voice assistant applications
- Speech recognition systems
- Conversational AI models

### Research Applications
Support studies in:
- Healthcare communication patterns
- Age-related speech characteristics
- Care environment acoustics
- Dialogue effectiveness analysis

## Technical Requirements

### For Demo Mode
- Python 3.7+
- Basic Python libraries (included in requirements_voice.txt)

### For Full System
- Python 3.7+
- Deepgram API account and API key
- Internet connection for Deepgram API calls

### Deepgram API Setup
1. Sign up at https://deepgram.com
2. Get your API key from the dashboard
3. Set environment variable: `export DEEPGRAM_API_KEY="your_key"`

## Troubleshooting

### Common Issues

**API Key Error**
```bash
# Check if API key is set
echo $DEEPGRAM_API_KEY
# Set API key
export DEEPGRAM_API_KEY="your_api_key_here"
```

**Module Import Errors**
```bash
# Activate virtual environment
source venv_voice/bin/activate
# Reinstall requirements
pip install -r requirements_voice.txt
```

**Empty Utterances**
- The system automatically skips empty utterances and logs warnings
- Check the processing report for details on skipped content

**Voice Generation Failures**
- Check Deepgram API status and quota
- Verify API key is valid
- Review processing logs for detailed error messages

### Performance Optimization

- Use `--max-scenarios` to process in batches
- Monitor Deepgram API rate limits and usage
- Check disk space for audio file storage
- Consider processing during off-peak hours for better API performance

## Integration Examples

### With Training Platforms
```python
from voice_generation_system import DeepgramVoiceSystem

# Initialize system
vgs = DeepgramVoiceSystem(api_key="your_deepgram_api_key")

# Generate audio for specific training module
report = await vgs.generate_all_voices(
    scenario_filter=["ADL_001", "ADL_002", "ADL_003"]
)

# Use generated files in training platform
for result in report['detailed_results']:
    for file_info in result['generated_files']:
        training_platform.add_audio(file_info['file_path'])
```

## Next Steps

1. **Run the demo** to understand the system workflow
2. **Get Deepgram API key** from https://deepgram.com
3. **Set up environment** with your API credentials
4. **Process your scenarios** with the corrected dialogue structure
5. **Integrate generated audio** into your healthcare training applications
6. **Analyze results** using the comprehensive reporting features

The voice generation system is now ready to transform your corrected ADL dialogue scenarios into realistic audio training data using Deepgram's advanced neural voices!
