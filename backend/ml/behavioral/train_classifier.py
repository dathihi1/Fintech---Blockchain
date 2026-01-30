"""
Behavioral Pattern Classifier
Trains XGBoost model to predict FOMO/Revenge/Tilt patterns
Enhanced with model registry and better synthetic data generation
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import pickle
import numpy as np
import pandas as pd
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix, f1_score, precision_score, recall_score

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️ XGBoost not installed. Run: pip install xgboost")

from ml.config import BEHAVIORAL_CONFIG, MODEL_PATHS
from ml.model_registry import get_model_registry, ModelMetrics


def load_dataset(path: str = "ml/training/behavioral_dataset.json"):
    """Load prepared behavioral dataset"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return pd.DataFrame(data)


def generate_synthetic_samples(label: str, n: int = 10) -> List[Dict]:
    """
    Generate realistic synthetic samples for a given behavioral pattern.
    Uses domain knowledge instead of pure random numbers.
    
    Args:
        label: Target label (NORMAL, FOMO, REVENGE_TRADING, TILT)
        n: Number of samples to generate
        
    Returns:
        List of synthetic samples
    """
    samples = []
    
    for _ in range(n):
        if label == "FOMO":
            # FOMO: Quick trades after seeing price movement, high sentiment
            sample = {
                'time_since_last_trade_minutes': np.random.randint(5, 30),  # Quick succession
                'last_trade_pnl': np.random.uniform(-50, -20),  # Often after a loss
                'last_trade_pnl_pct': np.random.uniform(-3, -1),
                'note_sentiment': np.random.uniform(0.3, 0.8),  # Positive (excited)
                'note_quality': np.random.uniform(0.1, 0.4),  # Low quality reasoning
                'note_length': np.random.randint(20, 80),
                'target': label
            }
        elif label == "REVENGE_TRADING":
            # Revenge: After losses, increasing size, negative sentiment
            sample = {
                'time_since_last_trade_minutes': np.random.randint(2, 15),  # Very quick
                'last_trade_pnl': np.random.uniform(-100, -30),  # After big loss
                'last_trade_pnl_pct': np.random.uniform(-8, -2),
                'note_sentiment': np.random.uniform(-0.8, -0.2),  # Negative/frustrated
                'note_quality': np.random.uniform(0.1, 0.3),  # Very low quality
                'note_length': np.random.randint(30, 100),
                'target': label
            }
        elif label == "TILT":
            # Tilt: Multiple quick trades, erratic, very low quality
            sample = {
                'time_since_last_trade_minutes': np.random.randint(1, 10),  # Extremely quick
                'last_trade_pnl': np.random.uniform(-150, 50),  # Random results
                'last_trade_pnl_pct': np.random.uniform(-10, 5),
                'note_sentiment': np.random.uniform(-1, 1),  # Erratic sentiment
                'note_quality': np.random.uniform(0.0, 0.2),  # Extremely low quality
                'note_length': np.random.randint(10, 50),
                'target': label
            }
        else:  # NORMAL
            # Normal: Planned trades, reasonable timing, high quality
            sample = {
                'time_since_last_trade_minutes': np.random.randint(30, 240),  # Patient
                'last_trade_pnl': np.random.uniform(-30, 60),  # Balanced results
                'last_trade_pnl_pct': np.random.uniform(-2, 4),
                'note_sentiment': np.random.uniform(-0.3, 0.5),  # Balanced sentiment
                'note_quality': np.random.uniform(0.5, 1.0),  # High quality
                'note_length': np.random.randint(50, 200),
                'target': label
            }
        
        samples.append(sample)
    
    return samples
    """Prepare features for training"""
    feature_cols = [col for col in df.columns if col not in ['target', 'trade_id']]
    
    X = df[feature_cols].copy()
    y = df['target'].copy()
    
    # Handle missing values
    X = X.fillna(0)
    
    return X, y, feature_cols


def train_xgboost(X_train, y_train, X_val, y_val, label_encoder):
    """Train XGBoost classifier"""
    # Encode labels
    y_train_enc = label_encoder.fit_transform(y_train)
    y_val_enc = label_encoder.transform(y_val)
    
    # Create DMatrix
    dtrain = xgb.DMatrix(X_train, label=y_train_enc)
    dval = xgb.DMatrix(X_val, label=y_val_enc)
    
    # Parameters
    params = BEHAVIORAL_CONFIG['xgboost_params'].copy()
    params['num_class'] = len(label_encoder.classes_)
    
    # Train
    evals = [(dtrain, 'train'), (dval, 'val')]
    model = xgb.train(
        params,
        dtrain,
        num_boost_round=100,
        evals=evals,
        early_stopping_rounds=10,
        verbose_eval=10
    )
    
    return model


def evaluate_model(model, X_test, y_test, label_encoder, feature_names):
    """Evaluate model performance"""
    y_test_enc = label_encoder.transform(y_test)
    
    dtest = xgb.DMatrix(X_test)
    preds_proba = model.predict(dtest)
    preds = np.argmax(preds_proba, axis=1) if len(preds_proba.shape) > 1 else preds_proba.astype(int)
    
    accuracy = accuracy_score(y_test_enc, preds)
    
    print("\n📊 Classification Report:")
    # Get unique labels in test set
    unique_labels = sorted(set(y_test_enc) | set(preds))
    label_names = [label_encoder.classes_[i] for i in unique_labels if i < len(label_encoder.classes_)]
    
    print(classification_report(
        y_test_enc, preds, 
        labels=unique_labels,
        target_names=label_names,
        zero_division=0
    ))
    
    print("\n🔍 Feature Importance:")
    importance = model.get_score(importance_type='gain')
    sorted_importance = sorted(importance.items(), key=lambda x: x[1], reverse=True)
    for feat, score in sorted_importance[:10]:
        print(f"   {feat}: {score:.4f}")
    
    return accuracy, preds


def save_model(model, scaler, label_encoder, feature_names):
    """Save trained model and preprocessing objects"""
    os.makedirs(os.path.dirname(MODEL_PATHS['behavioral_model']), exist_ok=True)
    
    # Save XGBoost model
    model.save_model(MODEL_PATHS['behavioral_model'].replace('.pkl', '.json'))
    
    # Save scaler and label encoder
    with open(MODEL_PATHS['feature_scaler'], 'wb') as f:
        pickle.dump({
            'scaler': scaler,
            'label_encoder': label_encoder,
            'feature_names': feature_names
        }, f)
    
    print(f"💾 Model saved to: {MODEL_PATHS['behavioral_model']}")
    print(f"💾 Scaler saved to: {MODEL_PATHS['feature_scaler']}")


def main():
    print("=" * 50)
    print("🧠 Behavioral Pattern Classifier Training")
    print("=" * 50)
    
    if not XGBOOST_AVAILABLE:
        print("\n❌ Cannot train without XGBoost library")
        print("   Install with: pip install xgboost")
        return
    
    # Load dataset
    dataset_path = "ml/training/behavioral_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"\n❌ Dataset not found: {dataset_path}")
        print("   Run prepare_dataset.py first")
        return
    
    print(f"\n📁 Loading dataset from {dataset_path}")
    df = load_dataset(dataset_path)
    print(f"   Total samples: {len(df)}")
    
    # Check label distribution
    print("\n📊 Label distribution:")
    print(df['target'].value_counts())
    
    if len(df) < 10:
        print("\n⚠️ Very small dataset. Adding realistic synthetic samples...")
        # Add realistic synthetic samples based on behavioral patterns
        synthetic = []
        for label in BEHAVIORAL_CONFIG['target_labels']:
            synthetic.extend(generate_synthetic_samples(label, n=15))
        
        df = pd.concat([df, pd.DataFrame(synthetic)], ignore_index=True)
        print(f"   New total samples: {len(df)}")
    
    # Prepare features
    X, y, feature_names = prepare_features(df)
    print(f"\n📐 Features: {feature_names}")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    X_scaled = pd.DataFrame(X_scaled, columns=feature_names)
    
    # Encode labels
    label_encoder = LabelEncoder()
    
    # Split data
    X_train, X_temp, y_train, y_temp = train_test_split(
        X_scaled, y, 
        test_size=BEHAVIORAL_CONFIG['test_size'],
        random_state=BEHAVIORAL_CONFIG['random_state'],
        stratify=y
    )
    
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp, y_temp,
        test_size=0.5,
        random_state=BEHAVIORAL_CONFIG['random_state']
    )
    
    print(f"\n📊 Data split:")
    print(f"   Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
    
    # Train model
    print("\n🚀 Training XGBoost classifier...")
    model = train_xgboost(X_train, y_train, X_val, y_val, label_encoder)
    
    # Evaluate
    accuracy, preds = evaluate_model(model, X_test, y_test, label_encoder, feature_names)
    
    # Calculate additional metrics for registry
    y_test_enc = label_encoder.transform(y_test)
    precision = precision_score(y_test_enc, preds, average='macro', zero_division=0)
    recall = recall_score(y_test_enc, preds, average='macro', zero_division=0)
    f1 = f1_score(y_test_enc, preds, average='macro', zero_division=0)
    
    # Save model
    save_model(model, scaler, label_encoder, feature_names)
    
    # Register model in registry
    print("\n📝 Registering model in registry...")
    registry = get_model_registry()
    metrics = ModelMetrics(
        accuracy=float(accuracy),
        precision=float(precision),
        recall=float(recall),
        f1_score=float(f1),
        samples_tested=len(X_test)
    )
    
    model_version = registry.register_model(
        model_id=f"behavioral_xgboost_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        version="1.0.0",
        model_type="behavioral_pattern",
        path=MODEL_PATHS['behavioral_model'],
        base_model="XGBoost",
        metrics=metrics,
        notes="Trained with realistic synthetic data augmentation"
    )
    
    # Activate model
    registry.activate_model(model_version.version)
    
    print("\n" + "=" * 50)
    print(f"✅ Training complete!")
    print(f"   Test accuracy: {accuracy:.4f}")
    print(f"   F1 Score: {f1:.4f}")
    print(f"   Model registered and activated")
    print("=" * 50)


if __name__ == "__main__":
    main()
