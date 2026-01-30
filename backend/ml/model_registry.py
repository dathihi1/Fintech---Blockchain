"""
Model Performance Monitor
Tracks model versions, metrics, and A/B testing results
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ModelMetrics:
    """Metrics for a trained model"""
    accuracy: float
    precision: float
    recall: float
    f1_score: float
    samples_tested: int
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ModelVersion:
    """Information about a model version"""
    version: str
    model_type: str  # "nlp_sentiment", "emotion_classifier", "behavioral"
    path: str
    base_model: str
    trained_at: str
    metrics: ModelMetrics
    is_active: bool = False
    notes: str = ""
    
    def to_dict(self) -> dict:
        result = asdict(self)
        result['metrics'] = asdict(self.metrics)
        return result


class ModelRegistry:
    """
    Registry for tracking model versions and performance.
    Supports A/B testing and model comparison.
    """
    
    def __init__(self, registry_path: str = "ml/models/registry.json"):
        self.registry_path = registry_path
        self.models: Dict[str, ModelVersion] = {}
        self.load_registry()
    
    def load_registry(self):
        """Load model registry from disk"""
        if os.path.exists(self.registry_path):
            try:
                with open(self.registry_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for model_id, model_data in data.items():
                    metrics_data = model_data.pop('metrics')
                    metrics = ModelMetrics(**metrics_data)
                    self.models[model_id] = ModelVersion(**model_data, metrics=metrics)
            except Exception as e:
                print(f"Warning: Could not load model registry: {e}")
    
    def save_registry(self):
        """Save model registry to disk"""
        os.makedirs(os.path.dirname(self.registry_path), exist_ok=True)
        
        data = {
            model_id: model.to_dict()
            for model_id, model in self.models.items()
        }
        
        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def register_model(
        self,
        model_id: str,
        version: str,
        model_type: str,
        path: str,
        base_model: str,
        metrics: ModelMetrics,
        notes: str = ""
    ) -> ModelVersion:
        """
        Register a new model version.
        
        Args:
            model_id: Unique identifier (e.g., "finbert_v1", "phobert_v1")
            version: Version string (e.g., "1.0.0")
            model_type: Type of model
            path: Path to model files
            base_model: Base model used for fine-tuning
            metrics: Model performance metrics
            notes: Optional notes about this version
            
        Returns:
            Registered ModelVersion
        """
        model_version = ModelVersion(
            version=version,
            model_type=model_type,
            path=path,
            base_model=base_model,
            trained_at=datetime.now().isoformat(),
            metrics=metrics,
            is_active=False,
            notes=notes
        )
        
        self.models[model_id] = model_version
        self.save_registry()
        
        return model_version
    
    def activate_model(self, model_id: str):
        """Set a model as active (for production use)"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found in registry")
        
        # Deactivate all models of the same type
        model_type = self.models[model_id].model_type
        for mid, model in self.models.items():
            if model.model_type == model_type:
                model.is_active = False
        
        # Activate the selected model
        self.models[model_id].is_active = True
        self.save_registry()
    
    def get_active_model(self, model_type: str) -> Optional[ModelVersion]:
        """Get the active model for a given type"""
        for model in self.models.values():
            if model.model_type == model_type and model.is_active:
                return model
        return None
    
    def compare_models(self, model_ids: List[str]) -> Dict:
        """
        Compare metrics across multiple models.
        
        Returns:
            Dictionary with comparison results
        """
        comparison = {
            "models": [],
            "best_accuracy": None,
            "best_f1": None
        }
        
        best_acc = -1
        best_f1 = -1
        
        for model_id in model_ids:
            if model_id not in self.models:
                continue
            
            model = self.models[model_id]
            metrics = model.metrics
            
            comparison["models"].append({
                "id": model_id,
                "version": model.version,
                "accuracy": metrics.accuracy,
                "f1_score": metrics.f1_score,
                "trained_at": model.trained_at,
                "is_active": model.is_active
            })
            
            if metrics.accuracy > best_acc:
                best_acc = metrics.accuracy
                comparison["best_accuracy"] = model_id
            
            if metrics.f1_score > best_f1:
                best_f1 = metrics.f1_score
                comparison["best_f1"] = model_id
        
        return comparison
    
    def list_models(self, model_type: Optional[str] = None) -> List[ModelVersion]:
        """
        List all registered models, optionally filtered by type.
        
        Args:
            model_type: Optional filter by model type
            
        Returns:
            List of ModelVersion objects
        """
        if model_type:
            return [m for m in self.models.values() if m.model_type == model_type]
        return list(self.models.values())


# Singleton registry
_registry: Optional[ModelRegistry] = None


def get_model_registry() -> ModelRegistry:
    """Get or create model registry singleton"""
    global _registry
    if _registry is None:
        _registry = ModelRegistry()
    return _registry


# Example usage
if __name__ == "__main__":
    registry = get_model_registry()
    
    # Register a model
    metrics = ModelMetrics(
        accuracy=0.87,
        precision=0.85,
        recall=0.86,
        f1_score=0.855,
        samples_tested=200
    )
    
    registry.register_model(
        model_id="finbert_v1.0",
        version="1.0.0",
        model_type="nlp_sentiment",
        path="ml/models/finbert_trading_vi",
        base_model="ProsusAI/finbert",
        metrics=metrics,
        notes="Initial fine-tuned model on Vietnamese trading notes"
    )
    
    registry.activate_model("finbert_v1.0")
    
    print("✅ Model registered and activated")
    print(f"   Active models: {[m for m in registry.list_models() if m.is_active]}")
