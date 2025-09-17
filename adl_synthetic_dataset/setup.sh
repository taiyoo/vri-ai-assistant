#!/bin/bash
# ADL Synthetic Dataset Setup Script
# Sets up the environment and dependencies for the dataset

set -e

echo "🚀 Setting up ADL Synthetic Dataset Environment..."

# Check Python version
python_version=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "📍 Python version: $python_version"

if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "❌ Python 3.8+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
if [ -f "06_config/requirements.txt" ]; then
    pip install -r 06_config/requirements.txt
else
    # Install basic requirements
    pip install aiohttp deepgram-sdk pydub matplotlib seaborn pandas numpy jupyter
fi

# Create necessary directories
echo "📁 Creating output directories..."
mkdir -p 03_outputs/{visualizations,audio/{individual_turns,full_conversations,generation_reports},analysis_reports}

# Set up environment variables template
if [ ! -f ".env" ]; then
    echo "⚙️ Creating environment template..."
    cp 06_config/environment_template.env .env 2>/dev/null || echo "# Add your API keys here" > .env
    echo "📝 Please edit .env file with your API keys"
fi

# Make scripts executable
echo "🔨 Setting script permissions..."
find 02_scripts -name "*.py" -exec chmod +x {} \;
find 05_examples -name "*.py" -exec chmod +x {} \;

echo "✅ Setup complete!"
echo ""
echo "🎯 Quick start:"
echo "  source venv/bin/activate"
echo "  python3 05_examples/basic_usage.py"
echo ""
echo "📚 Documentation: 04_documentation/"
echo "🔬 Examples: 05_examples/"
