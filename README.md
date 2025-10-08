# 🎯 AI Habit Coach - Single Habit Mastery

> An ML/RL-powered app that helps you master **ONE** habit at a time through intelligent behavioral modeling and prediction.

## 🧠 The Philosophy

Most habit apps let you track 10+ habits. You juggle too many things, build none effectively.

**This app is different:**
- Focus on **exactly ONE habit** at a time
- Put your maximum cognitive effort on it
- Use ML/RL to optimize YOUR specific approach
- Graduate when it's truly installed, then move to the next

## 🚀 Quick Start

```bash
# Setup (one time)
./setup.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Get started (5 minutes)
python main.py profile      # Answer questions about yourself
python main.py simulate     # Generate training data (90 days)
python main.py train        # Train ML models
python main.py track        # Start tracking!
```

See [QUICKSTART.md](QUICKSTART.md) for detailed guide.

## 🎯 How It Works

### 1. **Profile** (5 minutes)
Answer questions about your schedule, personality, past habits, and weekly patterns.

### 2. **Simulate** (30 seconds)
Generate 90 days of synthetic behavioral data based on your profile using our behavioral simulator.

### 3. **Pre-train** (1 minute)
Train ML models on synthetic data so predictions work from day 1.

### 4. **Track** (daily)
Log your habit, get AI recommendations, watch models learn YOUR patterns.

### 5. **Graduate** (90+ days)
When the habit is truly installed, move to your next one.

## 🤖 The AI

### What It Predicts
- **Completion Probability**: Given current context, will you do it?
- **Optimal Times**: When are you most likely to succeed today?
- **Failure Patterns**: Identifies when you typically skip
- **Intervention Timing**: When to remind, when to back off

### How It Learns
- **Days 1-14**: Runs on synthetic data from your profile
- **Days 15-30**: Combines synthetic + real (real weighted 3x)
- **Days 30+**: Primarily real data, high confidence predictions

### What It Considers
- Day of week, time of day, hour-by-hour patterns
- Current streak, days since last completion
- Sleep quality, stress level, work intensity
- Social obligations, environmental context
- Difficulty ratings, motivation levels
- Interaction effects (streak × motivation, etc.)

## 🎨 Features

- ✅ **Personalized Simulation**: No cold start problem
- 📊 **Behavioral Modeling**: Learn what works for YOU
- 🔮 **Predictive Intervention**: Stop failures before they happen
- 📈 **Progress Tracking**: Streaks, stats, insights
- 🤖 **Adaptive Learning**: Models retrain as you add data
- 🎯 **Single Focus**: One habit, maximum effort

## 📁 Project Structure

```
habits/
├── main.py                 # Main CLI entry point
├── setup.sh                # Setup script
├── QUICKSTART.md          # Detailed guide
├── src/
│   ├── models.py          # Data models
│   ├── profiler.py        # Interactive profiling
│   ├── simulator.py       # Behavioral simulator
│   ├── train.py           # ML training pipeline
│   └── app.py             # Tracking app
├── data/
│   ├── profiles/          # User profiles
│   ├── synthetic/         # Simulated data
│   └── real/              # Actual tracking data
└── models/                # Trained ML models
```

## 🔬 The Science

This system combines concepts from:
- **Behavioral Psychology**: Habit formation phases, trigger-routine-reward
- **Machine Learning**: Random Forest, feature engineering, online learning
- **Reinforcement Learning**: Multi-armed bandits, Q-learning (planned)
- **Simulation**: Agent-based modeling of human behavior

## 🚧 Roadmap

**Phase 1: MVP** ✅ (Current)
- Profiling system
- Behavioral simulator
- ML prediction models
- CLI tracking app

**Phase 2: RL Agents** (Next)
- Contextual bandits for message A/B testing
- Q-learning for dynamic difficulty adjustment
- Predictive intervention system

**Phase 3: Advanced** (Future)
- Mobile app (React Native)
- LLM-powered coach conversations
- Wearable integration (real sleep/stress data)
- Community learning (federated learning)
- Habit graduation detection

## 🎯 Example Usage

```bash
# Day 1: Setup
$ python main.py profile
# ... answer questions ...
✅ Profile saved!

$ python main.py simulate razaool
🔮 Simulating 90 days...
  📊 Success rate: 68%
  🔥 Max streak: 14 days

$ python main.py train razaool
🤖 Training models...
  ✅ Accuracy: 85%
  📅 Monday best time: 08:00 (82% success)

# Daily: Track
$ python main.py track razaool
🎯 AI HABIT COACH - RAZAOOL
  Your habit: Meditate 20 minutes
  Current streak: 🔥 5 days

What would you like to do?
  1. Log today's habit
  2. View stats & insights
  3. Get AI recommendations
```

## 🤝 Contributing

This is currently a personal project for Razaool's self-experimentation.

Future plans:
- Open source after validation
- Research paper on personalized habit formation
- Community dataset (anonymized)

## 📄 License

MIT (will be added when open sourced)

## 🙏 Acknowledgments

Inspired by:
- James Clear's *Atomic Habits*
- BJ Fogg's *Tiny Habits*
- Charles Duhigg's *The Power of Habit*
- Reinforcement Learning research
- Personal frustration with habit apps

---

**Ready to master your first habit?**

```bash
python main.py profile
```

Let's do this! 🎯
