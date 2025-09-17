# ADL Synthetic Dataset

A comprehensive synthetic dataset for Activities of Daily Living (ADL) interactions in aged care settings, featuring realistic dialogue scenarios, resident profiles, and high-quality voice synthesis.

## 🎯 Overview

This dataset contains **120 synthetic ADL scenarios** with:
- **Realistic dialogue turns** between caregivers and residents
- **Detailed resident profiles** (demographics, health conditions, preferences)
- **Contextual scenarios** (personal care, mobility, medication, etc.)
- **High-quality voice synthesis** using Deepgram Aura 2 models
- **Comprehensive analysis tools** for research applications

## 🗂️ Dataset Structure

```
01_data/          # All dataset files (raw → processed → analysis)
02_scripts/       # Processing and analysis scripts
03_outputs/       # Generated results and visualizations
04_documentation/ # Comprehensive guides and API docs
05_examples/      # Ready-to-use examples and demos
06_config/        # Configuration files and templates
```

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Clone and setup
git clone <repository-url>
cd adl_synthetic_dataset
chmod +x setup.sh
./setup.sh
```

### 2. Basic Usage
```python
# Load the dataset
python3 05_examples/basic_usage.py

# Generate voice synthesis
python3 05_examples/voice_generation_demo.py

# Explore with Jupyter
jupyter notebook 05_examples/jupyter_notebooks/dataset_exploration.ipynb
```

### 3. Research Workflow
```bash
# Data analysis
python3 02_scripts/analysis/visualizer.py

# Voice generation
python3 02_scripts/voice_generation/voice_generation_system.py

# Profile extraction
python3 02_scripts/analysis/profile_extractor.py
```

## 📊 Dataset Statistics

- **Total Scenarios**: 120 ADL interactions
- **Dialogue Turns**: ~720 total turns (avg 6 per scenario)
- **Resident Profiles**: 102 unique profiles
- **Voice Models**: 7 Deepgram Aura 2 neural voices
- **Audio Duration**: ~50+ hours of synthetic speech
- **File Formats**: JSON (data), WAV (audio), PNG/HTML (visualizations)

## 🎤 Voice Features

- **Personalized Voices**: Age and condition-appropriate voice selection
- **Professional Quality**: Deepgram Aura 2 neural text-to-speech
- **Multiple Formats**: Individual turns + combined conversations
- **Natural Pauses**: Realistic conversation timing
- **Scalable Generation**: Batch processing capabilities

## 📚 Documentation

- **[Dataset Specification](04_documentation/dataset_specification.md)**: Data format and structure
- **[API Documentation](04_documentation/api_documentation.md)**: Script usage and parameters
- **[Voice Generation Guide](04_documentation/voice_generation_guide.md)**: Voice synthesis tutorial
- **[Research Methodology](04_documentation/research_methodology.md)**: Research approach and validation

## 🔬 Research Applications

- **Healthcare AI**: Training conversational agents for aged care
- **Voice Synthesis**: Developing personalized TTS systems
- **Dialogue Systems**: Building context-aware chatbots
- **Accessibility Research**: Improving communication tools
- **Clinical Training**: Simulating patient interactions

## 📈 Analysis Features

- **Interactive Visualizations**: Scenario distributions, demographics
- **Network Analysis**: Interaction patterns and relationships
- **Profile Clustering**: Resident segmentation and analysis
- **Quality Metrics**: Dataset validation and quality assessment
- **Statistical Reports**: Comprehensive dataset analytics

## 🤝 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on:
- Adding new scenarios
- Improving voice models
- Extending analysis tools
- Documentation updates

## 📄 Citation

If you use this dataset in your research, please cite:
```bibtex
@dataset{adl_synthetic_dataset_2025,
  title={ADL Synthetic Dataset: Realistic Healthcare Dialogue with Voice Synthesis},
  author={[Your Name]},
  year={2025},
  publisher={[Your Institution]},
  version={1.0}
}
```

## 📞 Support

- **Issues**: Report bugs and feature requests via GitHub Issues
- **Documentation**: Check [04_documentation/](04_documentation/) for detailed guides
- **Examples**: See [05_examples/](05_examples/) for usage patterns
- **Troubleshooting**: [04_documentation/troubleshooting.md](04_documentation/troubleshooting.md)

## 📋 License

[Specify your license here - e.g., MIT, Apache 2.0, CC BY 4.0]

---

**Built with**: Python, OpenAI GPT, Deepgram TTS, Jupyter, and ❤️ for healthcare research
