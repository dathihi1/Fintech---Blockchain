"""
Model Performance Evaluator
Monitors model performance in production and triggers retraining when needed
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
import numpy as np


@dataclass
class PredictionLog:
    """Log entry for a model prediction"""
    timestamp: str
    model_id: str
    input_text: str
    prediction: str
    confidence: float
    ground_truth: Optional[str] = None  # Set later when actual label is known
    correct: Optional[bool] = None


class ModelEvaluator:
    """
    Evaluates model performance in production.
    Tracks accuracy drift and triggers retraining alerts.
    """
    
    def __init__(self, log_path: str = "ml/logs/predictions.jsonl"):
        self.log_path = log_path
        self.logs: List[PredictionLog] = []
        self.load_logs()
    
    def load_logs(self):
        """Load prediction logs from disk"""
        if not os.path.exists(self.log_path):
            return
        
        try:
            with open(self.log_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        data = json.loads(line)
                        self.logs.append(PredictionLog(**data))
        except Exception as e:
            print(f"Warning: Could not load prediction logs: {e}")
    
    def log_prediction(
        self,
        model_id: str,
        input_text: str,
        prediction: str,
        confidence: float,
        ground_truth: Optional[str] = None
    ):
        """
        Log a model prediction.
        
        Args:
            model_id: ID of the model that made the prediction
            input_text: Input text (truncated for privacy)
            prediction: Model's prediction
            confidence: Confidence score
            ground_truth: Actual label (if known)
        """
        log_entry = PredictionLog(
            timestamp=datetime.now().isoformat(),
            model_id=model_id,
            input_text=input_text[:100],  # Truncate for privacy
            prediction=prediction,
            confidence=confidence,
            ground_truth=ground_truth,
            correct=prediction == ground_truth if ground_truth else None
        )
        
        self.logs.append(log_entry)
        
        # Append to log file
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(asdict(log_entry), ensure_ascii=False) + '\n')
    
    def update_ground_truth(self, timestamp: str, ground_truth: str):
        """Update ground truth for a logged prediction"""
        for log in self.logs:
            if log.timestamp == timestamp:
                log.ground_truth = ground_truth
                log.correct = log.prediction == ground_truth
                break
        
        # Rewrite log file
        self.save_logs()
    
    def save_logs(self):
        """Save all logs to disk"""
        os.makedirs(os.path.dirname(self.log_path), exist_ok=True)
        with open(self.log_path, 'w', encoding='utf-8') as f:
            for log in self.logs:
                f.write(json.dumps(asdict(log), ensure_ascii=False) + '\n')
    
    def calculate_accuracy(
        self,
        model_id: str,
        time_window_days: int = 7
    ) -> Optional[float]:
        """
        Calculate model accuracy over a time window.
        
        Args:
            model_id: Model to evaluate
            time_window_days: Number of days to look back
            
        Returns:
            Accuracy score or None if insufficient data
        """
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        # Filter logs
        relevant_logs = [
            log for log in self.logs
            if log.model_id == model_id
            and log.correct is not None
            and datetime.fromisoformat(log.timestamp) >= cutoff_date
        ]
        
        if len(relevant_logs) < 10:
            return None  # Not enough data
        
        correct_count = sum(1 for log in relevant_logs if log.correct)
        return correct_count / len(relevant_logs)
    
    def detect_drift(
        self,
        model_id: str,
        baseline_accuracy: float,
        drift_threshold: float = 0.05
    ) -> bool:
        """
        Detect if model performance has drifted significantly.
        
        Args:
            model_id: Model to check
            baseline_accuracy: Expected accuracy (from training)
            drift_threshold: Maximum acceptable accuracy drop
            
        Returns:
            True if drift detected (retraining recommended)
        """
        current_accuracy = self.calculate_accuracy(model_id, time_window_days=7)
        
        if current_accuracy is None:
            return False  # Not enough data to determine
        
        drift = baseline_accuracy - current_accuracy
        
        if drift > drift_threshold:
            print(f"⚠️ DRIFT DETECTED for {model_id}")
            print(f"   Baseline: {baseline_accuracy:.4f}")
            print(f"   Current: {current_accuracy:.4f}")
            print(f"   Drift: {drift:.4f}")
            return True
        
        return False
    
    def get_confidence_distribution(self, model_id: str, time_window_days: int = 7) -> Dict:
        """
        Analyze distribution of confidence scores.
        Low confidence might indicate model uncertainty.
        """
        cutoff_date = datetime.now() - timedelta(days=time_window_days)
        
        relevant_logs = [
            log.confidence for log in self.logs
            if log.model_id == model_id
            and datetime.fromisoformat(log.timestamp) >= cutoff_date
        ]
        
        if not relevant_logs:
            return {}
        
        confidences = np.array(relevant_logs)
        
        return {
            "mean": float(np.mean(confidences)),
            "median": float(np.median(confidences)),
            "std": float(np.std(confidences)),
            "min": float(np.min(confidences)),
            "max": float(np.max(confidences)),
            "samples": len(confidences)
        }
    
    def get_performance_report(self, model_id: str) -> Dict:
        """
        Generate comprehensive performance report for a model.
        
        Returns:
            Dictionary with performance metrics and insights
        """
        # Recent accuracy
        acc_7d = self.calculate_accuracy(model_id, time_window_days=7)
        acc_30d = self.calculate_accuracy(model_id, time_window_days=30)
        
        # Confidence distribution
        conf_dist = self.get_confidence_distribution(model_id, time_window_days=7)
        
        # Prediction count
        total_predictions = sum(1 for log in self.logs if log.model_id == model_id)
        
        # Recent predictions with ground truth
        labeled_predictions = sum(
            1 for log in self.logs
            if log.model_id == model_id and log.ground_truth is not None
        )
        
        return {
            "model_id": model_id,
            "total_predictions": total_predictions,
            "labeled_predictions": labeled_predictions,
            "accuracy_7d": acc_7d,
            "accuracy_30d": acc_30d,
            "confidence_distribution": conf_dist,
            "label_coverage": f"{labeled_predictions}/{total_predictions}",
            "drift_warning": acc_7d is not None and acc_30d is not None and acc_30d - acc_7d > 0.05
        }


# Singleton
_evaluator: Optional[ModelEvaluator] = None


def get_evaluator() -> ModelEvaluator:
    """Get or create model evaluator singleton"""
    global _evaluator
    if _evaluator is None:
        _evaluator = ModelEvaluator()
    return _evaluator


if __name__ == "__main__":
    # Example usage
    evaluator = get_evaluator()
    
    # Log a prediction
    evaluator.log_prediction(
        model_id="finbert_v1.0",
        input_text="BTC phải vào ngay kẻo lỡ!",
        prediction="negative",
        confidence=0.87
    )
    
    # Get performance report
    report = evaluator.get_performance_report("finbert_v1.0")
    print(json.dumps(report, indent=2, ensure_ascii=False))
