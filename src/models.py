"""Data models for the habit coach system"""

from datetime import datetime, time
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User behavioral profile for habit formation"""
    
    # Basic info
    name: str
    habit_description: str
    habit_target_duration: int  # minutes
    habit_target_frequency: str = "daily"  # daily, weekday, etc.
    
    # Schedule & Routine
    wake_time: str  # HH:MM format
    sleep_time: str  # HH:MM format
    work_schedule: str  # e.g., "9-5 weekdays", "flexible", "shift-work"
    peak_energy_times: List[str]  # ["morning", "afternoon", "evening", "night"]
    
    # Behavioral patterns
    personality_type: str  # "morning_person", "night_owl", "flexible"
    motivation_style: List[str]  # ["data_driven", "encouragement", "accountability", "guilt", "rewards"]
    distraction_prone: int = Field(ge=1, le=10)  # 1-10 scale
    stress_response: str  # "shutdown", "power_through", "adaptive"
    
    # Past habit attempts
    past_habit_successes: List[str] = []
    past_habit_failures: List[str] = []
    longest_streak: int = 0  # days
    typical_failure_triggers: List[str] = []  # ["weekends", "work_stress", "social_events", "travel"]
    
    # Environmental context
    typical_environment: str  # "home", "office", "gym", "outdoor"
    social_support: bool
    has_accountability_partner: bool
    
    # Preferences
    reminder_style: str = "gentle"  # "gentle", "firm", "data_focused", "motivational"
    comfort_with_difficulty: int = Field(ge=1, le=10)  # how much challenge they want
    
    # Days of week patterns (1-10 difficulty rating for completing habits)
    monday_difficulty: Optional[int] = Field(default=5, ge=1, le=10)
    tuesday_difficulty: Optional[int] = Field(default=5, ge=1, le=10)
    wednesday_difficulty: Optional[int] = Field(default=5, ge=1, le=10)
    thursday_difficulty: Optional[int] = Field(default=5, ge=1, le=10)
    friday_difficulty: Optional[int] = Field(default=5, ge=1, le=10)
    saturday_difficulty: Optional[int] = Field(default=5, ge=1, le=10)
    sunday_difficulty: Optional[int] = Field(default=5, ge=1, le=10)
    
    # Metadata
    created_at: datetime = Field(default_factory=datetime.now)


class HabitCompletion(BaseModel):
    """Record of a single habit completion or skip"""
    
    timestamp: datetime
    completed: bool
    difficulty_rating: Optional[int] = Field(default=None, ge=1, le=10)
    motivation_rating: Optional[int] = Field(default=None, ge=1, le=10)
    duration_minutes: Optional[int] = None
    context_notes: Optional[str] = None
    
    # Context at time of attempt
    time_of_day: str  # "morning", "afternoon", "evening", "night"
    day_of_week: str
    location: Optional[str] = None
    
    # What intervention was used
    reminder_sent: bool = False
    reminder_type: Optional[str] = None
    message_shown: Optional[str] = None


class SimulatedDay(BaseModel):
    """A simulated day of behavior for training"""
    
    day_number: int  # Day in the habit journey
    day_of_week: str
    time_attempted: str  # HH:MM
    completed: bool
    difficulty: float  # 1-10
    motivation: float  # 1-10
    
    # Context factors
    sleep_quality: float  # 1-10
    stress_level: float  # 1-10
    social_obligations: bool
    work_intensity: float  # 1-10
    
    # Derived from profile
    days_since_last: int
    current_streak: int
    total_completions: int
