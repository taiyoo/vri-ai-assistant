# Data Directory

This directory contains all dataset files organized by processing stage.

## Structure

### `raw/`
Original generated data without processing:
- `synthetic_adl_scenarios_openai.json` - Raw OpenAI-generated scenarios
- `generation_metadata.json` - Generation parameters and timestamps

### `processed/`
Cleaned and standardized data ready for analysis:
- `synthetic_adl_scenarios_standardized.json` - Standardized format
- `synthetic_adl_scenarios_enhanced.json` - Enhanced with metadata
- `processing_report.json` - Processing statistics and changes

### `analysis/`
Derived datasets from analysis:
- `resident_profiles.json` - Extracted unique resident profiles
- `scenario_statistics.json` - Statistical summaries
- `validation_report.json` - Data quality metrics

## Data Format

Each scenario follows this structure:
```json
{
  "scenario_id": "ADL_XXX",
  "context": {
    "setting": "Personal Care",
    "time_of_day": "Morning",
    "activity": "Morning hygiene routine"
  },
  "resident_profile": {
    "demographics": {...},
    "health_conditions": [...],
    "preferences": {...}
  },
  "dialogue": [
    {
      "turn_id": 1,
      "speaker": "Personal Care Assistant",
      "utterance": "Good morning! Ready for your morning routine?"
    }
  ]
}
```

## Usage

```python
import json

# Load processed data
with open('01_data/processed/synthetic_adl_scenarios_enhanced.json', 'r') as f:
    scenarios = json.load(f)

# Access specific scenario
scenario = scenarios[0]
print(f"Activity: {scenario['context']['activity']}")
print(f"Turns: {len(scenario['dialogue'])}")
```
