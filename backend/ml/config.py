"""
ML Training Configuration
"""

# Model configurations
NLP_CONFIG = {
    # Base model for fine-tuning
    "base_model": "ProsusAI/finbert",
    
    # Alternative smaller models
    "base_model_alt": "distilbert-base-uncased-finetuned-sst-2-english",
    
    # Fine-tuning hyperparameters
    "learning_rate": 2e-5,
    "batch_size": 16,
    "epochs": 3,
    "warmup_steps": 100,
    "weight_decay": 0.01,
    
    # Data split
    "train_split": 0.8,
    "val_split": 0.1,
    "test_split": 0.1,
    
    # Max sequence length
    "max_length": 128,
    
    # Labels
    "sentiment_labels": ["negative", "neutral", "positive"],
    "emotion_labels": ["FOMO", "FEAR", "GREED", "REVENGE", "RATIONAL", "CONFIDENT", "DISCIPLINE", "NEUTRAL"]
}

BEHAVIORAL_CONFIG = {
    # Model type
    "model_type": "xgboost",  # Options: xgboost, random_forest, neural_net
    
    # Features to use
    "features": [
        "time_since_last_trade_minutes",
        "last_trade_pnl",
        "last_trade_pnl_pct",
        "trades_last_hour",
        "trades_last_day",
        "win_streak",
        "loss_streak",
        "session_pnl",
        "session_drawdown_pct",
        "note_sentiment",
        "note_has_fomo_keywords",
        "note_has_revenge_keywords",
        "note_length",
        "price_change_1h",
        "volatility_1h"
    ],
    
    # Target labels
    "target_labels": ["NORMAL", "FOMO", "REVENGE_TRADING", "TILT"],
    
    # XGBoost parameters
    "xgboost_params": {
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "objective": "multi:softmax",
        "eval_metric": "mlogloss"
    },
    
    # Training parameters
    "test_size": 0.2,
    "random_state": 42
}

# Paths
MODEL_PATHS = {
    "nlp_model": "ml/models/finbert_trading_vi",
    "nlp_model_fallback": "ProsusAI/finbert",
    "phobert_model": "ml/models/phobert_trading_vi",
    "phobert_fallback": "vinai/phobert-base",
    "behavioral_model": "ml/models/behavioral_classifier.json",
    "feature_scaler": "ml/models/feature_scaler.pkl"
}

# Model Versioning
MODEL_VERSIONS = {
    "nlp_finbert": {
        "version": "1.0.0",
        "path": "ml/models/finbert_trading_vi",
        "trained_at": "2026-01-26",
        "metrics": {"accuracy": 0.85, "f1": 0.82},
        "base_model": "ProsusAI/finbert"
    },
    "nlp_phobert": {
        "version": "1.0.0",
        "path": "ml/models/phobert_trading_vi",
        "trained_at": "2026-01-26",
        "metrics": {"accuracy": 0.87, "f1": 0.84},
        "base_model": "vinai/phobert-base"
    },
    "behavioral_xgboost": {
        "version": "1.0.0",
        "path": "ml/models/behavioral_classifier.json",
        "trained_at": "2026-01-26",
        "metrics": {"accuracy": 0.78, "f1": 0.75}
    }
}

# Database
DATABASE_URL = "sqlite:///./trading_journal.db"
