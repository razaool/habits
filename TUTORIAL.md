# 📚 Tutorial: Understanding the Adaptive Reminder System

This tutorial walks you through the key concepts and code of the Adaptive Reminder Timing RL system.

## Table of Contents
1. [The RL Problem Formulation](#the-rl-problem-formulation)
2. [Understanding the State Space](#understanding-the-state-space)
3. [How the Agent Learns](#how-the-agent-learns)
4. [Training Process Explained](#training-process-explained)
5. [Interpreting Results](#interpreting-results)
6. [Customization Guide](#customization-guide)

---

## The RL Problem Formulation

### What are we solving?

**Goal:** Learn when to send habit reminders to maximize user completion rates.

### Why is this an RL problem?

1. **Sequential Decision Making**: Each action affects future states
   - Sending a reminder now → user might complete or ignore
   - If ignored → user becomes fatigued, less likely to respond later
   - If completed → streak increases, user more motivated tomorrow

2. **Delayed Rewards**: Consequences aren't immediate
   - Reminder sent at 6 PM → user might complete at 7 PM
   - Maintaining a streak → benefits compound over days

3. **Exploration vs Exploitation**: 
   - Must try different times to learn (exploration)
   - But also use what we know works (exploitation)

4. **Personalization**: Each user is different
   - Can't use fixed rules
   - Must learn from interaction

### The MDP (Markov Decision Process)

```
State (s_t) → Action (a_t) → Reward (r_t) → Next State (s_{t+1})
     ↑                                              ↓
     └──────────────────────────────────────────────┘
```

**Example Episode:**

```
Day 1, 7 AM:
  State: {hour=7, day=Mon, streak=0, completed_today=False}
  Agent Action: Wait 1 hour
  Environment: Time advances to 8 AM
  Reward: 0 (nothing happened)

Day 1, 8 AM:
  State: {hour=8, day=Mon, streak=0, completed_today=False}
  Agent Action: Send reminder now
  User Response: Ignored
  Reward: -1 (ignored reminder)
  New State: {hour=8, day=Mon, streak=0, completed_today=False, ignored=1}

Day 1, 6 PM:
  State: {hour=18, day=Mon, streak=0, completed_today=False}
  Agent Action: Send reminder now
  User Response: Completed within 30 min!
  Reward: +15 (immediate completion)
  New State: {hour=18, day=Mon, streak=1, completed_today=True}

Day 2, 6 PM:
  Agent has learned: "6 PM on weekdays works well!"
  → More likely to send reminder at 6 PM again
```

---

## Understanding the State Space

The agent observes a 15-dimensional state vector. Let's understand each component:

### Temporal Features

```python
state[0] = hour_of_day        # 0-23: What time is it?
state[1] = day_of_week        # 0-6: Monday to Sunday
state[2] = is_weekend         # 0 or 1: Weekend behavior differs
```

**Why these matter:**
- People have different schedules on weekdays vs weekends
- Morning people vs night owls
- Work hours vs leisure time

### Historical Performance

```python
state[3] = current_streak      # Days in a row of completion
state[4] = completion_rate_7d  # Success rate over last week
state[5] = avg_completion_hour # When user usually completes
```

**Why these matter:**
- Streak length affects motivation (people don't want to break streaks!)
- Past performance predicts future behavior
- Knowing typical completion time helps timing

### Daily Status

```python
state[6] = reminders_sent_today    # How many reminders already sent
state[7] = reminders_ignored_today # How many ignored
state[8] = time_since_last_reminder # Hours since last reminder
state[9] = completed_today         # Already done today?
```

**Why these matter:**
- Avoid spamming (too many reminders = fatigue)
- If already completed, don't send more
- Spacing between reminders matters

### Contextual Information

```python
state[10] = user_engagement_score  # Energy/mood composite
state[11] = location              # Home/work/gym/other
state[12] = phone_activity        # Is user active on phone?
state[13] = calendar_busy         # Does calendar show busy?
state[14] = habit_difficulty      # How hard is this habit?
```

**Why these matter:**
- Context is everything! 
- Reminder at gym for "exercise" habit = perfect timing
- Reminder during meeting = likely to be ignored
- Phone activity = user will see notification

### Example State Vector

```python
state = [
    18.0,  # 6 PM
    3,     # Thursday
    0,     # Not weekend
    5,     # 5-day streak
    0.85,  # 85% completion rate last week
    18.5,  # Usually completes around 6:30 PM
    0,     # No reminders sent today yet
    0,     # None ignored today
    24.0,  # 24 hours since last reminder (yesterday)
    0,     # Not completed yet today
    0.7,   # Moderate engagement
    0,     # At home
    0.8,   # High phone activity
    0,     # Calendar not busy
    0.5    # Medium difficulty habit
]

# Agent looks at this and thinks:
# "Perfect time! 6 PM, at home, on phone, 5-day streak to maintain!"
# → Decision: SEND REMINDER NOW
```

---

## How the Agent Learns

### The Q-Function

The agent learns a function `Q(s, a)` that estimates: 
> "How good is taking action `a` in state `s`?"

```python
Q(state, "Send Now") = 12.5      ← High value, good action
Q(state, "Wait 1 hour") = 3.2    ← Lower value, less optimal
Q(state, "Skip today") = -2.1    ← Negative value, bad action
```

### The Neural Network

```
Input: State (15 dimensions)
          ↓
    [Dense Layer: 128 neurons + ReLU]
          ↓
    [Dense Layer: 64 neurons + ReLU]
          ↓
    [Dense Layer: 32 neurons + ReLU]
          ↓
Output: Q-values (5 values, one per action)
```

### The Learning Algorithm (DQN)

**Step 1: Experience Collection**
```python
# Agent interacts with environment
state = env.reset()
action = agent.select_action(state)
next_state, reward, done = env.step(action)

# Store in replay buffer
memory.store(state, action, reward, next_state, done)
```

**Step 2: Training**
```python
# Sample random batch from memory
batch = memory.sample(64)

# For each experience:
# 1. Current Q-value: Q(s, a) from main network
current_q = q_network(state)[action]

# 2. Target Q-value: r + γ * max_a' Q(s', a') from target network
target_q = reward + gamma * max(target_network(next_state))

# 3. Compute loss
loss = (current_q - target_q)²

# 4. Update network to minimize loss
optimizer.step()
```

**Step 3: Periodic Target Update**
```python
# Every 100 steps, update target network
if steps % 100 == 0:
    target_network = copy(q_network)
```

### Why This Works

**Temporal Difference Learning:**
- Learn from experience (no need for perfect simulator)
- Bootstrap: use current estimates to improve estimates
- Converges to optimal policy given enough data

**Experience Replay:**
- Break correlation between consecutive samples
- Reuse data efficiently (sample-efficient)
- Stabilize training

**Target Network:**
- Prevent moving target problem
- Reduce oscillations
- More stable convergence

---

## Training Process Explained

### Epsilon-Greedy Exploration

```python
if random() < epsilon:
    action = random_action()      # Explore
else:
    action = best_action(state)   # Exploit

# Epsilon decays over time:
# Episode 1: epsilon = 1.0 → 100% random (pure exploration)
# Episode 250: epsilon = 0.3 → 30% random
# Episode 500: epsilon = 0.05 → 5% random (mostly exploitation)
```

**Why decay?**
- Early: Don't know anything → explore widely
- Middle: Have some knowledge → explore intelligently
- Late: Know a lot → mostly use what we learned

### Training Phases

**Phase 1: Random Exploration (Episodes 1-50)**
```
Agent: *tries random times*
"Let me send a reminder at 3 AM... negative reward"
"How about noon... some success!"
"Evening seems better... collecting data..."

Completion Rate: 40-50%
```

**Phase 2: Pattern Recognition (Episodes 51-200)**
```
Agent: *starts noticing patterns*
"Wait, 6-8 PM has higher rewards than morning"
"Weekends are different from weekdays"
"Streaks seem important..."

Completion Rate: 50-65%
```

**Phase 3: Optimization (Episodes 201-400)**
```
Agent: *fine-tunes strategy*
"For this user, 6 PM on weekdays is optimal"
"Weekend mornings work better"
"If streak > 7, send reminder earlier to ensure completion"

Completion Rate: 65-75%
```

**Phase 4: Mastery (Episodes 401-500)**
```
Agent: *highly personalized*
"I know this user's patterns perfectly"
"Adapts to context automatically"
"Maintains long streaks efficiently"

Completion Rate: 75-80%
```

### What the Agent Learns

After training, examining Q-values reveals learned strategies:

**Learned Strategy 1: Time of Day Preferences**
```
Hour 7 AM:  Q(send) = -2.1  ← "Don't send in morning"
Hour 12 PM: Q(send) = 5.3   ← "Lunch is okay"
Hour 6 PM:  Q(send) = 15.2  ← "Best time!"
Hour 10 PM: Q(send) = 3.1   ← "Too late, might be tired"
```

**Learned Strategy 2: Streak Preservation**
```
Streak = 0:  Less aggressive (trying to build habit)
Streak = 7:  More aggressive (don't break week streak!)
Streak = 30: Very aggressive (month milestone!)
```

**Learned Strategy 3: Adaptive Timing**
```
If ignored twice today:
  → Don't send more (avoid spam)
  
If high phone activity + at home:
  → Send now (perfect moment!)
  
If calendar busy:
  → Wait (user is occupied)
```

---

## Interpreting Results

### Training Curves

**1. Episode Rewards**
```
   Reward
     ↑
 150 |                            ╱──────
     |                       ╱────
 100 |                  ╱────
     |             ╱────
  50 |        ╱────
     |   ╱────
   0 |───┴────────────────────────────────→ Episodes
     0   100   200   300   400   500
```
- Should trend upward (agent improving)
- Will have noise (exploration)
- Plateaus when near-optimal

**2. Completion Rate**
```
   Rate
     ↑
 80% |                         ──────────
     |                    ╱────
 60% |              ╱─────
     |         ╱────
 40% |    ╱────
     |────
     └────────────────────────────────────→
     0   100   200   300   400   500
```
- Most important metric!
- Compare to baseline (random: ~40%, fixed: ~50%)
- Target: 75-80% for good agent

**3. Streak Length**
```
  Days
     ↑
  15 |                           ╱╲
     |                      ╱───╱  ╲╱╲
  10 |                ╱────╱          
     |           ╱───╱
   5 |      ╱───╱
     | ╱───╱
   0 |─┴────────────────────────────────→
     0   100   200   300   400   500
```
- Longer streaks = better long-term engagement
- Variance is normal (streaks break)
- Trend should be upward

### Q-Value Heatmaps

```
         Hour of Day
Streak  0  4  8  12 16 20 23
   0    ❄️ ❄️ 🔥 🔥 🔥 ⭐ 🔥
   7    ❄️ ❄️ 🔥 ⭐ ⭐ ⭐ 🔥  
  30    ❄️ ❄️ ⭐ ⭐ ⭐ ⭐ ⭐

Legend: ❄️ = Low Q-value  🔥 = Medium  ⭐ = High
```

**Insights:**
- Early hours (0-8): Low values (user sleeping/commuting)
- Mid-day (12-16): Medium values (work time, hit or miss)
- Evening (18-20): High values (best window!)
- Higher streaks → higher Q-values (more valuable)

---

## Customization Guide

### 1. Changing User Profiles

**Add New Profile** (`config.yaml`):
```yaml
user_profiles:
  night_owl:
    preferred_hours: [22, 23, 0, 1]  # Late night
    completion_prob: 0.75
    weekend_boost: 0.1
```

**Use in Training** (`src/train.py`):
```python
self.user_profile = "night_owl"
```

### 2. Adjusting Rewards

**Make Agent More Conservative** (fewer reminders):
```yaml
rewards:
  ignored: -3.0        # Increase penalty
  dismissed: -5.0      # Increase penalty
  spam_penalty: -5.0   # Increase penalty
```

**Make Agent More Aggressive** (maintain streaks):
```yaml
rewards:
  streak_bonus: 10.0   # Increase bonus
  completion_immediate: 20.0  # Increase reward
```

### 3. Network Architecture

**Deeper Network** (more capacity):
```yaml
agent:
  hidden_dims: [256, 128, 64, 32]
```

**Wider Network** (more features):
```yaml
agent:
  hidden_dims: [256, 256, 128]
```

### 4. Training Duration

**Quick Test**:
```yaml
training:
  num_episodes: 50
  max_steps_per_episode: 30
```

**Full Training**:
```yaml
training:
  num_episodes: 1000
  max_steps_per_episode: 200
```

### 5. Adding New State Features

**Example: Add Weather** (`src/environment.py`):

```python
# In observation_space definition:
low=np.array([..., 0]),    # weather (0-3: sunny/cloudy/rainy/snow)
high=np.array([..., 3]),   # weather

# In _get_observation:
weather = self.user_simulator.get_weather()
obs = np.array([..., weather])
```

### 6. Custom Reward Function

**Example: Add Time Penalty** (`src/environment.py`):

```python
def _calculate_reward(self, response):
    reward = 0.0
    
    # Existing reward logic...
    
    # NEW: Penalize very late reminders
    if self.current_hour > 22:  # After 10 PM
        reward -= 2.0  # "Too late!"
    
    return reward
```

---

## Advanced Topics

### Multi-Habit Coordination

Train agent to manage multiple habits:
- State includes habit type
- Learn interactions (gym habit + meal prep habit)
- Optimize scheduling across habits

### Transfer Learning

Train on one user, transfer to another:
- Pre-train on general population
- Fine-tune on individual user
- Few-shot personalization

### Explainable AI

Add interpretability:
- Attention mechanisms (which state features matter?)
- Counterfactual explanations ("I sent now because...")
- Confidence estimates ("80% sure this will work")

### Real User Integration

Deploy to production:
- Collect real user interaction data
- Online learning (continue training in production)
- A/B testing framework
- Privacy-preserving learning

---

## Debugging Tips

### Agent Not Learning?

**Check 1: Rewards**
```python
# Add logging in environment.py
print(f"Reward: {reward}, Response: {response}")
```
- Are rewards actually being given?
- Are they scaled properly? (not too small)

**Check 2: State Representation**
```python
# Log state vectors
print(f"State: {state}")
```
- Are features normalized? (0-1 range or similar)
- Are they informative? (do they change meaningfully?)

**Check 3: Exploration**
```python
# Log epsilon
print(f"Epsilon: {agent.epsilon}")
```
- Too low too fast? (increase epsilon_decay to 0.999)
- Too high too long? (decrease epsilon_decay to 0.99)

### Agent Performing Worse Than Random?

**Likely Issues:**
1. Reward function bug (negative rewards dominating)
2. State features not normalized
3. Learning rate too high (0.001 → 0.0001)
4. Network too large for problem (overfit)

### Training Unstable?

**Solutions:**
1. Add gradient clipping (already implemented)
2. Use smaller learning rate
3. Increase batch size
4. Use simpler network architecture

---

## Next Steps

1. **Try It Out**: Run `python quick_start.py`
2. **Experiment**: Modify config.yaml and see effects
3. **Analyze**: Run visualizations to understand behavior
4. **Extend**: Add your own features and rewards
5. **Deploy**: Integrate with real habit tracking app

Happy learning! 🎯🚀

