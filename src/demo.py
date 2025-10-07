"""
Demo Script for Adaptive Reminder Timing Agent

Interactive demonstration of the trained RL agent in action.
"""

import os
import yaml
import numpy as np
from datetime import datetime, timedelta

from environment import HabitReminderEnv, Action
from user_simulator import create_user_simulator
from dqn_agent import DQNAgent


class InteractiveDemo:
    """
    Interactive demonstration of the trained agent
    """
    
    def __init__(self, agent_path: str, config_path: str = "config.yaml"):
        """
        Initialize demo
        
        Args:
            agent_path: Path to trained agent checkpoint
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        print("\n" + "=" * 70)
        print(" " * 15 + "🎯 Adaptive Reminder Timing Agent Demo 🎯")
        print("=" * 70)
        
        # Initialize environment
        self.user_profile = "evening_person"  # Can be changed
        self.user_simulator = create_user_simulator(
            self.user_profile,
            self.config,
            seed=42
        )
        self.env = HabitReminderEnv(self.user_simulator, self.config)
        
        # Initialize and load agent
        state_dim = self.env.observation_space.shape[0]
        action_dim = self.env.action_space.n
        self.agent = DQNAgent(state_dim, action_dim, self.config)
        self.agent.load(agent_path)
        
        print(f"\n✓ Agent loaded successfully from: {agent_path}")
        print(f"✓ User profile: {self.user_profile}")
        print(f"✓ Ready to demonstrate!\n")
    
    def run_week_simulation(self):
        """
        Run a week-long simulation showing agent behavior
        """
        print("\n" + "=" * 70)
        print("Running 7-Day Simulation")
        print("=" * 70 + "\n")
        
        state, _ = self.env.reset()
        
        current_day = 0
        day_events = []
        week_summary = []
        
        done = False
        steps = 0
        max_steps = 200  # Enough for a week
        
        start_date = datetime.now()
        
        while not done and steps < max_steps and current_day < 7:
            hour = state[0]
            day_of_week = int(state[1])
            streak = int(state[3])
            completed_today = bool(state[9])
            reminders_sent = int(state[6])
            
            # Track day changes
            if int(state[0]) >= 23.5 or (steps > 0 and hour < 6):
                if day_events:
                    # Summarize the day
                    day_date = start_date + timedelta(days=current_day)
                    day_name = day_date.strftime("%A")
                    
                    print(f"\n📅 Day {current_day + 1} - {day_name}")
                    print("-" * 70)
                    
                    for event in day_events:
                        print(f"  {event}")
                    
                    # Day summary
                    completed = any('✓ COMPLETED' in e for e in day_events)
                    week_summary.append({
                        'day': current_day + 1,
                        'day_name': day_name,
                        'completed': completed,
                        'reminders_sent': reminders_sent,
                        'streak': streak
                    })
                    
                    if completed:
                        print(f"  ✅ Habit completed! Streak: {streak} days")
                    else:
                        print(f"  ❌ Habit not completed. Streak reset.")
                    
                    day_events = []
                    current_day += 1
            
            # Get action from agent
            action = self.agent.select_action(state, training=False)
            action_names = ['Send Now', 'Wait 30 min', 'Wait 1 hour', 'Wait 2 hours', 'Skip today']
            
            # Take step
            next_state, reward, terminated, truncated, info = self.env.step(action)
            done = terminated or truncated
            
            # Log significant events
            if action == Action.SEND_NOW and info.get('reminder_sent'):
                time_str = f"{int(hour):02d}:{int((hour % 1) * 60):02d}"
                response = info.get('response', 'N/A')
                
                if 'COMPLETED' in response:
                    day_events.append(f"  🔔 {time_str} - Sent reminder → ✓ COMPLETED!")
                else:
                    day_events.append(f"  🔔 {time_str} - Sent reminder → {response}")
            
            state = next_state
            steps += 1
        
        # Print week summary
        print("\n" + "=" * 70)
        print("Week Summary")
        print("=" * 70 + "\n")
        
        completion_rate = sum(d['completed'] for d in week_summary) / len(week_summary) * 100
        max_streak = max(d['streak'] for d in week_summary) if week_summary else 0
        total_reminders = sum(d['reminders_sent'] for d in week_summary)
        
        print(f"{'Day':<12} {'Status':<15} {'Reminders':<12} {'Streak':<10}")
        print("-" * 70)
        for day_info in week_summary:
            status = "✅ Completed" if day_info['completed'] else "❌ Missed"
            print(f"{day_info['day_name']:<12} {status:<15} {day_info['reminders_sent']:<12} {day_info['streak']:<10}")
        
        print("-" * 70)
        print(f"\n📊 Statistics:")
        print(f"  • Completion Rate: {completion_rate:.1f}%")
        print(f"  • Max Streak: {max_streak} days")
        print(f"  • Total Reminders Sent: {total_reminders}")
        print(f"  • Avg Reminders/Day: {total_reminders/len(week_summary):.1f}")
        print("\n")
    
    def demonstrate_decision_making(self):
        """
        Show detailed decision-making process for different scenarios
        """
        print("\n" + "=" * 70)
        print("Agent Decision-Making Analysis")
        print("=" * 70 + "\n")
        
        scenarios = [
            {
                'name': 'Early Morning (7 AM, Weekday)',
                'hour': 7,
                'day': 2,
                'streak': 5,
                'is_weekend': 0
            },
            {
                'name': 'Lunch Time (12 PM, Weekday)',
                'hour': 12,
                'day': 3,
                'streak': 5,
                'is_weekend': 0
            },
            {
                'name': 'Evening (6 PM, Weekday)',
                'hour': 18,
                'day': 4,
                'streak': 5,
                'is_weekend': 0
            },
            {
                'name': 'Weekend Morning (10 AM, Saturday)',
                'hour': 10,
                'day': 5,
                'streak': 5,
                'is_weekend': 1
            },
            {
                'name': 'Late Night (10 PM, Weekday)',
                'hour': 22,
                'day': 1,
                'streak': 5,
                'is_weekend': 0
            },
        ]
        
        action_names = ['Send Now', 'Wait 30 min', 'Wait 1 hour', 'Wait 2 hours', 'Skip today']
        
        for scenario in scenarios:
            print(f"\n📍 Scenario: {scenario['name']}")
            print("-" * 70)
            
            # Create state for this scenario
            state = np.array([
                scenario['hour'],
                scenario['day'],
                scenario['is_weekend'],
                scenario['streak'],
                0.7,   # completion_rate_7d
                18,    # avg_completion_hour
                0,     # reminders_sent_today
                0,     # reminders_ignored_today
                24,    # time_since_last_reminder
                0,     # completed_today
                0.7,   # user_engagement_score
                0,     # location (home)
                0.6,   # phone_activity
                0,     # calendar_busy
                0.5,   # habit_difficulty
            ], dtype=np.float32)
            
            # Get Q-values and decision
            q_values = self.agent.get_q_values(state)
            action = np.argmax(q_values)
            
            print(f"  Agent Decision: {action_names[action]}")
            print(f"\n  Q-Values for all actions:")
            for i, (name, q_val) in enumerate(zip(action_names, q_values)):
                marker = "→" if i == action else " "
                print(f"    {marker} {name:<15}: {q_val:>8.3f}")
            
            # Explain the decision
            if action == Action.SEND_NOW:
                print(f"\n  💡 Agent chose to send reminder now.")
            elif action in [Action.WAIT_30_MIN, Action.WAIT_1_HOUR, Action.WAIT_2_HOURS]:
                wait_times = ['30 minutes', '1 hour', '2 hours']
                wait_idx = action - 1
                print(f"\n  💡 Agent chose to wait {wait_times[wait_idx]} before deciding.")
            else:
                print(f"\n  💡 Agent chose to skip reminders for today.")
        
        print("\n")
    
    def show_learning_insights(self):
        """
        Display insights about what the agent has learned
        """
        print("\n" + "=" * 70)
        print("What The Agent Has Learned")
        print("=" * 70 + "\n")
        
        print("The agent has been trained to optimize reminder timing by learning:\n")
        
        print("1. ⏰ Optimal Time Windows")
        print("   • Identifies when users are most receptive to reminders")
        print("   • Learns individual user patterns and preferences")
        print("   • Adapts to different days of the week\n")
        
        print("2. 🎯 Context Awareness")
        print("   • Considers user's current location and activity")
        print("   • Accounts for calendar busy status")
        print("   • Adjusts based on phone activity levels\n")
        
        print("3. 📈 Streak Preservation")
        print("   • Values maintaining habit streaks")
        print("   • More aggressive reminders when streak is at risk")
        print("   • Celebrates consistency\n")
        
        print("4. 🚫 Avoiding Spam")
        print("   • Learns not to send too many reminders")
        print("   • Adapts if user ignores reminders")
        print("   • Respects user's implicit feedback\n")
        
        print("5. 🔄 Long-term Thinking")
        print("   • Plans ahead rather than being greedy")
        print("   • Considers future consequences of actions")
        print("   • Balances immediate vs. long-term rewards\n")


def main():
    """Main demo function"""
    import sys
    
    # Find the trained model
    models_dir = "outputs/models"
    
    if not os.path.exists(models_dir):
        print("\n❌ Error: No trained models found!")
        print("Please train a model first by running: python src/train.py\n")
        sys.exit(1)
    
    # Look for final model or most recent checkpoint
    model_files = [f for f in os.listdir(models_dir) if f.endswith('.pt')]
    
    if not model_files:
        print("\n❌ Error: No trained models found!")
        print("Please train a model first by running: python src/train.py\n")
        sys.exit(1)
    
    if 'agent_final.pt' in model_files:
        model_path = os.path.join(models_dir, 'agent_final.pt')
    else:
        # Get most recent checkpoint
        model_path = os.path.join(models_dir, sorted(model_files)[-1])
    
    # Initialize demo
    demo = InteractiveDemo(model_path)
    
    # Run demonstrations
    print("\n" + "=" * 70)
    print(" " * 25 + "Demo Menu")
    print("=" * 70)
    print("\n1. Week-long simulation")
    print("2. Decision-making analysis")
    print("3. Learning insights")
    print("4. Run all demos")
    print("\n")
    
    try:
        choice = input("Select option (1-4) or press Enter for all: ").strip()
        
        if choice == '1':
            demo.run_week_simulation()
        elif choice == '2':
            demo.demonstrate_decision_making()
        elif choice == '3':
            demo.show_learning_insights()
        else:
            # Run all demos
            demo.show_learning_insights()
            demo.demonstrate_decision_making()
            demo.run_week_simulation()
        
        print("=" * 70)
        print(" " * 20 + "Demo completed! 🎉")
        print("=" * 70 + "\n")
        
    except KeyboardInterrupt:
        print("\n\nDemo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error running demo: {e}")


if __name__ == "__main__":
    main()

