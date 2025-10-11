"""Process habit log CSV to auto-calculate time_of_day from timestamp"""

import pandas as pd
from datetime import datetime

def get_time_of_day(timestamp_str):
    """Derive time_of_day from timestamp"""
    try:
        dt = pd.to_datetime(timestamp_str)
        hour = dt.hour
        
        if 6 <= hour < 12:
            return 'morning'
        elif 12 <= hour < 17:
            return 'afternoon'
        elif 17 <= hour < 22:
            return 'evening'
        else:  # 22-6
            return 'night'
    except:
        return 'evening'  # default


def process_habit_log(input_file='data/habit_log_template_jan_oct.csv', 
                      output_file='data/real/razaool_real.csv'):
    """Process the habit log and auto-calculate time_of_day"""
    
    print("📊 Processing habit log...")
    print("=" * 70)
    
    # Read the CSV
    df = pd.read_csv(input_file)
    
    # Auto-calculate time_of_day from timestamp
    df['time_of_day'] = df['timestamp'].apply(get_time_of_day)
    
    # Filter to only rows where completed is filled in
    completed_df = df[df['completed'].notna()].copy()
    
    print(f"✅ Total rows: {len(df)}")
    print(f"✅ Completed rows (with data): {len(completed_df)}")
    print(f"📅 Date range: {completed_df['timestamp'].min()[:10]} to {completed_df['timestamp'].max()[:10]}")
    
    if len(completed_df) == 0:
        print("\n⚠️  No completed entries found!")
        print("Fill in the 'completed' column (True/False) for days you want to log.")
        return
    
    # Show summary
    print(f"\n📊 SUMMARY:")
    print(f"  Completed: {completed_df['completed'].sum()} days")
    print(f"  Skipped: {len(completed_df) - completed_df['completed'].sum()} days")
    
    # Show time of day distribution
    print(f"\n⏰ TIME OF DAY DISTRIBUTION:")
    time_dist = completed_df['time_of_day'].value_counts()
    for tod, count in time_dist.items():
        print(f"  {tod.capitalize()}: {count} times")
    
    # Save to output file
    completed_df.to_csv(output_file, index=False)
    print(f"\n💾 Saved to: {output_file}")
    
    # Show first few rows
    print(f"\n📋 FIRST 5 ENTRIES:")
    print("=" * 70)
    sample = completed_df[['timestamp', 'completed', 'difficulty_rating', 'motivation_rating', 
                           'time_of_day', 'sleep_quality', 'energy_level']].head()
    print(sample.to_string(index=False))
    
    return completed_df


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        input_file = sys.argv[1]
        process_habit_log(input_file)
    else:
        process_habit_log()

