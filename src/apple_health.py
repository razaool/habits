"""Apple HealthKit Integration

This module provides integration with Apple Health data.

TODO: Implement actual HealthKit API calls
- Requires Mac with HealthKit access
- Need to handle permissions
- Parse XML export or use HealthKit API directly
"""

from datetime import datetime, date, timedelta
from typing import Optional, Dict, Any
from pathlib import Path
import json


class AppleHealthIntegration:
    """Integration with Apple Health / HealthKit"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cache_dir = Path("data/health_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if health data file exists in iCloud
        self.icloud_path = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/habit_coach/health_data.json"
        self.enabled = self.icloud_path.exists()
        
        if self.enabled:
            print(f"  ✅ Found Apple Health data at: {self.icloud_path}")
        else:
            print(f"  ℹ️  Apple Health file not found at: {self.icloud_path}")
        
    def is_available(self) -> bool:
        """Check if Apple Health data is available"""
        # TODO: Check if HealthKit is accessible
        # TODO: Check if user has granted permissions
        return self.enabled
    
    def get_sleep_data(self, target_date: date) -> Optional[Dict[str, Any]]:
        """
        Get sleep data for a specific date
        
        Returns:
            {
                'duration_hours': float,  # Total sleep duration
                'quality_score': float,   # 1-10 scale
                'deep_sleep_minutes': int,
                'rem_sleep_minutes': int,
                'awake_minutes': int,
                'bedtime': str,           # HH:MM
                'wake_time': str          # HH:MM
            }
        """
        if not self.is_available():
            return None
        
        try:
            with open(self.icloud_path, 'r') as f:
                health_data = json.load(f)
            
            # Parse the data from iOS Shortcuts
            sleep_hours = health_data.get('sleep_hours', 7.0)
            
            return {
                'duration_hours': sleep_hours,
                'quality_score': self._calculate_sleep_quality_from_hours(sleep_hours),
                'deep_sleep_minutes': 0,  # Could be added to shortcut
                'rem_sleep_minutes': 0,
                'awake_minutes': 0,
                'bedtime': '23:00',
                'wake_time': '07:00'
            }
        except Exception as e:
            print(f"  ⚠️  Error reading health data: {e}")
            return None
    
    def _calculate_sleep_quality_from_hours(self, hours: float) -> float:
        """Convert sleep hours to quality score"""
        if 7 <= hours <= 9:
            return 9.0
        elif 6 <= hours < 7:
            return 7.0
        elif 5 <= hours < 6:
            return 5.0
        elif hours < 5:
            return 3.0
        else:  # >9 hours
            return 6.0
    
    def get_activity_data(self, target_date: date) -> Optional[Dict[str, Any]]:
        """
        Get activity data for a specific date
        
        Returns:
            {
                'active_energy': int,      # Calories burned
                'steps': int,
                'exercise_minutes': int,
                'stand_hours': int,
                'energy_level': float      # 1-10 derived score
            }
        """
        if not self.is_available():
            return None
        
        try:
            with open(self.icloud_path, 'r') as f:
                health_data = json.load(f)
            
            active_energy = health_data.get('active_energy', 300)
            
            # Calculate energy level from activity
            energy_level = self._calculate_energy_from_activity(active_energy)
            
            return {
                'active_energy': active_energy,
                'steps': 0,  # Could add to shortcut
                'exercise_minutes': 0,
                'stand_hours': 0,
                'energy_level': energy_level
            }
        except Exception as e:
            print(f"  ⚠️  Error reading activity data: {e}")
            return None
    
    def _calculate_energy_from_activity(self, active_energy: int) -> float:
        """Calculate energy level from activity calories"""
        # More activity yesterday = less energy today (recovery)
        # 200-500 cal = optimal, >800 = tired next day
        if 200 <= active_energy <= 500:
            return 8.0
        elif active_energy > 800:
            return 5.0  # Tired from hard workout
        else:
            return 7.0
    
    def get_hrv_data(self, target_date: date) -> Optional[Dict[str, Any]]:
        """
        Get Heart Rate Variability (stress indicator)
        
        Returns:
            {
                'avg_hrv': float,          # milliseconds
                'stress_score': float,     # 1-10 (derived)
                'resting_hr': int          # bpm
            }
        """
        if not self.is_available():
            return None
        
        try:
            with open(self.icloud_path, 'r') as f:
                health_data = json.load(f)
            
            hrv = health_data.get('hrv', 50)
            resting_hr = health_data.get('resting_hr', 60)
            
            # Calculate stress from HRV (lower HRV = higher stress)
            stress = self._calculate_stress_from_hrv(hrv, resting_hr)
            
            return {
                'avg_hrv': hrv,
                'stress_score': stress,
                'resting_hr': resting_hr
            }
        except Exception as e:
            print(f"  ⚠️  Error reading HRV data: {e}")
            return None
    
    def _calculate_stress_from_hrv(self, hrv: float, resting_hr: int) -> float:
        """Calculate stress score from HRV and HR"""
        # Higher HRV = less stress, Lower resting HR = less stress
        # Typical HRV: 20-100ms
        hrv_score = min(10, max(1, hrv / 10))  # Normalize to 1-10
        hr_score = 10 - (resting_hr - 50) / 5  # Lower HR = better
        
        # Invert HRV score for stress (high HRV = low stress)
        stress = 10 - (hrv_score + hr_score) / 2
        return max(1, min(10, stress))
    
    def get_comprehensive_health_snapshot(self, target_date: date) -> Dict[str, Any]:
        """
        Get all health data for a specific date
        
        This combines sleep, activity, and HRV data into features
        suitable for the ML model.
        
        Returns:
            {
                'sleep_quality': float,     # 1-10
                'energy_level': float,      # 1-10
                'stress_level': float,      # 1-10
                'recovery_score': float,    # 1-10
                'data_source': str          # 'apple_health' or 'simulated'
            }
        """
        if not self.is_available():
            return self._get_simulated_data(target_date)
        
        # Get all data
        sleep = self.get_sleep_data(target_date)
        activity = self.get_activity_data(target_date)
        hrv = self.get_hrv_data(target_date)
        
        # Combine into ML features
        return {
            'sleep_quality': self._calculate_sleep_quality(sleep),
            'energy_level': self._calculate_energy_level(activity),
            'stress_level': self._calculate_stress_level(hrv),
            'recovery_score': self._calculate_recovery_score(sleep, hrv),
            'data_source': 'apple_health'
        }
    
    def _calculate_sleep_quality(self, sleep_data: Optional[Dict]) -> float:
        """Convert sleep data to 1-10 quality score"""
        if not sleep_data:
            return 7.0  # Default
        
        # TODO: Implement scoring algorithm
        # Consider: duration, deep sleep %, interruptions
        duration = sleep_data.get('duration_hours', 7)
        
        # Simple scoring: 7-9 hours is optimal
        if 7 <= duration <= 9:
            score = 9.0
        elif 6 <= duration < 7:
            score = 7.0
        elif 5 <= duration < 6:
            score = 5.0
        else:
            score = 3.0
        
        return min(10.0, max(1.0, score))
    
    def _calculate_energy_level(self, activity_data: Optional[Dict]) -> float:
        """Convert activity data to 1-10 energy score"""
        if not activity_data:
            return 7.0  # Default
        
        # TODO: Implement scoring algorithm
        # Higher activity yesterday = lower energy today
        # Moderate activity = optimal
        
        return 7.0
    
    def _calculate_stress_level(self, hrv_data: Optional[Dict]) -> float:
        """Convert HRV data to 1-10 stress score"""
        if not hrv_data:
            return 5.0  # Default
        
        # TODO: Implement scoring algorithm
        # Lower HRV = higher stress
        # Higher resting HR = higher stress
        
        return 5.0
    
    def _calculate_recovery_score(self, sleep_data: Optional[Dict], 
                                  hrv_data: Optional[Dict]) -> float:
        """Calculate overall recovery score (like Whoop/Oura)"""
        if not sleep_data or not hrv_data:
            return 7.0
        
        # TODO: Implement recovery algorithm
        # Combine sleep quality + HRV + resting HR
        
        return 7.0
    
    def _get_simulated_data(self, target_date: date) -> Dict[str, Any]:
        """Return simulated data when HealthKit not available"""
        import random
        random.seed(target_date.toordinal())  # Consistent per date
        
        return {
            'sleep_quality': random.uniform(5, 9),
            'energy_level': random.uniform(5, 9),
            'stress_level': random.uniform(3, 7),
            'recovery_score': random.uniform(6, 9),
            'data_source': 'simulated'
        }
    
    def export_health_data_to_csv(self, start_date: date, end_date: date, 
                                  output_file: Path):
        """
        Export health data for date range to CSV
        Useful for debugging and manual inspection
        """
        # TODO: Implement export
        pass
    
    def setup_permissions(self):
        """
        Request necessary HealthKit permissions
        
        Permissions needed:
        - Sleep Analysis
        - Heart Rate
        - Heart Rate Variability
        - Active Energy
        - Steps
        - Exercise Minutes
        """
        # TODO: Implement permission request
        print("⚠️  Apple Health integration not yet implemented")
        print("\nTo implement:")
        print("  1. Enable HealthKit in Xcode project")
        print("  2. Request permissions in Info.plist")
        print("  3. Use HealthKit APIs to query data")
        print("  4. Or parse exported health data XML")
        print("\nFor now, using simulated health data.")


def get_health_integration(user_id: str) -> AppleHealthIntegration:
    """Factory function to get health integration"""
    return AppleHealthIntegration(user_id)


# IMPLEMENTATION NOTES:
# 
# Option 1: Direct HealthKit API (macOS only)
# - Use PyObjC to access HealthKit framework
# - Requires macOS app with proper entitlements
# - Real-time access to health data
#
# Option 2: Export XML parsing
# - User exports health data from iPhone (Settings > Health > Export)
# - Parse the massive XML file
# - Less real-time but works without special permissions
#
# Option 3: Shortcuts Integration (easiest for MVP)
# - Create iOS Shortcut that logs data to file
# - Read file from iCloud/Dropbox
# - User runs shortcut daily
#
# RECOMMENDED: Start with Option 3 (Shortcuts)
# 
# Example Shortcut workflow:
# 1. Get sleep data from last night
# 2. Get HRV data from today
# 3. Append to CSV in iCloud
# 4. Python app reads CSV file
#
# This requires no special permissions and works immediately!


if __name__ == "__main__":
    """Test the health integration"""
    health = AppleHealthIntegration("test_user")
    
    print("Apple Health Integration Test")
    print("="*50)
    print(f"Available: {health.is_available()}")
    
    today = date.today()
    snapshot = health.get_comprehensive_health_snapshot(today)
    
    print(f"\nHealth data for {today}:")
    print(f"  Sleep Quality: {snapshot['sleep_quality']:.1f}/10")
    print(f"  Energy Level: {snapshot['energy_level']:.1f}/10")
    print(f"  Stress Level: {snapshot['stress_level']:.1f}/10")
    print(f"  Recovery Score: {snapshot['recovery_score']:.1f}/10")
    print(f"  Data Source: {snapshot['data_source']}")

