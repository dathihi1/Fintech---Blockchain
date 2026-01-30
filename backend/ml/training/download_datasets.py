"""
Download Large Training Datasets for Financial NLP and Behavioral Analysis
Sources: Kaggle, HuggingFace, and public repositories
"""

import os
import sys
import json
from pathlib import Path

# Try to import required libraries
try:
    from datasets import load_dataset
    HF_AVAILABLE = True
except ImportError:
    HF_AVAILABLE = False
    print("⚠️ Install: pip install datasets")

try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("⚠️ Install: pip install pandas")


# Dataset configurations
DATASETS = {
    "financial_phrasebank": {
        "source": "huggingface",
        "name": "financial_phrasebank",
        "subset": "sentences_allagree",
        "description": "4,845 financial sentences with sentiment labels",
        "size": "~5K"
    },
    "financial_tweets": {
        "source": "huggingface", 
        "name": "zeroshot/twitter-financial-news-sentiment",
        "subset": None,
        "description": "11,932 financial tweets with sentiment",
        "size": "~12K"
    },
    "stocktwits_crypto": {
        "source": "huggingface",
        "name": "TimKoworkerData/stocktwits-crypto",
        "subset": None,
        "description": "Crypto trading sentiment from StockTwits",
        "size": "~200K"
    },
    "trading_sentiment": {
        "source": "huggingface",
        "name": "nickmuchi/financial-classification",
        "subset": None,
        "description": "Financial news classification",
        "size": "~10K"
    }
}

# Kaggle datasets (require kaggle CLI)
KAGGLE_DATASETS = {
    "daily_financial_news": {
        "name": "miguelaenlle/massive-stock-news-analysis-db-for-nlpbacktests",
        "description": "1.8M+ stock news headlines",
        "file": "analyst_ratings_processed.csv"
    },
    "stock_tweets": {
        "name": "equinton/stock-tweets-for-sentiment-analysis-and-prediction",
        "description": "Stock tweets with price data",
        "file": "stocktweets.csv"
    },
    "crypto_reddit": {
        "name": "gpreda/reddit-cryptocurrency-data",
        "description": "Crypto discussions from Reddit",
        "file": "reddit_cryptocurrency.csv"
    }
}


def download_huggingface_dataset(config: dict, output_dir: str) -> int:
    """Download dataset from HuggingFace"""
    if not HF_AVAILABLE:
        print("❌ datasets library not installed")
        return 0
    
    print(f"📥 Downloading: {config['name']}...")
    
    try:
        if config['subset']:
            dataset = load_dataset(config['name'], config['subset'])
        else:
            dataset = load_dataset(config['name'])
        
        # Get all splits
        all_data = []
        for split_name in dataset.keys():
            split_data = dataset[split_name]
            for item in split_data:
                all_data.append(item)
        
        # Save to JSON
        output_file = os.path.join(output_dir, f"{config['name'].replace('/', '_')}.json")
        os.makedirs(output_dir, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Saved {len(all_data)} records to {output_file}")
        return len(all_data)
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return 0


def download_kaggle_dataset(config: dict, output_dir: str) -> int:
    """Download dataset from Kaggle (requires kaggle CLI configured)"""
    try:
        import kaggle
        kaggle.api.authenticate()
        
        print(f"📥 Downloading from Kaggle: {config['name']}...")
        
        kaggle.api.dataset_download_files(
            config['name'], 
            path=output_dir, 
            unzip=True
        )
        
        print(f"   ✅ Downloaded to {output_dir}")
        return -1  # Unknown count
        
    except ImportError:
        print("❌ kaggle library not installed. Run: pip install kaggle")
        print("   Also set up ~/.kaggle/kaggle.json with your API key")
        return 0
    except Exception as e:
        print(f"   ❌ Kaggle error: {e}")
        return 0


def convert_to_training_format(input_file: str, output_file: str, format_type: str = "nlp"):
    """Convert downloaded dataset to our training format"""
    if not PANDAS_AVAILABLE:
        print("❌ pandas not installed")
        return
    
    print(f"🔄 Converting {input_file} to training format...")
    
    try:
        # Load data
        if input_file.endswith('.json'):
            with open(input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            df = pd.DataFrame(data)
        else:
            df = pd.read_csv(input_file)
        
        converted = []
        
        for _, row in df.iterrows():
            # Try to find text column
            text = None
            for col in ['sentence', 'text', 'title', 'headline', 'content', 'body']:
                if col in row and row[col]:
                    text = str(row[col])
                    break
            
            if not text:
                continue
            
            # Try to find sentiment
            sentiment = "neutral"
            sentiment_score = 0.0
            
            for col in ['label', 'sentiment', 'sentiment_label']:
                if col in row:
                    label = str(row[col]).lower()
                    if 'positive' in label or label in ['1', 'bullish', 'pos']:
                        sentiment = "positive"
                        sentiment_score = 0.6
                    elif 'negative' in label or label in ['0', 'bearish', 'neg']:
                        sentiment = "negative"
                        sentiment_score = -0.6
                    break
            
            converted.append({
                "text": text,
                "sentiment": sentiment,
                "sentiment_score": sentiment_score,
                "emotions": [],
                "behavioral_flags": [],
                "quality_score": 0.5,
                "trade_result": "unknown",
                "pnl_pct": None
            })
        
        # Save
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(converted, f, ensure_ascii=False, indent=2)
        
        print(f"   ✅ Converted {len(converted)} records to {output_file}")
        
    except Exception as e:
        print(f"   ❌ Conversion error: {e}")


def main():
    print("=" * 60)
    print("📊 Large Dataset Downloader for Financial NLP & ML")
    print("=" * 60)
    
    output_dir = "ml/training/datasets"
    os.makedirs(output_dir, exist_ok=True)
    
    total_records = 0
    
    # Download HuggingFace datasets
    print("\n📦 HuggingFace Datasets:")
    print("-" * 40)
    
    for name, config in DATASETS.items():
        count = download_huggingface_dataset(config, output_dir)
        total_records += count
    
    # Instructions for Kaggle
    print("\n📦 Kaggle Datasets (Manual Download):")
    print("-" * 40)
    print("To download from Kaggle:")
    print("1. Install: pip install kaggle")
    print("2. Get API key from kaggle.com/account")
    print("3. Save to ~/.kaggle/kaggle.json")
    print("\nRecommended large datasets:")
    for name, config in KAGGLE_DATASETS.items():
        print(f"  • {config['name']}")
        print(f"    {config['description']}")
        print(f"    kaggle datasets download -d {config['name']}")
        print()
    
    # Print summary
    print("\n" + "=" * 60)
    print(f"✅ Downloaded {total_records:,} records total")
    print(f"📁 Saved to: {output_dir}/")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Run conversion: python ml/training/convert_datasets.py")
    print("2. Train NLP: python ml/training/train_nlp.py")
    print("3. Train Behavioral: python ml/behavioral/train_classifier.py")


if __name__ == "__main__":
    main()
