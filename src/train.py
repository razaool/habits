"""
Training Pipeline for Adaptive Reminder Timing Agent

Trains the DQN agent using the habit reminder environment and user simulator.
"""

import os
import yaml
import numpy as np
import torch
from typing import Dict, List
import matplotlib.pyplot as plt
from datetime import datetime
from tqdm import tqdm

from environment import HabitReminderEnv
from user_simulator import create_user_simulator
from dqn_agent import DQNAgent


class Trainer:
    """
    Handles training loop, evaluation, and logging
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize trainer
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print("=" * 60)
        print("Adaptive Reminder Timing - RL Training")
        print("=" * 60)
        
        # Create directories
        self.setup_directories()
        
        # Initialize environment with user simulator
        self.user_profile = "evening_person"  # Can be parameterized
        self.user_simulator = create_user_simulator(
            self.user_profile,
            self.config,
            seed=42
        )
        
        self.env = HabitReminderEnv(self.user_simulator, self.config)
        
        # Initialize agent
        state_dim = self.env.observation_space.shape[0]
        action_dim = self.env.action_space.n
        self.agent = DQNAgent(state_dim, action_dim, self.config)
        
        print(f"\nEnvironment initialized:")
        print(f"  State dimension: {state_dim}")
        print(f"  Action dimension: {action_dim}")
        print(f"  User profile: {self.user_profile}")
        
        # Training statistics
        self.episode_rewards = []
        self.episode_completions = []
        self.episode_lengths = []
        self.episode_streaks = []
        self.eval_rewards = []
        
    def setup_directories(self):
        """Create necessary directories for outputs"""
        self.base_dir = "outputs"
        self.models_dir = os.path.join(self.base_dir, "models")
        self.logs_dir = os.path.join(self.base_dir, "logs")
        self.plots_dir = os.path.join(self.base_dir, "plots")
        
        for directory in [self.models_dir, self.logs_dir, self.plots_dir]:
            os.makedirs(directory, exist_ok=True)
    
    def train(self):
        """Main training loop"""
        num_episodes = self.config['training']['num_episodes']
        max_steps = self.config['training']['max_steps_per_episode']
        save_freq = self.config['training']['save_freq']
        eval_freq = self.config['training']['eval_freq']
        
        print(f"\nStarting training for {num_episodes} episodes...")
        print(f"Max steps per episode: {max_steps}")
        print(f"Save frequency: every {save_freq} episodes")
        print(f"Eval frequency: every {eval_freq} episodes\n")
        
        for episode in tqdm(range(num_episodes), desc="Training"):
            episode_reward, episode_info = self.train_episode(max_steps)
            
            # Store statistics
            self.episode_rewards.append(episode_reward)
            self.episode_completions.append(episode_info['completions'])
            self.episode_lengths.append(episode_info['steps'])
            self.episode_streaks.append(episode_info['max_streak'])
            
            # Evaluate periodically
            if (episode + 1) % eval_freq == 0:
                eval_reward = self.evaluate()
                self.eval_rewards.append(eval_reward)
                
                # Print progress
                avg_reward = np.mean(self.episode_rewards[-eval_freq:])
                avg_completions = np.mean(self.episode_completions[-eval_freq:])
                print(f"\nEpisode {episode + 1}/{num_episodes}")
                print(f"  Avg Reward (last {eval_freq}): {avg_reward:.2f}")
                print(f"  Avg Completions: {avg_completions:.2f}")
                print(f"  Eval Reward: {eval_reward:.2f}")
                print(f"  Epsilon: {self.agent.epsilon:.4f}")
                print(f"  Buffer Size: {len(self.agent.memory)}")
            
            # Save model periodically
            if (episode + 1) % save_freq == 0:
                self.save_checkpoint(episode + 1)
        
        print("\n" + "=" * 60)
        print("Training completed!")
        print("=" * 60)
        
        # Save final model
        self.save_checkpoint(num_episodes, final=True)
        
        # Generate plots
        self.plot_training_curves()
        
        # Save training log
        self.save_training_log()
    
    def train_episode(self, max_steps: int) -> tuple:
        """
        Train for one episode
        
        Args:
            max_steps: Maximum steps per episode
            
        Returns:
            Tuple of (total_reward, info_dict)
        """
        state, _ = self.env.reset()
        episode_reward = 0.0
        steps = 0
        completions = 0
        max_streak = 0
        
        for step in range(max_steps):
            # Select action
            action = self.agent.select_action(state, training=True)
            
            # Take step in environment
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            # Store experience
            self.agent.store_experience(state, action, reward, next_state, done)
            
            # Train agent
            loss = self.agent.train_step()
            
            # Update state
            state = next_state
            episode_reward += reward
            steps += 1
            
            # Track completions
            if info.get('response') in ['COMPLETED_IMMEDIATE', 'COMPLETED_SOON', 'COMPLETED_LATER']:
                completions += 1
            
            # Track max streak
            max_streak = max(max_streak, int(state[3]))  # state[3] is current_streak
            
            if done:
                break
        
        # Episode finished
        self.agent.episode_finished()
        
        info_dict = {
            'steps': steps,
            'completions': completions,
            'max_streak': max_streak
        }
        
        return episode_reward, info_dict
    
    def evaluate(self, num_episodes: int = None) -> float:
        """
        Evaluate agent performance (no exploration)
        
        Args:
            num_episodes: Number of episodes to evaluate
            
        Returns:
            Average reward over evaluation episodes
        """
        if num_episodes is None:
            num_episodes = self.config['training']['eval_episodes']
        
        eval_rewards = []
        
        for _ in range(num_episodes):
            state, _ = self.env.reset()
            episode_reward = 0.0
            done = False
            steps = 0
            max_steps = self.config['training']['max_steps_per_episode']
            
            while not done and steps < max_steps:
                # Greedy action selection (no exploration)
                action = self.agent.select_action(state, training=False)
                next_state, reward, terminated, truncated, _ = self.env.step(action)
                done = terminated or truncated
                
                state = next_state
                episode_reward += reward
                steps += 1
            
            eval_rewards.append(episode_reward)
        
        return np.mean(eval_rewards)
    
    def save_checkpoint(self, episode: int, final: bool = False):
        """
        Save model checkpoint
        
        Args:
            episode: Current episode number
            final: Whether this is the final checkpoint
        """
        if final:
            filename = "agent_final.pt"
        else:
            filename = f"agent_episode_{episode}.pt"
        
        filepath = os.path.join(self.models_dir, filename)
        self.agent.save(filepath)
    
    def plot_training_curves(self):
        """Generate and save training visualization plots"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Plot 1: Episode Rewards
        ax = axes[0, 0]
        ax.plot(self.episode_rewards, alpha=0.3, color='blue', label='Episode Reward')
        if len(self.episode_rewards) > 10:
            window = min(50, len(self.episode_rewards) // 10)
            smoothed = self._moving_average(self.episode_rewards, window)
            ax.plot(smoothed, color='red', linewidth=2, label=f'Moving Avg ({window})')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Total Reward')
        ax.set_title('Training Rewards Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 2: Completions per Episode
        ax = axes[0, 1]
        ax.plot(self.episode_completions, alpha=0.3, color='green', label='Completions')
        if len(self.episode_completions) > 10:
            window = min(50, len(self.episode_completions) // 10)
            smoothed = self._moving_average(self.episode_completions, window)
            ax.plot(smoothed, color='darkgreen', linewidth=2, label=f'Moving Avg ({window})')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Number of Completions')
        ax.set_title('Habit Completions Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 3: Max Streak per Episode
        ax = axes[1, 0]
        ax.plot(self.episode_streaks, alpha=0.3, color='purple', label='Max Streak')
        if len(self.episode_streaks) > 10:
            window = min(50, len(self.episode_streaks) // 10)
            smoothed = self._moving_average(self.episode_streaks, window)
            ax.plot(smoothed, color='darkviolet', linewidth=2, label=f'Moving Avg ({window})')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Max Streak (days)')
        ax.set_title('Maximum Streak Length Over Time')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Plot 4: Evaluation Rewards
        ax = axes[1, 1]
        if self.eval_rewards:
            eval_freq = self.config['training']['eval_freq']
            eval_episodes = [i * eval_freq for i in range(1, len(self.eval_rewards) + 1)]
            ax.plot(eval_episodes, self.eval_rewards, marker='o', color='orange', linewidth=2)
            ax.set_xlabel('Episode')
            ax.set_ylabel('Average Evaluation Reward')
            ax.set_title('Evaluation Performance')
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plot_path = os.path.join(self.plots_dir, f"training_curves_{timestamp}.png")
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"\nTraining curves saved to: {plot_path}")
        plt.close()
    
    def _moving_average(self, data: List[float], window: int) -> List[float]:
        """Calculate moving average"""
        if len(data) < window:
            return data
        
        smoothed = []
        for i in range(len(data)):
            start = max(0, i - window + 1)
            smoothed.append(np.mean(data[start:i+1]))
        return smoothed
    
    def save_training_log(self):
        """Save training statistics to file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_path = os.path.join(self.logs_dir, f"training_log_{timestamp}.txt")
        
        with open(log_path, 'w') as f:
            f.write("=" * 60 + "\n")
            f.write("Adaptive Reminder Timing - Training Log\n")
            f.write("=" * 60 + "\n\n")
            
            f.write(f"User Profile: {self.user_profile}\n")
            f.write(f"Total Episodes: {len(self.episode_rewards)}\n")
            f.write(f"Final Epsilon: {self.agent.epsilon:.4f}\n\n")
            
            f.write("Training Statistics:\n")
            f.write(f"  Average Reward: {np.mean(self.episode_rewards):.2f}\n")
            f.write(f"  Best Reward: {np.max(self.episode_rewards):.2f}\n")
            f.write(f"  Average Completions: {np.mean(self.episode_completions):.2f}\n")
            f.write(f"  Average Max Streak: {np.mean(self.episode_streaks):.2f}\n")
            f.write(f"  Best Streak: {np.max(self.episode_streaks):.0f} days\n\n")
            
            if self.eval_rewards:
                f.write("Evaluation Statistics:\n")
                f.write(f"  Final Eval Reward: {self.eval_rewards[-1]:.2f}\n")
                f.write(f"  Best Eval Reward: {np.max(self.eval_rewards):.2f}\n\n")
            
            f.write("Last 10 Episode Rewards:\n")
            for i, reward in enumerate(self.episode_rewards[-10:], 1):
                f.write(f"  Episode {len(self.episode_rewards) - 10 + i}: {reward:.2f}\n")
        
        print(f"Training log saved to: {log_path}")


def main():
    """Main training function"""
    # Parse arguments (could add argparse for more flexibility)
    config_path = "config.yaml"
    
    # Initialize trainer
    trainer = Trainer(config_path)
    
    # Train agent
    trainer.train()
    
    print("\nAll done! Check the outputs/ directory for results.")


if __name__ == "__main__":
    main()

