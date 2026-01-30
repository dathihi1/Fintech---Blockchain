"""
Smart Trading Journal - Colab Training Script
Dùng Kaggle API + Lưu config vào Google Drive

Hướng dẫn:
1. Vào https://colab.new
2. Copy toàn bộ code này vào cell
3. Runtime > Change runtime type > T4 GPU
4. Nhấn Shift+Enter để chạy
"""

# ============================================
# BƯỚC 1: Cài đặt và kiểm tra GPU
# ============================================
print("=" * 50)
print("🚀 Smart Trading Journal - Model Training")
print("=" * 50)

import subprocess
subprocess.run(['pip', 'install', '-q', 'torch', 'transformers', 'datasets', 
                'scikit-learn', 'pandas', 'numpy', 'kaggle', 'accelerate'])

import torch
print(f"\n✅ PyTorch: {torch.__version__}")
print(f"✅ CUDA: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"✅ GPU: {torch.cuda.get_device_name(0)}")

# ============================================
# BƯỚC 2: Mount Google Drive & Setup Kaggle
# ============================================
print("\n" + "=" * 50)
print("� Mount Google Drive")
print("=" * 50)

from google.colab import drive
import os
import json

# Mount Drive
drive.mount('/content/drive')

# Đường dẫn lưu config trên Drive
KAGGLE_CONFIG_DIR = '/content/drive/MyDrive/colab_configs'
KAGGLE_JSON_PATH = f'{KAGGLE_CONFIG_DIR}/kaggle.json'

os.makedirs(KAGGLE_CONFIG_DIR, exist_ok=True)
os.makedirs('/root/.kaggle', exist_ok=True)

# Kiểm tra xem đã có config chưa
if os.path.exists(KAGGLE_JSON_PATH):
    print("✅ Tìm thấy Kaggle config trên Drive!")
    os.system(f'cp {KAGGLE_JSON_PATH} /root/.kaggle/kaggle.json')
    os.chmod('/root/.kaggle/kaggle.json', 0o600)
    print("✅ Đã load Kaggle config từ Drive")
else:
    print("⚠️ Chưa có Kaggle config. Đang tạo mới...")
    
    # Tạo config với API token mới (dạng KGAT_xxx)
    # Kaggle hiện dùng format username + API token
    print("""
📝 Cách lấy thông tin:
1. Vào https://www.kaggle.com/settings
2. Scroll xuống mục "API" 
3. Bạn cần:
   - Username: tên tài khoản Kaggle của bạn
   - API Token: dạng KGAT_xxxxxxx (như bạn đã có)
    """)
    
    kaggle_username = input("Nhập Kaggle username: ")
    kaggle_token = input("Nhập API Token (KGAT_xxx): ")
    
    # Tạo kaggle.json
    kaggle_config = {
        "username": kaggle_username,
        "key": kaggle_token
    }
    
    # Lưu vào Drive (để dùng lần sau)
    with open(KAGGLE_JSON_PATH, 'w') as f:
        json.dump(kaggle_config, f)
    print(f"✅ Đã lưu config vào Drive: {KAGGLE_JSON_PATH}")
    
    # Copy vào thư mục kaggle
    os.system(f'cp {KAGGLE_JSON_PATH} /root/.kaggle/kaggle.json')
    os.chmod('/root/.kaggle/kaggle.json', 0o600)
    print("✅ Config đã được setup!")

print("\n💡 Lần sau config sẽ tự động load từ Drive!")

# ============================================
# BƯỚC 3: Download Dataset từ Kaggle
# ============================================
print("\n" + "=" * 50)
print("� Download Dataset từ Kaggle")
print("=" * 50)

# Set environment variable cho API Token mới
os.environ['KAGGLE_API_TOKEN'] = open('/root/.kaggle/kaggle.json').read()

# Download Financial Sentiment dataset
print("\n📦 Đang tải dataset...")
os.system('kaggle datasets download -d ankurzing/sentiment-analysis-for-financial-news -p /content/data --unzip')

# Load data
import pandas as pd

data_path = '/content/data/all-data.csv'
if os.path.exists(data_path):
    df = pd.read_csv(data_path, encoding='latin-1', header=None, names=['sentiment', 'text'])
    print(f"✅ Loaded {len(df)} samples")
else:
    # Thử tìm file khác
    print("⚠️ Đang tìm file data...")
    os.system('ls -la /content/data/')
    
    # Fallback: dùng HuggingFace
    print("\n📦 Fallback: Tải từ HuggingFace...")
    from datasets import load_dataset
    dataset = load_dataset("zeroshot/twitter-financial-news-sentiment")
    df = pd.DataFrame({
        'text': dataset['train']['text'],
        'sentiment': [['negative', 'positive', 'neutral'][l] for l in dataset['train']['label']]
    })
    print(f"✅ Loaded {len(df)} samples từ HuggingFace")

# Map labels
sentiment_map = {'negative': 0, 'neutral': 1, 'positive': 2}
df['label'] = df['sentiment'].map(sentiment_map)
df = df.dropna()

print(f"\n📊 Label distribution:")
print(df['sentiment'].value_counts())

# ============================================
# BƯỚC 4: Chuẩn bị & Training
# ============================================
print("\n" + "=" * 50)
print("� Preparing Data & Training")
print("=" * 50)

import numpy as np
from sklearn.model_selection import train_test_split
from transformers import (
    AutoTokenizer, 
    AutoModelForSequenceClassification,
    TrainingArguments,
    Trainer,
    DataCollatorWithPadding
)
from datasets import Dataset
from sklearn.metrics import accuracy_score, classification_report

# Config
CONFIG = {
    "base_model": "ProsusAI/finbert",
    "learning_rate": 2e-5,
    "batch_size": 16,
    "epochs": 3,
    "max_length": 128,
    "sentiment_labels": ["negative", "neutral", "positive"]
}

# Split
train_texts, test_texts, train_labels, test_labels = train_test_split(
    df['text'].tolist(), df['label'].tolist(), 
    test_size=0.2, random_state=42
)
print(f"✅ Train: {len(train_texts)}, Test: {len(test_texts)}")

# Load model
print(f"\n📦 Loading {CONFIG['base_model']}...")
tokenizer = AutoTokenizer.from_pretrained(CONFIG['base_model'])
model = AutoModelForSequenceClassification.from_pretrained(
    CONFIG['base_model'], num_labels=3
)

# Tokenize
def tokenize_fn(examples):
    return tokenizer(examples['text'], padding='max_length', 
                     truncation=True, max_length=128)

train_ds = Dataset.from_dict({"text": train_texts, "label": train_labels})
test_ds = Dataset.from_dict({"text": test_texts, "label": test_labels})
train_ds = train_ds.map(tokenize_fn, batched=True)
test_ds = test_ds.map(tokenize_fn, batched=True)

# Training
print("\n🚀 TRAINING (5-10 phút)...")

def compute_metrics(p):
    preds = np.argmax(p.predictions, axis=1)
    return {'accuracy': accuracy_score(p.label_ids, preds)}

trainer = Trainer(
    model=model,
    args=TrainingArguments(
        output_dir="./results",
        learning_rate=2e-5,
        per_device_train_batch_size=16,
        num_train_epochs=3,
        eval_strategy="epoch",
        save_strategy="epoch",
        load_best_model_at_end=True,
        fp16=torch.cuda.is_available(),
        report_to="none"
    ),
    train_dataset=train_ds,
    eval_dataset=test_ds,
    tokenizer=tokenizer,
    data_collator=DataCollatorWithPadding(tokenizer),
    compute_metrics=compute_metrics
)

trainer.train()

# Evaluate
print("\n📊 Results:")
preds = np.argmax(trainer.predict(test_ds).predictions, axis=1)
print(classification_report(test_labels, preds, target_names=CONFIG['sentiment_labels']))

# ============================================
# BƯỚC 5: Save Model (cả local và Drive)
# ============================================
print("\n" + "=" * 50)
print("💾 Saving Model")
print("=" * 50)

# Save local
output_dir = "./finbert_trading_vi"
trainer.save_model(output_dir)
tokenizer.save_pretrained(output_dir)

# Save to Drive
drive_model_path = '/content/drive/MyDrive/colab_configs/finbert_trading_vi'
os.system(f'cp -r {output_dir} {drive_model_path}')
print(f"✅ Model saved to Drive: {drive_model_path}")

# Zip & Download
os.system(f"zip -r finbert_trading_vi.zip {output_dir}/")

from google.colab import files
print("\n📥 Downloading...")
files.download('finbert_trading_vi.zip')

print("\n" + "=" * 50)
print("✅ HOÀN TẤT!")
print("=" * 50)
print("""
📁 Model đã được lưu:
   - Google Drive: /MyDrive/colab_configs/finbert_trading_vi/
   - Downloaded: finbert_trading_vi.zip

📌 Copy vào: backend/ml/models/finbert_trading_vi/
""")
