"""
Quick Start Script - Train a small model quickly to test the system

This script trains a minimal model (50 episodes) to verify everything works.
For full training, use: python src/train.py
"""

import os
import sys
import yaml

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from train import Trainer


def quick_start():
    """Run a quick training session to verify setup"""
    print("\n" + "=" * 70)
    print(" " * 20 + "🚀 Quick Start Demo")
    print("=" * 70)
    print("\nThis will train a small model (50 episodes) to verify your setup.")
    print("For full training, use: python src/train.py\n")
    
    # Load config and modify for quick training
    with open("config.yaml", 'r') as f:
        config = yaml.safe_load(f)
    
    # Reduce training time
    config['training']['num_episodes'] = 50
    config['training']['max_steps_per_episode'] = 50
    config['training']['save_freq'] = 25
    config['training']['eval_freq'] = 10
    
    # Save temporary config
    temp_config_path = "config_quickstart.yaml"
    with open(temp_config_path, 'w') as f:
        yaml.dump(config, f)
    
    try:
        # Initialize and train
        trainer = Trainer(temp_config_path)
        trainer.train()
        
        print("\n" + "=" * 70)
        print("✅ Quick start completed successfully!")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Check outputs/plots/ for training curves")
        print("2. Run full training: python src/train.py")
        print("3. Visualize results: python src/visualize.py")
        print("4. Run demo: python src/demo.py")
        print("\n")
        
    finally:
        # Cleanup temp config
        if os.path.exists(temp_config_path):
            os.remove(temp_config_path)


if __name__ == "__main__":
    try:
        quick_start()
    except KeyboardInterrupt:
        print("\n\nQuick start interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nIf you're having issues, please check:")
        print("1. All dependencies are installed: pip install -r requirements.txt")
        print("2. You're in the correct directory")
        print("3. config.yaml exists")
        sys.exit(1)

