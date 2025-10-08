"""Behavioral simulator to generate synthetic training data"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from src.models import UserProfile, SimulatedDay
from src.profiler import HabitProfiler
import json


class BehaviorSimulator:
    """Simulates user behavior based on their profile"""
    
    def __init__(self, profile: UserProfile):
        self.profile = profile
        self.rng = np.random.RandomState(42)  # Reproducible randomness
        
        # Parse difficulty by day
        self.day_difficulty = {
            'monday': profile.monday_difficulty,
            'tuesday': profile.tuesday_difficulty,
            'wednesday': profile.wednesday_difficulty,
            'thursday': profile.thursday_difficulty,
            'friday': profile.friday_difficulty,
            'saturday': profile.saturday_difficulty,
            'sunday': profile.sunday_difficulty,
        }
    
    def simulate_days(self, num_days: int = 90) -> pd.DataFrame:
        """Simulate N days of behavior"""
        print(f"\n🔮 Simulating {num_days} days of behavior for {self.profile.name}...")
        
        simulated_days = []
        current_streak = 0
        total_completions = 0
        days_since_last = 0
        
        for day_num in range(num_days):
            # Determine day of week
            start_date = datetime.now()
            current_date = start_date + timedelta(days=day_num)
            day_of_week = current_date.strftime('%A').lower()
            
            # Simulate the day
            sim_day = self._simulate_single_day(
                day_num=day_num,
                day_of_week=day_of_week,
                current_streak=current_streak,
                total_completions=total_completions,
                days_since_last=days_since_last
            )
            
            # Update tracking variables
            if sim_day.completed:
                current_streak += 1
                total_completions += 1
                days_since_last = 0
            else:
                current_streak = 0
                days_since_last += 1
            
            simulated_days.append(sim_day)
        
        # Convert to DataFrame
        df = pd.DataFrame([day.model_dump() for day in simulated_days])
        
        print(f"  ✅ Generated {num_days} simulated days")
        print(f"  📊 Success rate: {df['completed'].mean():.1%}")
        print(f"  🔥 Max streak: {max(df['current_streak'])}")
        print(f"  📉 Avg difficulty: {df['difficulty'].mean():.1f}/10")
        
        return df
    
    def _simulate_single_day(
        self,
        day_num: int,
        day_of_week: str,
        current_streak: int,
        total_completions: int,
        days_since_last: int
    ) -> SimulatedDay:
        """Simulate a single day of behavior"""
        
        # Base difficulty from profile
        base_difficulty = self.day_difficulty[day_of_week]
        
        # Context factors (random with some patterns)
        sleep_quality = self._sample_sleep_quality()
        stress_level = self._sample_stress_level(day_of_week)
        social_obligations = self._has_social_obligations(day_of_week)
        work_intensity = self._sample_work_intensity(day_of_week)
        
        # Determine optimal time based on peak energy
        time_attempted = self._select_attempt_time()
        
        # Calculate actual difficulty considering all factors
        difficulty = self._calculate_difficulty(
            base_difficulty=base_difficulty,
            day_num=day_num,
            current_streak=current_streak,
            days_since_last=days_since_last,
            sleep_quality=sleep_quality,
            stress_level=stress_level,
            social_obligations=social_obligations,
            work_intensity=work_intensity,
            time_attempted=time_attempted
        )
        
        # Calculate motivation
        motivation = self._calculate_motivation(
            current_streak=current_streak,
            days_since_last=days_since_last,
            difficulty=difficulty,
            total_completions=total_completions
        )
        
        # Determine if completed (probability based on difficulty and motivation)
        completion_probability = self._calculate_completion_probability(
            difficulty=difficulty,
            motivation=motivation
        )
        completed = self.rng.random() < completion_probability
        
        return SimulatedDay(
            day_number=day_num,
            day_of_week=day_of_week,
            time_attempted=time_attempted,
            completed=completed,
            difficulty=difficulty,
            motivation=motivation,
            sleep_quality=sleep_quality,
            stress_level=stress_level,
            social_obligations=social_obligations,
            work_intensity=work_intensity,
            days_since_last=days_since_last,
            current_streak=current_streak,
            total_completions=total_completions
        )
    
    def _calculate_difficulty(
        self,
        base_difficulty: float,
        day_num: int,
        current_streak: int,
        days_since_last: int,
        sleep_quality: float,
        stress_level: float,
        social_obligations: bool,
        work_intensity: float,
        time_attempted: str
    ) -> float:
        """Calculate actual difficulty considering all factors"""
        
        difficulty = base_difficulty
        
        # Early days are harder (learning curve)
        if day_num < 14:
            difficulty += (14 - day_num) * 0.2
        
        # Long streaks make it easier (momentum)
        if current_streak > 7:
            difficulty -= min(2.0, current_streak * 0.1)
        
        # Gaps make it harder to restart
        if days_since_last > 3:
            difficulty += min(3.0, days_since_last * 0.3)
        
        # Poor sleep makes it harder
        if sleep_quality < 5:
            difficulty += (5 - sleep_quality) * 0.3
        
        # High stress impact based on profile
        if stress_level > 6:
            if self.profile.stress_response == "shutdown":
                difficulty += (stress_level - 6) * 0.5
            elif self.profile.stress_response == "adaptive":
                difficulty += (stress_level - 6) * 0.2
            # power_through types aren't affected as much
        
        # Social obligations
        if social_obligations and "social_events" in self.profile.typical_failure_triggers:
            difficulty += 1.5
        
        # High work intensity
        if work_intensity > 7 and "work_stress" in self.profile.typical_failure_triggers:
            difficulty += (work_intensity - 7) * 0.4
        
        # Time of day alignment with peak energy
        is_peak_time = any(self._time_in_period(time_attempted, period) 
                          for period in self.profile.peak_energy_times)
        if not is_peak_time:
            difficulty += 1.0
        
        # Distraction factor
        difficulty += (self.profile.distraction_prone - 5) * 0.1
        
        # Clamp to 1-10 range
        return max(1.0, min(10.0, difficulty))
    
    def _calculate_motivation(
        self,
        current_streak: int,
        days_since_last: int,
        difficulty: float,
        total_completions: int
    ) -> float:
        """Calculate motivation level"""
        
        # Base motivation from comfort with difficulty
        motivation = self.profile.comfort_with_difficulty
        
        # Streaks are motivating
        if current_streak > 0:
            motivation += min(3.0, current_streak * 0.2)
        
        # Missing days is demotivating
        if days_since_last > 2:
            motivation -= min(3.0, days_since_last * 0.3)
        
        # Early progress is exciting
        if total_completions < 30:
            motivation += 1.0
        
        # Milestone effects (data-driven people love milestones)
        if "seeing data/progress" in self.profile.motivation_style:
            if current_streak in [7, 14, 21, 30, 60, 90]:
                motivation += 2.0
        
        # If it seems too hard, motivation drops
        if difficulty > 8:
            motivation -= 1.5
        
        # Add some randomness
        motivation += self.rng.normal(0, 0.5)
        
        return max(1.0, min(10.0, motivation))
    
    def _calculate_completion_probability(
        self,
        difficulty: float,
        motivation: float
    ) -> float:
        """Convert difficulty and motivation into completion probability"""
        
        # Higher motivation and lower difficulty = higher probability
        # Use a sigmoid-like function
        score = motivation - difficulty
        
        # Base probability from score
        if score >= 4:
            prob = 0.95
        elif score >= 2:
            prob = 0.85
        elif score >= 0:
            prob = 0.70
        elif score >= -2:
            prob = 0.50
        elif score >= -4:
            prob = 0.30
        else:
            prob = 0.15
        
        # Past success matters
        if self.profile.longest_streak > 30:
            prob += 0.05  # They've proven they can do it
        
        # Add some randomness (life happens)
        prob += self.rng.normal(0, 0.05)
        
        return max(0.05, min(0.95, prob))
    
    def _sample_sleep_quality(self) -> float:
        """Sample sleep quality (1-10)"""
        # Most people have decent sleep, but occasional bad nights
        return np.clip(self.rng.normal(7, 1.5), 1, 10)
    
    def _sample_stress_level(self, day_of_week: str) -> float:
        """Sample stress level based on day"""
        # Weekdays typically more stressful
        if day_of_week in ['monday', 'tuesday', 'wednesday', 'thursday']:
            base_stress = 6
        elif day_of_week == 'friday':
            base_stress = 5
        else:  # weekend
            base_stress = 4
        
        return np.clip(self.rng.normal(base_stress, 1.5), 1, 10)
    
    def _has_social_obligations(self, day_of_week: str) -> bool:
        """Check if day has social obligations"""
        # More likely on weekends
        if day_of_week in ['friday', 'saturday']:
            return self.rng.random() < 0.4
        elif day_of_week == 'sunday':
            return self.rng.random() < 0.3
        else:
            return self.rng.random() < 0.15
    
    def _sample_work_intensity(self, day_of_week: str) -> float:
        """Sample work intensity"""
        if day_of_week in ['saturday', 'sunday']:
            return np.clip(self.rng.normal(3, 1), 1, 10)
        else:
            return np.clip(self.rng.normal(6, 1.5), 1, 10)
    
    def _select_attempt_time(self) -> str:
        """Select time to attempt habit based on peak energy"""
        # Convert peak energy periods to specific times
        time_options = []
        
        if "morning" in [p.split()[0] for p in self.profile.peak_energy_times]:
            time_options.extend(['07:00', '08:00', '09:00', '10:00'])
        if "afternoon" in [p.split()[0] for p in self.profile.peak_energy_times]:
            time_options.extend(['12:00', '13:00', '14:00', '15:00'])
        if "evening" in [p.split()[0] for p in self.profile.peak_energy_times]:
            time_options.extend(['17:00', '18:00', '19:00', '20:00'])
        if "night" in [p.split()[0] for p in self.profile.peak_energy_times]:
            time_options.extend(['21:00', '22:00', '23:00'])
        
        if not time_options:
            time_options = ['09:00', '12:00', '18:00']
        
        return self.rng.choice(time_options)
    
    def _time_in_period(self, time_str: str, period: str) -> bool:
        """Check if time falls in period"""
        hour = int(time_str.split(':')[0])
        period_lower = period.lower().split()[0]
        
        if period_lower == "morning":
            return 6 <= hour < 12
        elif period_lower == "afternoon":
            return 12 <= hour < 17
        elif period_lower == "evening":
            return 17 <= hour < 22
        elif period_lower == "night":
            return hour >= 22 or hour < 6
        return False
    
    def save_synthetic_data(self, df: pd.DataFrame, filename: str = None):
        """Save synthetic data to CSV"""
        synthetic_dir = Path("data/synthetic")
        synthetic_dir.mkdir(parents=True, exist_ok=True)
        
        if filename is None:
            filename = f"{self.profile.name.lower().replace(' ', '_')}_synthetic.csv"
        
        filepath = synthetic_dir / filename
        df.to_csv(filepath, index=False)
        
        print(f"\n💾 Saved synthetic data to: {filepath}")
        return filepath


def main():
    """Generate synthetic data from profile"""
    import sys
    
    print("\n" + "="*70)
    print("  🔮 BEHAVIORAL SIMULATOR")
    print("="*70)
    
    # Load profile
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
    else:
        profile_name = input("\nEnter profile name to simulate: ").strip()
    
    try:
        profile = HabitProfiler.load_profile(profile_name)
        print(f"\n✅ Loaded profile: {profile.name}")
        print(f"   Habit: {profile.habit_description}")
    except FileNotFoundError:
        print(f"\n❌ Profile not found: {profile_name}")
        print("\nAvailable profiles:")
        profiles_dir = Path("data/profiles")
        if profiles_dir.exists():
            for f in profiles_dir.glob("*.json"):
                print(f"  - {f.stem}")
        return
    
    # Generate synthetic data
    num_days = int(input("\nHow many days to simulate? [default: 90]: ").strip() or "90")
    
    simulator = BehaviorSimulator(profile)
    df = simulator.simulate_days(num_days)
    
    # Save
    simulator.save_synthetic_data(df)
    
    print("\n" + "="*70)
    print("  ✅ SIMULATION COMPLETE!")
    print("="*70)
    print("\nNext step: Train initial models")
    print("  python -m src.train")


if __name__ == "__main__":
    main()
