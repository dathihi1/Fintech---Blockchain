"""
Train Multi-label Emotion Classifier
Trains a model to detect multiple emotions simultaneously
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, precision_score, recall_score
from transformers import AutoTokenizer
import numpy as np

try:
    from ml.emotion_classifier import EmotionClassifier
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False
    print("⚠️ PyTorch not available. Install with: pip install torch transformers")


class EmotionDataset(Dataset):
    """Dataset for multi-label emotion classification"""
    
    def __init__(self, texts: List[str], labels: List[List[int]], tokenizer, max_length: int = 128):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = self.texts[idx]
        label = self.labels[idx]
        
        # Tokenize
        encoding = self.tokenizer(
            text,
            truncation=True,
            max_length=self.max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].squeeze(0),
            'attention_mask': encoding['attention_mask'].squeeze(0),
            'labels': torch.tensor(label, dtype=torch.float)
        }


def load_dataset(path: str = "ml/training/nlp_dataset.json"):
    """Load and prepare dataset for multi-label classification"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    emotion_labels = ["FOMO", "FEAR", "GREED", "REVENGE", "RATIONAL", "CONFIDENT", "DISCIPLINE", "OVERCONFIDENCE"]
    
    texts = []
    labels = []
    
    for item in data:
        if 'text' not in item or 'emotions' not in item:
            continue
        
        texts.append(item['text'])
        
        # Create multi-label vector
        label_vector = [0] * len(emotion_labels)
        for emotion in item.get('emotions', []):
            if emotion in emotion_labels:
                label_vector[emotion_labels.index(emotion)] = 1
        labels.append(label_vector)
    
    return texts, labels, emotion_labels


def train_epoch(model, dataloader, optimizer, criterion, device):
    """Train for one epoch"""
    model.train()
    total_loss = 0
    
    for batch in dataloader:
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['labels'].to(device)
        
        # Forward pass
        outputs = model(input_ids, attention_mask)
        loss = criterion(outputs, labels)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        total_loss += loss.item()
    
    return total_loss / len(dataloader)


def evaluate(model, dataloader, device, threshold: float = 0.5):
    """Evaluate model on validation/test set"""
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for batch in dataloader:
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['labels'].to(device)
            
            outputs = model(input_ids, attention_mask)
            preds = (outputs > threshold).int()
            
            all_preds.append(preds.cpu().numpy())
            all_labels.append(labels.cpu().numpy())
    
    all_preds = np.vstack(all_preds)
    all_labels = np.vstack(all_labels)
    
    # Calculate metrics
    f1_micro = f1_score(all_labels, all_preds, average='micro', zero_division=0)
    f1_macro = f1_score(all_labels, all_preds, average='macro', zero_division=0)
    precision = precision_score(all_labels, all_preds, average='macro', zero_division=0)
    recall = recall_score(all_labels, all_preds, average='macro', zero_division=0)
    
    return {
        'f1_micro': f1_micro,
        'f1_macro': f1_macro,
        'precision': precision,
        'recall': recall
    }


def save_model(model, tokenizer, emotion_labels, base_model: str, output_dir: str, metrics: dict):
    """Save trained model and configuration"""
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model weights
    torch.save(model.state_dict(), os.path.join(output_dir, "pytorch_model.bin"))
    
    # Save config
    config = {
        "base_model": base_model,
        "num_emotions": len(emotion_labels),
        "emotion_labels": emotion_labels,
        "metrics": metrics,
        "model_type": "multi_label_emotion_classifier"
    }
    with open(os.path.join(output_dir, "config.json"), 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Model saved to {output_dir}")


def main():
    print("=" * 60)
    print("🧠 Multi-label Emotion Classifier Training")
    print("=" * 60)
    
    if not TORCH_AVAILABLE:
        print("\n❌ PyTorch not available")
        return
    
    # Configuration
    BASE_MODEL = "ProsusAI/finbert"  # or "vinai/phobert-base" for Vietnamese
    OUTPUT_DIR = "ml/models/emotion_classifier"
    BATCH_SIZE = 16
    LEARNING_RATE = 2e-5
    EPOCHS = 5
    
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"📦 Using device: {device}")
    
    # Load dataset
    dataset_path = "ml/training/nlp_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"\n❌ Dataset not found: {dataset_path}")
        return
    
    print(f"\n📁 Loading dataset from {dataset_path}")
    texts, labels, emotion_labels = load_dataset(dataset_path)
    print(f"   Total samples: {len(texts)}")
    print(f"   Emotions: {emotion_labels}")
    
    # Split data
    train_texts, temp_texts, train_labels, temp_labels = train_test_split(
        texts, labels, test_size=0.2, random_state=42
    )
    val_texts, test_texts, val_labels, test_labels = train_test_split(
        temp_texts, temp_labels, test_size=0.5, random_state=42
    )
    
    print(f"   Train: {len(train_texts)}, Val: {len(val_texts)}, Test: {len(test_texts)}")
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL)
    
    # Create datasets
    train_dataset = EmotionDataset(train_texts, train_labels, tokenizer)
    val_dataset = EmotionDataset(val_texts, val_labels, tokenizer)
    test_dataset = EmotionDataset(test_texts, test_labels, tokenizer)
    
    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)
    test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)
    
    # Initialize model
    model = EmotionClassifier(BASE_MODEL, num_emotions=len(emotion_labels))
    model.to(device)
    
    # Training setup
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE)
    criterion = nn.BCELoss()
    
    # Training loop
    print("\n🚀 Starting training...")
    best_f1 = 0
    
    for epoch in range(EPOCHS):
        train_loss = train_epoch(model, train_loader, optimizer, criterion, device)
        val_metrics = evaluate(model, val_loader, device)
        
        print(f"\nEpoch {epoch + 1}/{EPOCHS}")
        print(f"  Train loss: {train_loss:.4f}")
        print(f"  Val F1 (micro): {val_metrics['f1_micro']:.4f}")
        print(f"  Val F1 (macro): {val_metrics['f1_macro']:.4f}")
        print(f"  Val Precision: {val_metrics['precision']:.4f}")
        print(f"  Val Recall: {val_metrics['recall']:.4f}")
        
        # Save best model
        if val_metrics['f1_macro'] > best_f1:
            best_f1 = val_metrics['f1_macro']
            save_model(model, tokenizer, emotion_labels, BASE_MODEL, OUTPUT_DIR, val_metrics)
    
    # Final evaluation on test set
    print("\n📊 Evaluating on test set...")
    test_metrics = evaluate(model, test_loader, device)
    
    print(f"\nTest Results:")
    print(f"  F1 (micro): {test_metrics['f1_micro']:.4f}")
    print(f"  F1 (macro): {test_metrics['f1_macro']:.4f}")
    print(f"  Precision: {test_metrics['precision']:.4f}")
    print(f"  Recall: {test_metrics['recall']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ Training complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
