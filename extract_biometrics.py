"""Extract biometric data from Apple Health export and calculate daily scores"""

import pandas as pd
from pathlib import Path
import numpy as np

def normalize_score(series, min_val, max_val, inverse=False):
    """Normalize series to 1-10 scale. If inverse=True, lower is better."""
    # Fill NaN with middle value
    series = series.fillna((min_val + max_val) / 2)
    
    # Normalize to 0-1
    normalized = (series - min_val) / (max_val - min_val)
    normalized = normalized.clip(0, 1)
    
    if inverse:
        normalized = 1 - normalized
    
    # Scale to 1-10
    return 1 + (normalized * 9)


def extract_biometrics():
    """Extract and calculate biometric scores from health export"""
    
    # Load the main health export
    base = Path("/Users/razaool/Library/Mobile Documents/com~apple~CloudDocs/habit_coach/Real export data")
    health_dir = None
    
    for item in base.iterdir():
        if item.is_dir() and 'HealthAutoExport' in item.name:
            health_dir = item
            break
    
    export_file = health_dir / "HealthAutoExport-2025-01-01-2025-10-10.csv"
    print("📊 Loading health data from January 1st to October 10th...")
    
    df = pd.read_csv(export_file)
    df['Date/Time'] = pd.to_datetime(df['Date/Time'])
    df['Date'] = df['Date/Time'].dt.date
    
    print(f"✅ Loaded {len(df)} rows of data")
    
    # Calculate daily aggregates for each metric
    daily_metrics = []
    
    for current_date in pd.date_range(start='2025-01-01', end='2025-10-10', freq='D'):
        day_data = df[df['Date'] == current_date.date()]
        
        if len(day_data) == 0:
            continue
        
        # Extract key metrics
        metrics = {
            'date': current_date.date(),
            'hrv_avg': day_data['Heart Rate Variability (ms)'].mean(),
            'resting_hr': day_data['Resting Heart Rate (count/min)'].mean(),
            'hr_min': day_data['Heart Rate [Min] (count/min)'].mean(),
            'hr_max': day_data['Heart Rate [Max] (count/min)'].mean(),
            'hr_avg': day_data['Heart Rate [Avg] (count/min)'].mean(),
            'blood_oxygen': day_data['Blood Oxygen Saturation (%)'].mean(),
            'respiratory_rate': day_data['Respiratory Rate (count/min)'].mean(),
            'sleep_total': day_data['Sleep Analysis [Total] (hr)'].sum(),
            'sleep_deep': day_data['Sleep Analysis [Deep] (hr)'].sum(),
            'sleep_rem': day_data['Sleep Analysis [REM] (hr)'].sum(),
            'sleep_awake': day_data['Sleep Analysis [Awake] (hr)'].sum(),
            'sleep_core': day_data['Sleep Analysis [Core] (hr)'].sum(),
            'wrist_temp': day_data['Apple Sleeping Wrist Temperature (degC)'].mean(),
            'step_count': day_data['Step Count (count)'].sum(),
            'active_energy': day_data['Active Energy (kJ)'].sum(),
            'vo2_max': day_data['VO2 Max (ml/(kg·min))'].mean(),
        }
        
        daily_metrics.append(metrics)
    
    # Convert to DataFrame
    metrics_df = pd.DataFrame(daily_metrics)
    
    print(f"\n✅ Calculated daily metrics for {len(metrics_df)} days")
    print(f"📅 Date range: {metrics_df['date'].min()} to {metrics_df['date'].max()}")
    
    # Calculate Energy Level (1-10)
    metrics_df['energy_level'] = (
        normalize_score(metrics_df['hrv_avg'], 20, 100, inverse=False) * 0.3 +
        normalize_score(metrics_df['resting_hr'], 45, 80, inverse=True) * 0.2 +
        normalize_score(metrics_df['blood_oxygen'], 94, 100, inverse=False) * 0.2 +
        normalize_score(metrics_df['sleep_total'], 4, 9, inverse=False) * 0.3
    )
    
    # Calculate Stress Level (1-10, higher = more stressed)
    metrics_df['stress_level'] = (
        normalize_score(metrics_df['hrv_avg'], 20, 100, inverse=True) * 0.4 +
        normalize_score(metrics_df['resting_hr'], 45, 80, inverse=False) * 0.3 +
        normalize_score(metrics_df['respiratory_rate'], 12, 20, inverse=False) * 0.3
    )
    
    # Calculate Sleep Quality (1-10)
    metrics_df['sleep_quality'] = (
        normalize_score(metrics_df['sleep_total'], 4, 9, inverse=False) * 0.3 +
        normalize_score(metrics_df['sleep_deep'], 0.5, 2.5, inverse=False) * 0.3 +
        normalize_score(metrics_df['sleep_rem'], 1, 3, inverse=False) * 0.2 +
        normalize_score(metrics_df['sleep_awake'], 0, 1, inverse=True) * 0.2
    )
    
    # Round to 1 decimal
    metrics_df['energy_level'] = metrics_df['energy_level'].round(1)
    metrics_df['stress_level'] = metrics_df['stress_level'].round(1)
    metrics_df['sleep_quality'] = metrics_df['sleep_quality'].round(1)
    
    # Show summary statistics
    print("\n📊 CALCULATED METRICS SUMMARY:")
    print("=" * 70)
    print(f"Energy Level:  avg={metrics_df['energy_level'].mean():.1f}, min={metrics_df['energy_level'].min():.1f}, max={metrics_df['energy_level'].max():.1f}")
    print(f"Stress Level:  avg={metrics_df['stress_level'].mean():.1f}, min={metrics_df['stress_level'].min():.1f}, max={metrics_df['stress_level'].max():.1f}")
    print(f"Sleep Quality: avg={metrics_df['sleep_quality'].mean():.1f}, min={metrics_df['sleep_quality'].min():.1f}, max={metrics_df['sleep_quality'].max():.1f}")
    
    # Save to CSV for reference
    output_file = 'data/biometric_scores_jan_oct.csv'
    metrics_df.to_csv(output_file, index=False)
    print(f"\n💾 Saved biometric scores to: {output_file}")
    
    # Show first 10 days as sample
    print("\n📋 SAMPLE DATA (First 10 days):")
    print("=" * 70)
    sample = metrics_df[['date', 'sleep_quality', 'energy_level', 'stress_level', 'hrv_avg', 'resting_hr']].head(10)
    print(sample.to_string(index=False))
    
    return metrics_df


if __name__ == '__main__':
    metrics_df = extract_biometrics()

