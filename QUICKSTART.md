# 🎯 AI Habit Coach - Quick Start Guide

## What This Is

An ML/RL-powered app that helps you master **ONE** habit at a time through intelligent behavioral modeling and prediction.

### The Approach

1. **Profile You** - Deep questionnaire about your patterns, preferences, and past behavior
2. **Simulate You** - Generate synthetic behavioral data based on your profile
3. **Pre-train Models** - Train ML models on synthetic data before you even start
4. **Track Reality** - Collect real behavioral data as you work on your habit
5. **Adapt & Optimize** - Models retrain daily, learning what works for YOU specifically

## Installation

```bash
# Run setup script
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Getting Started (5 Minutes)

### Step 1: Create Your Profile

```bash
python main.py profile
```

This will ask you ~30 questions about:
- Your daily schedule and energy patterns
- Personality traits and motivation style
- Past habit successes/failures
- Typical failure triggers
- Weekly difficulty patterns

**Be honest!** The model quality depends on accurate profiling.

### Step 2: Generate Synthetic Data

```bash
python main.py simulate your_name
```

This generates 90 days of simulated behavior based on your profile. The simulator models:
- Day-of-week effects
- Sleep quality and stress
- Streak momentum
- Gap restart difficulty
- Environmental factors

You'll see output like:
```
🔮 Simulating 90 days of behavior...
  ✅ Generated 90 simulated days
  📊 Success rate: 67.8%
  🔥 Max streak: 14
```

### Step 3: Train Initial Models

```bash
python main.py train your_name
```

This trains a Random Forest classifier to predict:
- **Completion probability** given context
- **Optimal times** for habit attempts
- **Feature importance** (what matters most for you)

You'll see:
```
🤖 Training completion predictor...
  ✅ Accuracy: 85%
  
📅 OPTIMAL TIMES ANALYSIS
  Monday:
    08:00 - 82% success probability
    19:00 - 76% success probability
```

### Step 4: Start Tracking!

```bash
python main.py track your_name
```

The app will:
- Let you log daily completions
- Show your stats and streaks
- Give AI-powered recommendations
- Predict optimal times for today
- Automatically retrain as you add data

## Daily Workflow

1. **Morning**: Check AI recommendations for today's optimal time
2. **Do Your Habit**: At the suggested time
3. **Log It**: Track completion, difficulty, motivation
4. **Get Insight**: AI shows predictions for tomorrow

## How The AI Works

### Initial Phase (Days 1-14)
- Models run on **synthetic data** generated from your profile
- Predictions are educated guesses based on your archetype
- Still useful! The simulator captures real behavioral patterns

### Learning Phase (Days 15-30)
- Models retrain with **real data** weighted 3x more than synthetic
- Predictions improve rapidly as system learns YOUR patterns
- Feature importance shifts to match your reality

### Optimized Phase (Days 30+)
- Models primarily use **real data**
- High confidence predictions
- Identifies subtle patterns (e.g., "you skip on Wednesdays after 6pm")
- Can predict failure before it happens

## Model Features

The ML models consider:
- **Temporal**: Day of week, time of day, day number in journey
- **Momentum**: Current streak, days since last completion
- **Psychological**: Difficulty, motivation, stress, sleep quality
- **Environmental**: Work intensity, social obligations
- **Interactions**: Streak × motivation, gap × difficulty, etc.

## What Makes This Different

### 1. Single Habit Focus
- You're not trying to build 10 habits
- All cognitive resources on ONE thing
- Higher success rate

### 2. Personalized Simulation
- Don't need months of data to start
- Simulator bootstraps from your profile
- Models work from day 1

### 3. You're The Training Data
- No generic advice
- Models learn YOUR specific patterns
- Adapts to your life changes

### 4. Predictive Intervention
- Doesn't just track, predicts
- "You typically fail in this context, let's adjust"
- Proactive coaching

## Future Enhancements (Not Built Yet)

- **RL Agent**: Learns optimal reminder timing and difficulty adjustment
- **Contextual Bandits**: A/B tests different message types
- **Habit Graduation**: Determines when habit is truly "installed"
- **Mobile App**: Native iOS/Android app
- **Wearable Integration**: Use real sleep/stress data
- **LLM Coach**: Natural language conversations about struggles

## File Structure

```
habits/
├── main.py                  # Main entry point
├── setup.sh                 # Setup script
├── requirements.txt         # Dependencies
├── src/
│   ├── models.py           # Data models (Pydantic)
│   ├── profiler.py         # Interactive profiling
│   ├── simulator.py        # Behavioral simulator
│   ├── train.py            # ML training pipeline
│   └── app.py              # Tracking application
├── data/
│   ├── profiles/           # Your profile JSON
│   ├── synthetic/          # Generated training data
│   └── real/               # Your actual tracking data
└── models/                 # Trained ML models (.joblib)
```

## Tips for Success

1. **Be Brutally Honest in Profiling**
   - Wrong profile = wrong predictions
   - No judgment, the AI just needs truth

2. **Log Every Day**
   - Even failures
   - Especially failures (that's where the learning happens)

3. **Retrain Weekly**
   - As you accumulate real data
   - Models get smarter

4. **Start Small**
   - Don't pick "exercise 2 hours daily" if you're sedentary
   - Build up difficulty over time

5. **Trust The Process**
   - First week might feel weird
   - By week 3, predictions will be eerily accurate

## Troubleshooting

**"No trained models yet"**
- Run: `python main.py train your_name`

**"Profile not found"**
- Run: `python main.py profile`

**"Accuracy is low"**
- Normal for first few days
- Improve by logging more real data

**"Predictions seem wrong"**
- Profile might be inaccurate
- Delete profile and re-run profiling

## Next Steps

After you've mastered your first habit (90+ days, 90%+ completion rate), you can:

1. **Graduate This Habit**
   - Archive the data
   - Mark as "installed"

2. **Start Your Next Habit**
   - Create new profile
   - System learns from previous success

3. **Contribute to Research**
   - Anonymized behavioral data is valuable
   - Could help others build habits

---

**Ready to start?**

```bash
python main.py profile
```

Let's build that habit! 🎯
