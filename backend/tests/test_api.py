"""
Test API Endpoints
Integration tests for the FastAPI routes
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Import main app
from main import app


# Create test client
client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints"""
    
    def test_root(self):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert data["name"] == "Smart Trading Journal API"
        print("✅ Root endpoint working")
    
    def test_health(self):
        """Test health endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✅ Health endpoint working")


class TestNLPEndpoints:
    """Test NLP API endpoints"""
    
    def test_analyze_vietnamese(self):
        """Test NLP analyze with Vietnamese text"""
        response = client.post(
            "/api/nlp/analyze",
            json={"text": "BTC breakout, phải vào ngay kẻo lỡ!"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["language"] == "vi"
        assert "sentiment_score" in data
        assert "emotions" in data
        assert len(data["behavioral_flags"]) > 0  # Should detect FOMO
        print(f"✅ Vietnamese NLP analysis: sentiment={data['sentiment_label']}")
    
    def test_analyze_english(self):
        """Test NLP analyze with English text"""
        response = client.post(
            "/api/nlp/analyze",
            json={"text": "Following the plan, stop loss set at 2%"}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["language"] == "en"
        assert data["quality_score"] > 0.5  # Should be high quality
        print(f"✅ English NLP analysis: quality_score={data['quality_score']}")
    
    def test_analyze_batch(self):
        """Test batch analysis"""
        response = client.post(
            "/api/nlp/analyze-batch",
            json={"texts": [
                "FOMO quá!",
                "Theo plan",
                "Gỡ gạc thôi"
            ]}
        )
        assert response.status_code == 200
        data = response.json()
        
        assert len(data) == 3
        print(f"✅ Batch NLP analysis: {len(data)} texts analyzed")
    
    def test_get_keywords(self):
        """Test get keywords endpoint"""
        response = client.get("/api/nlp/keywords")
        assert response.status_code == 200
        data = response.json()
        
        assert "vi" in data
        assert "en" in data
        assert "fomo" in data["vi"]
        print(f"✅ Keywords endpoint: {len(data['vi'])} Vietnamese categories")
    
    def test_get_emotions(self):
        """Test get emotion types"""
        response = client.get("/api/nlp/emotions")
        assert response.status_code == 200
        data = response.json()
        
        assert "negative_emotions" in data
        assert "positive_emotions" in data
        print(f"✅ Emotions endpoint: {len(data['negative_emotions'])} negative, {len(data['positive_emotions'])} positive")


class TestAlertsEndpoints:
    """Test Alerts API endpoints"""
    
    def test_analyze_behavior(self):
        """Test behavioral analysis without creating trade"""
        response = client.post(
            "/api/alerts/analyze",
            json={
                "notes": "All in! Phải gỡ lại!",
                "price_change_1h": 8.0,
                "recent_loss_pct": 5.0,
                "current_drawdown": 10.0,
                "trades_last_hour": 8
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert "alerts" in data
        assert len(data["alerts"]) > 0
        assert data["overall_risk_score"] > 0
        print(f"✅ Behavioral analysis: {len(data['alerts'])} alerts, risk={data['overall_risk_score']}")
    
    def test_analyze_safe_behavior(self):
        """Test with rational trading behavior"""
        response = client.post(
            "/api/alerts/analyze",
            json={
                "notes": "Following plan, SL 2%",
                "price_change_1h": 1.0,
                "recent_loss_pct": 0.0,
                "current_drawdown": 0.0,
                "trades_last_hour": 1
            }
        )
        assert response.status_code == 200
        data = response.json()
        
        assert data["should_block_trade"] == False
        print(f"✅ Safe behavior: should_block_trade={data['should_block_trade']}")


def run_all_tests():
    """Run all API tests"""
    print("\n" + "="*60)
    print("🧪 Running API Endpoint Tests")
    print("="*60 + "\n")
    
    test_classes = [
        TestHealthEndpoints,
        TestNLPEndpoints,
        TestAlertsEndpoints,
    ]
    
    passed = 0
    failed = 0
    
    for test_class in test_classes:
        print(f"\n📁 {test_class.__name__}")
        print("-" * 40)
        
        instance = test_class()
        for method_name in dir(instance):
            if method_name.startswith("test_"):
                try:
                    getattr(instance, method_name)()
                    passed += 1
                except Exception as e:
                    print(f"❌ {method_name}: {e}")
                    failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
