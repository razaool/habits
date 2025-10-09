"""Main habit tracking application"""

import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, List
from src.models import UserProfile, HabitCompletion
from src.profiler import HabitProfiler
from src.train import HabitModelTrainer
from src.apple_health import get_health_integration
import json


class HabitTrackerApp:
    """Main application for habit tracking"""
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.profile = HabitProfiler.load_profile(profile_name)
        self.real_data_dir = Path("data/real")
        self.real_data_dir.mkdir(parents=True, exist_ok=True)
        self.data_file = self.real_data_dir / f"{profile_name}_real.csv"
        
        # Apple Health integration
        self.health = get_health_integration(profile_name)
        if self.health.is_available():
            print(f"✅ Apple Health connected")
        else:
            print(f"ℹ️  Apple Health not available (using simulated health data)")
        
        # Try to load trained models
        try:
            self.trainer = HabitModelTrainer.load_models(profile_name)
            self.has_models = True
            print(f"✅ Loaded trained models for {profile_name}")
        except FileNotFoundError:
            self.trainer = None
            self.has_models = False
            print(f"ℹ️  No trained models yet - run training first")
    
    def run(self):
        """Run the main app loop"""
        print("\n" + "="*70)
        print(f"  🎯 AI HABIT COACH - {self.profile.name.upper()}")
        print("="*70)
        print(f"\n  Your habit: {self.profile.habit_description}")
        print(f"  Target: {self.profile.habit_target_duration} minutes daily")
        
        # Show stats
        self._show_stats()
        
        # Main menu
        while True:
            print("\n" + "-"*70)
            print("\nWhat would you like to do?")
            print("  1. Log today's habit")
            print("  2. View stats & insights")
            print("  3. Get AI recommendations")
            print("  4. Retrain models (with new data)")
            print("  5. View health data (Apple Health)")
            print("  6. Exit")
            
            choice = input("\n> ").strip()
            
            if choice == "1":
                self._log_completion()
            elif choice == "2":
                self._show_detailed_stats()
            elif choice == "3":
                self._show_recommendations()
            elif choice == "4":
                self._retrain_models()
            elif choice == "5":
                self._show_health_data()
            elif choice == "6":
                print("\n👋 Keep up the great work! See you tomorrow.")
                break
            else:
                print("  ⚠️  Invalid choice")
    
    def _log_completion(self):
        """Log a habit completion"""
        print("\n" + "="*70)
        print("  📝 LOG HABIT COMPLETION")
        print("="*70)
        
        # Get health data for context
        from datetime import date
        health_snapshot = self.health.get_comprehensive_health_snapshot(date.today())
        
        if health_snapshot['data_source'] == 'apple_health':
            print(f"\n📊 Your Apple Health data today:")
        else:
            print(f"\n📊 Your health context today (simulated):")
        
        print(f"  💤 Sleep Quality: {health_snapshot['sleep_quality']:.1f}/10")
        print(f"  ⚡ Energy Level: {health_snapshot['energy_level']:.1f}/10")
        print(f"  😰 Stress Level: {health_snapshot['stress_level']:.1f}/10")
        
        # Check if already logged today
        if self._has_logged_today():
            print("\n⚠️  You've already logged today! Do you want to update it?")
            update = input("(y/n) > ").strip().lower()
            if update != 'y':
                return
        
        # Did you complete it?
        print(f"\nDid you complete your habit today?")
        print(f"  ({self.profile.habit_description})")
        completed = input("(y/n) > ").strip().lower() == 'y'
        
        # Get details
        difficulty = None
        motivation = None
        duration = None
        context_notes = None
        
        if completed:
            difficulty = self._ask_rating("How difficult was it?", 1, 10)
            motivation = self._ask_rating("How motivated were you?", 1, 10)
            duration = int(input(f"\nHow long did it take? (minutes) [{self.profile.habit_target_duration}]\n> ").strip() 
                          or self.profile.habit_target_duration)
        else:
            print("\nWhy did you skip it? (optional)")
            context_notes = input("> ").strip() or None
        
        # Get current time info
        now = datetime.now()
        time_of_day = self._get_time_of_day(now.hour)
        day_of_week = now.strftime('%A').lower()
        
        # Create completion record
        completion = HabitCompletion(
            timestamp=now,
            completed=completed,
            difficulty_rating=difficulty,
            motivation_rating=motivation,
            duration_minutes=duration,
            context_notes=context_notes,
            time_of_day=time_of_day,
            day_of_week=day_of_week,
            reminder_sent=False
        )
        
        # Save
        self._save_completion(completion)
        
        if completed:
            print("\n🎉 Great job! Habit logged.")
            current_streak = self._get_current_streak()
            if current_streak > 0:
                print(f"   🔥 Current streak: {current_streak} days")
        else:
            print("\n✅ Logged. Tomorrow is a new day!")
        
        # Show AI insight if available
        if self.has_models:
            self._show_ai_insight(completion)
    
    def _save_completion(self, completion: HabitCompletion):
        """Save completion to data file"""
        # Load existing data
        if self.data_file.exists():
            df = pd.read_csv(self.data_file)
        else:
            df = pd.DataFrame()
        
        # Convert to row format matching simulator
        stats = self._get_current_stats()
        
        row = {
            'day_number': stats['total_days'],
            'day_of_week': completion.day_of_week,
            'time_attempted': completion.timestamp.strftime('%H:%M'),
            'completed': completion.completed,
            'difficulty': completion.difficulty_rating or 5,
            'motivation': completion.motivation_rating or 5,
            'sleep_quality': 7,  # Could ask for this
            'stress_level': 5,  # Could ask for this
            'social_obligations': False,  # Could infer
            'work_intensity': 5,  # Could ask for this
            'days_since_last': stats['days_since_last'],
            'current_streak': stats['current_streak'] if completion.completed else 0,
            'total_completions': stats['total_completions'] + (1 if completion.completed else 0),
        }
        
        # Remove today's entry if updating
        today_str = completion.timestamp.strftime('%Y-%m-%d')
        if not df.empty and 'timestamp' in df.columns:
            df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
            df = df[df['date'] != today_str]
            df = df.drop('date', axis=1)
        
        # Get health data
        from datetime import date
        health_snapshot = self.health.get_comprehensive_health_snapshot(date.today())
        
        # Add new row (using completion format)
        completion_dict = {
            'timestamp': completion.timestamp.isoformat(),
            'completed': completion.completed,
            'difficulty_rating': completion.difficulty_rating,
            'motivation_rating': completion.motivation_rating,
            'duration_minutes': completion.duration_minutes,
            'context_notes': completion.context_notes,
            'time_of_day': completion.time_of_day,
            'day_of_week': completion.day_of_week,
            'sleep_quality': health_snapshot['sleep_quality'],
            'stress_level': health_snapshot['stress_level'],
            'energy_level': health_snapshot['energy_level'],
            'health_data_source': health_snapshot['data_source'],
        }
        
        df = pd.concat([df, pd.DataFrame([completion_dict])], ignore_index=True)
        df.to_csv(self.data_file, index=False)
        
        # Also save in simulator format for training
        simulator_file = self.real_data_dir / f"{self.profile_name}_real.csv"
        if simulator_file.exists():
            df_sim = pd.read_csv(simulator_file)
        else:
            df_sim = pd.DataFrame()
        
        # Update row with actual health data
        row['sleep_quality'] = health_snapshot['sleep_quality']
        row['stress_level'] = health_snapshot['stress_level']
        row['work_intensity'] = 5  # Could ask user or infer
        
        df_sim = pd.concat([df_sim, pd.DataFrame([row])], ignore_index=True)
        df_sim.to_csv(simulator_file, index=False)
    
    def _has_logged_today(self) -> bool:
        """Check if already logged today"""
        if not self.data_file.exists():
            return False
        
        df = pd.read_csv(self.data_file)
        if df.empty or 'timestamp' not in df.columns:
            return False
        
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        today = datetime.now().date()
        
        return today in df['date'].values
    
    def _get_current_stats(self) -> dict:
        """Get current tracking stats"""
        if not self.data_file.exists():
            return {
                'total_days': 0,
                'total_completions': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'completion_rate': 0.0,
                'days_since_last': 0
            }
        
        df = pd.read_csv(self.data_file)
        if df.empty:
            return {
                'total_days': 0,
                'total_completions': 0,
                'current_streak': 0,
                'longest_streak': 0,
                'completion_rate': 0.0,
                'days_since_last': 0
            }
        
        df['date'] = pd.to_datetime(df['timestamp']).dt.date
        df = df.sort_values('date')
        
        total_days = len(df)
        total_completions = df['completed'].sum()
        completion_rate = total_completions / total_days if total_days > 0 else 0
        
        # Calculate current streak
        current_streak = 0
        for completed in reversed(df['completed'].tolist()):
            if completed:
                current_streak += 1
            else:
                break
        
        # Calculate longest streak
        longest_streak = 0
        temp_streak = 0
        for completed in df['completed']:
            if completed:
                temp_streak += 1
                longest_streak = max(longest_streak, temp_streak)
            else:
                temp_streak = 0
        
        # Days since last completion
        if total_completions > 0:
            last_completion = df[df['completed'] == True]['date'].max()
            days_since_last = (datetime.now().date() - last_completion).days
        else:
            days_since_last = total_days
        
        return {
            'total_days': total_days,
            'total_completions': total_completions,
            'current_streak': current_streak,
            'longest_streak': longest_streak,
            'completion_rate': completion_rate,
            'days_since_last': days_since_last
        }
    
    def _get_current_streak(self) -> int:
        """Get current streak"""
        return self._get_current_stats()['current_streak']
    
    def _show_stats(self):
        """Show quick stats"""
        stats = self._get_current_stats()
        
        print("\n" + "-"*70)
        print("  📊 YOUR PROGRESS")
        print("-"*70)
        print(f"  Total days tracked: {stats['total_days']}")
        print(f"  Completions: {stats['total_completions']}")
        print(f"  Success rate: {stats['completion_rate']:.1%}")
        print(f"  Current streak: 🔥 {stats['current_streak']} days")
        print(f"  Longest streak: 🏆 {stats['longest_streak']} days")
    
    def _show_detailed_stats(self):
        """Show detailed statistics"""
        print("\n" + "="*70)
        print("  📊 DETAILED STATISTICS")
        print("="*70)
        
        if not self.data_file.exists():
            print("\n  No data yet - start logging!")
            return
        
        df = pd.read_csv(self.data_file)
        if df.empty:
            print("\n  No data yet - start logging!")
            return
        
        stats = self._get_current_stats()
        
        print(f"\n  📈 Overall Performance:")
        print(f"     Total days: {stats['total_days']}")
        print(f"     Completions: {stats['total_completions']}")
        print(f"     Success rate: {stats['completion_rate']:.1%}")
        print(f"     Current streak: {stats['current_streak']} days")
        print(f"     Longest streak: {stats['longest_streak']} days")
        
        # Day of week analysis
        if 'day_of_week' in df.columns:
            print(f"\n  📅 By Day of Week:")
            dow_stats = df.groupby('day_of_week')['completed'].agg(['sum', 'count', 'mean'])
            days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
            for day in days_order:
                if day in dow_stats.index:
                    rate = dow_stats.loc[day, 'mean']
                    count = int(dow_stats.loc[day, 'count'])
                    print(f"     {day.capitalize()}: {rate:.1%} ({count} days)")
        
        # Difficulty and motivation
        if 'difficulty_rating' in df.columns:
            df_completed = df[df['completed'] == True]
            if not df_completed.empty:
                avg_diff = df_completed['difficulty_rating'].mean()
                avg_motiv = df_completed['motivation_rating'].mean()
                print(f"\n  💪 When You Succeed:")
                print(f"     Avg difficulty: {avg_diff:.1f}/10")
                print(f"     Avg motivation: {avg_motiv:.1f}/10")
    
    def _show_recommendations(self):
        """Show AI-powered recommendations"""
        print("\n" + "="*70)
        print("  🤖 AI RECOMMENDATIONS")
        print("="*70)
        
        if not self.has_models:
            print("\n  ⚠️  Models not trained yet. Run: python -m src.train")
            return
        
        now = datetime.now()
        today = now.strftime('%A').lower()
        
        # Optimal times for today
        print(f"\n  ⏰ Best times for today ({today.capitalize()}):")
        optimal_times = self.trainer.get_optimal_times(today, n_times=3)
        for hour, prob in optimal_times:
            print(f"     {hour:02d}:00 - {prob:.1%} predicted success")
        
        # Current context prediction
        stats = self._get_current_stats()
        current_features = {
            'day_of_week_encoded': self.trainer.day_encoder.transform([today])[0],
            'hour': now.hour,
            'is_morning': 6 <= now.hour < 12,
            'is_afternoon': 12 <= now.hour < 17,
            'is_evening': 17 <= now.hour < 22,
            'is_night': now.hour >= 22,
            'day_number': stats['total_days'],
            'current_streak': stats['current_streak'],
            'days_since_last': stats['days_since_last'],
            'total_completions': stats['total_completions'],
            'sleep_quality': 7,
            'stress_level': 5,
            'work_intensity': 5,
            'social_obligations_int': 0,
            'difficulty': 5,
            'motivation': 7,
            'streak_momentum': stats['current_streak'] * 7,
            'gap_penalty': stats['days_since_last'] * 5,
            'stress_workload': 25
        }
        
        current_prob = self.trainer.predict_completion_probability(current_features)
        
        print(f"\n  🎯 Right now ({now.strftime('%H:%M')}):")
        print(f"     Predicted success: {current_prob:.1%}")
        
        if current_prob > 0.7:
            print(f"     💚 Great time to do your habit!")
        elif current_prob > 0.5:
            print(f"     💛 Decent time, you can do this!")
        else:
            print(f"     🧡 Challenging time - maybe wait for optimal window?")
        
        # Insights based on patterns
        if stats['days_since_last'] > 2:
            print(f"\n  ⚠️  Warning: {stats['days_since_last']} days since last completion")
            print(f"     Getting back on track is crucial!")
        
        if stats['current_streak'] >= 7:
            print(f"\n  🔥 Amazing! You're on a {stats['current_streak']}-day streak!")
            print(f"     Keep the momentum going!")
    
    def _show_ai_insight(self, completion: HabitCompletion):
        """Show AI insight after logging"""
        if not self.has_models:
            return
        
        stats = self._get_current_stats()
        
        # Predict tomorrow's best time
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%A').lower()
        optimal_times = self.trainer.get_optimal_times(tomorrow, n_times=1)
        
        if optimal_times:
            hour, prob = optimal_times[0]
            print(f"\n💡 AI Tip: Tomorrow ({tomorrow}), try {hour:02d}:00 ({prob:.1%} success rate)")
    
    def _retrain_models(self):
        """Retrain models with latest data"""
        print("\n" + "="*70)
        print("  🔄 RETRAINING MODELS")
        print("="*70)
        
        trainer = HabitModelTrainer(self.profile_name)
        df = trainer.load_data()
        
        if df is None:
            print("\n❌ No data available")
            return
        
        print(f"\n📊 Training with {len(df)} data points...")
        X, y, weights = trainer.prepare_features(df)
        trainer.train_completion_model(X, y, weights)
        trainer.save_models()
        
        # Reload models
        self.trainer = HabitModelTrainer.load_models(self.profile_name)
        self.has_models = True
        
        print("\n✅ Models retrained successfully!")
    
    def _show_health_data(self):
        """Show Apple Health data"""
        print("\n" + "="*70)
        print("  🍎 APPLE HEALTH DATA")
        print("="*70)
        
        if not self.health.is_available():
            print("\n⚠️  Apple Health integration not yet implemented")
            print("\n📋 Current status: Using simulated health data")
            print("\n🔮 When implemented, you'll see:")
            print("  • Real sleep duration and quality from Apple Watch")
            print("  • Heart rate variability (stress indicator)")
            print("  • Activity levels and energy expenditure")
            print("  • Recovery scores")
            print("\n📖 See src/apple_health.py for implementation notes")
            print("\n💡 Three implementation options:")
            print("  1. Direct HealthKit API (macOS app)")
            print("  2. Parse exported Health data XML")
            print("  3. iOS Shortcuts automation (easiest!)")
        else:
            from datetime import date, timedelta
            
            print("\n📊 Health data for last 7 days:\n")
            
            for i in range(7):
                day = date.today() - timedelta(days=6-i)
                snapshot = self.health.get_comprehensive_health_snapshot(day)
                
                print(f"  {day.strftime('%a, %b %d')}:")
                print(f"    💤 Sleep: {snapshot['sleep_quality']:.1f}/10")
                print(f"    ⚡ Energy: {snapshot['energy_level']:.1f}/10")
                print(f"    😰 Stress: {snapshot['stress_level']:.1f}/10")
                print(f"    🔄 Recovery: {snapshot['recovery_score']:.1f}/10")
                print()
    
    @staticmethod
    def _get_time_of_day(hour: int) -> str:
        """Convert hour to time of day"""
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 22:
            return "evening"
        else:
            return "night"
    
    @staticmethod
    def _ask_rating(question: str, min_val: int, max_val: int) -> int:
        """Ask for a rating"""
        while True:
            try:
                answer = input(f"\n{question} [{min_val}-{max_val}]\n> ").strip()
                value = int(answer)
                if min_val <= value <= max_val:
                    return value
                print(f"  ⚠️  Please enter {min_val}-{max_val}")
            except ValueError:
                print(f"  ⚠️  Please enter a number")


def main():
    """Run the app"""
    import sys
    
    # Get profile name
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
    else:
        profile_name = input("\nEnter your profile name: ").strip()
    
    try:
        app = HabitTrackerApp(profile_name)
        app.run()
    except FileNotFoundError:
        print(f"\n❌ Profile not found: {profile_name}")
        print("\nRun profiling first: python -m src.profiler")


if __name__ == "__main__":
    main()
