# 🚀 Get Started in 5 Minutes

This guide will get you up and running with the Adaptive Reminder Timing RL system in just a few minutes.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- 5-10 minutes of time

## Installation (2 minutes)

### Option 1: Automated Setup (Recommended)

```bash
# Navigate to the project directory
cd /Users/razaool/ai-habit-coach/ai-habit-coach/habits

# Run setup script
./setup.sh
```

This will:
- Create a virtual environment
- Install all dependencies
- Set up output directories

### Option 2: Manual Setup

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Mac/Linux
# Or on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create directories
mkdir -p outputs/{models,logs,plots}
```

## Quick Test (2 minutes)

Test that everything works with a quick training run:

```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Run quick start (trains a small model in ~2 minutes)
python quick_start.py
```

You should see:
```
========================================
         🚀 Quick Start Demo
========================================
Training for 50 episodes...
Episode 10/50
  Avg Reward: 45.23
  Avg Completions: 3.2
  Epsilon: 0.7821
...
✅ Quick start completed successfully!
```

## Full Training (10-30 minutes)

Now train a full model:

```bash
# Train full model (500 episodes)
python src/train.py
```

Or use Make:
```bash
make train
```

**Training Output:**
- Models saved to: `outputs/models/`
- Training curves: `outputs/plots/`
- Logs: `outputs/logs/`

## Visualize Results (1 minute)

Analyze what the agent learned:

```bash
python src/visualize.py
# or: make visualize
```

**Generates:**
- Hourly preference charts
- Q-value heatmaps
- Strategy comparisons
- Performance analysis

## Interactive Demo (2 minutes)

See the agent in action:

```bash
python src/demo.py
# or: make demo
```

**Choose from:**
1. Week-long simulation
2. Decision-making analysis
3. Learning insights
4. Run all demos

## What You Should See

### After Quick Start
```
outputs/
├── models/
│   └── agent_final.pt         ← Trained model
├── plots/
│   └── training_curves_*.png  ← Learning curves
└── logs/
    └── training_log_*.txt     ← Statistics
```

### Training Curves
You should see rewards increasing over time:
- Early episodes: ~20-40 reward
- Late episodes: ~80-120 reward
- Completion rate: 40% → 75%+

### Visualization Outputs
- **Hourly Preferences**: Shows optimal times (usually evening)
- **Q-value Heatmaps**: Shows agent's learned values
- **Strategy Comparison**: RL agent beats baselines

## Troubleshooting

### "Module not found"
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### "No trained models found"
```bash
# Train a model first
python quick_start.py
# or for full training:
python src/train.py
```

### Training is slow
```bash
# Use quick start instead (50 episodes)
python quick_start.py

# Or reduce episodes in config.yaml:
# training:
#   num_episodes: 100
```

### Import errors
```bash
# Make sure you're in the right directory
cd /Users/razaool/ai-habit-coach/ai-habit-coach/habits

# Check Python version
python --version  # Should be 3.8+
```

## Next Steps

### 1. Understand the System
Read the documentation:
```bash
# Comprehensive guide
open README.md

# Detailed tutorial
open TUTORIAL.md

# Architecture overview
open ARCHITECTURE.md
```

### 2. Experiment
Try different configurations:
```bash
# Edit config.yaml
nano config.yaml

# Change user profiles, rewards, hyperparameters
# Then retrain:
python src/train.py
```

### 3. Customize
Modify the code:
- `src/environment.py` - Change state/reward
- `src/user_simulator.py` - Add user types
- `src/dqn_agent.py` - Adjust network
- `src/train.py` - Modify training

### 4. Extend
Add new features:
- Multi-habit support
- Real user integration
- Mobile app backend
- Advanced visualizations

## Quick Reference

### Common Commands
```bash
# Setup
./setup.sh                    # Initial setup
make install                  # Install dependencies

# Training
python quick_start.py         # Quick test (50 episodes)
python src/train.py           # Full training (500 episodes)
make train                    # Same as above

# Analysis
python src/visualize.py       # Generate visualizations
python src/demo.py            # Interactive demo
make visualize                # Visualizations
make demo                     # Demo

# Cleanup
make clean                    # Remove outputs/cache
```

### File Locations
```
Configuration:     config.yaml
Source Code:       src/
Models:            outputs/models/
Visualizations:    outputs/plots/
Logs:              outputs/logs/
Documentation:     *.md files
```

### Key Files to Explore
1. **config.yaml** - All settings
2. **src/train.py** - Training pipeline
3. **src/environment.py** - RL environment
4. **src/dqn_agent.py** - DQN implementation
5. **README.md** - Full documentation

## Expected Timeline

| Task | Time | Output |
|------|------|--------|
| Setup | 2 min | Virtual env + dependencies |
| Quick Start | 2-5 min | Small trained model |
| Full Training | 10-30 min | Production model |
| Visualization | 1 min | Charts and analysis |
| Demo | 2 min | Interactive walkthrough |
| **Total** | **15-40 min** | **Complete system** |

## Success Checklist

✅ Virtual environment created  
✅ Dependencies installed  
✅ Quick start runs successfully  
✅ Model saved in `outputs/models/`  
✅ Training curves generated  
✅ Visualizations created  
✅ Demo runs interactively  
✅ Understanding the system  

## Getting Help

### Documentation
- **README.md** - Full system documentation
- **TUTORIAL.md** - Detailed learning guide
- **ARCHITECTURE.md** - Technical details
- **IMPLEMENTATION_SUMMARY.md** - What was built

### Check Your Work
```bash
# Verify installation
python -c "import torch; import gymnasium; print('✓ All good!')"

# Check trained model exists
ls outputs/models/

# Verify plots generated
ls outputs/plots/
```

### Common Issues
1. **Import errors** → Activate virtual environment
2. **No models found** → Run training first
3. **Slow training** → Use quick_start.py
4. **GPU not detected** → PyTorch will use CPU (fine!)

## What's Next?

Once you've completed the quick start:

1. 📖 **Read TUTORIAL.md** to understand the RL concepts
2. 🔬 **Experiment** with different configurations
3. 📊 **Analyze** the visualizations to see what was learned
4. 🎨 **Customize** the system for your needs
5. 🚀 **Extend** with new features

## Support

If you run into issues:
1. Check this guide
2. Review TUTORIAL.md
3. Examine error messages
4. Open an issue on GitHub

---

**Ready to Go!** 🎯

Your complete Adaptive Reminder Timing RL system is ready to use.

Start with: `python quick_start.py`

*Built with ❤️ and Reinforcement Learning*

