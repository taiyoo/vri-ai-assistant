#!/bin/bash
# Load environment variables from .env.local
export $(grep -v '^#' .env.local | xargs)

# Run the agent
python app/livekit_agent.py dev