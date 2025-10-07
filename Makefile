.PHONY: help setup install train visualize demo quick-start clean

help:
	@echo "Adaptive Reminder Timing RL - Available Commands"
	@echo "=================================================="
	@echo ""
	@echo "  make setup       - Create venv and install dependencies"
	@echo "  make install     - Install dependencies (venv must exist)"
	@echo "  make quick-start - Train a small model quickly (50 episodes)"
	@echo "  make train       - Train the full model (500 episodes)"
	@echo "  make visualize   - Generate visualizations from trained model"
	@echo "  make demo        - Run interactive demo"
	@echo "  make clean       - Remove outputs and cache files"
	@echo ""

setup:
	@echo "Setting up environment..."
	./setup.sh

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt

quick-start:
	@echo "Running quick start (50 episodes)..."
	python quick_start.py

train:
	@echo "Training full model (500 episodes)..."
	python src/train.py

visualize:
	@echo "Generating visualizations..."
	python src/visualize.py

demo:
	@echo "Running interactive demo..."
	python src/demo.py

clean:
	@echo "Cleaning up..."
	rm -rf outputs/
	rm -rf src/__pycache__
	rm -rf __pycache__
	rm -f *.pyc
	rm -f config_quickstart.yaml
	@echo "✓ Cleanup complete"

