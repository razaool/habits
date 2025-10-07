# System Architecture

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Adaptive Reminder System                      │
│                                                                   │
│  ┌────────────────┐         ┌──────────────┐                    │
│  │  User Context  │────────▶│  RL Agent    │                    │
│  │                │         │   (DQN)      │                    │
│  │ • Time         │         │              │                    │
│  │ • Location     │         │  Q-Network   │                    │
│  │ • Activity     │         │  + Memory    │                    │
│  │ • History      │         └──────┬───────┘                    │
│  └────────────────┘                │                            │
│                                     │                            │
│                                     ▼                            │
│                          ┌──────────────────┐                   │
│                          │  Action Decision │                   │
│                          │                  │                   │
│                          │ • Send Now       │                   │
│                          │ • Wait           │                   │
│                          │ • Skip           │                   │
│                          └────────┬─────────┘                   │
│                                   │                             │
│                                   ▼                             │
│  ┌──────────────────────────────────────────┐                  │
│  │         User Simulator / Real User       │                  │
│  │                                          │                  │
│  │  Responds: Complete / Ignore / Dismiss  │                  │
│  └──────────────────┬───────────────────────┘                  │
│                     │                                           │
│                     ▼                                           │
│           ┌──────────────────┐                                 │
│           │  Reward Signal   │                                 │
│           │                  │                                 │
│           │ • +15 Complete!  │                                 │
│           │ • -1  Ignored    │                                 │
│           │ • +3  Streak     │                                 │
│           └────────┬─────────┘                                 │
│                    │                                            │
│                    └───────────▶ Learning Loop                 │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## Component Architecture

### 1. Environment Layer (`environment.py`)

```
┌────────────────────────────────────────────────────┐
│              HabitReminderEnv                       │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │           State Construction                 │  │
│  │                                              │  │
│  │  hour, day, streak, context ... (15 dims)   │  │
│  └────────────┬─────────────────────────────────┘  │
│               │                                     │
│               ▼                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │           Step Function                      │  │
│  │                                              │  │
│  │  1. Execute action                          │  │
│  │  2. Update time/state                       │  │
│  │  3. Get user response                       │  │
│  │  4. Calculate reward                        │  │
│  │  5. Check termination                       │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         Reward Function                      │  │
│  │                                              │  │
│  │  Completion    → +15/+12/+8                 │  │
│  │  Ignored       → -1                         │  │
│  │  Dismissed     → -3                         │  │
│  │  Streak Bonus  → +3                         │  │
│  │  Spam Penalty  → -2                         │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### 2. User Simulator Layer (`user_simulator.py`)

```
┌────────────────────────────────────────────────────┐
│              UserSimulator                          │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │         User Profile                         │  │
│  │                                              │  │
│  │  • Preferred hours: [18, 19, 20]           │  │
│  │  • Completion probability: 0.8              │  │
│  │  • Weekend boost: +0.2                      │  │
│  │  • Streak motivation: 0.1                   │  │
│  │  • Fatigue factor: 0.15                     │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │      Context Generation                      │  │
│  │                                              │  │
│  │  Location ─────┐                            │  │
│  │  Phone Activity│                            │  │
│  │  Calendar      ├──▶ Context Dict            │  │
│  │  Engagement    │                            │  │
│  └────────────────┴──────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │      Response Model                          │  │
│  │                                              │  │
│  │  P(complete) = f(hour, context, streak)     │  │
│  │                                              │  │
│  │  Sample response based on probability       │  │
│  └──────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────┘
```

### 3. Agent Layer (`dqn_agent.py`)

```
┌──────────────────────────────────────────────────────────┐
│                      DQN Agent                            │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │              Q-Network                             │  │
│  │                                                    │  │
│  │    Input (15)                                     │  │
│  │        ↓                                          │  │
│  │    Dense(128) + ReLU + LayerNorm                 │  │
│  │        ↓                                          │  │
│  │    Dense(64) + ReLU + LayerNorm                  │  │
│  │        ↓                                          │  │
│  │    Dense(32) + ReLU + LayerNorm                  │  │
│  │        ↓                                          │  │
│  │    Dense(5)  [Q-values for each action]          │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │           Target Network (Copy)                    │  │
│  │                                                    │  │
│  │    Same architecture, updated every 100 steps     │  │
│  │    Provides stable training targets               │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         Experience Replay Buffer                   │  │
│  │                                                    │  │
│  │  Stores: (state, action, reward, next_state)      │  │
│  │  Capacity: 10,000 experiences                     │  │
│  │  Sampling: Random batch of 64                     │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │         Action Selection                           │  │
│  │                                                    │  │
│  │  if random() < ε:                                 │  │
│  │      action = random()        # Explore           │  │
│  │  else:                                            │  │
│  │      action = argmax(Q(s,a))  # Exploit           │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### 4. Training Pipeline (`train.py`)

```
┌──────────────────────────────────────────────────────────┐
│                   Training Loop                           │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Episode Loop (500 episodes)                       │  │
│  │                                                    │  │
│  │  For each episode:                                │  │
│  │    1. Reset environment                           │  │
│  │    │                                              │  │
│  │    2. Step Loop (until done):                     │  │
│  │    │   ├─ Observe state                          │  │
│  │    │   ├─ Select action (ε-greedy)               │  │
│  │    │   ├─ Execute in environment                 │  │
│  │    │   ├─ Store experience in buffer             │  │
│  │    │   ├─ Sample batch & train network           │  │
│  │    │   └─ Update target network (periodic)       │  │
│  │    │                                              │  │
│  │    3. Decay epsilon                               │  │
│  │    │                                              │  │
│  │    4. Log statistics                              │  │
│  │    │                                              │  │
│  │    5. Periodic evaluation (every 10 episodes)     │  │
│  │    │                                              │  │
│  │    6. Save checkpoint (every 50 episodes)         │  │
│  │                                                    │  │
│  └────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌────────────────────────────────────────────────────┐  │
│  │  Output Generation                                 │  │
│  │                                                    │  │
│  │  • Training curves (plots)                        │  │
│  │  • Model checkpoints                              │  │
│  │  • Training logs                                  │  │
│  └────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Training Phase

```
1. Initialize
   ├─ Create environment
   ├─ Create user simulator
   ├─ Create DQN agent
   └─ Set hyperparameters

2. For each episode:
   │
   ├─ Reset environment
   │  └─ Get initial state s₀
   │
   ├─ For each step:
   │  │
   │  ├─ Agent observes state sₜ
   │  │  └─ [hour, day, streak, context...] (15 dims)
   │  │
   │  ├─ Agent selects action aₜ
   │  │  └─ ε-greedy: explore or exploit
   │  │
   │  ├─ Environment executes action
   │  │  ├─ Update time/state
   │  │  └─ If "send reminder":
   │  │      ├─ User simulator responds
   │  │      └─ Calculate reward rₜ
   │  │
   │  ├─ Get next state sₜ₊₁
   │  │
   │  ├─ Store transition (sₜ, aₜ, rₜ, sₜ₊₁) in buffer
   │  │
   │  ├─ Sample random batch from buffer
   │  │
   │  ├─ Compute loss:
   │  │  │  Q_current = Q_net(sₜ)[aₜ]
   │  │  │  Q_target = rₜ + γ·max(Q_target_net(sₜ₊₁))
   │  │  └─ loss = (Q_current - Q_target)²
   │  │
   │  ├─ Backpropagate & update Q_net
   │  │
   │  └─ If step % 100 == 0:
   │      └─ Q_target_net ← Q_net
   │
   └─ Log episode statistics

3. Generate visualizations
4. Save final model
```

### Inference Phase

```
1. Load trained agent
   └─ Q_net with learned weights

2. For each decision point:
   │
   ├─ Observe current state s
   │  └─ Get user context
   │
   ├─ Compute Q-values
   │  Q(s, "Send Now") = ?
   │  Q(s, "Wait 30m") = ?
   │  Q(s, "Wait 1h")  = ?
   │  Q(s, "Wait 2h")  = ?
   │  Q(s, "Skip")     = ?
   │
   ├─ Select best action (greedy)
   │  action = argmax(Q(s, a))
   │
   └─ Execute action
```

---

## Training Algorithm Pseudocode

```python
# Initialize
env = HabitReminderEnv(user_simulator, config)
agent = DQNAgent(state_dim=15, action_dim=5, config)

# Training loop
for episode in range(num_episodes):
    state = env.reset()
    episode_reward = 0
    
    while not done:
        # Select action
        if random() < epsilon:
            action = random_action()  # Explore
        else:
            action = argmax(Q(state))  # Exploit
        
        # Execute action
        next_state, reward, done = env.step(action)
        
        # Store experience
        memory.store(state, action, reward, next_state, done)
        
        # Train
        if len(memory) >= batch_size:
            batch = memory.sample(batch_size)
            
            # Compute targets
            current_q = Q_net(batch.states)[batch.actions]
            next_q = Q_target_net(batch.next_states).max()
            target_q = batch.rewards + gamma * next_q
            
            # Update network
            loss = MSE(current_q, target_q)
            optimizer.step(loss)
        
        # Update target network periodically
        if steps % target_update_freq == 0:
            Q_target_net = copy(Q_net)
        
        state = next_state
        episode_reward += reward
    
    # Decay exploration
    epsilon *= epsilon_decay
    
    # Evaluate periodically
    if episode % eval_freq == 0:
        eval_reward = evaluate(agent, env)
        print(f"Episode {episode}: {eval_reward}")
    
    # Save checkpoint
    if episode % save_freq == 0:
        agent.save(f"checkpoint_{episode}.pt")
```

---

## Key Design Decisions

### 1. State Representation
**Decision**: 15-dimensional continuous vector  
**Rationale**: 
- Captures all relevant context
- Normalized for stable learning
- Not too high-dimensional (efficient)

### 2. Action Space
**Decision**: 5 discrete actions  
**Rationale**:
- Simple enough for DQN
- Provides flexibility (wait times)
- Includes "skip" for efficiency

### 3. Reward Function
**Decision**: Shaped rewards with multiple components  
**Rationale**:
- Immediate completion gets highest reward
- Penalties discourage bad behavior
- Bonuses encourage long-term thinking

### 4. Algorithm: DQN
**Decision**: Deep Q-Network with replay & target network  
**Rationale**:
- Well-suited for discrete actions
- Stable and proven
- Efficient for this problem size

### 5. Network Architecture
**Decision**: 3-layer MLP [128, 64, 32]  
**Rationale**:
- Sufficient capacity for problem
- Not too large (fast training)
- Layer norm for stability

### 6. User Simulator
**Decision**: Probabilistic model with profiles  
**Rationale**:
- Realistic behavior patterns
- Controllable for experiments
- Diverse user types

---

## Performance Characteristics

### Memory Usage
- **Replay Buffer**: ~40 MB (10,000 × 15 floats)
- **Q-Network**: ~500 KB (weights)
- **Total**: < 100 MB

### Training Time
- **CPU**: ~20-30 minutes (500 episodes)
- **GPU**: ~10-15 minutes (500 episodes)
- **Quick Start**: ~2-5 minutes (50 episodes)

### Inference Speed
- **Decision Time**: < 1 ms per action
- **Real-time Capable**: Yes

### Scalability
- **State Dimension**: Can handle 50+ features
- **Users**: Separate model per user or shared
- **Habits**: Multi-task learning possible

---

## Extension Points

### Easy to Add
1. **New State Features**: Modify observation space in `environment.py`
2. **New Rewards**: Adjust reward function in `environment.py`
3. **New User Types**: Add to `config.yaml` profiles
4. **More Visualizations**: Extend `visualize.py`

### Moderate Effort
1. **Different Algorithms**: Replace `DQNAgent` (same interface)
2. **Multi-Habit Support**: Expand state/action spaces
3. **Online Learning**: Add continuous training mode
4. **Transfer Learning**: Pre-train, then fine-tune

### Significant Effort
1. **Real User Integration**: Mobile app backend
2. **Multi-Agent System**: User community coordination
3. **Causal Inference**: Learn intervention effects
4. **Explainable AI**: Attention mechanisms

---

## Testing Strategy

### Unit Tests (Recommended to Add)
```python
# test_environment.py
def test_reset():
    env = HabitReminderEnv(...)
    obs, info = env.reset()
    assert obs.shape == (15,)

def test_step():
    env = HabitReminderEnv(...)
    obs, _ = env.reset()
    next_obs, reward, done, _, info = env.step(0)
    assert isinstance(reward, float)

# test_agent.py
def test_action_selection():
    agent = DQNAgent(...)
    state = np.random.randn(15)
    action = agent.select_action(state)
    assert 0 <= action < 5

# test_user_simulator.py
def test_response():
    sim = UserSimulator(...)
    response = sim.respond_to_reminder(18, 3, 5, 0)
    assert response in UserResponse
```

### Integration Tests
```python
# test_training.py
def test_training_loop():
    trainer = Trainer("config.yaml")
    trainer.config['training']['num_episodes'] = 5
    trainer.train()
    assert os.path.exists("outputs/models/agent_final.pt")
```

### System Tests
1. Quick start completes successfully
2. Training converges (reward increases)
3. Visualizations generate without errors
4. Demo runs interactively

---

This architecture provides a solid foundation for an intelligent habit reminder system, with clear separation of concerns and extensibility for future enhancements.

