# Implementation Guide - Hướng Dẫn Triển Khai

## 📋 TỔNG QUAN DỰ ÁN

```
smart-trading-journal/
├── backend/                      # FastAPI backend
│   ├── api/                      # API endpoints
│   ├── core/                     # Config, dependencies
│   ├── ml/                       # ML models
│   ├── nlp/                      # NLP engine
│   ├── analyzers/                # Active/Passive analyzers
│   ├── models/                   # Database models
│   └── main.py                   # Application entry
│
├── frontend/                     # React frontend
│   ├── src/
│   │   ├── components/           # UI components
│   │   ├── pages/                # Pages
│   │   ├── services/             # API calls
│   │   └── App.tsx
│   └── package.json
│
├── infrastructure/               # Docker, Kafka
│   ├── docker-compose.yml
│   └── kafka/
│
├── notebooks/                    # Jupyter notebooks
│   ├── 01_data_exploration.ipynb
│   ├── 02_nlp_training.ipynb
│   └── 03_ml_training.ipynb
│
└── scripts/                      # Utility scripts
    ├── setup.py
    ├── train_nlp.py
    └── train_ml.py
```

---

## 🚀 PHASE 1: Foundation (Tuần 1-2)

### 1.1 Setup Project Structure

```bash
# Create project structure
mkdir -p smart-trading-journal/{backend,frontend,infrastructure,notebooks,scripts,data}

cd smart-trading-journal

# Initialize Python project
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
# FastAPI
fastapi==0.109.0
uvicorn[standard]==0.27.0
websockets==13.0.0
python-multipart==0.0.6

# Database
sqlalchemy==2.0.25
psycopg2-binary==2.9.9
alembic==1.13.1
redis==5.0.1

# Kafka
kafka-python==2.0.2
confluent-kafka==2.3.0

# ML/NLP
torch==2.1.2
transformers==4.37.2
scikit-learn==1.4.0
pandas==2.2.0
numpy==1.26.3

# NLP Specific
underthesea==1.1.5
vaderSentiment==3.3.2

# Data Processing
pydantic==2.5.3
pydantic-settings==2.1.0
python-dotenv==1.0.0

# Testing
pytest==7.4.4
pytest-asyncio==0.23.3
httpx==0.26.0

# Monitoring
prometheus-client==0.19.0
structlog==24.1.0
EOF

pip install -r requirements.txt
```

### 1.2 Database Schema

```python
# backend/models/database.py

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Trade(Base):
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)

    # Trade details
    symbol = Column(String, index=True)
    side = Column(String)  # 'long' or 'short'
    entry_price = Column(Float)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float)
    leverage = Column(Integer, default=1)

    # Timing
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    hold_duration_minutes = Column(Integer, nullable=True)

    # P&L
    pnl = Column(Float, nullable=True)
    pnl_pct = Column(Float, nullable=True)

    # Notes & NLP
    notes = Column(Text, nullable=True)
    nlp_sentiment = Column(Float, nullable=True)
    nlp_emotions = Column(JSON, nullable=True)  # ["FOMO", "RATIONAL"]
    nlp_quality_score = Column(Float, nullable=True)

    # Behavioral flags
    behavioral_flags = Column(JSON, nullable=True)

    # Market context
    market_conditions = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class NLPAnalysis(Base):
    __tablename__ = "nlp_analyses"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, index=True)

    # Analysis results
    language = Column(String)
    sentiment_score = Column(Float)
    sentiment_label = Column(String)
    emotions = Column(JSON)
    behavioral_flags = Column(JSON)
    quality_score = Column(Float)

    # Advanced analysis
    aspects = Column(JSON, nullable=True)  # Aspect-based sentiment
    behavioral_pattern = Column(JSON, nullable=True)
    manipulation_signals = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class ManipulationAlert(Base):
    __tablename__ = "manipulation_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    symbol = Column(String, index=True)

    # Alert details
    manipulation_types = Column(JSON)  # ["pump_dump", "wash_trading"]
    severity = Column(String)  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'
    confidence = Column(Float)
    evidence = Column(JSON)

    # Status
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class BehavioralMetric(Base):
    __tablename__ = "behavioral_metrics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)

    # Metrics
    metric_name = Column(String, index=True)
    metric_value = Column(Float)
    metric_type = Column(String)  # 'interval', 'sizing', 'hold', etc.

    # Context
    period = Column(String)  # 'daily', 'weekly', 'monthly'
    calculated_at = Column(DateTime, default=datetime.utcnow)
```

### 1.3 Core Configuration

```python
# backend/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    # API
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_PREFIX: str = "/api"

    # Database
    DATABASE_URL: str = "postgresql://user:pass@localhost:5432/trading_journal"
    REDIS_URL: str = "redis://localhost:6379"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_TRADES: str = "raw-trades"
    KAFKA_TOPIC_ALERTS: str = "behavioral-alerts"

    # ML Models
    NLP_MODEL_PATH: str = "models/nlp"
    ML_MODEL_PATH: str = "models/ml"

    # External APIs
    BINANCE_API_KEY: Optional[str] = None
    BINANCE_API_SECRET: Optional[str] = None

    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    class Config:
        env_file = ".env"

settings = Settings()
```

---

## 🧠 PHASE 2: NLP Engine (Tuần 3-4)

### 2.1 Basic NLP Engine

```python
# backend/nlp/engine.py

from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from underthesea import word_tokenize
import torch

class NLPEngine:
    def __init__(self):
        # Load models
        device = 0 if torch.cuda.is_available() else -1

        # FinBERT for financial sentiment
        self.finbert = pipeline(
            "sentiment-analysis",
            model="ProsusAI/finbert",
            device=device,
            return_all_scores=True
        )

        # VADER as fallback
        self.vader = SentimentIntensityAnalyzer()

        # Vietnamese keywords
        self.vn_keywords = self._load_vietnamese_keywords()

    def _load_vietnamese_keywords(self) -> dict:
        return {
            "fomo": {
                "keywords": ["sợ lỡ", "phải vào ngay", "mua gáp", "không kịp"],
                "weight": -0.8,
                "emotion": "FOMO"
            },
            "fear": {
                "keywords": ["sợ", "lo lắng", "hoang mang", "panic"],
                "weight": -0.6,
                "emotion": "FEAR"
            },
            "greed": {
                "keywords": ["x10", "moon", "rich", "giàu", "lời to"],
                "weight": -0.5,
                "emotion": "GREED"
            },
            "revenge": {
                "keywords": ["gỡ gạc", "gỡ lại", "trả thù", "thua đủ rồi"],
                "weight": -0.9,
                "emotion": "REVENGE"
            },
            "rational": {
                "keywords": ["phân tích", "RR", "stop loss", "quản lý vốn"],
                "weight": 0.7,
                "emotion": "RATIONAL"
            }
        }

    def analyze(self, text: str) -> dict:
        """Analyze trading note"""
        if not text:
            return self._empty_result()

        # Detect language
        is_vietnamese = self._is_vietnamese(text)

        # Sentiment analysis
        if is_vietnamese:
            sentiment = self._analyze_vietnamese(text)
        else:
            sentiment = self._analyze_english(text)

        # Detect emotions
        emotions = self._detect_emotions(text, is_vietnamese)

        # Quality assessment
        quality_score = self._assess_quality(text, emotions)

        return {
            "text": text,
            "language": "vi" if is_vietnamese else "en",
            "sentiment_score": sentiment["score"],
            "sentiment_label": sentiment["label"],
            "emotions": emotions,
            "behavioral_flags": [e["type"] for e in emotions if e["weight"] < 0],
            "quality_score": quality_score,
            "warnings": self._generate_warnings(emotions)
        }

    def _analyze_vietnamese(self, text: str) -> dict:
        """Vietnamese sentiment analysis"""
        # For Vietnamese, use keyword-based + VADER on translated
        score = 0.0

        # Check Vietnamese keywords
        text_lower = text.lower()
        for category, data in self.vn_keywords.items():
            if any(kw in text_lower for kw in data["keywords"]):
                score += data["weight"]

        # Normalize
        score = max(-1, min(1, score))

        if score > 0.3:
            label = "positive"
        elif score < -0.3:
            label = "negative"
        else:
            label = "neutral"

        return {"score": score, "label": label}

    def _analyze_english(self, text: str) -> dict:
        """English sentiment using FinBERT"""
        try:
            results = self.finbert(text)[0]
            # Convert to score
            label_to_score = {"positive": 1, "negative": -1, "neutral": 0}
            best = max(results, key=lambda x: x["score"])
            return {
                "score": label_to_score[best["label"]] * best["score"],
                "label": best["label"]
            }
        except:
            # Fallback to VADER
            scores = self.vader.polarity_scores(text)
            return {
                "score": scores["compound"],
                "label": "positive" if scores["compound"] > 0.05 else "negative" if scores["compound"] < -0.05 else "neutral"
            }

    def _detect_emotions(self, text: str, is_vietnamese: bool) -> list:
        """Detect emotions from text"""
        emotions = []
        text_lower = text.lower()

        for category, data in self.vn_keywords.items():
            matched = [kw for kw in data["keywords"] if kw in text_lower]
            if matched:
                emotions.append({
                    "type": data["emotion"],
                    "confidence": min(len(matched) * 0.3, 1.0),
                    "matched_keywords": matched,
                    "weight": data["weight"]
                })

        return emotions

    def _assess_quality(self, text: str, emotions: list) -> float:
        """Assess reasoning quality"""
        score = 0.5

        # Positive indicators
        positive_keywords = ["stop loss", "take profit", "rr", "kế hoạch", "plan"]
        for kw in positive_keywords:
            if kw in text.lower():
                score += 0.1

        # Negative indicators
        for emotion in emotions:
            if emotion["type"] in ["FOMO", "REVENGE", "GREED"]:
                score -= 0.2 * emotion["confidence"]

        return max(0, min(1, score))

    def _is_vietnamese(self, text: str) -> bool:
        """Detect if text is Vietnamese"""
        vietnamese_chars = set("àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ")
        return len([c for c in text if c in vietnamese_chars]) > len(text) * 0.1

    def _generate_warnings(self, emotions: list) -> list:
        """Generate warnings based on emotions"""
        warnings = []
        for emotion in emotions:
            if emotion["type"] == "FOMO":
                warnings.append("CẢNH BÁO FOMO: Hãy kiểm tra lại lý do vào lệnh")
            elif emotion["type"] == "REVENGE":
                warnings.append("CẢNH BÁO REVENGE: Nghỉ ngơi trước khi trade tiếp")
            elif emotion["type"] == "GREED":
                warnings.append("CẢNH BÁO GREED: Giảm position size")
        return warnings

    def _empty_result(self) -> dict:
        return {
            "text": "",
            "language": "unknown",
            "sentiment_score": 0.0,
            "sentiment_label": "neutral",
            "emotions": [],
            "behavioral_flags": [],
            "quality_score": 0.5,
            "warnings": []
        }
```

### 2.2 NLP API Endpoints

```python
# backend/api/nlp.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter(prefix="/nlp", tags=["NLP"])

class AnalyzeRequest(BaseModel):
    text: str

class AnalyzeResponse(BaseModel):
    sentiment_score: float
    sentiment_label: str
    emotions: List[dict]
    behavioral_flags: List[str]
    quality_score: float
    warnings: List[str]

@router.post("/analyze", response_model=AnalyzeResponse)
async def analyze_text(
    request: AnalyzeRequest,
    nlp_engine=Depends(get_nlp_engine)
):
    """Analyze text using NLP engine"""
    result = nlp_engine.analyze(request.text)

    return AnalyzeResponse(**result)
```

---

## 🤖 PHASE 3: ML Detection (Tuần 5-6)

### 3.1 Price Anomaly Detection

```python
# backend/ml/anomaly_detector.py

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import pandas as pd
import numpy as np

class PriceAnomalyDetector:
    def __init__(self, contamination=0.1):
        self.scaler = StandardScaler()
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.is_trained = False

    def prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        """Calculate features from OHLCV data"""
        features = pd.DataFrame()

        # Price changes
        features['price_change_1'] = df['close'].pct_change(1)
        features['price_change_5'] = df['close'].pct_change(5)
        features['price_change_15'] = df['close'].pct_change(15)

        # Volume
        features['volume_ratio'] = df['volume'] / df['volume'].rolling(50).mean()
        features['volume_change'] = df['volume'].pct_change(1)

        # Volatility
        features['volatility'] = df['close'].rolling(15).std()

        # RSI
        features['rsi'] = self._calculate_rsi(df['close'])

        return features.fillna(0).values

    def train(self, historical_data: pd.DataFrame):
        """Train on historical data"""
        features = self.prepare_features(historical_data)
        self.scaler.fit(features)
        scaled_features = self.scaler.transform(features)
        self.model.fit(scaled_features)
        self.is_trained = True

    def detect(self, current_data: pd.DataFrame) -> dict:
        """Detect anomalies"""
        if not self.is_trained:
            return {"is_anomaly": False, "score": 0}

        features = self.prepare_features(current_data)
        scaled_features = self.scaler.transform(features)

        prediction = self.model.predict(scaled_features)
        scores = self.model.score_samples(scaled_features)

        return {
            "is_anomaly": prediction[-1] == -1,
            "score": float(scores[-1])
        }

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))
```

### 3.2 ML API Endpoints

```python
# backend/api/ml.py

from fastapi import APIRouter, Depends
from pydantic import BaseModel

router = APIRouter(prefix="/ml", tags=["ML"])

class DetectAnomalyRequest(BaseModel):
    symbol: str
    ohlcv: List[dict]  # [{time, open, high, low, close, volume}]

@router.post("/detect-anomaly")
async def detect_anomaly(
    request: DetectAnomalyRequest,
    detector=Depends(get_anomaly_detector)
):
    """Detect price anomalies"""
    df = pd.DataFrame(request.ohlcv)
    result = detector.detect(df)
    return result
```

---

## 🔌 PHASE 4: API Integration (Tuần 7-8)

### 4.1 Main FastAPI Application

```python
# backend/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import trades, nlp, ml, alerts
from core.config import settings

app = FastAPI(
    title="Smart Trading Journal API",
    version="1.0.0",
    description="AI-powered trading journal with behavioral analysis"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trades.router, prefix=settings.API_PREFIX)
app.include_router(nlp.router, prefix=settings.API_PREFIX)
app.include_router(ml.router, prefix=settings.API_PREFIX)
app.include_router(alerts.router, prefix=settings.API_PREFIX)

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
```

### 4.2 Trade Endpoints

```python
# backend/api/trades.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models.database import get_db, Trade
from nlp.engine import NLPEngine

router = APIRouter(prefix="/trades", tags=["Trades"])

class TradeCreate(BaseModel):
    user_id: str
    symbol: str
    side: str
    entry_price: float
    quantity: float
    leverage: int = 1
    notes: Optional[str] = None

class TradeResponse(BaseModel):
    id: int
    symbol: str
    side: str
    entry_price: float
    quantity: float
    notes: Optional[str]
    nlp_sentiment: Optional[float]
    nlp_emotions: Optional[dict]
    created_at: datetime

@router.post("/", response_model=TradeResponse)
async def create_trade(
    trade: TradeCreate,
    db: Session = Depends(get_db),
    nlp: NLPEngine = Depends(get_nlp_engine)
):
    """Create a new trade with NLP analysis"""
    # NLP analysis
    nlp_result = None
    if trade.notes:
        nlp_result = nlp.analyze(trade.notes)

    # Create trade
    db_trade = Trade(
        user_id=trade.user_id,
        symbol=trade.symbol,
        side=trade.side,
        entry_price=trade.entry_price,
        quantity=trade.quantity,
        leverage=trade.leverage,
        notes=trade.notes,
        nlp_sentiment=nlp_result.get("sentiment_score") if nlp_result else None,
        nlp_emotions=nlp_result.get("emotions") if nlp_result else None,
        behavioral_flags=nlp_result.get("behavioral_flags") if nlp_result else None,
        nlp_quality_score=nlp_result.get("quality_score") if nlp_result else None
    )

    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)

    return db_trade

@router.get("/", response_model=List[TradeResponse])
async def get_trades(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get all trades for user"""
    trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    return trades
```

---

## 📱 PHASE 5: Frontend (Tuần 9-10)

### 5.1 Setup React App

```bash
cd frontend

npx create-react-app . --template typescript
npm install axios react-query @mui/material @emotion/react @emotion/styled
npm install recharts date-fns
```

### 5.2 API Service

```typescript
// frontend/src/services/api.ts

import axios from 'axios';

const API_BASE = 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// NLP
export const analyzeText = async (text: string) => {
  const { data } = await api.post('/nlp/analyze', { text });
  return data;
};

// Trades
export const createTrade = async (trade: any) => {
  const { data } = await api.post('/trades/', trade);
  return data;
};

export const getTrades = async (userId: string) => {
  const { data } = await api.get(`/trades/?user_id=${userId}`);
  return data;
};

// ML
export const detectAnomaly = async (symbol: string, ohlcv: any[]) => {
  const { data } = await api.post('/ml/detect-anomaly', { symbol, ohlcv });
  return data;
};
```

### 5.3 Trade Entry Component

```typescript
// frontend/src/components/TradeEntry.tsx

import React, { useState } from 'react';
import { Box, TextField, Button, MenuItem } from '@mui/material';
import { createTrade, analyzeText } from '../services/api';

export const TradeEntry: React.FC = () => {
  const [symbol, setSymbol] = useState('');
  const [side, setSide] = useState('long');
  const [entryPrice, setEntryPrice] = useState('');
  const [quantity, setQuantity] = useState('');
  const [notes, setNotes] = useState('');
  const [nlpResult, setNlpResult] = useState<any>(null);
  const [loading, setloading] = useState(false);

  const handleNotesChange = async (value: string) => {
    setNotes(value);
    if (value.length > 10) {
      const result = await analyzeText(value);
      setNlpResult(result);
    }
  };

  const handleSubmit = async () => {
    setloading(true);
    try {
      await createTrade({
        user_id: 'user1',  // From auth
        symbol,
        side,
        entry_price: parseFloat(entryPrice),
        quantity: parseFloat(quantity),
        notes
      });
      // Reset form
      setSymbol('');
      setNotes('');
      setNlpResult(null);
    } catch (error) {
      console.error('Error creating trade:', error);
    }
    setloading(false);
  };

  return (
    <Box>
      <TextField
        label="Symbol"
        value={symbol}
        onChange={(e) => setSymbol(e.target.value)}
      />
      <TextField
        select
        label="Side"
        value={side}
        onChange={(e) => setSide(e.target.value)}
      >
        <MenuItem value="long">Long</MenuItem>
        <MenuItem value="short">Short</MenuItem>
      </TextField>
      <TextField
        label="Entry Price"
        type="number"
        value={entryPrice}
        onChange={(e) => setEntryPrice(e.target.value)}
      />
      <TextField
        label="Quantity"
        type="number"
        value={quantity}
        onChange={(e) => setQuantity(e.target.value)}
      />
      <TextField
        label="Notes"
        multiline
        rows={4}
        value={notes}
        onChange={(e) => handleNotesChange(e.target.value)}
      />

      {/* NLP Result Display */}
      {nlpResult && (
        <Box>
          <h4>NLP Analysis:</h4>
          <p>Sentiment: {nlpResult.sentiment_label}</p>
          <p>Quality Score: {(nlpResult.quality_score * 100).toFixed(0)}%</p>
          {nlpResult.warnings.length > 0 && (
            <ul>
              {nlpResult.warnings.map((w: string, i: string) => (
                <li key={i}>{w}</li>
              ))}
            </ul>
          )}
        </Box>
      )}

      <Button onClick={handleSubmit} disabled={loading}>
        Add Trade
      </Button>
    </Box>
  );
};
```

---

## 🐳 PHASE 6: Deployment (Tuần 11-12)

### 6.1 Docker Compose

```yaml
# docker-compose.yml

version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: trading_journal
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  kafka:
    image: confluentinc/cp-kafka:latest
    ports:
      - "9092:9092"
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1

  zookeeper:
    image: confluentinc/cp-zookeeper:latest
    ports:
      - "2181:2181"
    environment:
      ZOOKEEPER_CLIENT_PORT: 2181

  backend:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - postgres
      - redis
      - kafka
    environment:
      DATABASE_URL: postgresql://trader:password@postgres:5432/trading_journal
      REDIS_URL: redis://redis:6379
      KAFKA_BOOTSTRAP_SERVERS: kafka:9092

volumes:
  postgres_data:
```

---

## 📊 CHECKLIST TRIỂN KHAI

### Week 1-2: Foundation
- [ ] Setup project structure
- [ ] Database schema migration
- [ ] Core configuration
- [ ] Basic API endpoints

### Week 3-4: NLP Engine
- [ ] Implement basic NLP engine
- [ ] Vietnamese keyword matching
- [ ] FinBERT integration
- [ ] NLP API endpoints

### Week 5-6: ML Detection
- [ ] Price anomaly detector
- [ ] Feature engineering
- [ ] Model training pipeline
- [ ] ML API endpoints

### Week 7-8: API Integration
- [ ] Trade CRUD operations
- [ ] Real-time alerts
- [ ] Kafka integration
- [ ] WebSocket endpoints

### Week 9-10: Frontend
- [ ] Trade entry UI
- [ ] Dashboard
- [ ] NLP result display
- [ ] Alert notifications

### Week 11-12: Testing & Deployment
- [ ] Unit tests
- [ ] Integration tests
- [ ] Docker deployment
- [ ] Documentation
