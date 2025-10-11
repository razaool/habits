"""GitHub Integration - Pull commit history as habit completions"""

import requests
from datetime import datetime, timedelta
import pandas as pd
from collections import defaultdict
import time

class GitHubHabitTracker:
    def __init__(self, username):
        self.username = username
        self.base_url = "https://api.github.com"
        self.headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
    
    def get_all_repos(self):
        """Get all public repositories for the user"""
        print(f"📦 Fetching repositories for {self.username}...")
        
        repos = []
        page = 1
        
        while True:
            url = f"{self.base_url}/users/{self.username}/repos"
            params = {'per_page': 100, 'page': page, 'type': 'all'}
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                print(f"❌ Error fetching repos: {response.status_code}")
                break
            
            page_repos = response.json()
            if not page_repos:
                break
            
            repos.extend(page_repos)
            page += 1
            
            # Rate limit handling
            time.sleep(0.5)
        
        print(f"✅ Found {len(repos)} repositories")
        return repos
    
    def get_commits_for_repo(self, repo_name, since_date, until_date):
        """Get commits for a specific repository within date range"""
        commits = []
        page = 1
        
        while True:
            url = f"{self.base_url}/repos/{self.username}/{repo_name}/commits"
            params = {
                'author': self.username,
                'since': since_date.isoformat(),
                'until': until_date.isoformat(),
                'per_page': 100,
                'page': page
            }
            
            response = requests.get(url, headers=self.headers, params=params)
            
            if response.status_code != 200:
                break
            
            page_commits = response.json()
            if not page_commits:
                break
            
            commits.extend(page_commits)
            page += 1
            
            # Rate limit handling
            time.sleep(0.5)
        
        return commits
    
    def extract_commit_data(self, commits):
        """Extract relevant data from commits"""
        commit_data = []
        
        for commit in commits:
            try:
                commit_info = {
                    'timestamp': commit['commit']['author']['date'],
                    'message': commit['commit']['message'],
                    'sha': commit['sha'][:7],
                }
                commit_data.append(commit_info)
            except (KeyError, TypeError):
                continue
        
        return commit_data
    
    def aggregate_by_day(self, all_commits):
        """Aggregate commits by day"""
        daily_commits = defaultdict(list)
        
        for commit in all_commits:
            timestamp = datetime.fromisoformat(commit['timestamp'].replace('Z', '+00:00'))
            date_key = timestamp.date()
            daily_commits[date_key].append({
                'time': timestamp,
                'message': commit['message'],
                'sha': commit['sha']
            })
        
        return daily_commits
    
    def calculate_difficulty(self, num_commits):
        """Estimate difficulty based on number of commits"""
        if num_commits == 1:
            return 3
        elif num_commits <= 3:
            return 5
        elif num_commits <= 5:
            return 6
        elif num_commits <= 10:
            return 7
        else:
            return 8
    
    def calculate_motivation(self, commits_on_day, recent_streak):
        """Estimate motivation based on patterns"""
        num_commits = len(commits_on_day)
        
        # Base motivation from commit count
        base = min(10, 5 + num_commits * 0.5)
        
        # Bonus for being on a streak
        streak_bonus = min(2, recent_streak * 0.3)
        
        return min(10, int(base + streak_bonus))
    
    def estimate_duration(self, num_commits):
        """Estimate duration based on commits"""
        # Rough estimate: each commit represents ~20-40 minutes of work
        base_minutes = num_commits * 30
        return min(180, max(15, base_minutes))  # Cap at 3 hours, min 15 mins
    
    def fetch_all_commits(self, since_date, until_date):
        """Fetch all commits across all repos within date range"""
        print("\n🔍 GITHUB COMMIT HISTORY")
        print("=" * 70)
        
        repos = self.get_all_repos()
        all_commits = []
        
        print(f"\n📥 Fetching commits from {since_date.date()} to {until_date.date()}...")
        print("(This may take a few minutes for many repos)")
        
        for i, repo in enumerate(repos, 1):
            repo_name = repo['name']
            print(f"  [{i}/{len(repos)}] {repo_name}...", end=' ')
            
            commits = self.get_commits_for_repo(repo_name, since_date, until_date)
            if commits:
                commit_data = self.extract_commit_data(commits)
                all_commits.extend(commit_data)
                print(f"✅ {len(commit_data)} commits")
            else:
                print("(no commits)")
        
        print(f"\n✅ Total commits found: {len(all_commits)}")
        return all_commits
    
    def create_habit_entries(self, since_date, until_date):
        """Create habit log entries from GitHub commits"""
        
        # Fetch all commits
        all_commits = self.fetch_all_commits(since_date, until_date)
        
        if not all_commits:
            print("\n⚠️  No commits found in date range")
            return pd.DataFrame()
        
        # Aggregate by day
        daily_commits = self.aggregate_by_day(all_commits)
        
        print(f"\n📅 Commits spread across {len(daily_commits)} days")
        
        # Create habit entries
        habit_entries = []
        sorted_dates = sorted(daily_commits.keys())
        
        for i, date in enumerate(sorted_dates):
            commits = daily_commits[date]
            
            # Calculate streak (how many consecutive days before this)
            recent_streak = 0
            check_date = date - timedelta(days=1)
            while check_date in daily_commits:
                recent_streak += 1
                check_date -= timedelta(days=1)
            
            # Get first commit time of the day
            first_commit_time = min(c['time'] for c in commits)
            
            # Create entry
            entry = {
                'date': date,
                'timestamp': first_commit_time.isoformat(),
                'completed': True,
                'difficulty_rating': self.calculate_difficulty(len(commits)),
                'motivation_rating': self.calculate_motivation(commits, recent_streak),
                'duration_minutes': self.estimate_duration(len(commits)),
                'context_notes': f"GitHub: {len(commits)} commit(s) - {commits[0]['message'][:50]}...",
                'commit_count': len(commits),
                'commit_messages': ' | '.join([c['message'][:30] for c in commits[:3]])
            }
            
            habit_entries.append(entry)
        
        df = pd.DataFrame(habit_entries)
        
        # Show summary
        print(f"\n📊 GITHUB HABIT SUMMARY:")
        print("=" * 70)
        print(f"Total coding days: {len(df)}")
        print(f"Total commits: {sum(df['commit_count'])}")
        print(f"Avg commits/day: {df['commit_count'].mean():.1f}")
        print(f"Avg difficulty: {df['difficulty_rating'].mean():.1f}/10")
        print(f"Avg motivation: {df['motivation_rating'].mean():.1f}/10")
        print(f"Avg duration: {df['duration_minutes'].mean():.0f} minutes")
        
        return df


def integrate_github_data(username='razaool', 
                         since_date=datetime(2025, 1, 1),
                         until_date=datetime(2025, 10, 10, 23, 59, 59),
                         output_file='data/github_habit_log.csv'):
    """Main function to integrate GitHub data"""
    
    tracker = GitHubHabitTracker(username)
    github_df = tracker.create_habit_entries(since_date, until_date)
    
    if len(github_df) > 0:
        # Save GitHub data
        github_df.to_csv(output_file, index=False)
        print(f"\n💾 Saved GitHub data to: {output_file}")
        
        # Show sample
        print(f"\n📋 SAMPLE ENTRIES (First 5):")
        print("=" * 70)
        sample = github_df[['date', 'timestamp', 'commit_count', 'difficulty_rating', 
                           'motivation_rating', 'duration_minutes']].head()
        print(sample.to_string(index=False))
        
        return github_df
    
    return None


if __name__ == '__main__':
    import sys
    
    username = sys.argv[1] if len(sys.argv) > 1 else 'razaool'
    
    print("🚀 GITHUB HABIT INTEGRATION")
    print("=" * 70)
    print(f"Username: {username}")
    print(f"Date range: Jan 1, 2025 - Oct 10, 2025")
    print("\nThis will fetch all your commits and convert them to habit entries!")
    print("(Using GitHub public API - no authentication needed for public repos)")
    print()
    
    github_df = integrate_github_data(username)
    
    if github_df is not None:
        print("\n✅ SUCCESS!")
        print("\nNext steps:")
        print("  1. Review: data/github_habit_log.csv")
        print("  2. Run: python3 merge_habit_data.py (to merge with manual entries)")
        print("  3. Run: python3 main.py train razaool (to retrain with all data)")

