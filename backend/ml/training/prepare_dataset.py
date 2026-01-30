"""
Prepare Dataset for ML Training
Exports trade notes and labels from database for NLP and behavioral model training
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from ml.config import NLP_CONFIG, BEHAVIORAL_CONFIG, DATABASE_URL


def load_trades_from_db():
    """Load all trades from database"""
    engine = create_engine(DATABASE_URL)
    
    query = """
    SELECT 
        t.id,
        t.user_id,
        t.symbol,
        t.side,
        t.entry_price,
        t.exit_price,
        t.quantity,
        t.pnl,
        t.pnl_pct,
        t.entry_time,
        t.exit_time,
        t.hold_duration_minutes,
        t.notes,
        t.nlp_sentiment,
        t.nlp_emotions,
        t.nlp_quality_score,
        t.behavioral_flags
    FROM trades t
    WHERE t.notes IS NOT NULL AND t.notes != ''
    ORDER BY t.entry_time DESC
    """
    
    df = pd.read_sql(query, engine)
    return df


def prepare_nlp_dataset(df: pd.DataFrame, output_path: str = "ml/training/nlp_dataset.json"):
    """
    Prepare dataset for NLP model fine-tuning.
    
    Format:
    {
        "text": "FOMO vào lệnh, pump quá nhanh",
        "sentiment": "negative",
        "emotions": ["FOMO"],
        "quality_score": 0.35
    }
    """
    dataset = []
    
    for _, row in df.iterrows():
        if not row['notes']:
            continue
            
        # Determine sentiment label
        sentiment = "neutral"
        if row['nlp_sentiment']:
            if row['nlp_sentiment'] > 0.2:
                sentiment = "positive"
            elif row['nlp_sentiment'] < -0.2:
                sentiment = "negative"
        
        # Parse emotions
        emotions = []
        if row['nlp_emotions']:
            try:
                emotions_data = json.loads(row['nlp_emotions']) if isinstance(row['nlp_emotions'], str) else row['nlp_emotions']
                emotions = [e.get('type', e) for e in emotions_data] if emotions_data else []
            except:
                pass
        
        # Parse behavioral flags
        flags = []
        if row['behavioral_flags']:
            try:
                flags = json.loads(row['behavioral_flags']) if isinstance(row['behavioral_flags'], str) else row['behavioral_flags']
            except:
                pass
        
        dataset.append({
            "text": row['notes'],
            "sentiment": sentiment,
            "sentiment_score": row['nlp_sentiment'] or 0,
            "emotions": emotions,
            "behavioral_flags": flags,
            "quality_score": row['nlp_quality_score'] or 0.5,
            "trade_result": "win" if row['pnl'] and row['pnl'] > 0 else "loss" if row['pnl'] else "open",
            "pnl_pct": row['pnl_pct']
        })
    
    # Save dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"✅ NLP dataset saved: {output_path}")
    print(f"   Total samples: {len(dataset)}")
    print(f"   Sentiment distribution:")
    for s in ["positive", "neutral", "negative"]:
        count = len([d for d in dataset if d['sentiment'] == s])
        print(f"      {s}: {count} ({count/len(dataset)*100:.1f}%)")
    
    return dataset


def prepare_behavioral_dataset(df: pd.DataFrame, output_path: str = "ml/training/behavioral_dataset.json"):
    """
    Prepare dataset for behavioral pattern classifier.
    Creates features from trade sequences.
    """
    # Sort by user and time
    df = df.sort_values(['user_id', 'entry_time'])
    
    dataset = []
    
    for user_id in df['user_id'].unique():
        user_trades = df[df['user_id'] == user_id].copy()
        
        for i in range(1, len(user_trades)):
            current = user_trades.iloc[i]
            previous = user_trades.iloc[i-1]
            
            # Calculate time since last trade
            time_diff = None
            if current['entry_time'] and previous['exit_time']:
                try:
                    curr_time = pd.to_datetime(current['entry_time'])
                    prev_exit = pd.to_datetime(previous['exit_time'])
                    time_diff = (curr_time - prev_exit).total_seconds() / 60
                except:
                    pass
            
            # Determine target label from behavioral flags
            flags = []
            if current['behavioral_flags']:
                try:
                    flags = json.loads(current['behavioral_flags']) if isinstance(current['behavioral_flags'], str) else current['behavioral_flags']
                except:
                    pass
            
            target = "NORMAL"
            if "TILT" in flags:
                target = "TILT"
            elif "REVENGE" in flags or "REVENGE_TRADING" in flags:
                target = "REVENGE_TRADING"
            elif "FOMO" in flags:
                target = "FOMO"
            
            # Create feature dict
            features = {
                "time_since_last_trade_minutes": time_diff or 60,
                "last_trade_pnl": previous['pnl'] or 0,
                "last_trade_pnl_pct": previous['pnl_pct'] or 0,
                "note_sentiment": current['nlp_sentiment'] or 0,
                "note_quality": current['nlp_quality_score'] or 0.5,
                "note_length": len(current['notes']) if current['notes'] else 0,
                "target": target,
                "trade_id": current['id']
            }
            
            dataset.append(features)
    
    # Save dataset
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Behavioral dataset saved: {output_path}")
    print(f"   Total samples: {len(dataset)}")
    print(f"   Label distribution:")
    for label in BEHAVIORAL_CONFIG['target_labels']:
        count = len([d for d in dataset if d['target'] == label])
        print(f"      {label}: {count}")
    
    return dataset


def main():
    print("=" * 50)
    print("📊 Preparing ML Training Datasets")
    print("=" * 50)
    
    # Load data from database
    print("\n📁 Loading trades from database...")
    try:
        df = load_trades_from_db()
        print(f"   Found {len(df)} trades with notes")
    except Exception as e:
        print(f"❌ Error loading from database: {e}")
        print("\n💡 Creating sample dataset for demonstration...")
        
        # Create sample data if no database
        sample_data = [
            {"id": 1, "user_id": "demo", "symbol": "BTCUSDT", "notes": "Entry theo plan, breakout confirmed", 
             "nlp_sentiment": 0.5, "nlp_emotions": None, "behavioral_flags": None, "pnl": 100, "pnl_pct": 2.5},
            {"id": 2, "user_id": "demo", "symbol": "ETHUSDT", "notes": "FOMO vào vội, pump quá nhanh", 
             "nlp_sentiment": -0.3, "nlp_emotions": '[{"type": "FOMO"}]', "behavioral_flags": '["FOMO"]', "pnl": -50, "pnl_pct": -1.5},
            {"id": 3, "user_id": "demo", "symbol": "SOLUSDT", "notes": "Gỡ lỗ từ lệnh trước, tăng size gấp đôi", 
             "nlp_sentiment": -0.4, "nlp_emotions": '[{"type": "REVENGE"}]', "behavioral_flags": '["REVENGE"]', "pnl": -80, "pnl_pct": -3.2},
        ]
        df = pd.DataFrame(sample_data)
        df['entry_time'] = pd.Timestamp.now()
        df['exit_time'] = pd.Timestamp.now()
        df['entry_price'] = 50000
        df['exit_price'] = 50100
        df['quantity'] = 0.1
        df['nlp_quality_score'] = 0.5
        df['side'] = 'long'
        df['hold_duration_minutes'] = 30
    
    if len(df) == 0:
        print("❌ No data found. Please add trades first.")
        return
    
    # Prepare NLP dataset
    print("\n📝 Preparing NLP dataset...")
    prepare_nlp_dataset(df)
    
    # Prepare behavioral dataset
    print("\n🧠 Preparing behavioral dataset...")
    prepare_behavioral_dataset(df)
    
    print("\n" + "=" * 50)
    print("✅ Dataset preparation complete!")
    print("=" * 50)
    print("\nNext steps:")
    print("  1. python ml/training/train_nlp.py")
    print("  2. python ml/behavioral/train_classifier.py")


if __name__ == "__main__":
    main()
