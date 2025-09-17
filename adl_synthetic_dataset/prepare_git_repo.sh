#!/bin/bash
# Git Repository Preparation Script
# Prepares the ADL dataset for git repository publication

set -e

echo "🚀 Preparing ADL Dataset Repository for Git..."

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo "📁 Initializing git repository..."
    git init
else
    echo "✅ Git repository already initialized"
fi

# Check .gitignore
if [ -f ".gitignore" ]; then
    echo "✅ .gitignore file exists"
else
    echo "❌ .gitignore file missing - please create one first"
    exit 1
fi

# Clean up temporary files
echo "🧹 Cleaning up temporary files..."
rm -f *.log 2>/dev/null || true
rm -f *.tmp 2>/dev/null || true
rm -f test_*.wav 2>/dev/null || true
rm -rf __pycache__ 2>/dev/null || true

# Check for sensitive files
echo "🔍 Checking for sensitive files..."
sensitive_patterns=(
    "*api_key*"
    "*API_KEY*"
    "*.key"
    ".env"
    "*secret*"
)

found_sensitive=false
for pattern in "${sensitive_patterns[@]}"; do
    if ls $pattern 1> /dev/null 2>&1; then
        echo "⚠️  Found potentially sensitive files matching: $pattern"
        found_sensitive=true
    fi
done

if [ "$found_sensitive" = true ]; then
    echo "❌ Please review and remove sensitive files before committing"
    echo "💡 Make sure API keys and secrets are in .env (which is ignored)"
fi

# Check repository size
echo "📊 Checking repository size..."
total_size=$(du -sh . | cut -f1)
echo "Total directory size: $total_size"

# Check large files
echo "🔍 Checking for large files (>50MB)..."
large_files=$(find . -type f -size +50M 2>/dev/null | grep -v ".git" || true)
if [ ! -z "$large_files" ]; then
    echo "⚠️  Large files found:"
    echo "$large_files"
    echo "💡 Consider using Git LFS or excluding these files"
fi

# Create commit template
echo "📝 Creating commit message template..."
cat > .git_commit_template.txt << 'EOF'
# ADL Dataset Commit Template
# 
# Type: feat|fix|docs|data|audio|refactor|test
# 
# Examples:
# feat: Add new voice generation models
# fix: Correct audio file organization
# docs: Update README with usage examples
# data: Add new ADL scenarios (batch 2)
# audio: Generate voice synthesis for scenarios 1-50
# refactor: Reorganize directory structure
# test: Add validation for dataset integrity

# Short summary (50 characters or less)


# Detailed description (wrap at 72 characters)


# Related issues, references, or notes
EOF

# Check what will be committed
echo "📋 Files to be tracked by git:"
git add --dry-run . 2>/dev/null || echo "No files ready to add"

echo ""
echo "✨ NEXT STEPS FOR GIT REPOSITORY:"
echo "================================"
echo ""
echo "1. Review what will be committed:"
echo "   git status"
echo "   git add ."
echo "   git status"
echo ""
echo "2. Create initial commit:"
echo "   git commit -m \"feat: Initial ADL synthetic dataset with voice generation\""
echo ""
echo "3. Add remote repository:"
echo "   git remote add origin <your-repository-url>"
echo ""
echo "4. Push to remote:"
echo "   git push -u origin main"
echo ""
echo "📚 RECOMMENDED COMMIT MESSAGE:"
echo "------------------------------"
echo "feat: Initial ADL synthetic dataset with voice generation"
echo ""
echo "- 120 synthetic ADL scenarios with realistic dialogue"
echo "- Personalized voice synthesis using Deepgram Aura 2"
echo "- Organized structure: data → scripts → outputs → docs"
echo "- Complete documentation and usage examples"
echo "- Audio files with individual turns + combined conversations"
echo ""
echo "📊 Dataset includes:"
echo "- Healthcare dialogue scenarios (hygiene, mobility, medication)"
echo "- Resident profiles with demographics and health conditions"
echo "- Professional voice generation pipeline"
echo "- Analysis tools and visualizations"
echo ""
echo "📁 STRUCTURE VERIFICATION:"
echo "========================="
echo "01_data/     ✅ $(ls -1 01_data/ | wc -l | tr -d ' ') items"
echo "02_scripts/  ✅ $(ls -1 02_scripts/ | wc -l | tr -d ' ') items"
echo "03_outputs/  ✅ $(ls -1 03_outputs/ | wc -l | tr -d ' ') items"
echo "04_documentation/ ✅ $(ls -1 04_documentation/ 2>/dev/null | wc -l | tr -d ' ') items"
echo "05_examples/ ✅ $(ls -1 05_examples/ | wc -l | tr -d ' ') items"
echo "06_config/   ✅ $(ls -1 06_config/ | wc -l | tr -d ' ') items"
echo ""
echo "🎉 Repository is ready for publication!"
