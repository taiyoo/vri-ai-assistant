# Voice Generation Configuration - Deepgram TTS
# =============================================

# Deepgram Configuration
DEEPGRAM_API_KEY_ENV = "DEEPGRAM_API_KEY"  # Environment variable name
DEEPGRAM_BASE_URL = "https://api.deepgram.com"

# Voice Selection - Deepgram TTS Aura 2 Voices
CAREGIVER_VOICES = {
    "female": "aura-2-hera-en",       # Professional, warm female voice (Aura 2)
    "male": "aura-2-zeus-en"          # Professional, deep male voice (Aura 2)
}

# Personalized Resident Voice Profiles (Based on Top 5 Most Common Profiles)
RESIDENT_VOICE_PROFILES = {
    # Profile 1: 85F with Mild Dementia (5 scenarios)
    ("85", "Female", "Mild Dementia"): {
        "voice_model": "aura-2-vesta-en",
        "speed": 0.7,
        "characteristics": "Natural, empathetic, patient, very clear speech"
    },
    
    # Profile 2: 87M with Hearing impaired, Limited mobility (3 scenarios)  
    ("87", "Male", "Hearing impaired"): {
        "voice_model": "aura-2-mars-en", 
        "speed": 0.8,
        "characteristics": "Smooth, patient, trustworthy, clear enunciation"
    },
    
    # Profile 3: 94F with Diabetes, Hypertension (3 scenarios)
    ("94", "Female", "Diabetes"): {
        "voice_model": "aura-2-athena-en",
        "speed": 1.0, 
        "characteristics": "Calm, mature, gentle"
    },
    
    # Profile 4: 80F with Heart Condition, Blood Pressure (2 scenarios)
    ("80", "Female", "Heart Condition"): {
        "voice_model": "aura-2-luna-en",
        "speed": 1.0,
        "characteristics": "Friendly, natural, engaging"
    },
    
    # Profile 5: 79F with Moderate Dementia (2 scenarios)
    ("79", "Female", "Moderate Dementia"): {
        "voice_model": "aura-2-luna-en", 
        "speed": 0.7,
        "characteristics": "Friendly, natural, engaging, very clear speech"
    }
}

# Default fallback voices for other resident profiles
RESIDENT_VOICES = {
    "elderly_female": "aura-2-athena-en",   # Calm, mature female voice (Aura 2)
    "elderly_male": "aura-2-orpheus-en"     # Professional, trustworthy male voice (Aura 2)
}

# Audio Quality Settings
AUDIO_CONFIG = {
    "model": "aura-2-hera-en",        # Default Aura 2 model
    "encoding": "linear16",           # Linear PCM encoding
    "sample_rate": 24000,             # Sample rate for good quality
    "container": "wav"                # Container format - wav supported
}

# Speech Customization
SPEECH_RATES = {
    "very_slow": "x-slow",
    "slow": "slow", 
    "normal": "medium",
    "fast": "fast"
}

SPEECH_VOLUMES = {
    "quiet": "x-soft",
    "soft": "soft",
    "normal": "medium", 
    "loud": "loud",
    "very_loud": "x-loud"
}

# Health Condition Voice Adjustments
HEALTH_ADJUSTMENTS = {
    "hearing_impaired": {
        "volume": "loud",
        "rate": "slow",
        "emphasis": "strong"
    },
    "parkinson": {
        "rate": "x-slow",
        "pitch": "low",
        "volume": "soft"
    },
    "dementia": {
        "rate": "slow",
        "emphasis": "strong",
        "clarity": "high"
    },
    "cognitive_impairment": {
        "rate": "slow",
        "emphasis": "moderate",
        "volume": "medium"
    }
}

# Environment-based Adjustments
ENVIRONMENT_ADJUSTMENTS = {
    "bathroom": {
        "volume": "soft",
        "echo": "minimal"
    },
    "dining_area": {
        "volume": "medium",
        "background": "ambient"
    },
    "private_room": {
        "volume": "soft",
        "intimacy": "high"
    },
    "hallway": {
        "volume": "medium",
        "projection": "clear"
    },
    "lounge": {
        "volume": "medium",
        "warmth": "high"
    }
}

# Time-based Adjustments
TIME_ADJUSTMENTS = {
    "morning": {
        "energy": "gentle",
        "volume": "medium",
        "rate": "medium"
    },
    "afternoon": {
        "energy": "normal",
        "volume": "medium", 
        "rate": "medium"
    },
    "evening": {
        "energy": "calm",
        "volume": "soft",
        "rate": "slow"
    }
}

# Output Organization
OUTPUT_STRUCTURE = {
    "create_scenario_folders": True,
    "include_metadata": True,
    "generate_playlists": True,
    "create_training_sets": True
}
