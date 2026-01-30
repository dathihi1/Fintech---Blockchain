"""
Multi-label Emotion Classifier
Predicts multiple emotions simultaneously from trading notes
"""

import os
import json
import torch
import torch.nn as nn
from typing import List, Dict, Tuple
from transformers import AutoTokenizer, AutoModel


class EmotionClassifier(nn.Module):
    """
    Multi-label emotion classifier built on top of BERT/PhoBERT.
    Can detect multiple emotions simultaneously (e.g., FOMO + GREED).
    """
    
    def __init__(self, base_model: str, num_emotions: int = 8, dropout: float = 0.3):
        super().__init__()
        self.bert = AutoModel.from_pretrained(base_model)
        self.dropout = nn.Dropout(dropout)
        
        # Multi-label classification head
        self.classifier = nn.Linear(self.bert.config.hidden_size, num_emotions)
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        
        # Use [CLS] token representation
        pooled = outputs.last_hidden_state[:, 0, :]
        pooled = self.dropout(pooled)
        
        # Multi-label output (each emotion independent)
        logits = self.classifier(pooled)
        probs = self.sigmoid(logits)
        
        return probs


class EmotionPredictor:
    """
    Wrapper class for emotion prediction with fine-tuned model.
    """
    
    def __init__(self, model_path: str = "ml/models/emotion_classifier", use_gpu: bool = False):
        self.model_path = model_path
        self.device = "cuda" if use_gpu and torch.cuda.is_available() else "cpu"
        
        # Emotion labels
        self.emotion_labels = [
            "FOMO", "FEAR", "GREED", "REVENGE", 
            "RATIONAL", "CONFIDENT", "DISCIPLINE", "OVERCONFIDENCE"
        ]
        
        # Lazy load
        self._model = None
        self._tokenizer = None
    
    def _load_model(self):
        """Load model and tokenizer"""
        if not os.path.exists(self.model_path):
            print(f"Warning: Emotion classifier not found at {self.model_path}")
            return False
        
        try:
            # Load config
            config_path = os.path.join(self.model_path, "config.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            # Load tokenizer
            self._tokenizer = AutoTokenizer.from_pretrained(config["base_model"])
            
            # Load model
            self._model = EmotionClassifier(
                base_model=config["base_model"],
                num_emotions=len(self.emotion_labels)
            )
            
            # Load weights
            weights_path = os.path.join(self.model_path, "pytorch_model.bin")
            state_dict = torch.load(weights_path, map_location=self.device)
            self._model.load_state_dict(state_dict)
            self._model.to(self.device)
            self._model.eval()
            
            return True
        except Exception as e:
            print(f"Failed to load emotion classifier: {e}")
            return False
    
    def predict(self, text: str, threshold: float = 0.3) -> List[Tuple[str, float]]:
        """
        Predict emotions from text.
        
        Args:
            text: Input text to analyze
            threshold: Confidence threshold for emotion detection (0 to 1)
            
        Returns:
            List of (emotion_label, confidence) tuples
        """
        # Lazy load model
        if self._model is None:
            if not self._load_model():
                return []
        
        try:
            # Tokenize
            inputs = self._tokenizer(
                text,
                return_tensors="pt",
                truncation=True,
                max_length=128,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Predict
            with torch.no_grad():
                probs = self._model(inputs["input_ids"], inputs["attention_mask"])
            
            # Get probabilities
            probs = probs[0].cpu().numpy()
            
            # Filter by threshold
            detected_emotions = []
            for i, prob in enumerate(probs):
                if prob >= threshold:
                    detected_emotions.append((self.emotion_labels[i], float(prob)))
            
            # Sort by confidence
            detected_emotions.sort(key=lambda x: x[1], reverse=True)
            
            return detected_emotions
            
        except Exception as e:
            print(f"Emotion prediction failed: {e}")
            return []
    
    def predict_dict(self, text: str, threshold: float = 0.3) -> Dict[str, float]:
        """
        Predict emotions and return as dictionary.
        
        Returns:
            Dictionary mapping emotion labels to confidence scores
        """
        emotions = self.predict(text, threshold)
        return {emotion: confidence for emotion, confidence in emotions}


# Singleton instance
_emotion_predictor: EmotionPredictor = None


def get_emotion_predictor(use_gpu: bool = False) -> EmotionPredictor:
    """Get or create emotion predictor singleton"""
    global _emotion_predictor
    if _emotion_predictor is None:
        _emotion_predictor = EmotionPredictor(use_gpu=use_gpu)
    return _emotion_predictor
