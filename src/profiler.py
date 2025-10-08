"""Interactive profiling system to understand user behavior"""

import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from src.models import UserProfile


class HabitProfiler:
    """Interactive questionnaire to build user behavioral profile"""
    
    def __init__(self):
        self.profile_data = {}
        self.profiles_dir = Path("data/profiles")
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
    
    def run_interactive_profiling(self) -> UserProfile:
        """Run the interactive profiling session"""
        print("\n" + "="*70)
        print("  🎯 AI HABIT COACH - BEHAVIORAL PROFILING")
        print("="*70)
        print("\nThis questionnaire helps me understand YOUR unique patterns")
        print("so I can build a personalized model of your behavior.\n")
        print("Be honest - there are no wrong answers!\n")
        
        # Basic info
        print("\n--- BASIC INFORMATION ---\n")
        self.profile_data['name'] = self._ask("What's your name?")
        self.profile_data['habit_description'] = self._ask(
            "What's the ONE habit you want to master?\n"
            "  (e.g., 'meditate 20 minutes', 'run 3 miles', 'write 500 words')"
        )
        self.profile_data['habit_target_duration'] = self._ask_int(
            "How many minutes should this take daily?", 1, 300
        )
        
        # Schedule & Routine
        print("\n--- YOUR DAILY RHYTHM ---\n")
        self.profile_data['wake_time'] = self._ask_time("What time do you typically wake up?")
        self.profile_data['sleep_time'] = self._ask_time("What time do you typically go to sleep?")
        self.profile_data['work_schedule'] = self._ask(
            "Describe your work schedule\n"
            "  (e.g., '9-5 weekdays', 'flexible remote', 'shift work', 'student')"
        )
        
        print("\nWhen is your energy highest? (select all that apply)")
        self.profile_data['peak_energy_times'] = self._ask_multiple_choice(
            ["morning (6am-12pm)", "afternoon (12pm-5pm)", "evening (5pm-10pm)", "night (10pm-2am)"]
        )
        
        # Personality & Motivation
        print("\n--- PERSONALITY & MOTIVATION ---\n")
        self.profile_data['personality_type'] = self._ask_choice(
            "Are you a...",
            ["morning_person", "night_owl", "flexible"]
        )
        
        print("\nWhat motivates you? (select all that apply)")
        self.profile_data['motivation_style'] = self._ask_multiple_choice([
            "seeing data/progress",
            "encouragement & positivity",
            "accountability to others",
            "fear of loss/guilt",
            "rewards & gamification"
        ])
        
        self.profile_data['distraction_prone'] = self._ask_int(
            "How easily distracted are you? (1=laser focused, 10=squirrel!)", 1, 10
        )
        
        self.profile_data['stress_response'] = self._ask_choice(
            "When stressed, you tend to...",
            ["shutdown (skip habits)", "power_through (force habits)", "adaptive (adjust habits)"]
        )
        
        # Past patterns
        print("\n--- PAST HABIT PATTERNS ---\n")
        successes = self._ask(
            "List habits you've successfully built in the past (comma separated)\n"
            "  (leave blank if none)"
        )
        self.profile_data['past_habit_successes'] = [s.strip() for s in successes.split(",")] if successes else []
        
        failures = self._ask(
            "List habits you tried but failed to maintain (comma separated)\n"
            "  (leave blank if none)"
        )
        self.profile_data['past_habit_failures'] = [f.strip() for f in failures.split(",")] if failures else []
        
        self.profile_data['longest_streak'] = self._ask_int(
            "What's the longest you've maintained a daily habit? (days)", 0, 3650
        )
        
        print("\nWhat typically causes you to break habits? (select all that apply)")
        self.profile_data['typical_failure_triggers'] = self._ask_multiple_choice([
            "weekends",
            "work stress",
            "social events",
            "travel",
            "illness",
            "boredom",
            "lack of immediate results"
        ])
        
        # Environment
        print("\n--- ENVIRONMENT & SUPPORT ---\n")
        self.profile_data['typical_environment'] = self._ask_choice(
            "Where will you usually do this habit?",
            ["home", "office", "gym", "outdoor", "varies"]
        )
        
        self.profile_data['social_support'] = self._ask_yes_no(
            "Do you have friends/family who support your habit goals?"
        )
        
        self.profile_data['has_accountability_partner'] = self._ask_yes_no(
            "Do you have an accountability partner?"
        )
        
        # Preferences
        print("\n--- YOUR PREFERENCES ---\n")
        self.profile_data['reminder_style'] = self._ask_choice(
            "What reminder style do you prefer?",
            ["gentle (soft nudges)", "firm (you need to do this)", 
             "data_focused (here's your stats)", "motivational (you've got this!)"]
        )
        
        self.profile_data['comfort_with_difficulty'] = self._ask_int(
            "How much challenge do you want? (1=super easy, 10=push me hard)", 1, 10
        )
        
        # Day-of-week patterns
        print("\n--- WEEKLY PATTERNS ---\n")
        print("Rate how difficult it typically is to maintain habits on each day")
        print("  (1=super easy, 10=nearly impossible)\n")
        
        for day in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']:
            self.profile_data[f'{day}_difficulty'] = self._ask_int(
                f"  {day.capitalize()}", 1, 10
            )
        
        # Build and validate profile
        self.profile_data['habit_target_frequency'] = 'daily'
        self.profile_data['created_at'] = datetime.now()
        
        profile = UserProfile(**self.profile_data)
        
        # Save profile
        self._save_profile(profile)
        
        print("\n" + "="*70)
        print("  ✅ PROFILE COMPLETE!")
        print("="*70)
        filename = profile.name.lower().replace(' ', '_') + '.json'
        print(f"\nProfile saved to: {self.profiles_dir / filename}")
        print("\nNext step: Run the simulator to generate training data")
        print("  python -m src.simulator")
        
        return profile
    
    def _ask(self, question: str) -> str:
        """Ask a free-form question"""
        while True:
            answer = input(f"\n{question}\n> ").strip()
            if answer:
                return answer
            print("  ⚠️  Please provide an answer")
    
    def _ask_int(self, question: str, min_val: int, max_val: int) -> int:
        """Ask for an integer within range"""
        while True:
            try:
                answer = input(f"\n{question} [{min_val}-{max_val}]\n> ").strip()
                value = int(answer)
                if min_val <= value <= max_val:
                    return value
                print(f"  ⚠️  Please enter a number between {min_val} and {max_val}")
            except ValueError:
                print(f"  ⚠️  Please enter a valid number")
    
    def _ask_time(self, question: str) -> str:
        """Ask for time in HH:MM format"""
        while True:
            answer = input(f"\n{question} (HH:MM format, e.g., 07:30)\n> ").strip()
            try:
                # Validate time format
                parts = answer.split(':')
                if len(parts) == 2:
                    hour, minute = int(parts[0]), int(parts[1])
                    if 0 <= hour <= 23 and 0 <= minute <= 59:
                        return f"{hour:02d}:{minute:02d}"
                print("  ⚠️  Please use HH:MM format (e.g., 07:30)")
            except ValueError:
                print("  ⚠️  Please use HH:MM format (e.g., 07:30)")
    
    def _ask_choice(self, question: str, choices: List[str]) -> str:
        """Ask user to pick one option"""
        print(f"\n{question}")
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            try:
                answer = input("> ").strip()
                idx = int(answer) - 1
                if 0 <= idx < len(choices):
                    # Clean up the choice (remove parenthetical explanations)
                    return choices[idx].split(' (')[0]
                print(f"  ⚠️  Please enter a number between 1 and {len(choices)}")
            except ValueError:
                print(f"  ⚠️  Please enter a valid number")
    
    def _ask_multiple_choice(self, choices: List[str]) -> List[str]:
        """Ask user to pick multiple options"""
        for i, choice in enumerate(choices, 1):
            print(f"  {i}. {choice}")
        
        while True:
            answer = input("Enter numbers separated by commas (e.g., 1,3,4) or 'none'\n> ").strip()
            if answer.lower() == 'none':
                return []
            
            try:
                indices = [int(x.strip()) - 1 for x in answer.split(',')]
                if all(0 <= idx < len(choices) for idx in indices):
                    # Clean up choices
                    return [choices[idx].split(' (')[0] for idx in indices]
                print(f"  ⚠️  Please enter numbers between 1 and {len(choices)}")
            except ValueError:
                print(f"  ⚠️  Please enter valid numbers separated by commas")
    
    def _ask_yes_no(self, question: str) -> bool:
        """Ask a yes/no question"""
        while True:
            answer = input(f"\n{question} (y/n)\n> ").strip().lower()
            if answer in ['y', 'yes']:
                return True
            elif answer in ['n', 'no']:
                return False
            print("  ⚠️  Please enter 'y' or 'n'")
    
    def _save_profile(self, profile: UserProfile):
        """Save profile to JSON"""
        name_clean = profile.name.lower().replace(' ', '_')
        filename = f"{name_clean}.json"
        filepath = self.profiles_dir / filename
        
        with open(filepath, 'w') as f:
            json.dump(profile.model_dump(mode='json'), f, indent=2, default=str)
    
    @staticmethod
    def load_profile(name: str) -> UserProfile:
        """Load a profile from file"""
        profiles_dir = Path("data/profiles")
        name_clean = name.lower().replace(' ', '_')
        filename = f"{name_clean}.json"
        filepath = profiles_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Profile not found: {filepath}")
        
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        return UserProfile(**data)


def main():
    """Run the profiler"""
    profiler = HabitProfiler()
    profile = profiler.run_interactive_profiling()
    
    print("\n📊 Your profile summary:")
    print(f"  Name: {profile.name}")
    print(f"  Habit: {profile.habit_description}")
    print(f"  Duration: {profile.habit_target_duration} minutes")
    print(f"  Peak energy: {', '.join(profile.peak_energy_times)}")
    print(f"  Motivation: {', '.join(profile.motivation_style)}")
    print(f"  Past successes: {len(profile.past_habit_successes)}")
    print(f"  Longest streak: {profile.longest_streak} days")


if __name__ == "__main__":
    main()
