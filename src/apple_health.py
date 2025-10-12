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
import re


class AppleHealthIntegration:
    """Integration with Apple Health / HealthKit"""
    
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.cache_dir = Path("data/health_cache")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Check if health data file exists in iCloud
        self.icloud_dir = Path.home() / "Library/Mobile Documents/com~apple~CloudDocs/habit_coach"
        self.icloud_path = self.icloud_dir / "health_data.json"
        
        # Check for any health data files (JSON or TXT from shortcut)
        self.enabled = self.icloud_path.exists() or (self.icloud_dir.exists() and any(self.icloud_dir.glob('*.txt')))
        
        if self.enabled:
            print(f"  ✅ Found Apple Health data at: {self.icloud_dir}")
        else:
            print(f"  ℹ️  Apple Health file not found at: {self.icloud_dir}")
        
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
            # Find the text file that matches the target date
            txt_files = list(self.icloud_dir.glob('*.txt'))
            
            for txt_file in txt_files:
                # Read first line to check date
                with open(txt_file, 'r') as f:
                    first_line = f.readline().strip()
                
                # Parse date from format: "9 Oct 2025 at 1:49 am-9 Oct 2025 at 8:56 am"
                if ' at ' in first_line and '-' in first_line:
                    # Extract the date part (wake up date is what matters)
                    wake_part = first_line.split('-')[1].strip()
                    date_str = wake_part.split(' at ')[0].strip()
                    
                    # Parse date (format: "9 Oct 2025")
                    try:
                        from datetime import datetime
                        file_date = datetime.strptime(date_str, '%d %b %Y').date()
                        
                        # Match with target date
                        if file_date == target_date:
                            parsed_data = self._parse_sleep_text_file(txt_file)
                            if parsed_data:
                                sleep_hours = parsed_data.get('total_hours', 7.0)
                                sleep_dict = {
                                    'duration_hours': sleep_hours,
                                    'deep_sleep_minutes': parsed_data.get('deep_minutes', 0),
                                    'rem_sleep_minutes': parsed_data.get('rem_minutes', 0),
                                    'awake_minutes': parsed_data.get('awake_minutes', 0),
                                    'bedtime': parsed_data.get('bedtime_str', '23:00'),
                                    'wake_time': parsed_data.get('waketime_str', '07:00')
                                }
                                # Calculate comprehensive quality score
                                sleep_dict['quality_score'] = self._calculate_sleep_quality(sleep_dict)
                                return sleep_dict
                    except Exception as e:
                        print(f"  ⚠️  Error parsing date from {txt_file.name}: {e}")
                        continue
            
            # Fall back to JSON format
            if self.icloud_path.exists():
                with open(self.icloud_path, 'r') as f:
                    health_data = json.load(f)
                
                # Parse the data from iOS Shortcuts
                sleep_hours = health_data.get('sleep_hours', 7.0)
                
                return {
                    'duration_hours': sleep_hours,
                    'quality_score': self._calculate_sleep_quality_from_hours(sleep_hours),
                    'deep_sleep_minutes': 0,
                    'rem_sleep_minutes': 0,
                    'awake_minutes': 0,
                    'bedtime': '23:00',
                    'wake_time': '07:00'
                }
                
        except Exception as e:
            print(f"  ⚠️  Error reading health data: {e}")
            return None
    
    def _parse_sleep_text_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse Apple Health sleep data from text file created by iOS Shortcut"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse format like:
            # 9 Oct 2025 at 1:49 am-9 Oct 2025 at 8:56 am
            # Total Time Asleep:6 hours 39 minutes
            # Deep for 0 hours and 54 minutes
            # REM for 2 hours and 0 minutes
            # Awake for 0 hours and 28 minutes
            
            data = {}
            
            # Extract total sleep
            if 'Total Time Asleep:' in content:
                sleep_line = [l for l in content.split('\n') if 'Total Time Asleep:' in l][0]
                # Extract hours and minutes
                import re
                hours_match = re.search(r'(\d+)\s+hours?', sleep_line)
                minutes_match = re.search(r'(\d+)\s+minutes?', sleep_line)
                
                hours = int(hours_match.group(1)) if hours_match else 0
                minutes = int(minutes_match.group(1)) if minutes_match else 0
                data['total_hours'] = hours + (minutes / 60.0)
            
            # Extract deep sleep
            if 'Deep for' in content:
                deep_line = [l for l in content.split('\n') if 'Deep for' in l][0]
                import re
                hours_match = re.search(r'(\d+)\s+hours?', deep_line)
                minutes_match = re.search(r'(\d+)\s+minutes?', deep_line)
                
                hours = int(hours_match.group(1)) if hours_match else 0
                minutes = int(minutes_match.group(1)) if minutes_match else 0
                data['deep_minutes'] = (hours * 60) + minutes
            
            # Extract REM sleep
            if 'REM for' in content:
                rem_line = [l for l in content.split('\n') if 'REM for' in l][0]
                import re
                hours_match = re.search(r'(\d+)\s+hours?', rem_line)
                minutes_match = re.search(r'(\d+)\s+minutes?', rem_line)
                
                hours = int(hours_match.group(1)) if hours_match else 0
                minutes = int(minutes_match.group(1)) if minutes_match else 0
                data['rem_minutes'] = (hours * 60) + minutes
            
            # Extract awake time
            if 'Awake for' in content:
                awake_line = [l for l in content.split('\n') if 'Awake for' in l][0]
                import re
                hours_match = re.search(r'(\d+)\s+hours?', awake_line)
                minutes_match = re.search(r'(\d+)\s+minutes?', awake_line)
                
                hours = int(hours_match.group(1)) if hours_match else 0
                minutes = int(minutes_match.group(1)) if minutes_match else 0
                data['awake_minutes'] = (hours * 60) + minutes
            
            # Extract times from first line
            first_line = content.split('\n')[0]
            if ' at ' in first_line and '-' in first_line:
                times = first_line.split('-')
                if len(times) == 2:
                    # Extract bedtime (first part)
                    bedtime_str = times[0].split(' at ')[-1].strip()
                    # Extract wake time (second part)
                    waketime_str = times[1].split(' at ')[-1].strip()
                    data['bedtime_str'] = bedtime_str
                    data['waketime_str'] = waketime_str
            
            return data
            
        except Exception as e:
            print(f"  ⚠️  Error parsing text file: {e}")
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
            # Silently fail - using biometric CSV data instead
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
            # Silently fail - using biometric CSV data instead
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
        """
        Convert sleep data to 1-10 quality score using comprehensive algorithm
        
        Scoring breakdown (100 points total):
        - Total Sleep Duration: 0-25 points
        - Deep Sleep Percentage: 0-25 points
        - REM Sleep Percentage: 0-25 points
        - Time Awake: 0-15 points
        - Sleep Timing: 0-10 points
        
        Final score converted to 1-10 scale
        """
        if not sleep_data:
            return 7.0  # Default
        
        total_score = 0
        
        # 1. Total Sleep Duration (0-25 points)
        duration_hours = sleep_data.get('duration_hours', 7)
        if 7 <= duration_hours <= 9:
            total_score += 25
        elif (6 <= duration_hours < 7) or (9 < duration_hours <= 10):
            total_score += 20
        elif (5 <= duration_hours < 6) or (10 < duration_hours <= 11):
            total_score += 15
        else:
            total_score += 10
        
        # 2. Deep Sleep Percentage (0-25 points)
        deep_min = sleep_data.get('deep_sleep_minutes', 0)
        total_min = duration_hours * 60
        deep_pct = (deep_min / total_min * 100) if total_min > 0 else 0
        
        if 15 <= deep_pct <= 25:
            total_score += 25
        elif (10 <= deep_pct < 15) or (25 < deep_pct <= 30):
            total_score += 20
        elif 5 <= deep_pct < 10:
            total_score += 15
        else:
            total_score += 10
        
        # 3. REM Sleep Percentage (0-25 points)
        rem_min = sleep_data.get('rem_sleep_minutes', 0)
        rem_pct = (rem_min / total_min * 100) if total_min > 0 else 0
        
        if 20 <= rem_pct <= 25:
            total_score += 25
        elif (15 <= rem_pct < 20) or (25 < rem_pct <= 30):
            total_score += 20
        elif 10 <= rem_pct < 15:
            total_score += 15
        else:
            total_score += 10
        
        # 4. Time Awake (0-15 points)
        awake_min = sleep_data.get('awake_minutes', 0)
        if awake_min < 5:
            total_score += 15
        elif 5 <= awake_min < 15:
            total_score += 12
        elif 15 <= awake_min < 30:
            total_score += 8
        else:
            total_score += 5
        
        # 5. Sleep Timing (0-10 points)
        bedtime_str = sleep_data.get('bedtime', '')
        wake_time_str = sleep_data.get('wake_time', '')
        
        timing_score = 0
        
        # Parse bedtime (looking for 9 PM - 11 PM optimal)
        if bedtime_str:
            try:
                # Handle formats like "10:30 pm" or "22:30"
                bedtime_str_lower = bedtime_str.lower().strip()
                if 'pm' in bedtime_str_lower or 'am' in bedtime_str_lower:
                    # 12-hour format
                    time_part = bedtime_str_lower.replace('pm', '').replace('am', '').strip()
                    hour = int(time_part.split(':')[0])
                    is_pm = 'pm' in bedtime_str_lower
                    
                    if is_pm:
                        if hour == 12:
                            bedtime_hour = 12
                        else:
                            bedtime_hour = hour + 12
                    else:
                        if hour == 12:
                            bedtime_hour = 0
                        else:
                            bedtime_hour = hour
                else:
                    # 24-hour format
                    bedtime_hour = int(bedtime_str.split(':')[0])
                
                # Optimal: 21:00 (9 PM) - 23:00 (11 PM)
                if 21 <= bedtime_hour <= 23:
                    timing_score += 5
                elif (20 <= bedtime_hour < 21) or (23 < bedtime_hour <= 24) or bedtime_hour == 0:
                    timing_score += 3  # Within 1 hour
            except:
                pass
        
        # Parse wake time (looking for 6 AM - 8 AM optimal)
        if wake_time_str:
            try:
                wake_time_str_lower = wake_time_str.lower().strip()
                if 'pm' in wake_time_str_lower or 'am' in wake_time_str_lower:
                    # 12-hour format
                    time_part = wake_time_str_lower.replace('pm', '').replace('am', '').strip()
                    hour = int(time_part.split(':')[0])
                    is_pm = 'pm' in wake_time_str_lower
                    
                    if is_pm:
                        if hour == 12:
                            wake_hour = 12
                        else:
                            wake_hour = hour + 12
                    else:
                        if hour == 12:
                            wake_hour = 0
                        else:
                            wake_hour = hour
                else:
                    # 24-hour format
                    wake_hour = int(wake_time_str.split(':')[0])
                
                # Optimal: 6:00 - 8:00 AM
                if 6 <= wake_hour <= 8:
                    timing_score += 5
                elif (5 <= wake_hour < 6) or (8 < wake_hour <= 9):
                    timing_score += 3  # Within 1 hour
            except:
                pass
        
        total_score += timing_score
        
        # Convert 0-100 score to 1-10 scale
        final_score = (total_score / 100) * 9 + 1  # Maps 0→1, 100→10
        
        return round(min(10.0, max(1.0, final_score)), 1)
    
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

