"""
Custom Gymnasium Environment for Habit Reminder Timing

This environment simulates the interaction between a reminder system and a user.
The agent learns when to send reminders to maximize habit completion.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Dict, Tuple, Optional, Any
from enum import IntEnum


class Action(IntEnum):
    """Available actions for the reminder agent"""
    SEND_NOW = 0
    WAIT_30_MIN = 1
    WAIT_1_HOUR = 2
    WAIT_2_HOURS = 3
    SKIP_TODAY = 4


class UserResponse(IntEnum):
    """Possible user responses to reminders"""
    COMPLETED_IMMEDIATE = 0  # Within 30 minutes
    COMPLETED_SOON = 1       # Within 2 hours
    COMPLETED_LATER = 2      # Same day
    IGNORED = 3
    DISMISSED = 4
    SNOOZED = 5


class HabitReminderEnv(gym.Env):
    """
    Reinforcement Learning Environment for Adaptive Reminder Timing
    
    State Space:
        - hour_of_day (0-23)
        - day_of_week (0-6)
        - is_weekend (0-1)
        - current_streak (0-infinity)
        - completion_rate_7d (0-1)
        - avg_completion_hour (0-23)
        - reminders_sent_today (0-max_reminders)
        - reminders_ignored_today (0-max_reminders)
        - time_since_last_reminder (0-24, in hours)
        - completed_today (0-1)
        - user_engagement_score (0-1)
        - location (0-3: home, work, gym, other)
        - phone_activity_last_hour (0-1, normalized)
        - calendar_busy_next_2h (0-1)
        - habit_difficulty (0-1)
    
    Action Space:
        - 0: Send reminder now
        - 1: Wait 30 minutes
        - 2: Wait 1 hour
        - 3: Wait 2 hours
        - 4: Skip today (don't send more reminders)
    
    Reward:
        - Positive rewards for habit completion (higher if sooner)
        - Negative rewards for ignored/dismissed reminders
        - Bonuses for streak maintenance and efficiency
    """
    
    metadata = {'render_modes': ['human']}
    
    def __init__(self, user_simulator, config: Dict[str, Any]):
        super().__init__()
        
        self.user_simulator = user_simulator
        self.config = config
        self.max_reminders_per_day = config['environment']['max_reminders_per_day']
        self.rewards_config = config['rewards']
        
        # Define action space: 5 discrete actions
        self.action_space = spaces.Discrete(5)
        
        # Define observation space: 15 continuous features
        self.observation_space = spaces.Box(
            low=np.array([
                0,    # hour_of_day
                0,    # day_of_week
                0,    # is_weekend
                0,    # current_streak
                0,    # completion_rate_7d
                0,    # avg_completion_hour
                0,    # reminders_sent_today
                0,    # reminders_ignored_today
                0,    # time_since_last_reminder
                0,    # completed_today
                0,    # user_engagement_score
                0,    # location
                0,    # phone_activity_last_hour
                0,    # calendar_busy_next_2h
                0,    # habit_difficulty
            ], dtype=np.float32),
            high=np.array([
                23,   # hour_of_day
                6,    # day_of_week
                1,    # is_weekend
                365,  # current_streak (max 1 year)
                1,    # completion_rate_7d
                23,   # avg_completion_hour
                self.max_reminders_per_day,  # reminders_sent_today
                self.max_reminders_per_day,  # reminders_ignored_today
                24,   # time_since_last_reminder
                1,    # completed_today
                1,    # user_engagement_score
                3,    # location (4 categories: 0-3)
                1,    # phone_activity_last_hour
                1,    # calendar_busy_next_2h
                1,    # habit_difficulty
            ], dtype=np.float32),
            dtype=np.float32
        )
        
        # Episode tracking
        self.current_step = 0
        self.max_steps_per_episode = config['training']['max_steps_per_episode']
        
        # State variables
        self.current_day = 0
        self.current_hour = 0
        self.current_streak = 0
        self.completion_history = []  # Last 7 days
        self.reminders_sent_today = 0
        self.reminders_ignored_today = 0
        self.time_since_last_reminder = 24.0  # Hours
        self.completed_today = False
        self.avg_completion_hour = 12.0  # Default noon
        
        # Statistics
        self.total_completions = 0
        self.total_reminders_sent = 0
        
    def _get_observation(self) -> np.ndarray:
        """Construct the current state observation"""
        day_of_week = self.current_day % 7
        is_weekend = 1.0 if day_of_week >= 5 else 0.0
        
        # Calculate completion rate over last 7 days
        completion_rate_7d = np.mean(self.completion_history[-7:]) if self.completion_history else 0.5
        
        # Get context from user simulator
        context = self.user_simulator.get_context(self.current_hour, day_of_week)
        
        obs = np.array([
            self.current_hour,
            day_of_week,
            is_weekend,
            self.current_streak,
            completion_rate_7d,
            self.avg_completion_hour,
            self.reminders_sent_today,
            self.reminders_ignored_today,
            self.time_since_last_reminder,
            1.0 if self.completed_today else 0.0,
            context['engagement_score'],
            context['location'],
            context['phone_activity'],
            context['calendar_busy'],
            context['habit_difficulty'],
        ], dtype=np.float32)
        
        return obs
    
    def _calculate_reward(self, response: UserResponse) -> float:
        """Calculate reward based on user response"""
        reward = 0.0
        
        if response == UserResponse.COMPLETED_IMMEDIATE:
            reward += self.rewards_config['completion_immediate']
            # Streak bonus
            if self.current_streak >= 7:
                reward += self.rewards_config['streak_bonus']
                
        elif response == UserResponse.COMPLETED_SOON:
            reward += self.rewards_config['completion_soon']
            if self.current_streak >= 7:
                reward += self.rewards_config['streak_bonus']
                
        elif response == UserResponse.COMPLETED_LATER:
            reward += self.rewards_config['completion_later']
            if self.current_streak >= 7:
                reward += self.rewards_config['streak_bonus'] * 0.5
                
        elif response == UserResponse.IGNORED:
            reward += self.rewards_config['ignored']
            # Extra penalty for spamming
            if self.reminders_ignored_today >= 2:
                reward += self.rewards_config['spam_penalty']
                
        elif response == UserResponse.DISMISSED:
            reward += self.rewards_config['dismissed']
            if self.reminders_ignored_today >= 2:
                reward += self.rewards_config['spam_penalty']
                
        elif response == UserResponse.SNOOZED:
            reward += self.rewards_config['snoozed']
        
        # Efficiency bonus: no ignored reminders today
        if self.reminders_ignored_today == 0 and self.reminders_sent_today > 0:
            reward += self.rewards_config['efficiency_bonus']
        
        return reward
    
    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """Execute one step in the environment"""
        self.current_step += 1
        reward = 0.0
        terminated = False
        truncated = False
        info = {}
        
        # Handle action
        if action == Action.SEND_NOW:
            # Send reminder and get user response
            if self.reminders_sent_today < self.max_reminders_per_day and not self.completed_today:
                self.reminders_sent_today += 1
                self.total_reminders_sent += 1
                self.time_since_last_reminder = 0.0
                
                # Get user response from simulator
                day_of_week = self.current_day % 7
                response = self.user_simulator.respond_to_reminder(
                    self.current_hour,
                    day_of_week,
                    self.current_streak,
                    self.reminders_ignored_today
                )
                
                # Update state based on response
                if response in [UserResponse.COMPLETED_IMMEDIATE, 
                               UserResponse.COMPLETED_SOON, 
                               UserResponse.COMPLETED_LATER]:
                    self.completed_today = True
                    self.current_streak += 1
                    self.total_completions += 1
                    self.completion_history.append(1)
                    
                    # Update average completion hour
                    if self.total_completions > 0:
                        self.avg_completion_hour = (
                            self.avg_completion_hour * (self.total_completions - 1) + self.current_hour
                        ) / self.total_completions
                    
                elif response in [UserResponse.IGNORED, UserResponse.DISMISSED]:
                    self.reminders_ignored_today += 1
                
                reward = self._calculate_reward(response)
                info['response'] = response.name
                info['reminder_sent'] = True
            else:
                # Can't send more reminders or already completed
                reward = 0.0
                info['reminder_sent'] = False
                info['reason'] = 'already_completed' if self.completed_today else 'max_reminders_reached'
        
        elif action == Action.WAIT_30_MIN:
            self.current_hour += 0.5
            self.time_since_last_reminder += 0.5
            info['action'] = 'waited_30min'
            
        elif action == Action.WAIT_1_HOUR:
            self.current_hour += 1.0
            self.time_since_last_reminder += 1.0
            info['action'] = 'waited_1hour'
            
        elif action == Action.WAIT_2_HOURS:
            self.current_hour += 2.0
            self.time_since_last_reminder += 2.0
            info['action'] = 'waited_2hours'
            
        elif action == Action.SKIP_TODAY:
            # Skip to end of day
            self.current_hour = 23.5
            info['action'] = 'skipped_today'
        
        # Check if day is over (move to next day)
        if self.current_hour >= 24:
            # End of day processing
            if not self.completed_today:
                self.current_streak = 0  # Streak broken
                self.completion_history.append(0)
                reward -= 5.0  # Penalty for missed day
                info['streak_broken'] = True
            
            # Reset daily counters
            self.current_day += 1
            self.current_hour = np.random.randint(6, 10)  # Start next day between 6-10 AM
            self.reminders_sent_today = 0
            self.reminders_ignored_today = 0
            self.completed_today = False
            self.time_since_last_reminder = 24.0
            
            info['day_completed'] = True
        
        # Check termination conditions
        if self.current_step >= self.max_steps_per_episode:
            truncated = True
        
        # Get next observation
        observation = self._get_observation()
        
        return observation, reward, terminated, truncated, info
    
    def reset(self, seed: Optional[int] = None, options: Optional[Dict] = None) -> Tuple[np.ndarray, Dict]:
        """Reset the environment to initial state"""
        super().reset(seed=seed)
        
        # Reset episode tracking
        self.current_step = 0
        self.current_day = 0
        self.current_hour = np.random.randint(6, 10)  # Start between 6-10 AM
        
        # Reset state variables
        self.current_streak = 0
        self.completion_history = []
        self.reminders_sent_today = 0
        self.reminders_ignored_today = 0
        self.time_since_last_reminder = 24.0
        self.completed_today = False
        self.avg_completion_hour = 12.0
        
        # Reset statistics
        self.total_completions = 0
        self.total_reminders_sent = 0
        
        # Reset user simulator
        self.user_simulator.reset()
        
        observation = self._get_observation()
        info = {}
        
        return observation, info
    
    def render(self):
        """Render the environment state"""
        if self.render_mode == 'human':
            print(f"\n=== Day {self.current_day}, Hour {self.current_hour:.1f} ===")
            print(f"Streak: {self.current_streak} days")
            print(f"Completed today: {self.completed_today}")
            print(f"Reminders sent today: {self.reminders_sent_today}/{self.max_reminders_per_day}")
            print(f"Reminders ignored today: {self.reminders_ignored_today}")
            print(f"7-day completion rate: {np.mean(self.completion_history[-7:]) if self.completion_history else 0:.2%}")
            print(f"Total completions: {self.total_completions}")

