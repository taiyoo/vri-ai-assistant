#!/bin/bash

# Voice Generation System Setup
# =============================

echo "Setting up Voice Generation System for ADL Healthcare Scenarios..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv_voice" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv_voice
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv_voice/bin/activate

# Install required packages
echo "Installing required packages..."
pip install --upgrade pip
pip install -r requirements_voice.txt

# Create output directories
echo "Creating output directories..."
mkdir -p generated_audio
mkdir -p demo_audio_output
mkdir -p logs

# Set permissions
chmod +x voice_generation_system.py
chmod +x voice_generation_demo.py

echo ""
echo "Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. For demo (no API required): python3 voice_generation_demo.py"
echo "2. For full system: Set DEEPGRAM_API_KEY and run python3 voice_generation_system.py"
echo ""
echo "Deepgram Configuration (for full system):"
echo "- Sign up at: https://deepgram.com"
echo "- Get API key from dashboard"
echo "- Set environment variable: export DEEPGRAM_API_KEY='your_key_here'"
echo "- Verify with: python3 -c \"import os; print('API Key set:', bool(os.getenv('DEEPGRAM_API_KEY')))\""
echo ""
echo "Virtual environment: source venv_voice/bin/activate"
