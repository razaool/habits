#!/usr/bin/env python3
"""
AI Habit Coach - Main Entry Point

A machine learning powered habit tracker focused on mastering ONE habit at a time.
"""

import sys
from pathlib import Path


def show_help():
    """Show help message"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                    🎯 AI HABIT COACH                              ║
║              Master ONE Habit with ML/RL                          ║
╚══════════════════════════════════════════════════════════════════╝

COMMANDS:
  profile              Create your behavioral profile
  simulate [name]      Generate synthetic training data
  train [name]         Train ML models
  track [name]         Start tracking your habit (CLI)
  web                  Start web app (use from iPhone!)
  visualize [name]     Generate insights visualizations
  help                 Show this help message

GETTING STARTED:
  1. python main.py profile          # Answer questions about yourself
  2. python main.py simulate razaool # Generate training data
  3. python main.py train razaool    # Train initial models
  4. python main.py track razaool    # Start tracking!
  5. python main.py visualize razaool # View insights

The system will learn from your behavior and adapt over time.

EXAMPLES:
  python main.py profile
  python main.py simulate john
  python main.py train john
  python main.py track john
  python main.py visualize john
    """)


def run_profiler():
    """Run the profiling questionnaire"""
    from src.profiler import main as profiler_main
    profiler_main()


def run_simulator(profile_name: str = None):
    """Run the behavioral simulator"""
    if profile_name:
        sys.argv = ['simulator', profile_name]
    from src.simulator import main as simulator_main
    simulator_main()


def run_trainer(profile_name: str = None):
    """Run model training"""
    if profile_name:
        sys.argv = ['train', profile_name]
    from src.train import main as train_main
    train_main()


def run_tracker(profile_name: str = None):
    """Run the habit tracker"""
    if profile_name:
        sys.argv = ['app', profile_name]
    from src.app import main as app_main
    app_main()


def run_visualizer(profile_name: str = None):
    """Generate visualizations"""
    if profile_name:
        sys.argv = ['visualize', profile_name]
    from src.visualize import main as visualize_main
    visualize_main()


def run_web_app():
    """Start the web application"""
    import subprocess
    subprocess.run(['python3', 'app_web.py'])


def main():
    """Main entry point"""
    
    if len(sys.argv) < 2:
        show_help()
        return
    
    command = sys.argv[1].lower()
    
    if command == "help" or command == "--help" or command == "-h":
        show_help()
    
    elif command == "profile":
        run_profiler()
    
    elif command == "simulate":
        profile_name = sys.argv[2] if len(sys.argv) > 2 else None
        run_simulator(profile_name)
    
    elif command == "train":
        profile_name = sys.argv[2] if len(sys.argv) > 2 else None
        run_trainer(profile_name)
    
    elif command == "track":
        profile_name = sys.argv[2] if len(sys.argv) > 2 else None
        run_tracker(profile_name)
    
    elif command == "visualize" or command == "viz":
        profile_name = sys.argv[2] if len(sys.argv) > 2 else None
        run_visualizer(profile_name)
    
    elif command == "web" or command == "webapp" or command == "server":
        run_web_app()
    
    else:
        print(f"\n❌ Unknown command: {command}")
        print("Run 'python main.py help' for usage information")
        sys.exit(1)


if __name__ == "__main__":
    main()
