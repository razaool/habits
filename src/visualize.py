"""
Visualization Tools for Adaptive Reminder Timing Agent

Tools to analyze and visualize agent behavior and learning patterns.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from typing import List, Dict
import torch
import yaml

from environment import HabitReminderEnv, Action
from user_simulator import create_user_simulator
from dqn_agent import DQNAgent


class AgentAnalyzer:
    """
    Analyzes trained agent behavior and creates visualizations
    """
    
    def __init__(self, agent_path: str, config_path: str = "config.yaml"):
        """
        Initialize analyzer
        
        Args:
            agent_path: Path to trained agent checkpoint
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize environment
        user_simulator = create_user_simulator("evening_person", self.config, seed=42)
        self.env = HabitReminderEnv(user_simulator, self.config)
        
        # Initialize and load agent
        state_dim = self.env.observation_space.shape[0]
        action_dim = self.env.action_space.n
        self.agent = DQNAgent(state_dim, action_dim, self.config)
        self.agent.load(agent_path)
        
        print(f"Loaded agent from {agent_path}")
    
    def analyze_time_preferences(self, num_episodes: int = 50) -> Dict:
        """
        Analyze which times the agent prefers to send reminders
        
        Returns:
            Dictionary with analysis results
        """
        hourly_actions = {hour: [] for hour in range(24)}
        hourly_rewards = {hour: [] for hour in range(24)}
        
        for episode in range(num_episodes):
            state, _ = self.env.reset()
            done = False
            steps = 0
            max_steps = 100
            
            while not done and steps < max_steps:
                hour = int(state[0])
                action = self.agent.select_action(state, training=False)
                
                hourly_actions[hour].append(action)
                
                next_state, reward, terminated, truncated, _ = self.env.step(action)
                done = terminated or truncated
                
                if action == Action.SEND_NOW:
                    hourly_rewards[hour].append(reward)
                
                state = next_state
                steps += 1
        
        # Calculate statistics
        send_now_by_hour = {}
        avg_reward_by_hour = {}
        
        for hour in range(24):
            if hourly_actions[hour]:
                send_now_count = sum(1 for a in hourly_actions[hour] if a == Action.SEND_NOW)
                send_now_by_hour[hour] = send_now_count / len(hourly_actions[hour])
            else:
                send_now_by_hour[hour] = 0
            
            if hourly_rewards[hour]:
                avg_reward_by_hour[hour] = np.mean(hourly_rewards[hour])
            else:
                avg_reward_by_hour[hour] = 0
        
        return {
            'send_now_by_hour': send_now_by_hour,
            'avg_reward_by_hour': avg_reward_by_hour,
            'hourly_actions': hourly_actions
        }
    
    def plot_hourly_preferences(self, save_path: str = None):
        """
        Plot agent's hourly reminder preferences
        
        Args:
            save_path: Optional path to save the plot
        """
        print("Analyzing hourly preferences...")
        results = self.analyze_time_preferences()
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10))
        
        # Plot 1: Probability of sending reminder by hour
        hours = list(range(24))
        send_probs = [results['send_now_by_hour'][h] for h in hours]
        
        ax1.bar(hours, send_probs, color='steelblue', alpha=0.7, edgecolor='navy')
        ax1.set_xlabel('Hour of Day', fontsize=12)
        ax1.set_ylabel('Probability of Sending Reminder', fontsize=12)
        ax1.set_title('Agent\'s Learned Reminder Timing Preferences', fontsize=14, fontweight='bold')
        ax1.set_xticks(hours)
        ax1.grid(True, alpha=0.3, axis='y')
        ax1.set_ylim([0, 1])
        
        # Highlight peak hours
        peak_hours = sorted(results['send_now_by_hour'].items(), key=lambda x: x[1], reverse=True)[:3]
        peak_hour_indices = [h for h, _ in peak_hours]
        for hour in peak_hour_indices:
            ax1.axvline(x=hour, color='red', linestyle='--', alpha=0.5, linewidth=2)
        
        # Plot 2: Average reward by hour (when reminder is sent)
        avg_rewards = [results['avg_reward_by_hour'][h] for h in hours]
        
        ax2.plot(hours, avg_rewards, marker='o', color='green', linewidth=2, markersize=6)
        ax2.set_xlabel('Hour of Day', fontsize=12)
        ax2.set_ylabel('Average Reward', fontsize=12)
        ax2.set_title('Average Reward When Reminder Sent By Hour', fontsize=14, fontweight='bold')
        ax2.set_xticks(hours)
        ax2.grid(True, alpha=0.3)
        ax2.axhline(y=0, color='black', linestyle='-', linewidth=0.5)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Plot saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
        
        # Print insights
        print("\n=== Hourly Preference Insights ===")
        print(f"Top 3 preferred hours for reminders:")
        for i, (hour, prob) in enumerate(peak_hours, 1):
            print(f"  {i}. Hour {hour}:00 - {prob*100:.1f}% of the time")
    
    def plot_q_value_heatmap(self, save_path: str = None):
        """
        Plot Q-values across different states
        
        Args:
            save_path: Optional path to save the plot
        """
        print("Generating Q-value heatmap...")
        
        # Create grid of states varying hour and streak
        hours = range(24)
        streaks = [0, 1, 3, 7, 14, 30]
        
        q_values_grid = np.zeros((len(streaks), len(hours), self.env.action_space.n))
        
        for i, streak in enumerate(streaks):
            for j, hour in enumerate(hours):
                # Create a typical state with varying hour and streak
                state = np.array([
                    hour,           # hour_of_day
                    3,              # day_of_week (Wednesday)
                    0,              # is_weekend
                    streak,         # current_streak
                    0.7,            # completion_rate_7d
                    18,             # avg_completion_hour
                    0,              # reminders_sent_today
                    0,              # reminders_ignored_today
                    24,             # time_since_last_reminder
                    0,              # completed_today
                    0.7,            # user_engagement_score
                    0,              # location (home)
                    0.6,            # phone_activity_last_hour
                    0,              # calendar_busy_next_2h
                    0.5,            # habit_difficulty
                ], dtype=np.float32)
                
                q_values = self.agent.get_q_values(state)
                q_values_grid[i, j, :] = q_values
        
        # Plot heatmap for "Send Now" action
        fig, axes = plt.subplots(2, 1, figsize=(16, 10))
        
        # Heatmap 1: Q-values for "Send Now" action
        send_now_values = q_values_grid[:, :, Action.SEND_NOW]
        
        sns.heatmap(
            send_now_values,
            ax=axes[0],
            xticklabels=hours,
            yticklabels=[f"{s} days" for s in streaks],
            cmap='RdYlGn',
            center=0,
            cbar_kws={'label': 'Q-Value'},
            annot=False,
            fmt='.1f'
        )
        axes[0].set_xlabel('Hour of Day', fontsize=12)
        axes[0].set_ylabel('Current Streak', fontsize=12)
        axes[0].set_title('Q-Values for "Send Reminder Now" Action', fontsize=14, fontweight='bold')
        
        # Heatmap 2: Best action by state
        best_actions = np.argmax(q_values_grid, axis=2)
        action_names = ['Send Now', 'Wait 30m', 'Wait 1h', 'Wait 2h', 'Skip']
        
        sns.heatmap(
            best_actions,
            ax=axes[1],
            xticklabels=hours,
            yticklabels=[f"{s} days" for s in streaks],
            cmap='viridis',
            cbar_kws={'label': 'Action', 'ticks': range(5)},
            annot=False
        )
        axes[1].set_xlabel('Hour of Day', fontsize=12)
        axes[1].set_ylabel('Current Streak', fontsize=12)
        axes[1].set_title('Best Action by Hour and Streak', fontsize=14, fontweight='bold')
        
        # Fix colorbar labels
        cbar = axes[1].collections[0].colorbar
        cbar.set_ticklabels(action_names)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"Heatmap saved to {save_path}")
        else:
            plt.show()
        
        plt.close()
    
    def simulate_day(self, verbose: bool = True) -> Dict:
        """
        Simulate a full day with the trained agent
        
        Args:
            verbose: Whether to print detailed information
            
        Returns:
            Dictionary with simulation results
        """
        state, _ = self.env.reset()
        
        timeline = []
        total_reward = 0
        completed = False
        
        if verbose:
            print("\n" + "=" * 60)
            print("Simulating a Day with Trained Agent")
            print("=" * 60 + "\n")
        
        step = 0
        done = False
        max_steps = 100
        
        while not done and step < max_steps:
            hour = state[0]
            streak = int(state[3])
            reminders_sent = int(state[6])
            completed_today = bool(state[9])
            
            # Get Q-values and action
            q_values = self.agent.get_q_values(state)
            action = self.agent.select_action(state, training=False)
            action_name = ['Send Now', 'Wait 30m', 'Wait 1h', 'Wait 2h', 'Skip'][action]
            
            if verbose:
                print(f"Step {step + 1} | Hour {hour:.1f} | Streak: {streak} days")
                print(f"  Action: {action_name}")
                print(f"  Q-values: {q_values}")
            
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            total_reward += reward
            
            if action == Action.SEND_NOW and info.get('reminder_sent'):
                response = info.get('response', 'N/A')
                if verbose:
                    print(f"  → Reminder sent! User response: {response}")
                    print(f"  → Reward: {reward:.2f}")
                
                if 'COMPLETED' in response:
                    completed = True
                
                timeline.append({
                    'hour': hour,
                    'action': action_name,
                    'response': response,
                    'reward': reward
                })
            
            if verbose and info.get('day_completed'):
                print(f"\n  --- Day Completed ---")
                print(f"  Habit completed: {completed}")
                print(f"  Total reminders sent: {reminders_sent}")
                print(f"  Day reward: {total_reward:.2f}\n")
            
            state = next_state
            step += 1
        
        return {
            'timeline': timeline,
            'total_reward': total_reward,
            'completed': completed,
            'steps': step
        }
    
    def compare_strategies(self, num_episodes: int = 100) -> Dict:
        """
        Compare RL agent against baseline strategies
        
        Args:
            num_episodes: Number of episodes to test each strategy
            
        Returns:
            Comparison results
        """
        print(f"\nComparing strategies over {num_episodes} episodes...")
        
        strategies = {
            'RL Agent': self._test_rl_agent,
            'Fixed 8 AM': lambda: self._test_fixed_time(8),
            'Fixed 6 PM': lambda: self._test_fixed_time(18),
            'Random': self._test_random
        }
        
        results = {}
        
        for name, strategy_fn in strategies.items():
            print(f"Testing {name}...")
            rewards, completions, streaks = [], [], []
            
            for _ in range(num_episodes):
                episode_result = strategy_fn()
                rewards.append(episode_result['reward'])
                completions.append(episode_result['completions'])
                streaks.append(episode_result['max_streak'])
            
            results[name] = {
                'avg_reward': np.mean(rewards),
                'avg_completions': np.mean(completions),
                'avg_streak': np.mean(streaks),
                'completion_rate': np.mean([c > 0 for c in completions])
            }
        
        # Print comparison table
        print("\n" + "=" * 80)
        print("Strategy Comparison Results")
        print("=" * 80)
        print(f"{'Strategy':<20} {'Avg Reward':<15} {'Avg Completions':<20} {'Avg Streak':<15}")
        print("-" * 80)
        
        for name, metrics in results.items():
            print(f"{name:<20} {metrics['avg_reward']:<15.2f} {metrics['avg_completions']:<20.2f} {metrics['avg_streak']:<15.2f}")
        
        print("=" * 80)
        
        return results
    
    def _test_rl_agent(self) -> Dict:
        """Test RL agent strategy"""
        state, _ = self.env.reset()
        total_reward = 0
        completions = 0
        max_streak = 0
        done = False
        steps = 0
        
        while not done and steps < 100:
            action = self.agent.select_action(state, training=False)
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            total_reward += reward
            if info.get('response') in ['COMPLETED_IMMEDIATE', 'COMPLETED_SOON', 'COMPLETED_LATER']:
                completions += 1
            
            max_streak = max(max_streak, int(next_state[3]))
            state = next_state
            steps += 1
        
        return {'reward': total_reward, 'completions': completions, 'max_streak': max_streak}
    
    def _test_fixed_time(self, target_hour: int) -> Dict:
        """Test fixed time strategy"""
        state, _ = self.env.reset()
        total_reward = 0
        completions = 0
        max_streak = 0
        done = False
        steps = 0
        sent_today = False
        
        while not done and steps < 100:
            hour = int(state[0])
            
            # Send reminder at target hour
            if hour >= target_hour and not sent_today and not state[9]:  # not completed_today
                action = Action.SEND_NOW
                sent_today = True
            else:
                action = Action.WAIT_1_HOUR
            
            # Reset daily flag
            if hour < target_hour:
                sent_today = False
            
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            total_reward += reward
            if info.get('response') in ['COMPLETED_IMMEDIATE', 'COMPLETED_SOON', 'COMPLETED_LATER']:
                completions += 1
            
            max_streak = max(max_streak, int(next_state[3]))
            state = next_state
            steps += 1
        
        return {'reward': total_reward, 'completions': completions, 'max_streak': max_streak}
    
    def _test_random(self) -> Dict:
        """Test random strategy"""
        state, _ = self.env.reset()
        total_reward = 0
        completions = 0
        max_streak = 0
        done = False
        steps = 0
        
        while not done and steps < 100:
            action = self.env.action_space.sample()
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            total_reward += reward
            if info.get('response') in ['COMPLETED_IMMEDIATE', 'COMPLETED_SOON', 'COMPLETED_LATER']:
                completions += 1
            
            max_streak = max(max_streak, int(next_state[3]))
            state = next_state
            steps += 1
        
        return {'reward': total_reward, 'completions': completions, 'max_streak': max_streak}


def main():
    """Main visualization function"""
    import os
    
    # Find the most recent model
    models_dir = "outputs/models"
    if not os.path.exists(models_dir):
        print(f"Error: Models directory not found: {models_dir}")
        print("Please train a model first using train.py")
        return
    
    # Look for final model or most recent checkpoint
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.pt')]
    if not model_files:
        print("Error: No trained models found")
        return
    
    if 'agent_final.pt' in model_files:
        model_path = os.path.join(models_dir, 'agent_final.pt')
    else:
        # Get most recent checkpoint
        model_path = os.path.join(models_dir, sorted(model_files)[-1])
    
    print(f"Using model: {model_path}\n")
    
    # Initialize analyzer
    analyzer = AgentAnalyzer(model_path)
    
    # Create visualizations
    plots_dir = "outputs/plots"
    os.makedirs(plots_dir, exist_ok=True)
    
    # Plot hourly preferences
    analyzer.plot_hourly_preferences(os.path.join(plots_dir, "hourly_preferences.png"))
    
    # Plot Q-value heatmap
    analyzer.plot_q_value_heatmap(os.path.join(plots_dir, "q_value_heatmap.png"))
    
    # Simulate a day
    analyzer.simulate_day(verbose=True)
    
    # Compare strategies
    analyzer.compare_strategies(num_episodes=50)
    
    print("\n✓ All visualizations generated successfully!")


if __name__ == "__main__":
    main()

