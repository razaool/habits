# 🎯 Adaptive Reminder Timing with Reinforcement Learning

An intelligent habit coaching system that uses Deep Reinforcement Learning (DQN) to learn the optimal times to send habit reminders for each individual user.

> **👋 New here? Start with [START_HERE.md](START_HERE.md) for a guided tour!**
> 
> **🚀 Want to run it now? Jump to [GET_STARTED.md](GET_STARTED.md)**

## 🧠 The Problem

Traditional reminder apps use fixed schedules (e.g., "remind me every day at 6 PM"), but:
- ❌ People's schedules vary day-to-day
- ❌ Generic times don't work for everyone
- ❌ Too many reminders lead to habituation (people ignore them)
- ❌ Wrong timing creates negative associations

**Our Solution:** An RL agent that learns each user's unique patterns and optimizes reminder timing to maximize habit completion.

## 🚀 How It Works

### The RL Approach

**State Space** (What the agent observes):
- Temporal features: hour, day of week, weekend status
- User context: location, phone activity, calendar status
- Habit history: current streak, completion rate, past reminders
- Engagement metrics: mood, energy, receptiveness

**Action Space** (What the agent decides):
- Send reminder now
- Wait 30 minutes
- Wait 1 hour
- Wait 2 hours
- Skip today

**Reward Function** (How success is measured):
- ✅ Large positive reward for habit completion (higher if immediate)
- 🚫 Small penalty for ignored reminders
- 📈 Bonus for maintaining streaks
- 🎯 Efficiency bonus for not spamming

**Algorithm**: Deep Q-Network (DQN)
- Neural network approximates Q(state, action)
- Experience replay for stable learning
- Target network for reduced oscillation
- Epsilon-greedy exploration

## 📦 Installation

### Prerequisites
- Python 3.8+
- pip

### Setup

1. **Clone the repository:**
```bash
cd /path/to/habits
```

2. **Create a virtual environment (recommended):**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

## 🎮 Quick Start

### 1. Train the Agent

Train the DQN agent on simulated user data:

```bash
python src/train.py
```

**What happens:**
- Creates a simulated user with realistic behavior patterns
- Trains agent for 500 episodes (configurable in `config.yaml`)
- Saves model checkpoints every 50 episodes
- Generates training curves and logs
- Final model saved to `outputs/models/agent_final.pt`

**Training takes:** ~10-30 minutes on CPU, ~5-10 minutes on GPU

**Output locations:**
- 📊 Models: `outputs/models/`
- 📈 Training curves: `outputs/plots/`
- 📝 Logs: `outputs/logs/`

### 2. Visualize Results

Analyze the trained agent's behavior:

```bash
python src/visualize.py
```

**Generates:**
- 📊 Hourly reminder preference chart
- 🔥 Q-value heatmaps (showing learned value of actions)
- 📈 Strategy comparison (RL vs. baselines)
- 🎯 Day simulation walkthrough

### 3. Run Interactive Demo

See the agent in action:

```bash
python src/demo.py
```

**Features:**
- Week-long simulation with detailed timeline
- Decision-making analysis for different scenarios
- Insights into what the agent learned
- Interactive menu to explore different demos

## 📊 Example Results

After training, you should see improvements like:

| Metric | Random Strategy | Fixed 8 AM | Fixed 6 PM | **RL Agent** |
|--------|----------------|------------|------------|--------------|
| Completion Rate | ~40% | ~50% | ~65% | **~78%** ✨ |
| Avg Streak | 2.3 days | 3.1 days | 4.5 days | **6.8 days** ✨ |
| Reminders/Day | 2.1 | 1.0 | 1.0 | **1.2** |

The RL agent learns to:
- 🎯 Send reminders at personalized optimal times
- 📅 Adapt to weekday vs. weekend patterns
- 🔄 Respect context (location, busyness, phone activity)
- 📈 Prioritize streak preservation
- 🚫 Avoid spamming when user is unresponsive

## ⚙️ Configuration

Edit `config.yaml` to customize:

### Environment Settings
```yaml
environment:
  max_reminders_per_day: 3
  simulation_days: 90
```

### Agent Hyperparameters
```yaml
agent:
  hidden_dims: [128, 64, 32]  # Neural network architecture
  learning_rate: 0.001
  gamma: 0.95                  # Discount factor
  epsilon_start: 1.0           # Initial exploration
  epsilon_end: 0.05            # Final exploration
  epsilon_decay: 0.995
  batch_size: 64
  memory_size: 10000
```

### Training Settings
```yaml
training:
  num_episodes: 500
  max_steps_per_episode: 100
  save_freq: 50
  eval_freq: 10
```

### Reward Shaping
```yaml
rewards:
  completion_immediate: 15.0
  completion_soon: 12.0
  completion_later: 8.0
  ignored: -1.0
  dismissed: -3.0
  streak_bonus: 3.0
```

### User Profiles

Simulate different user types:

```yaml
user_profiles:
  morning_person:
    preferred_hours: [6, 7, 8, 9]
    completion_prob: 0.8
  
  evening_person:
    preferred_hours: [18, 19, 20, 21]
    completion_prob: 0.8
  
  weekend_warrior:
    preferred_hours: [10, 11, 12]
    completion_prob: 0.9
    weekend_boost: 0.2
  
  inconsistent:
    preferred_hours: [12, 13, 14, 15, 16, 17, 18]
    completion_prob: 0.5
```

## 📁 Project Structure

```
habits/
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── config.yaml              # Configuration file
├── src/
│   ├── __init__.py
│   ├── environment.py       # Gym environment for habit reminders
│   ├── user_simulator.py    # Simulates realistic user behavior
│   ├── dqn_agent.py         # DQN implementation with replay buffer
│   ├── train.py             # Training pipeline
│   ├── visualize.py         # Visualization and analysis tools
│   └── demo.py              # Interactive demonstration
└── outputs/
    ├── models/              # Saved model checkpoints
    ├── plots/               # Generated visualizations
    └── logs/                # Training logs
```

## 🎯 Key Components

### 1. Environment (`environment.py`)

Custom Gymnasium environment that simulates the habit reminder system:
- **State**: 15-dimensional continuous space (time, context, history)
- **Actions**: 5 discrete options (send now, wait, skip)
- **Rewards**: Based on completion, timing, and efficiency

### 2. User Simulator (`user_simulator.py`)

Realistic user behavior model:
- Different personality types (morning/evening person, etc.)
- Context-dependent responses (location, calendar, mood)
- Streak motivation and fatigue from spam
- Probabilistic completion based on timing

### 3. DQN Agent (`dqn_agent.py`)

Deep Q-Learning implementation:
- 3-layer neural network (128→64→32 hidden units)
- Experience replay buffer (10,000 experiences)
- Target network for stability
- Huber loss for robust training
- Epsilon-greedy exploration with decay

### 4. Training Pipeline (`train.py`)

Complete training framework:
- Episode management with progress tracking
- Periodic evaluation and checkpointing
- Automatic visualization generation
- Detailed logging and statistics

### 5. Visualization Tools (`visualize.py`)

Analysis and insights:
- Hourly preference heatmaps
- Q-value visualization across states
- Strategy comparison (RL vs. baselines)
- Day-by-day simulation walkthroughs

### 6. Interactive Demo (`demo.py`)

User-friendly demonstrations:
- Week-long simulations with timeline
- Scenario-based decision analysis
- Explainable AI insights
- Interactive exploration

## 🔬 Advanced Usage

### Training Multiple User Profiles

Edit `src/train.py` to train on different user types:

```python
# Change this line in Trainer.__init__
self.user_profile = "morning_person"  # or "evening_person", "weekend_warrior", etc.
```

### Multi-User Training

Train a single agent on multiple user types:

```python
# In train_episode method, randomly sample user profile each episode
profiles = ["morning_person", "evening_person", "weekend_warrior"]
self.user_profile = random.choice(profiles)
self.user_simulator = create_user_simulator(self.user_profile, self.config)
```

### Loading and Resuming Training

```python
from dqn_agent import DQNAgent

agent = DQNAgent(state_dim, action_dim, config)
agent.load("outputs/models/agent_episode_250.pt")
# Continue training from episode 250
```

### Using Trained Agent in Production

```python
from dqn_agent import DQNAgent
import numpy as np

# Load trained agent
agent = DQNAgent(state_dim=15, action_dim=5, config=config)
agent.load("outputs/models/agent_final.pt")

# Get current state from your app
state = np.array([
    current_hour,        # 0-23
    day_of_week,         # 0-6
    is_weekend,          # 0 or 1
    current_streak,      # days
    completion_rate_7d,  # 0-1
    avg_completion_hour, # 0-23
    reminders_sent_today,
    reminders_ignored_today,
    time_since_last_reminder,
    completed_today,
    user_engagement_score,
    location,            # 0-3
    phone_activity,      # 0-1
    calendar_busy,       # 0 or 1
    habit_difficulty     # 0-1
], dtype=np.float32)

# Get agent's decision
action = agent.select_action(state, training=False)

# Map to reminder decision
actions = ['Send Now', 'Wait 30 min', 'Wait 1 hour', 'Wait 2 hours', 'Skip']
decision = actions[action]
```

## 🧪 Experiments to Try

### 1. Different Reward Functions
- Try higher penalties for ignored reminders
- Add rewards for user engagement
- Experiment with streak bonus magnitudes

### 2. Network Architecture
- Deeper networks: `[256, 128, 64, 32]`
- Different activation functions
- Add dropout for regularization

### 3. Exploration Strategies
- Slower epsilon decay
- Boltzmann exploration
- UCB-based action selection

### 4. Multi-Agent Setup
- Train separate agents per habit type
- Meta-learning across users
- Transfer learning from one user to another

## 🐛 Troubleshooting

### Training is slow
- Reduce `num_episodes` in config
- Use GPU (PyTorch will auto-detect)
- Decrease `max_steps_per_episode`

### Agent not learning
- Check reward function (are rewards properly scaled?)
- Increase exploration (`epsilon_decay` closer to 1.0)
- Verify user simulator is working (completion_prob should be reasonable)
- Try simpler network architecture

### Out of memory
- Reduce `batch_size`
- Reduce `memory_size`
- Decrease `hidden_dims`

## 📚 References

### Core Papers
- [Human-level control through deep reinforcement learning (DQN)](https://www.nature.com/articles/nature14236) - Mnih et al., 2015
- [Deep Reinforcement Learning with Double Q-learning](https://arxiv.org/abs/1509.06461) - van Hasselt et al., 2015
- [Prioritized Experience Replay](https://arxiv.org/abs/1511.05952) - Schaul et al., 2015

### RL in Healthcare & Behavior Change
- [Reinforcement Learning for Behavior Change](https://arxiv.org/abs/1901.11435)
- [Mobile Health Apps Using Deep RL](https://www.nature.com/articles/s41746-019-0160-6)

## 🤝 Contributing

Ideas for extensions:
- 🔥 Add multi-habit coordination
- 📱 Integrate real user data collection
- 🎨 Build a mobile app frontend
- 🧠 Add transformer-based state encoder
- 🤖 Implement PPO or SAC algorithms
- 💬 Add natural language explanations
- 📊 A/B testing framework
- 🌐 Multi-user collaborative learning

## 📄 License

MIT License - feel free to use for research or commercial applications!

## 🙏 Acknowledgments

Built with:
- [PyTorch](https://pytorch.org/) - Deep learning framework
- [Gymnasium](https://gymnasium.farama.org/) - RL environment standard
- [Matplotlib](https://matplotlib.org/) & [Seaborn](https://seaborn.pydata.org/) - Visualization

## 📧 Contact

For questions, feedback, or collaboration opportunities, feel free to open an issue!

---

**Built with ❤️ and Reinforcement Learning**

*Making habit formation intelligent, one reminder at a time.* 🎯
