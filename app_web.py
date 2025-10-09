"""Flask web app for habit tracking - mobile-friendly"""

from flask import Flask, render_template, request, jsonify, redirect, url_for
from datetime import datetime, date, timedelta
from pathlib import Path
import pandas as pd
from src.models import UserProfile
from src.profiler import HabitProfiler
from src.train import HabitModelTrainer
from src.apple_health import get_health_integration

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Change in production

# Global state (in production, use sessions)
CURRENT_USER = None


@app.context_processor
def inject_user():
    """Make get_current_user available to all templates"""
    return dict(get_current_user=get_current_user)


def get_current_user():
    """Get current user - loads from last used or prompts selection"""
    global CURRENT_USER
    if CURRENT_USER:
        return CURRENT_USER
    
    # Try to load from cache
    cache_file = Path("data/.current_user")
    if cache_file.exists():
        CURRENT_USER = cache_file.read_text().strip()
        return CURRENT_USER
    
    return None


def set_current_user(username: str):
    """Set current user"""
    global CURRENT_USER
    CURRENT_USER = username
    cache_file = Path("data/.current_user")
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    cache_file.write_text(username)


def get_user_stats(username: str):
    """Get user statistics"""
    data_file = Path(f"data/real/{username}_real.csv")
    
    if not data_file.exists():
        return {
            'total_days': 0,
            'total_completions': 0,
            'current_streak': 0,
            'longest_streak': 0,
            'completion_rate': 0.0,
            'days_since_last': 0
        }
    
    df = pd.read_csv(data_file)
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
    
    # Current streak
    current_streak = 0
    for completed in reversed(df['completed'].tolist()):
        if completed:
            current_streak += 1
        else:
            break
    
    # Longest streak
    longest_streak = 0
    temp_streak = 0
    for completed in df['completed']:
        if completed:
            temp_streak += 1
            longest_streak = max(longest_streak, temp_streak)
        else:
            temp_streak = 0
    
    # Days since last
    if total_completions > 0:
        last_completion = df[df['completed'] == True]['date'].max()
        days_since_last = (datetime.now().date() - last_completion).days
    else:
        days_since_last = total_days
    
    return {
        'total_days': total_days,
        'total_completions': int(total_completions),
        'current_streak': current_streak,
        'longest_streak': longest_streak,
        'completion_rate': completion_rate,
        'days_since_last': days_since_last
    }


@app.route('/')
def index():
    """Home page"""
    username = get_current_user()
    
    if not username:
        # Show user selection
        profiles_dir = Path("data/profiles")
        profiles = []
        if profiles_dir.exists():
            profiles = [f.stem for f in profiles_dir.glob("*.json")]
        
        return render_template('select_user.html', profiles=profiles)
    
    # Load user profile
    try:
        profile = HabitProfiler.load_profile(username)
        stats = get_user_stats(username)
        
        # Check if logged today
        data_file = Path(f"data/real/{username}_real.csv")
        logged_today = False
        if data_file.exists():
            df = pd.read_csv(data_file)
            if not df.empty and 'timestamp' in df.columns:
                df['date'] = pd.to_datetime(df['timestamp']).dt.date
                logged_today = datetime.now().date() in df['date'].values
        
        return render_template('dashboard.html', 
                             profile=profile, 
                             stats=stats,
                             logged_today=logged_today)
    except FileNotFoundError:
        return redirect(url_for('create_profile'))


@app.route('/select_user/<username>')
def select_user(username):
    """Select a user"""
    set_current_user(username)
    return redirect(url_for('index'))


@app.route('/logout')
def logout():
    """Logout current user"""
    global CURRENT_USER
    CURRENT_USER = None
    cache_file = Path("data/.current_user")
    if cache_file.exists():
        cache_file.unlink()
    return redirect(url_for('index'))


@app.route('/log')
def log_habit():
    """Log habit page"""
    username = get_current_user()
    if not username:
        return redirect(url_for('index'))
    
    profile = HabitProfiler.load_profile(username)
    
    # Get health data
    health = get_health_integration(username)
    health_snapshot = health.get_comprehensive_health_snapshot(date.today())
    
    return render_template('log_habit.html', 
                         profile=profile,
                         health=health_snapshot)


@app.route('/log', methods=['POST'])
def log_habit_post():
    """Handle habit logging"""
    username = get_current_user()
    if not username:
        return jsonify({'error': 'Not logged in'}), 401
    
    # Get form data
    completed = request.form.get('completed') == 'true'
    difficulty = int(request.form.get('difficulty', 5))
    motivation = int(request.form.get('motivation', 5))
    duration = int(request.form.get('duration', 0))
    notes = request.form.get('notes', '')
    
    # Get health data
    health = get_health_integration(username)
    health_snapshot = health.get_comprehensive_health_snapshot(date.today())
    
    # Save to data file
    data_file = Path(f"data/real/{username}_real.csv")
    data_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing
    if data_file.exists():
        df = pd.read_csv(data_file)
    else:
        df = pd.DataFrame()
    
    # Remove today if exists (update)
    if not df.empty and 'timestamp' in df.columns:
        df['date'] = pd.to_datetime(df['timestamp']).dt.strftime('%Y-%m-%d')
        today_str = datetime.now().strftime('%Y-%m-%d')
        df = df[df['date'] != today_str]
        df = df.drop('date', axis=1)
    
    # Add new entry
    now = datetime.now()
    day_of_week = now.strftime('%A').lower()
    
    # Determine time of day
    hour = now.hour
    if 6 <= hour < 12:
        time_of_day = "morning"
    elif 12 <= hour < 17:
        time_of_day = "afternoon"
    elif 17 <= hour < 22:
        time_of_day = "evening"
    else:
        time_of_day = "night"
    
    new_entry = {
        'timestamp': now.isoformat(),
        'completed': completed,
        'difficulty_rating': difficulty if completed else None,
        'motivation_rating': motivation if completed else None,
        'duration_minutes': duration if completed else None,
        'context_notes': notes,
        'time_of_day': time_of_day,
        'day_of_week': day_of_week,
        'sleep_quality': health_snapshot['sleep_quality'],
        'stress_level': health_snapshot['stress_level'],
        'energy_level': health_snapshot['energy_level'],
        'health_data_source': health_snapshot['data_source'],
    }
    
    df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
    df.to_csv(data_file, index=False)
    
    return redirect(url_for('index', logged='success'))


@app.route('/stats')
def stats():
    """Statistics page"""
    username = get_current_user()
    if not username:
        return redirect(url_for('index'))
    
    profile = HabitProfiler.load_profile(username)
    stats = get_user_stats(username)
    
    # Get detailed stats
    data_file = Path(f"data/real/{username}_real.csv")
    detailed_stats = None
    
    if data_file.exists():
        df = pd.read_csv(data_file)
        if not df.empty and 'day_of_week' in df.columns:
            # By day of week
            dow_stats = df.groupby('day_of_week')['completed'].agg(['sum', 'count', 'mean']).to_dict()
            
            # Recent trend
            df['date'] = pd.to_datetime(df['timestamp']).dt.date
            last_7_days = df[df['date'] >= (date.today() - timedelta(days=7))]
            recent_rate = last_7_days['completed'].mean() if len(last_7_days) > 0 else 0
            
            detailed_stats = {
                'by_day': dow_stats,
                'recent_rate': recent_rate,
                'recent_count': len(last_7_days)
            }
    
    return render_template('stats.html', 
                         profile=profile,
                         stats=stats,
                         detailed_stats=detailed_stats)


@app.route('/recommendations')
def recommendations():
    """AI recommendations page"""
    username = get_current_user()
    if not username:
        return redirect(url_for('index'))
    
    profile = HabitProfiler.load_profile(username)
    
    # Try to load model
    try:
        trainer = HabitModelTrainer.load_models(username)
        
        # Get optimal times for today
        today = datetime.now().strftime('%A').lower()
        optimal_times = trainer.get_optimal_times(today, n_times=3)
        
        # Current prediction
        stats = get_user_stats(username)
        now = datetime.now()
        
        current_features = {
            'day_of_week_encoded': trainer.day_encoder.transform([today])[0],
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
        
        current_prob = trainer.predict_completion_probability(current_features)
        
        return render_template('recommendations.html',
                             profile=profile,
                             optimal_times=optimal_times,
                             current_prob=current_prob,
                             stats=stats,
                             has_models=True)
    
    except FileNotFoundError:
        return render_template('recommendations.html',
                             profile=profile,
                             has_models=False)


@app.route('/health')
def health():
    """Health data page"""
    username = get_current_user()
    if not username:
        return redirect(url_for('index'))
    
    profile = HabitProfiler.load_profile(username)
    health_integration = get_health_integration(username)
    
    # Get last 7 days with detailed data, but ONLY show days with real data
    health_data = []
    for i in range(7):
        day = date.today() - timedelta(days=6-i)
        
        # Try to get real sleep data
        sleep_data = health_integration.get_sleep_data(day)
        
        # Only include days that have real data
        if sleep_data:
            snapshot = health_integration.get_comprehensive_health_snapshot(day)
            snapshot['date'] = day
            snapshot['sleep_hours'] = sleep_data.get('duration_hours', 0)
            snapshot['deep_sleep_min'] = sleep_data.get('deep_sleep_minutes', 0)
            snapshot['rem_sleep_min'] = sleep_data.get('rem_sleep_minutes', 0)
            snapshot['awake_min'] = sleep_data.get('awake_minutes', 0)
            snapshot['bedtime'] = sleep_data.get('bedtime', '')
            snapshot['wake_time'] = sleep_data.get('wake_time', '')
            
            health_data.append(snapshot)
    
    # Reverse to show most recent first
    health_data.reverse()
    
    return render_template('health.html',
                         profile=profile,
                         health_data=health_data,
                         is_available=health_integration.is_available(),
                         today=date.today(),
                         days_with_data=len(health_data))


@app.route('/api/stats')
def api_stats():
    """API endpoint for stats"""
    username = get_current_user()
    if not username:
        return jsonify({'error': 'Not logged in'}), 401
    
    stats = get_user_stats(username)
    return jsonify(stats)


if __name__ == '__main__':
    # Get local IP for iPhone access
    import socket
    hostname = socket.gethostname()
    local_ip = socket.gethostbyname(hostname)
    
    port = 5001  # Using 5001 to avoid macOS AirPlay Receiver on 5000
    
    print("\n" + "="*70)
    print("  🎯 AI HABIT COACH - WEB APP")
    print("="*70)
    print(f"\n📱 Access from your iPhone:")
    print(f"   http://{local_ip}:{port}")
    print(f"\n💻 Access from this computer:")
    print(f"   http://localhost:{port}")
    print("\n⚠️  Make sure your iPhone is on the same WiFi network!")
    print("\nPress Ctrl+C to stop the server")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=True)

