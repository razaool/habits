#!/bin/bash

# Setup script for Adaptive Reminder Timing RL System

echo "========================================"
echo "  Adaptive Reminder Timing RL Setup"
echo "========================================"
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python $python_version"
echo ""

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
echo "✓ Virtual environment created"
echo ""

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate
echo "✓ Virtual environment activated"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet
echo "✓ pip upgraded"
echo ""

# Install requirements
echo "Installing dependencies..."
pip install -r requirements.txt --quiet
echo "✓ Dependencies installed"
echo ""

# Create output directories
echo "Creating output directories..."
mkdir -p outputs/models
mkdir -p outputs/logs
mkdir -p outputs/plots
echo "✓ Directories created"
echo ""

echo "========================================"
echo "  Setup Complete! 🎉"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. Train the agent:"
echo "   python src/train.py"
echo ""
echo "3. Visualize results:"
echo "   python src/visualize.py"
echo ""
echo "4. Run interactive demo:"
echo "   python src/demo.py"
echo ""
echo "For more information, see README.md"
echo ""

