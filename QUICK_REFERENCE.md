# 🎯 Quick Reference Card

## Daily Commands

```bash
# Main tracking app
python main.py track your_name

# Generate insights
python main.py visualize your_name
```

## Menu Options (in tracking app)

```
1. Log today's habit       → Record completion, difficulty, motivation
2. View stats & insights   → Streaks, patterns, success rate
3. Get AI recommendations  → Optimal times, predictions
4. Retrain models         → Update ML models with new data
5. Exit                   → Save and quit
```

## One-Time Setup

```bash
# Install
./setup.sh

# Create profile (5 min)
python main.py profile

# Generate training data (30 sec)
python main.py simulate your_name

# Train models (1 min)
python main.py train your_name
```

## File Locations

```
Your profile:         data/profiles/your_name.json
Your tracking data:   data/real/your_name_real.csv
Your models:          models/your_name_models.joblib
Your visualizations:  data/visualizations/your_name_*.png
```

## Daily Workflow

### Morning (1 minute)
```bash
python main.py track your_name
# → Option 3: Get AI recommendations
# Check: "Best time today: 8am (82% success)"
```

### During Day
```
Do your habit at the recommended time
```

### Evening (2 minutes)
```bash
python main.py track your_name
# → Option 1: Log today's habit
# Answer: Did you complete it? (y/n)
# If yes: Rate difficulty (1-10) and motivation (1-10)
# If no: Note why (optional)
```

### Weekly (5 minutes)
```bash
# 1. View stats
python main.py track your_name
# → Option 2: View stats & insights

# 2. Generate visualizations
python main.py visualize your_name

# 3. Retrain models
python main.py track your_name
# → Option 4: Retrain models
```

## Understanding AI Predictions

### Completion Probability
- **80%+**: 💚 Great time, go for it!
- **60-80%**: 💛 Good time, likely to succeed
- **40-60%**: 🧡 Challenging, might skip
- **<40%**: ❤️ High risk, wait for better time

### Feature Importance
- Shows what predicts YOUR success
- Top features = what matters most for YOU
- Changes over time as you add data

### Optimal Times
- Model tests all hours of day
- Ranks by success probability
- Based on your historical patterns

## Troubleshooting

### "Profile not found"
```bash
python main.py profile
```

### "No trained models"
```bash
python main.py simulate your_name
python main.py train your_name
```

### "No data for visualization"
```bash
# Track for at least a few days first
python main.py track your_name
# Log some completions, then:
python main.py visualize your_name
```

### Models seem inaccurate
```bash
# Retrain with latest data
python main.py track your_name
# → Option 4: Retrain models
```

### Want to start over
```bash
# Delete your data files
rm data/profiles/your_name.json
rm data/real/your_name_real.csv
rm models/your_name_models.joblib

# Start fresh
python main.py profile
```

## Tips for Success

### 1. Be Honest
- Wrong profile = wrong predictions
- Rate difficulty accurately
- Don't skip logging failures

### 2. Log Every Day
- Even if you skip the habit
- Failures teach the model too
- Consistency matters

### 3. Follow Recommendations
- Trust the optimal times
- Try suggestions for 1 week
- Adjust if patterns change

### 4. Start Small
- Pick an achievable habit
- Better 70% success at easy habit
- Than 30% at impossible one

### 5. Review Weekly
- Check visualizations
- Note patterns
- Retrain models

### 6. Stay Focused
- ONE habit at a time
- Don't add more until this is installed
- Usually takes 60-90 days

## Understanding Your Stats

### Completion Rate
- **80%+**: Excellent, habit forming well
- **60-80%**: Good progress, keep going
- **40-60%**: Struggling, consider easier version
- **<40%**: Too hard, reduce difficulty

### Current Streak
- **21+ days**: Habit becoming automatic
- **14-21 days**: Strong momentum
- **7-14 days**: Getting into rhythm
- **<7 days**: Early stages, keep pushing

### Days Since Last
- **0 days**: On track!
- **1-2 days**: No problem, continue
- **3-5 days**: Warning, restart getting harder
- **6+ days**: Need intervention, make it easier

## Keyboard Shortcuts

None yet - it's a CLI app! But in future mobile app:
- Swipe right: Mark complete
- Swipe left: Skip with note
- Tap: View today's prediction
- Long press: View stats

## Getting Help

### Commands
```bash
python main.py help          # Show all commands
python main.py track --help  # Help for specific command (future)
```

### Documentation
- README.md - Project overview
- QUICKSTART.md - Detailed guide
- ARCHITECTURE.md - Technical details
- PROJECT_SUMMARY.md - What we built

### Debugging
```bash
# Check Python version (need 3.8+)
python --version

# Check dependencies
pip list | grep -E "(pandas|scikit-learn|pydantic)"

# Verify file structure
ls -R data/
ls models/
```

## Example Session

```bash
$ python main.py track razaool

🎯 AI HABIT COACH - RAZAOOL
  Your habit: Meditate 20 minutes
  Target: 20 minutes daily

📊 YOUR PROGRESS
  Total days tracked: 14
  Completions: 10
  Success rate: 71.4%
  Current streak: 🔥 3 days
  Longest streak: 🏆 5 days

What would you like to do?
  1. Log today's habit
  2. View stats & insights
  3. Get AI recommendations
  4. Retrain models
  5. Exit

> 3

🤖 AI RECOMMENDATIONS

⏰ Best times for today (wednesday):
   08:00 - 82% predicted success
   19:00 - 76% predicted success
   12:00 - 68% predicted success

🎯 Right now (10:30):
   Predicted success: 79%
   💚 Great time to do your habit!

> 1

📝 LOG HABIT COMPLETION

Did you complete your habit today?
  (Meditate 20 minutes)
(y/n) > y

How difficult was it? [1-10]
> 4

How motivated were you? [1-10]
> 8

How long did it take? (minutes) [20]
> 22

🎉 Great job! Habit logged.
   🔥 Current streak: 4 days

💡 AI Tip: Tomorrow (thursday), try 08:00 (85% success rate)
```

---

**Print this out or keep it handy!**

For full details, see [QUICKSTART.md](QUICKSTART.md)
