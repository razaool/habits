"""Visualization module for habit tracking insights"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime
import numpy as np


class HabitVisualizer:
    """Create visualizations of habit tracking data"""
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.real_data_file = Path(f"data/real/{profile_name}_real.csv")
        self.output_dir = Path("data/visualizations")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        sns.set_style("whitegrid")
        plt.rcParams['figure.figsize'] = (12, 8)
    
    def load_data(self) -> pd.DataFrame:
        """Load real tracking data"""
        if not self.real_data_file.exists():
            raise FileNotFoundError(f"No data found at {self.real_data_file}")
        
        df = pd.read_csv(self.real_data_file)
        if 'timestamp' in df.columns:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            df['date'] = df['timestamp'].dt.date
        
        return df
    
    def plot_completion_timeline(self, df: pd.DataFrame, save: bool = True):
        """Plot completion timeline"""
        fig, ax = plt.subplots(figsize=(14, 4))
        
        # Create timeline
        dates = pd.to_datetime(df['date']) if 'date' in df.columns else range(len(df))
        colors = ['#2ecc71' if c else '#e74c3c' for c in df['completed']]
        
        ax.scatter(dates, [1]*len(df), c=colors, s=100, alpha=0.7)
        ax.set_ylim(0.5, 1.5)
        ax.set_yticks([])
        ax.set_xlabel('Date', fontsize=12)
        ax.set_title(f'Habit Completion Timeline - {self.profile_name.title()}', 
                    fontsize=14, fontweight='bold')
        
        # Add streak annotations
        plt.text(0.02, 0.95, '🟢 Completed', transform=ax.transAxes, 
                fontsize=10, verticalalignment='top')
        plt.text(0.02, 0.85, '🔴 Skipped', transform=ax.transAxes, 
                fontsize=10, verticalalignment='top')
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / f"{self.profile_name}_timeline.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"📊 Saved timeline to {filepath}")
        
        plt.show()
        return fig
    
    def plot_weekly_heatmap(self, df: pd.DataFrame, save: bool = True):
        """Plot weekly completion heatmap"""
        if 'day_of_week' not in df.columns or len(df) < 7:
            print("⚠️  Need at least a week of data for heatmap")
            return None
        
        # Calculate completion rate by day
        days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
        completion_by_day = df.groupby('day_of_week')['completed'].mean()
        
        # Reindex to ensure all days
        completion_by_day = completion_by_day.reindex(days_order, fill_value=0)
        
        # Create heatmap
        fig, ax = plt.subplots(figsize=(10, 2))
        
        data = completion_by_day.values.reshape(1, -1)
        sns.heatmap(data, annot=True, fmt='.0%', cmap='RdYlGn', 
                   vmin=0, vmax=1, cbar_kws={'label': 'Completion Rate'},
                   xticklabels=[d.title()[:3] for d in days_order],
                   yticklabels=[''], ax=ax)
        
        ax.set_title(f'Weekly Completion Pattern - {self.profile_name.title()}', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / f"{self.profile_name}_weekly_heatmap.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"📊 Saved heatmap to {filepath}")
        
        plt.show()
        return fig
    
    def plot_streak_analysis(self, df: pd.DataFrame, save: bool = True):
        """Plot streak progression over time"""
        if 'current_streak' not in df.columns:
            print("⚠️  No streak data available")
            return None
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        
        # Streak over time
        ax1.plot(range(len(df)), df['current_streak'], 
                linewidth=2, color='#e74c3c', marker='o', markersize=4)
        ax1.fill_between(range(len(df)), df['current_streak'], 
                         alpha=0.3, color='#e74c3c')
        ax1.set_xlabel('Day Number', fontsize=12)
        ax1.set_ylabel('Streak Length', fontsize=12)
        ax1.set_title('Streak Progression', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Streak distribution
        streak_counts = df['current_streak'].value_counts().sort_index()
        ax2.bar(streak_counts.index, streak_counts.values, 
               color='#3498db', alpha=0.7)
        ax2.set_xlabel('Streak Length', fontsize=12)
        ax2.set_ylabel('Frequency', fontsize=12)
        ax2.set_title('Streak Length Distribution', fontsize=13, fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / f"{self.profile_name}_streaks.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"📊 Saved streak analysis to {filepath}")
        
        plt.show()
        return fig
    
    def plot_difficulty_motivation(self, df: pd.DataFrame, save: bool = True):
        """Plot difficulty vs motivation scatter"""
        df_completed = df[df['completed'] == True].copy()
        
        if df_completed.empty or 'difficulty_rating' not in df_completed.columns:
            print("⚠️  No difficulty/motivation data available")
            return None
        
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Scatter plot
        scatter = ax.scatter(df_completed['difficulty_rating'], 
                           df_completed['motivation_rating'],
                           c=df_completed['current_streak'],
                           s=100, alpha=0.6, cmap='viridis')
        
        # Add diagonal line (difficulty = motivation)
        ax.plot([1, 10], [1, 10], 'r--', alpha=0.3, label='Difficulty = Motivation')
        
        # Quadrant labels
        ax.axhline(5.5, color='gray', linestyle='--', alpha=0.3)
        ax.axvline(5.5, color='gray', linestyle='--', alpha=0.3)
        
        ax.text(3, 8, 'Easy & Motivated\n(Sweet Spot)', 
               ha='center', fontsize=9, alpha=0.5)
        ax.text(8, 8, 'Hard but Motivated\n(Growth Zone)', 
               ha='center', fontsize=9, alpha=0.5)
        ax.text(3, 2, 'Easy & Unmotivated\n(Boredom)', 
               ha='center', fontsize=9, alpha=0.5)
        ax.text(8, 2, 'Hard & Unmotivated\n(Danger Zone)', 
               ha='center', fontsize=9, alpha=0.5)
        
        ax.set_xlabel('Difficulty (1-10)', fontsize=12)
        ax.set_ylabel('Motivation (1-10)', fontsize=12)
        ax.set_title(f'Difficulty vs Motivation - {self.profile_name.title()}', 
                    fontsize=14, fontweight='bold')
        ax.set_xlim(0, 11)
        ax.set_ylim(0, 11)
        ax.legend()
        
        # Colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Streak Length', fontsize=10)
        
        plt.tight_layout()
        
        if save:
            filepath = self.output_dir / f"{self.profile_name}_difficulty_motivation.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"📊 Saved difficulty/motivation plot to {filepath}")
        
        plt.show()
        return fig
    
    def plot_summary_dashboard(self, df: pd.DataFrame, save: bool = True):
        """Create comprehensive summary dashboard"""
        fig = plt.figure(figsize=(16, 10))
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 1. Completion rate gauge
        ax1 = fig.add_subplot(gs[0, 0])
        completion_rate = df['completed'].mean()
        self._plot_gauge(ax1, completion_rate, 'Completion Rate')
        
        # 2. Current streak
        ax2 = fig.add_subplot(gs[0, 1])
        current_streak = df['current_streak'].iloc[-1] if len(df) > 0 else 0
        ax2.text(0.5, 0.5, f"🔥 {current_streak}", 
                ha='center', va='center', fontsize=48, fontweight='bold')
        ax2.text(0.5, 0.2, 'Current Streak', 
                ha='center', va='center', fontsize=12)
        ax2.axis('off')
        
        # 3. Total completions
        ax3 = fig.add_subplot(gs[0, 2])
        total_completions = df['completed'].sum()
        ax3.text(0.5, 0.5, f"✅ {total_completions}", 
                ha='center', va='center', fontsize=48, fontweight='bold')
        ax3.text(0.5, 0.2, 'Total Completions', 
                ha='center', va='center', fontsize=12)
        ax3.axis('off')
        
        # 4. Timeline
        ax4 = fig.add_subplot(gs[1, :])
        dates = range(len(df))
        colors = ['#2ecc71' if c else '#e74c3c' for c in df['completed']]
        ax4.scatter(dates, [1]*len(df), c=colors, s=80, alpha=0.7)
        ax4.set_ylim(0.5, 1.5)
        ax4.set_yticks([])
        ax4.set_xlabel('Day', fontsize=10)
        ax4.set_title('Completion Timeline', fontsize=12, fontweight='bold')
        
        # 5. Weekly pattern
        ax5 = fig.add_subplot(gs[2, 0])
        if 'day_of_week' in df.columns:
            days_order = ['monday', 'tuesday', 'wednesday', 'thursday', 
                         'friday', 'saturday', 'sunday']
            completion_by_day = df.groupby('day_of_week')['completed'].mean()
            completion_by_day = completion_by_day.reindex(days_order, fill_value=0)
            ax5.bar(range(7), completion_by_day.values, color='#3498db', alpha=0.7)
            ax5.set_xticks(range(7))
            ax5.set_xticklabels([d[:3] for d in days_order], fontsize=8)
            ax5.set_ylabel('Completion Rate', fontsize=10)
            ax5.set_title('By Day of Week', fontsize=12, fontweight='bold')
            ax5.set_ylim(0, 1)
        
        # 6. Difficulty trend
        ax6 = fig.add_subplot(gs[2, 1])
        if 'difficulty_rating' in df.columns:
            df_completed = df[df['completed'] == True]
            if len(df_completed) > 0:
                ax6.plot(range(len(df_completed)), 
                        df_completed['difficulty_rating'].values,
                        color='#e74c3c', linewidth=2, alpha=0.7)
                ax6.set_xlabel('Completion #', fontsize=10)
                ax6.set_ylabel('Difficulty', fontsize=10)
                ax6.set_title('Difficulty Over Time', fontsize=12, fontweight='bold')
                ax6.set_ylim(0, 11)
        
        # 7. Motivation trend
        ax7 = fig.add_subplot(gs[2, 2])
        if 'motivation_rating' in df.columns:
            df_completed = df[df['completed'] == True]
            if len(df_completed) > 0:
                ax7.plot(range(len(df_completed)), 
                        df_completed['motivation_rating'].values,
                        color='#2ecc71', linewidth=2, alpha=0.7)
                ax7.set_xlabel('Completion #', fontsize=10)
                ax7.set_ylabel('Motivation', fontsize=10)
                ax7.set_title('Motivation Over Time', fontsize=12, fontweight='bold')
                ax7.set_ylim(0, 11)
        
        fig.suptitle(f'Habit Dashboard - {self.profile_name.title()}', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        if save:
            filepath = self.output_dir / f"{self.profile_name}_dashboard.png"
            plt.savefig(filepath, dpi=150, bbox_inches='tight')
            print(f"📊 Saved dashboard to {filepath}")
        
        plt.show()
        return fig
    
    def _plot_gauge(self, ax, value: float, label: str):
        """Plot a gauge chart"""
        # Color based on value
        if value >= 0.8:
            color = '#2ecc71'
        elif value >= 0.6:
            color = '#f39c12'
        else:
            color = '#e74c3c'
        
        # Draw gauge
        theta = np.linspace(0, np.pi, 100)
        r = 1
        x = r * np.cos(theta)
        y = r * np.sin(theta)
        
        ax.plot(x, y, 'k-', linewidth=2)
        ax.fill_between(x, 0, y, alpha=0.1)
        
        # Fill up to value
        theta_val = np.linspace(0, np.pi * value, 100)
        x_val = r * np.cos(theta_val)
        y_val = r * np.sin(theta_val)
        ax.fill_between(x_val, 0, y_val, alpha=0.7, color=color)
        
        # Add needle
        needle_angle = np.pi * (1 - value)
        ax.plot([0, np.cos(needle_angle)], [0, np.sin(needle_angle)], 
               'r-', linewidth=3)
        
        # Add text
        ax.text(0, -0.3, f'{value:.0%}', ha='center', va='center', 
               fontsize=20, fontweight='bold')
        ax.text(0, -0.5, label, ha='center', va='center', fontsize=10)
        
        ax.set_xlim(-1.2, 1.2)
        ax.set_ylim(-0.6, 1.2)
        ax.axis('off')
    
    def generate_all_plots(self):
        """Generate all visualizations"""
        print("\n" + "="*70)
        print("  📊 GENERATING VISUALIZATIONS")
        print("="*70)
        
        try:
            df = self.load_data()
            print(f"\n✅ Loaded {len(df)} days of data")
            
            print("\n📈 Creating plots...")
            self.plot_summary_dashboard(df)
            self.plot_completion_timeline(df)
            self.plot_weekly_heatmap(df)
            self.plot_streak_analysis(df)
            self.plot_difficulty_motivation(df)
            
            print("\n" + "="*70)
            print("  ✅ ALL VISUALIZATIONS CREATED!")
            print("="*70)
            print(f"\nSaved to: {self.output_dir}/")
            
        except FileNotFoundError as e:
            print(f"\n❌ {e}")
            print("Start tracking to generate visualizations.")


def main():
    """Generate visualizations from command line"""
    import sys
    
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
    else:
        profile_name = input("Enter profile name: ").strip()
    
    visualizer = HabitVisualizer(profile_name)
    visualizer.generate_all_plots()


if __name__ == "__main__":
    main()
