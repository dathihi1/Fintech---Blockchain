"""
Convert Large CSV Datasets to Training Format
Converts the Kaggle financial news dataset (1.8M+ records) to NLP training format
"""

import os
import json
import pandas as pd
from typing import List, Dict
import random

# Paths
DATASETS_DIR = "ml/training/datasets"
OUTPUT_DIR = "ml/training"


def load_csv_dataset(filename: str, max_rows: int = None) -> pd.DataFrame:
    """Load CSV dataset with optional row limit"""
    filepath = os.path.join(DATASETS_DIR, filename)
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None
    
    print(f"📁 Loading {filename}...")
    
    try:
        if max_rows:
            df = pd.read_csv(filepath, nrows=max_rows)
        else:
            df = pd.read_csv(filepath)
        
        print(f"   Loaded {len(df):,} rows")
        return df
    except Exception as e:
        print(f"❌ Error loading {filename}: {e}")
        return None


def convert_analyst_ratings(df: pd.DataFrame) -> List[Dict]:
    """
    Convert analyst_ratings_processed.csv to NLP training format.
    Columns: date, stock, company, headline, url
    """
    dataset = []
    
    for _, row in df.iterrows():
        headline = row.get('headline') or row.get('title') or row.get('Headline')
        if not headline or pd.isna(headline):
            continue
        
        # Infer sentiment from keywords
        text = str(headline).lower()
        
        if any(w in text for w in ['upgrade', 'buy', 'positive', 'bullish', 'outperform', 'raise', 'beat']):
            sentiment = "positive"
            sentiment_score = 0.6
        elif any(w in text for w in ['downgrade', 'sell', 'negative', 'bearish', 'underperform', 'cut', 'miss']):
            sentiment = "negative"
            sentiment_score = -0.6
        else:
            sentiment = "neutral"
            sentiment_score = 0.0
        
        dataset.append({
            "text": str(headline)[:500],  # Truncate long headlines
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "emotions": [],
            "behavioral_flags": [],
            "quality_score": 0.5,
            "trade_result": "unknown",
            "pnl_pct": None
        })
    
    return dataset


def convert_partner_headlines(df: pd.DataFrame) -> List[Dict]:
    """
    Convert raw_partner_headlines.csv to NLP training format.
    """
    dataset = []
    
    # Find text column
    text_col = None
    for col in ['headline', 'title', 'Headline', 'Title', 'text']:
        if col in df.columns:
            text_col = col
            break
    
    if not text_col:
        print(f"   ⚠️ No text column found. Columns: {df.columns.tolist()}")
        return []
    
    print(f"   Using column: {text_col}")
    
    for _, row in df.iterrows():
        headline = row.get(text_col)
        if not headline or pd.isna(headline):
            continue
        
        text = str(headline).lower()
        
        # Infer sentiment
        if any(w in text for w in ['surge', 'jump', 'gain', 'rally', 'rise', 'up', 'high', 'record']):
            sentiment = "positive"
            sentiment_score = 0.5
        elif any(w in text for w in ['fall', 'drop', 'plunge', 'crash', 'down', 'low', 'loss', 'decline']):
            sentiment = "negative"
            sentiment_score = -0.5
        else:
            sentiment = "neutral"
            sentiment_score = 0.0
        
        dataset.append({
            "text": str(headline)[:500],
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "emotions": [],
            "behavioral_flags": [],
            "quality_score": 0.5,
            "trade_result": "unknown",
            "pnl_pct": None
        })
    
    return dataset


def convert_twitter_data(filepath: str) -> List[Dict]:
    """Convert HuggingFace Twitter sentiment JSON"""
    if not os.path.exists(filepath):
        return []
    
    print(f"📁 Loading Twitter data...")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    dataset = []
    for item in data:
        text = item.get('text') or item.get('sentence')
        if not text:
            continue
        
        label = item.get('label', 1)
        if isinstance(label, str):
            if 'positive' in label.lower() or label == '2':
                sentiment = "positive"
                score = 0.6
            elif 'negative' in label.lower() or label == '0':
                sentiment = "negative"
                score = -0.6
            else:
                sentiment = "neutral"
                score = 0.0
        else:
            # Numeric labels: 0=negative, 1=neutral, 2=positive
            if label == 2 or label == 1:
                sentiment = "positive"
                score = 0.6
            elif label == 0:
                sentiment = "negative"
                score = -0.6
            else:
                sentiment = "neutral"
                score = 0.0
        
        dataset.append({
            "text": str(text)[:500],
            "sentiment": sentiment,
            "sentiment_score": score,
            "emotions": [],
            "behavioral_flags": [],
            "quality_score": 0.5,
            "trade_result": "unknown",
            "pnl_pct": None
        })
    
    print(f"   Converted {len(dataset):,} records")
    return dataset


def balance_dataset(dataset: List[Dict], max_per_class: int = None) -> List[Dict]:
    """Balance dataset by undersampling majority class"""
    by_sentiment = {"positive": [], "neutral": [], "negative": []}
    
    for item in dataset:
        by_sentiment[item['sentiment']].append(item)
    
    # Find minimum class size
    min_size = min(len(v) for v in by_sentiment.values())
    
    if max_per_class:
        min_size = min(min_size, max_per_class)
    
    print(f"\n📊 Balancing dataset:")
    for label, items in by_sentiment.items():
        print(f"   {label}: {len(items):,} → {min_size:,}")
    
    balanced = []
    for label, items in by_sentiment.items():
        random.shuffle(items)
        balanced.extend(items[:min_size])
    
    random.shuffle(balanced)
    return balanced


def main():
    print("=" * 60)
    print("📊 Converting Large Datasets to NLP Training Format")
    print("=" * 60)
    
    all_data = []
    
    # 1. Convert analyst_ratings_processed.csv (main dataset)
    csv_files = [
        ("analyst_ratings_processed.csv", convert_analyst_ratings),
        ("raw_partner_headlines.csv", convert_partner_headlines),
    ]
    
    for filename, converter in csv_files:
        filepath = os.path.join(DATASETS_DIR, filename)
        if os.path.exists(filepath):
            # Load with limit to avoid memory issues
            df = load_csv_dataset(filename, max_rows=500000)  # 500K max per file
            if df is not None:
                data = converter(df)
                print(f"   Converted {len(data):,} records")
                all_data.extend(data)
    
    # 2. Convert Twitter/HuggingFace JSON
    twitter_file = os.path.join(DATASETS_DIR, "zeroshot_twitter-financial-news-sentiment.json")
    if os.path.exists(twitter_file):
        twitter_data = convert_twitter_data(twitter_file)
        all_data.extend(twitter_data)
    
    if not all_data:
        print("\n❌ No data converted. Check that datasets exist in:")
        print(f"   {DATASETS_DIR}/")
        return
    
    print(f"\n📈 Total records: {len(all_data):,}")
    
    # 3. Balance dataset
    balanced = balance_dataset(all_data, max_per_class=100000)  # 100K per class max
    
    # 4. Save to nlp_dataset.json
    output_file = os.path.join(OUTPUT_DIR, "nlp_dataset.json")
    
    print(f"\n💾 Saving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(balanced, f, ensure_ascii=False, indent=2)
    
    print(f"   Saved {len(balanced):,} records")
    
    # 5. Generate stats
    print("\n📊 Final Dataset Statistics:")
    sentiments = {"positive": 0, "neutral": 0, "negative": 0}
    for item in balanced:
        sentiments[item['sentiment']] += 1
    
    for label, count in sentiments.items():
        pct = count / len(balanced) * 100
        print(f"   {label}: {count:,} ({pct:.1f}%)")
    
    print("\n" + "=" * 60)
    print("✅ Conversion complete!")
    print("=" * 60)
    print("\nNext: python ml/training/train_nlp.py")


if __name__ == "__main__":
    main()
