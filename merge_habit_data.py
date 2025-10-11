"""Merge GitHub commits with manual habit entries"""

import pandas as pd
from datetime import datetime

def merge_habit_data(manual_file='data/real/razaool_real.csv',
                    github_file='data/github_habit_log.csv',
                    biometrics_file='data/biometric_scores_jan_oct.csv',
                    output_file='data/real/razaool_real.csv'):
    """Merge manual entries with GitHub commits and add biometrics"""
    
    print("🔄 MERGING HABIT DATA")
    print("=" * 70)
    
    # Load manual entries
    manual_df = pd.read_csv(manual_file)
    manual_df['date'] = pd.to_datetime(manual_df['timestamp']).dt.date
    print(f"✅ Manual entries: {len(manual_df)} days")
    
    # Load GitHub entries
    github_df = pd.read_csv(github_file)
    github_df['date'] = pd.to_datetime(github_df['timestamp']).dt.date
    print(f"✅ GitHub entries: {len(github_df)} days")
    
    # Load biometrics
    biometrics_df = pd.read_csv(biometrics_file)
    biometrics_df['date'] = pd.to_datetime(biometrics_df['date']).dt.date
    print(f"✅ Biometric data: {len(biometrics_df)} days")
    
    # Find overlapping dates
    manual_dates = set(manual_df['date'])
    github_dates = set(github_df['date'])
    overlap = manual_dates.intersection(github_dates)
    
    print(f"\n📊 OVERLAP ANALYSIS:")
    print(f"  Manual only: {len(manual_dates - github_dates)} days")
    print(f"  GitHub only: {len(github_dates - manual_dates)} days")
    print(f"  Both: {len(overlap)} days")
    
    # For overlapping dates, prioritize manual entries (they're more specific)
    github_only = github_df[~github_df['date'].isin(manual_dates)].copy()
    
    print(f"\n✅ Adding {len(github_only)} GitHub-only days to habit log")
    
    # Prepare GitHub entries for merge
    github_only['day_of_week'] = pd.to_datetime(github_only['timestamp']).dt.day_name().str.lower()
    
    # Calculate time_of_day from timestamp
    def get_time_of_day(timestamp_str):
        dt = pd.to_datetime(timestamp_str)
        hour = dt.hour
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:
            return 'night'
    
    github_only['time_of_day'] = github_only['timestamp'].apply(get_time_of_day)
    
    # Merge with biometrics
    github_only = github_only.merge(
        biometrics_df[['date', 'sleep_quality', 'stress_level', 'energy_level']], 
        on='date', 
        how='left'
    )
    
    # Fill missing biometrics with defaults
    github_only['sleep_quality'] = github_only['sleep_quality'].fillna(6.0)
    github_only['stress_level'] = github_only['stress_level'].fillna(5.0)
    github_only['energy_level'] = github_only['energy_level'].fillna(6.0)
    github_only['health_data_source'] = 'apple_health'
    
    # Select columns to match manual format
    columns_to_keep = [
        'timestamp', 'completed', 'difficulty_rating', 'motivation_rating',
        'duration_minutes', 'context_notes', 'time_of_day', 'day_of_week',
        'sleep_quality', 'stress_level', 'energy_level', 'health_data_source'
    ]
    
    github_prepared = github_only[columns_to_keep]
    
    # Combine with manual entries
    combined_df = pd.concat([manual_df, github_prepared], ignore_index=True)
    
    # Sort by timestamp (handle mixed timezone formats)
    def parse_timestamp(ts):
        try:
            dt = pd.to_datetime(ts, utc=True)
            return dt.tz_localize(None)
        except:
            return pd.to_datetime(ts)
    
    combined_df['timestamp'] = combined_df['timestamp'].apply(parse_timestamp)
    combined_df = combined_df.sort_values('timestamp')
    
    # Convert timestamp back to string for CSV
    combined_df['timestamp'] = combined_df['timestamp'].dt.strftime('%Y-%m-%dT%H:%M:%S')
    
    # Save
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved merged data to: {output_file}")
    print(f"✅ Total entries: {len(combined_df)} days")
    
    # Summary
    print(f"\n📊 FINAL DATASET:")
    print("=" * 70)
    print(f"Total habit completions: {combined_df['completed'].sum()}")
    print(f"Date range: {combined_df['timestamp'].min()[:10]} to {combined_df['timestamp'].max()[:10]}")
    
    # Time of day distribution
    print(f"\n⏰ TIME OF DAY DISTRIBUTION:")
    time_dist = combined_df['time_of_day'].value_counts()
    for tod, count in time_dist.items():
        print(f"  {tod.capitalize()}: {count} times")
    
    # Show sample
    print(f"\n📋 SAMPLE (Last 5 entries):")
    print("=" * 70)
    sample = combined_df[['timestamp', 'completed', 'difficulty_rating', 
                         'motivation_rating', 'time_of_day', 'sleep_quality']].tail()
    print(sample.to_string(index=False))
    
    return combined_df


if __name__ == '__main__':
    combined_df = merge_habit_data()
    
    print("\n✅ DATA MERGE COMPLETE!")
    print("\n🚀 Next step: Train the ML model")
    print("Run: python3 main.py train razaool")

