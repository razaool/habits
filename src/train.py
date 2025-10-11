"""Train ML models on synthetic + real data"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, mean_squared_error
from typing import Tuple, Dict, Any
import warnings
warnings.filterwarnings('ignore')


class HabitModelTrainer:
    """Train predictive models for habit completion"""
    
    def __init__(self, profile_name: str):
        self.profile_name = profile_name
        self.models_dir = Path("models")
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.completion_model = None
        self.difficulty_model = None
        self.scaler = StandardScaler()
        self.day_encoder = LabelEncoder()
        self.feature_names = None
        
    def load_data(self) -> pd.DataFrame:
        """Load synthetic and real data if available"""
        dfs = []
        
        # Load synthetic data
        synthetic_path = Path(f"data/synthetic/{self.profile_name}_synthetic.csv")
        if synthetic_path.exists():
            df_synthetic = pd.read_csv(synthetic_path)
            df_synthetic['source'] = 'synthetic'
            dfs.append(df_synthetic)
            print(f"✅ Loaded {len(df_synthetic)} synthetic days")
        else:
            print(f"❌ No synthetic data found at {synthetic_path}")
            return None
        
        # Load real data if available
        real_path = Path(f"data/real/{self.profile_name}_real.csv")
        if real_path.exists():
            df_real = pd.read_csv(real_path)
            df_real['source'] = 'real'
            dfs.append(df_real)
            print(f"✅ Loaded {len(df_real)} real days")
        else:
            print("ℹ️  No real data yet (this is expected initially)")
        
        if not dfs:
            return None
        
        df = pd.concat(dfs, ignore_index=True)
        
        # Weight real data higher
        if 'source' in df.columns:
            df['sample_weight'] = df['source'].map({'synthetic': 1.0, 'real': 3.0})
        else:
            df['sample_weight'] = 1.0
        
        return df
    
    def prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare features for modeling"""
        
        # Encode day of week
        df['day_of_week_encoded'] = self.day_encoder.fit_transform(df['day_of_week'])
        
        # Extract hour from timestamp or time_attempted
        if 'timestamp' in df.columns:
            df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        elif 'time_attempted' in df.columns:
            df['hour'] = df['time_attempted'].apply(lambda x: int(x.split(':')[0]) if isinstance(x, str) else 12)
        else:
            df['hour'] = 12  # Default to noon if no time info
        
        # Create time of day features
        df['is_morning'] = (df['hour'] >= 6) & (df['hour'] < 12)
        df['is_afternoon'] = (df['hour'] >= 12) & (df['hour'] < 17)
        df['is_evening'] = (df['hour'] >= 17) & (df['hour'] < 22)
        df['is_night'] = (df['hour'] >= 22) | (df['hour'] < 6)
        
        # Add missing columns with defaults if they don't exist
        if 'social_obligations' not in df.columns:
            df['social_obligations'] = 0
        if 'work_intensity' not in df.columns:
            df['work_intensity'] = 5  # Default middle value
        if 'motivation' not in df.columns:
            df['motivation'] = df.get('motivation_rating', 5)
        if 'difficulty' not in df.columns:
            df['difficulty'] = df.get('difficulty_rating', 5)
        
        # Fill NaN values before converting
        df['social_obligations'] = df['social_obligations'].fillna(0)
        df['work_intensity'] = df['work_intensity'].fillna(5)
        df['motivation'] = df['motivation'].fillna(5)
        df['difficulty'] = df['difficulty'].fillna(5)
        
        # Binary features
        df['social_obligations_int'] = df['social_obligations'].astype(int)
        
        # Interaction features
        df['streak_momentum'] = df['current_streak'] * df['motivation']
        df['gap_penalty'] = df['days_since_last'] * df['difficulty']
        df['stress_workload'] = df['stress_level'] * df['work_intensity']
        
        # Features for modeling
        feature_cols = [
            'day_of_week_encoded',
            'hour',
            'is_morning', 'is_afternoon', 'is_evening', 'is_night',
            'day_number',
            'current_streak',
            'days_since_last',
            'total_completions',
            'sleep_quality',
            'stress_level',
            'work_intensity',
            'social_obligations_int',
            'difficulty',
            'motivation',
            'streak_momentum',
            'gap_penalty',
            'stress_workload'
        ]
        
        X = df[feature_cols].copy()
        y = df['completed'].astype(int)
        weights = df['sample_weight']
        
        # Fill any remaining NaN values with appropriate defaults
        X = X.fillna({
            'day_of_week_encoded': 0,
            'hour': 12,
            'is_morning': False,
            'is_afternoon': False,
            'is_evening': False,
            'is_night': False,
            'day_number': df['day_number'].median(),
            'current_streak': 0,
            'days_since_last': df['days_since_last'].median(),
            'total_completions': 0,
            'sleep_quality': 6.0,
            'stress_level': 5.0,
            'work_intensity': 5.0,
            'social_obligations_int': 0,
            'difficulty': 5.0,
            'motivation': 5.0,
            'streak_momentum': 0,
            'gap_penalty': 0,
            'stress_workload': 25.0
        })
        
        # Fill any remaining NaN with column mean as last resort
        X = X.fillna(X.mean())
        
        return X, y, weights
    
    def train_completion_model(self, X: pd.DataFrame, y: pd.Series, weights: pd.Series):
        """Train model to predict habit completion"""
        print("\n🤖 Training completion predictor...")
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Split data
        X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
            X, y, weights, test_size=0.2, random_state=42, stratify=y
        )
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Train model
        self.completion_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            random_state=42,
            class_weight='balanced'
        )
        
        self.completion_model.fit(X_train_scaled, y_train, sample_weight=w_train)
        
        # Evaluate
        y_pred = self.completion_model.predict(X_test_scaled)
        accuracy = accuracy_score(y_test, y_pred)
        
        print(f"  ✅ Accuracy: {accuracy:.2%}")
        print("\n  Classification Report:")
        print(classification_report(y_test, y_pred, target_names=['Skip', 'Complete'], 
                                   zero_division=0))
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X.columns,
            'importance': self.completion_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n  Top 5 Predictive Features:")
        for idx, row in feature_importance.head().iterrows():
            print(f"    {row['feature']}: {row['importance']:.3f}")
        
        return accuracy
    
    def predict_completion_probability(self, features: Dict[str, Any]) -> float:
        """Predict probability of completing habit given context"""
        if self.completion_model is None:
            raise ValueError("Model not trained yet")
        
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        # Ensure all features exist
        for col in self.feature_names:
            if col not in df.columns:
                df[col] = 0
        
        df = df[self.feature_names]
        
        # Scale and predict
        X_scaled = self.scaler.transform(df)
        prob = self.completion_model.predict_proba(X_scaled)[0][1]  # Probability of completion
        
        return prob
    
    def save_models(self):
        """Save trained models"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        model_data = {
            'completion_model': self.completion_model,
            'scaler': self.scaler,
            'day_encoder': self.day_encoder,
            'feature_names': self.feature_names,
            'profile_name': self.profile_name,
            'trained_at': timestamp
        }
        
        filepath = self.models_dir / f"{self.profile_name}_models.joblib"
        joblib.dump(model_data, filepath)
        
        print(f"\n💾 Saved models to: {filepath}")
        return filepath
    
    @staticmethod
    def load_models(profile_name: str):
        """Load trained models"""
        filepath = Path(f"models/{profile_name}_models.joblib")
        if not filepath.exists():
            raise FileNotFoundError(f"No models found for {profile_name}")
        
        model_data = joblib.load(filepath)
        
        trainer = HabitModelTrainer(profile_name)
        trainer.completion_model = model_data['completion_model']
        trainer.scaler = model_data['scaler']
        trainer.day_encoder = model_data['day_encoder']
        trainer.feature_names = model_data.get('feature_names', None)
        
        return trainer
    
    def get_optimal_times(self, day_of_week: str, n_times: int = 3) -> list:
        """Get optimal times to attempt habit on given day"""
        if self.completion_model is None:
            raise ValueError("Model not trained yet")
        
        # Test different hours
        hours = range(6, 23)  # 6am to 10pm
        probabilities = []
        
        for hour in hours:
            features = {
                'day_of_week_encoded': self.day_encoder.transform([day_of_week])[0],
                'hour': hour,
                'is_morning': 6 <= hour < 12,
                'is_afternoon': 12 <= hour < 17,
                'is_evening': 17 <= hour < 22,
                'is_night': hour >= 22,
                'day_number': 30,  # assume mid-journey
                'current_streak': 7,  # assume moderate streak
                'days_since_last': 0,
                'total_completions': 30,
                'sleep_quality': 7,
                'stress_level': 5,
                'work_intensity': 5,
                'social_obligations_int': 0,
                'difficulty': 5,
                'motivation': 7,
                'streak_momentum': 49,
                'gap_penalty': 0,
                'stress_workload': 25
            }
            
            prob = self.predict_completion_probability(features)
            probabilities.append((hour, prob))
        
        # Sort by probability
        probabilities.sort(key=lambda x: x[1], reverse=True)
        
        return probabilities[:n_times]


def main():
    """Train models from command line"""
    import sys
    
    print("\n" + "="*70)
    print("  🤖 MODEL TRAINING")
    print("="*70)
    
    # Get profile name
    if len(sys.argv) > 1:
        profile_name = sys.argv[1]
    else:
        profile_name = input("\nEnter profile name: ").strip()
    
    # Initialize trainer
    trainer = HabitModelTrainer(profile_name)
    
    # Load data
    df = trainer.load_data()
    if df is None:
        print("\n❌ No data available for training")
        return
    
    print(f"\n📊 Total data points: {len(df)}")
    print(f"   Completion rate: {df['completed'].mean():.1%}")
    
    # Prepare features
    X, y, weights = trainer.prepare_features(df)
    
    # Train models
    trainer.train_completion_model(X, y, weights)
    
    # Save models
    trainer.save_models()
    
    # Show optimal times
    print("\n" + "="*70)
    print("  📅 OPTIMAL TIMES ANALYSIS")
    print("="*70)
    
    days = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']
    
    for day in days:
        optimal_times = trainer.get_optimal_times(day, n_times=3)
        print(f"\n  {day.capitalize()}:")
        for hour, prob in optimal_times:
            print(f"    {hour:02d}:00 - {prob:.1%} success probability")
    
    print("\n" + "="*70)
    print("  ✅ TRAINING COMPLETE!")
    print("="*70)
    print("\nNext step: Start tracking your habit")
    print("  python -m src.app")


if __name__ == "__main__":
    main()
