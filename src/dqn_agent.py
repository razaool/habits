"""
Deep Q-Network (DQN) Agent for Habit Reminder Timing

Implements DQN with experience replay and target network for stable learning.
"""

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque, namedtuple
from typing import List, Tuple, Optional
import random


# Experience tuple for replay buffer
Experience = namedtuple('Experience', ['state', 'action', 'reward', 'next_state', 'done'])


class QNetwork(nn.Module):
    """
    Deep Q-Network: Neural network that approximates Q(s, a) for all actions
    """
    
    def __init__(self, state_dim: int, action_dim: int, hidden_dims: List[int] = [128, 64, 32]):
        """
        Initialize Q-Network
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of discrete actions
            hidden_dims: List of hidden layer dimensions
        """
        super(QNetwork, self).__init__()
        
        # Build network layers
        layers = []
        input_dim = state_dim
        
        for hidden_dim in hidden_dims:
            layers.append(nn.Linear(input_dim, hidden_dim))
            layers.append(nn.ReLU())
            layers.append(nn.LayerNorm(hidden_dim))  # Layer normalization for stability
            input_dim = hidden_dim
        
        # Output layer: Q-values for each action
        layers.append(nn.Linear(input_dim, action_dim))
        
        self.network = nn.Sequential(*layers)
        
        # Initialize weights
        self._initialize_weights()
    
    def _initialize_weights(self):
        """Initialize network weights using Xavier initialization"""
        for module in self.modules():
            if isinstance(module, nn.Linear):
                nn.init.xavier_uniform_(module.weight)
                nn.init.constant_(module.bias, 0.0)
    
    def forward(self, state: torch.Tensor) -> torch.Tensor:
        """
        Forward pass: compute Q-values for all actions
        
        Args:
            state: Tensor of shape (batch_size, state_dim)
            
        Returns:
            Q-values of shape (batch_size, action_dim)
        """
        return self.network(state)


class ReplayBuffer:
    """
    Experience Replay Buffer for storing and sampling experiences
    """
    
    def __init__(self, capacity: int):
        """
        Initialize replay buffer
        
        Args:
            capacity: Maximum number of experiences to store
        """
        self.buffer = deque(maxlen=capacity)
    
    def push(self, state: np.ndarray, action: int, reward: float, 
             next_state: np.ndarray, done: bool):
        """Add experience to buffer"""
        experience = Experience(state, action, reward, next_state, done)
        self.buffer.append(experience)
    
    def sample(self, batch_size: int) -> List[Experience]:
        """
        Sample a batch of experiences
        
        Args:
            batch_size: Number of experiences to sample
            
        Returns:
            List of Experience tuples
        """
        return random.sample(self.buffer, batch_size)
    
    def __len__(self) -> int:
        """Return current size of buffer"""
        return len(self.buffer)


class DQNAgent:
    """
    Deep Q-Network Agent with experience replay and target network
    """
    
    def __init__(self, state_dim: int, action_dim: int, config: dict):
        """
        Initialize DQN Agent
        
        Args:
            state_dim: Dimension of state space
            action_dim: Number of discrete actions
            config: Configuration dictionary
        """
        self.state_dim = state_dim
        self.action_dim = action_dim
        self.config = config
        
        # Hyperparameters
        self.gamma = config['agent']['gamma']  # Discount factor
        self.epsilon = config['agent']['epsilon_start']  # Exploration rate
        self.epsilon_min = config['agent']['epsilon_end']
        self.epsilon_decay = config['agent']['epsilon_decay']
        self.learning_rate = config['agent']['learning_rate']
        self.batch_size = config['agent']['batch_size']
        self.target_update_freq = config['agent']['target_update_freq']
        
        # Device (GPU if available)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        # Q-Networks
        hidden_dims = config['agent']['hidden_dims']
        self.q_network = QNetwork(state_dim, action_dim, hidden_dims).to(self.device)
        self.target_network = QNetwork(state_dim, action_dim, hidden_dims).to(self.device)
        
        # Initialize target network with same weights
        self.target_network.load_state_dict(self.q_network.state_dict())
        self.target_network.eval()  # Target network is not trained directly
        
        # Optimizer
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)
        
        # Loss function
        self.criterion = nn.SmoothL1Loss()  # Huber loss (more stable than MSE)
        
        # Replay buffer
        memory_size = config['agent']['memory_size']
        self.memory = ReplayBuffer(memory_size)
        
        # Training statistics
        self.steps_done = 0
        self.episodes_done = 0
        self.losses = []
    
    def select_action(self, state: np.ndarray, training: bool = True) -> int:
        """
        Select action using epsilon-greedy policy
        
        Args:
            state: Current state
            training: If True, use epsilon-greedy; if False, use greedy
            
        Returns:
            Selected action (integer)
        """
        # Exploration vs exploitation
        if training and random.random() < self.epsilon:
            # Random action (exploration)
            return random.randrange(self.action_dim)
        else:
            # Greedy action (exploitation)
            with torch.no_grad():
                state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
                q_values = self.q_network(state_tensor)
                return q_values.argmax(dim=1).item()
    
    def store_experience(self, state: np.ndarray, action: int, reward: float,
                        next_state: np.ndarray, done: bool):
        """Store experience in replay buffer"""
        self.memory.push(state, action, reward, next_state, done)
    
    def train_step(self) -> Optional[float]:
        """
        Perform one training step (if enough experiences in buffer)
        
        Returns:
            Loss value if training occurred, None otherwise
        """
        # Check if enough experiences in buffer
        if len(self.memory) < self.batch_size:
            return None
        
        # Sample batch from replay buffer
        experiences = self.memory.sample(self.batch_size)
        
        # Convert to tensors
        states = torch.FloatTensor([e.state for e in experiences]).to(self.device)
        actions = torch.LongTensor([e.action for e in experiences]).unsqueeze(1).to(self.device)
        rewards = torch.FloatTensor([e.reward for e in experiences]).unsqueeze(1).to(self.device)
        next_states = torch.FloatTensor([e.next_state for e in experiences]).to(self.device)
        dones = torch.FloatTensor([e.done for e in experiences]).unsqueeze(1).to(self.device)
        
        # Compute current Q-values
        current_q_values = self.q_network(states).gather(1, actions)
        
        # Compute target Q-values using target network
        with torch.no_grad():
            next_q_values = self.target_network(next_states).max(1, keepdim=True)[0]
            target_q_values = rewards + (1 - dones) * self.gamma * next_q_values
        
        # Compute loss
        loss = self.criterion(current_q_values, target_q_values)
        
        # Optimize
        self.optimizer.zero_grad()
        loss.backward()
        # Gradient clipping for stability
        torch.nn.utils.clip_grad_norm_(self.q_network.parameters(), max_norm=1.0)
        self.optimizer.step()
        
        # Update steps counter
        self.steps_done += 1
        
        # Update target network periodically
        if self.steps_done % self.target_update_freq == 0:
            self.target_network.load_state_dict(self.q_network.state_dict())
        
        # Decay epsilon
        self.epsilon = max(self.epsilon_min, self.epsilon * self.epsilon_decay)
        
        # Store loss for logging
        loss_value = loss.item()
        self.losses.append(loss_value)
        
        return loss_value
    
    def save(self, filepath: str):
        """
        Save agent state to file
        
        Args:
            filepath: Path to save checkpoint
        """
        checkpoint = {
            'q_network_state_dict': self.q_network.state_dict(),
            'target_network_state_dict': self.target_network.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'epsilon': self.epsilon,
            'steps_done': self.steps_done,
            'episodes_done': self.episodes_done,
            'losses': self.losses,
            'config': self.config
        }
        torch.save(checkpoint, filepath)
        print(f"Agent saved to {filepath}")
    
    def load(self, filepath: str):
        """
        Load agent state from file
        
        Args:
            filepath: Path to load checkpoint from
        """
        checkpoint = torch.load(filepath, map_location=self.device)
        self.q_network.load_state_dict(checkpoint['q_network_state_dict'])
        self.target_network.load_state_dict(checkpoint['target_network_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.epsilon = checkpoint['epsilon']
        self.steps_done = checkpoint['steps_done']
        self.episodes_done = checkpoint['episodes_done']
        self.losses = checkpoint['losses']
        print(f"Agent loaded from {filepath}")
    
    def get_q_values(self, state: np.ndarray) -> np.ndarray:
        """
        Get Q-values for all actions in a given state
        
        Args:
            state: Current state
            
        Returns:
            Array of Q-values for each action
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(self.device)
            q_values = self.q_network(state_tensor)
            return q_values.cpu().numpy()[0]
    
    def episode_finished(self):
        """Call this at the end of each episode"""
        self.episodes_done += 1

