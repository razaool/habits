#!/bin/bash

echo "=================================="
echo "  🎯 AI Habit Coach - Setup"
echo "=================================="

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "=================================="
echo "  ✅ Setup Complete!"
echo "=================================="
echo ""
echo "To get started:"
echo "  1. Activate environment: source venv/bin/activate"
echo "  2. Run profiling: python main.py profile"
echo "  3. Generate data: python main.py simulate"
echo "  4. Train models: python main.py train"
echo "  5. Start tracking: python main.py track"
echo ""
