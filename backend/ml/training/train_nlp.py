"""
NLP Model Fine-tuning Script
Fine-tunes FinBERT on Vietnamese trading notes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import json
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score

try:
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModelForSequenceClassification,
        TrainingArguments,
        Trainer,
        DataCollatorWithPadding
    )
    from datasets import Dataset
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("⚠️ transformers not installed. Run: pip install transformers datasets torch")

from ml.config import NLP_CONFIG, MODEL_PATHS


def load_dataset(path: str = "ml/training/nlp_dataset.json"):
    """Load prepared NLP dataset"""
    with open(path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    return data


def prepare_training_data(data: list):
    """Prepare data for transformer training"""
    texts = [d['text'] for d in data]
    
    # Map sentiment labels to integers
    label_map = {label: i for i, label in enumerate(NLP_CONFIG['sentiment_labels'])}
    labels = [label_map.get(d['sentiment'], 1) for d in data]  # default neutral
    
    return texts, labels, label_map


def tokenize_function(examples, tokenizer):
    """Tokenize text for transformer"""
    return tokenizer(
        examples['text'],
        padding='max_length',
        truncation=True,
        max_length=NLP_CONFIG['max_length']
    )


def compute_metrics(eval_pred):
    """Compute evaluation metrics"""
    predictions, labels = eval_pred
    predictions = np.argmax(predictions, axis=1)
    return {
        'accuracy': accuracy_score(labels, predictions)
    }


def train_model(train_dataset, val_dataset, tokenizer, num_labels: int, output_dir: str):
    """Train the model"""
    # Load pre-trained model
    model = AutoModelForSequenceClassification.from_pretrained(
        NLP_CONFIG['base_model'],
        num_labels=num_labels
    )
    
    # Training arguments
    training_args = TrainingArguments(
        output_dir=output_dir,
        learning_rate=NLP_CONFIG['learning_rate'],
        per_device_train_batch_size=NLP_CONFIG['batch_size'],
        per_device_eval_batch_size=NLP_CONFIG['batch_size'],
        num_train_epochs=NLP_CONFIG['epochs'],
        weight_decay=NLP_CONFIG['weight_decay'],
        warmup_steps=NLP_CONFIG['warmup_steps'],
        eval_strategy="epoch",  # Updated from evaluation_strategy
        save_strategy="epoch",
        load_best_model_at_end=True,
        logging_steps=10,
        report_to="none"  # Disable wandb
    )
    
    # Create trainer
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        tokenizer=tokenizer,
        data_collator=DataCollatorWithPadding(tokenizer=tokenizer),
        compute_metrics=compute_metrics
    )
    
    # Train
    print("🚀 Starting training...")
    trainer.train()
    
    # Save model
    print(f"💾 Saving model to {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    
    return trainer


def evaluate_model(trainer, test_dataset, label_map):
    """Evaluate model on test set"""
    print("\n📊 Evaluating on test set...")
    
    predictions = trainer.predict(test_dataset)
    preds = np.argmax(predictions.predictions, axis=1)
    labels = predictions.label_ids
    
    # Reverse label map
    id_to_label = {v: k for k, v in label_map.items()}
    
    # Get unique labels in test set
    unique_labels = sorted(set(labels) | set(preds))
    target_names = [id_to_label[i] for i in unique_labels if i in id_to_label]
    
    print("\nClassification Report:")
    print(classification_report(labels, preds, labels=unique_labels, target_names=target_names, zero_division=0))
    
    return accuracy_score(labels, preds)


def main():
    print("=" * 50)
    print("🤖 NLP Model Fine-tuning")
    print("=" * 50)
    
    if not TRANSFORMERS_AVAILABLE:
        print("\n❌ Cannot train without transformers library")
        print("   Install with: pip install transformers datasets torch")
        return
    
    # Check for GPU
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"\n📦 Using device: {device}")
    
    # Load dataset
    dataset_path = "ml/training/nlp_dataset.json"
    if not os.path.exists(dataset_path):
        print(f"\n❌ Dataset not found: {dataset_path}")
        print("   Run prepare_dataset.py first")
        return
    
    print(f"\n📁 Loading dataset from {dataset_path}")
    data = load_dataset(dataset_path)
    print(f"   Total samples: {len(data)}")
    
    if len(data) < 10:
        print("⚠️ Very small dataset. Results may not be reliable.")
    
    # Prepare data
    texts, labels, label_map = prepare_training_data(data)
    print(f"   Labels: {label_map}")
    
    # Split data
    train_texts, temp_texts, train_labels, temp_labels = train_test_split(
        texts, labels, 
        test_size=1 - NLP_CONFIG['train_split'],
        random_state=42,
        stratify=labels if len(set(labels)) > 1 else None
    )
    
    val_texts, test_texts, val_labels, test_labels = train_test_split(
        temp_texts, temp_labels,
        test_size=0.5,
        random_state=42
    )
    
    print(f"   Train: {len(train_texts)}, Val: {len(val_texts)}, Test: {len(test_texts)}")
    
    # Load tokenizer
    print(f"\n🔤 Loading tokenizer: {NLP_CONFIG['base_model']}")
    tokenizer = AutoTokenizer.from_pretrained(NLP_CONFIG['base_model'])
    
    # Create datasets
    train_dataset = Dataset.from_dict({"text": train_texts, "label": train_labels})
    val_dataset = Dataset.from_dict({"text": val_texts, "label": val_labels})
    test_dataset = Dataset.from_dict({"text": test_texts, "label": test_labels})
    
    # Tokenize
    train_dataset = train_dataset.map(
        lambda x: tokenize_function(x, tokenizer), 
        batched=True
    )
    val_dataset = val_dataset.map(
        lambda x: tokenize_function(x, tokenizer), 
        batched=True
    )
    test_dataset = test_dataset.map(
        lambda x: tokenize_function(x, tokenizer), 
        batched=True
    )
    
    # Train
    output_dir = MODEL_PATHS['nlp_model']
    trainer = train_model(
        train_dataset, val_dataset, tokenizer,
        num_labels=len(label_map),
        output_dir=output_dir
    )
    
    # Evaluate
    accuracy = evaluate_model(trainer, test_dataset, label_map)
    
    print("\n" + "=" * 50)
    print(f"✅ Training complete!")
    print(f"   Model saved to: {output_dir}")
    print(f"   Test accuracy: {accuracy:.4f}")
    print("=" * 50)


if __name__ == "__main__":
    main()
