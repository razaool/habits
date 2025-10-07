"""
User Simulator for Habit Reminder System

Simulates realistic user behavior patterns for training the RL agent.
Different user types have different preferences and response patterns.
"""

import numpy as np
from typing import Dict, List, Tuple
from enum import IntEnum


class Location(IntEnum):
    """User location categories"""
    HOME = 0
    WORK = 1
    GYM = 2
    OTHER = 3


class UserResponse(IntEnum):
    """Possible user responses to reminders"""
    COMPLETED_IMMEDIATE = 0  # Within 30 minutes
    COMPLETED_SOON = 1       # Within 2 hours
    COMPLETED_LATER = 2      # Same day
    IGNORED = 3
    DISMISSED = 4
    SNOOZED = 5


class UserProfile:
    """Defines a user's behavior pattern"""
    
    def __init__(self, profile_config: Dict):
        self.preferred_hours = profile_config.get('preferred_hours', [18, 19, 20])
        self.base_completion_prob = profile_config.get('completion_prob', 0.7)
        self.weekend_boost = profile_config.get('weekend_boost', 0.0)
        self.streak_motivation = profile_config.get('streak_motivation', 0.1)
        self.fatigue_factor = profile_config.get('fatigue_factor', 0.15)
        self.context_sensitivity = profile_config.get('context_sensitivity', 0.2)
        
    def get_completion_probability(
        self,
        hour: int,
        day_of_week: int,
        streak: int,
        reminders_ignored: int,
        context: Dict
    ) -> float:
        """Calculate probability of completing habit given context"""
        
        # Base probability
        prob = self.base_completion_prob
        
        # Bonus for preferred hours
        if hour in self.preferred_hours:
            prob += 0.2
        # Penalty for non-preferred hours
        elif abs(hour - np.mean(self.preferred_hours)) > 4:
            prob -= 0.2
        
        # Weekend effect
        if day_of_week >= 5:  # Weekend
            prob += self.weekend_boost
        
        # Streak motivation (more likely to continue streak)
        if streak > 0:
            prob += min(streak * self.streak_motivation, 0.3)
        
        # Fatigue from too many reminders
        if reminders_ignored > 0:
            prob -= reminders_ignored * self.fatigue_factor
        
        # Context effects
        if context['location'] == Location.GYM and context['habit_type'] == 'exercise':
            prob += 0.3  # Very likely at gym for exercise habit
        elif context['location'] == Location.WORK:
            prob -= 0.15  # Less likely at work
        
        if context['calendar_busy']:
            prob -= 0.2  # Less likely when busy
        
        if context['phone_activity'] > 0.7:
            prob += 0.1  # More likely to see and respond to reminder
        
        # Clamp to [0, 1]
        return np.clip(prob, 0.0, 1.0)


class UserSimulator:
    """
    Simulates a user's response to habit reminders.
    Can be configured with different personality profiles.
    """
    
    def __init__(self, profile_type: str = "evening_person", config: Dict = None):
        """
        Initialize user simulator with a specific profile
        
        Args:
            profile_type: One of ["morning_person", "evening_person", 
                                  "weekend_warrior", "inconsistent"]
            config: Configuration dictionary with user profiles
        """
        self.profile_type = profile_type
        self.config = config or {}
        
        # Load profile configuration
        user_profiles = self.config.get('user_profiles', {})
        profile_config = user_profiles.get(profile_type, {
            'preferred_hours': [18, 19, 20],
            'completion_prob': 0.7
        })
        
        self.profile = UserProfile(profile_config)
        self.habit_type = "exercise"  # Default habit type
        
        # Internal state
        self.current_energy = 1.0
        self.current_mood = 0.7
        self.life_events = []  # Random life events that affect behavior
        
        # Randomness
        self.rng = np.random.RandomState()
    
    def reset(self):
        """Reset simulator state"""
        self.current_energy = 1.0
        self.current_mood = 0.7
        self.life_events = []
    
    def seed(self, seed: int):
        """Set random seed for reproducibility"""
        self.rng = np.random.RandomState(seed)
    
    def get_context(self, hour: int, day_of_week: int) -> Dict:
        """
        Generate context information for current time
        
        Returns:
            Dictionary with context features
        """
        # Simulate location based on time and day
        location = self._simulate_location(hour, day_of_week)
        
        # Simulate phone activity (higher during certain hours)
        phone_activity = self._simulate_phone_activity(hour)
        
        # Simulate calendar busy status
        calendar_busy = self._simulate_calendar_busy(hour, day_of_week)
        
        # Engagement score (composite of energy and mood)
        engagement_score = (self.current_energy * 0.6 + self.current_mood * 0.4)
        
        # Add some noise to engagement
        engagement_score += self.rng.normal(0, 0.1)
        engagement_score = np.clip(engagement_score, 0, 1)
        
        return {
            'location': location,
            'phone_activity': phone_activity,
            'calendar_busy': 1.0 if calendar_busy else 0.0,
            'engagement_score': engagement_score,
            'habit_difficulty': 0.5,  # Could be personalized
            'habit_type': self.habit_type,
        }
    
    def _simulate_location(self, hour: int, day_of_week: int) -> Location:
        """Simulate user location based on time"""
        if day_of_week < 5:  # Weekday
            if 9 <= hour < 17:
                return Location.WORK if self.rng.random() < 0.8 else Location.OTHER
            elif 17 <= hour < 19:
                return Location.GYM if self.rng.random() < 0.3 else Location.HOME
            else:
                return Location.HOME if self.rng.random() < 0.7 else Location.OTHER
        else:  # Weekend
            if 6 <= hour < 12:
                return Location.HOME if self.rng.random() < 0.8 else Location.OTHER
            elif 12 <= hour < 18:
                return Location.GYM if self.rng.random() < 0.2 else Location.OTHER
            else:
                return Location.HOME if self.rng.random() < 0.6 else Location.OTHER
    
    def _simulate_phone_activity(self, hour: int) -> float:
        """Simulate phone activity level"""
        # Higher activity during certain hours
        if 7 <= hour <= 9:  # Morning
            base_activity = 0.6
        elif 12 <= hour <= 14:  # Lunch
            base_activity = 0.7
        elif 17 <= hour <= 22:  # Evening
            base_activity = 0.8
        elif 0 <= hour <= 6:  # Night
            base_activity = 0.1
        else:
            base_activity = 0.5
        
        # Add noise
        activity = base_activity + self.rng.normal(0, 0.15)
        return np.clip(activity, 0, 1)
    
    def _simulate_calendar_busy(self, hour: int, day_of_week: int) -> bool:
        """Simulate whether calendar shows busy status"""
        if day_of_week < 5:  # Weekday
            if 9 <= hour < 17:
                return self.rng.random() < 0.6  # 60% chance busy during work
            elif 18 <= hour < 20:
                return self.rng.random() < 0.3  # 30% chance evening plans
        else:  # Weekend
            if 10 <= hour < 14:
                return self.rng.random() < 0.4  # 40% chance weekend plans
        
        return False
    
    def respond_to_reminder(
        self,
        hour: int,
        day_of_week: int,
        streak: int,
        reminders_ignored: int
    ) -> UserResponse:
        """
        Simulate user's response to a reminder
        
        Args:
            hour: Current hour (0-23)
            day_of_week: Day of week (0-6)
            streak: Current habit streak
            reminders_ignored: Number of reminders ignored today
            
        Returns:
            UserResponse enum value
        """
        context = self.get_context(hour, day_of_week)
        
        # Calculate completion probability
        completion_prob = self.profile.get_completion_probability(
            hour, day_of_week, streak, reminders_ignored, context
        )
        
        # Decide whether to complete
        if self.rng.random() < completion_prob:
            # Decide when to complete
            urgency = self.rng.random()
            if urgency < 0.4:
                return UserResponse.COMPLETED_IMMEDIATE
            elif urgency < 0.75:
                return UserResponse.COMPLETED_SOON
            else:
                return UserResponse.COMPLETED_LATER
        else:
            # Decide type of non-completion
            if reminders_ignored >= 2:
                # More likely to dismiss if already ignored multiple
                return UserResponse.DISMISSED if self.rng.random() < 0.6 else UserResponse.IGNORED
            
            # Check if might snooze
            if context['calendar_busy'] and self.rng.random() < 0.3:
                return UserResponse.SNOOZED
            
            # Default: ignore
            return UserResponse.IGNORED if self.rng.random() < 0.7 else UserResponse.DISMISSED
    
    def update_internal_state(self):
        """Update internal state variables (energy, mood) over time"""
        # Energy decreases slightly throughout the day, resets at night
        self.current_energy *= 0.98
        self.current_energy = max(0.3, self.current_energy)
        
        # Mood fluctuates
        self.current_mood += self.rng.normal(0, 0.05)
        self.current_mood = np.clip(self.current_mood, 0.2, 1.0)


def create_user_simulator(profile_type: str, config: Dict, seed: int = None) -> UserSimulator:
    """
    Factory function to create user simulators
    
    Args:
        profile_type: Type of user profile
        config: Configuration dictionary
        seed: Random seed for reproducibility
        
    Returns:
        UserSimulator instance
    """
    simulator = UserSimulator(profile_type, config)
    if seed is not None:
        simulator.seed(seed)
    return simulator

