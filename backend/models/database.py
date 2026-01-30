from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, JSON, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship
from datetime import datetime


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


class Trade(Base):
    """Trade model - Stores individual trades"""
    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)

    # Trade details
    symbol = Column(String, index=True, nullable=False)
    side = Column(String, nullable=False)  # 'long' or 'short'
    entry_price = Column(Float, nullable=False)
    exit_price = Column(Float, nullable=True)
    quantity = Column(Float, nullable=False)
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
    nlp_emotions = Column(JSON, nullable=True)  # [{"type": "FOMO", "confidence": 0.8}]
    nlp_quality_score = Column(Float, nullable=True)

    # Behavioral flags
    behavioral_flags = Column(JSON, nullable=True)  # ["FOMO", "REVENGE"]

    # Market context at entry
    market_context = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class NLPAnalysis(Base):
    """NLP Analysis results for trade notes"""
    __tablename__ = "nlp_analyses"

    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, ForeignKey("trades.id"), index=True)

    # Analysis results
    language = Column(String)  # 'vi' or 'en'
    sentiment_score = Column(Float)  # -1 to 1
    sentiment_label = Column(String)  # 'positive', 'negative', 'neutral'
    emotions = Column(JSON)  # [{"type": "FOMO", "confidence": 0.8, "matched_keywords": [...]}]
    behavioral_flags = Column(JSON)  # ["FOMO", "REVENGE"]
    quality_score = Column(Float)  # 0 to 1

    # Warnings generated
    warnings = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)


class BehavioralAlert(Base):
    """Real-time behavioral alerts from Active Analyzer"""
    __tablename__ = "behavioral_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)

    # Alert details
    alert_type = Column(String, nullable=False)  # 'FOMO', 'REVENGE_TRADING', 'TILT', 'OVERCONFIDENCE'
    severity = Column(String, nullable=False)  # 'INFO', 'MEDIUM', 'HIGH', 'CRITICAL'
    score = Column(Integer)  # 0-100

    # Details
    reasons = Column(JSON)  # ["Price đã tăng 8% trong 1h qua", "Matched keywords: phải vào ngay"]
    recommendation = Column(Text)

    # Status
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, index=True)


class UserSession(Base):
    """Track user trading session for Active Analyzer"""
    __tablename__ = "user_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)

    # Session stats
    session_start = Column(DateTime, default=datetime.utcnow)
    session_pnl = Column(Float, default=0.0)
    trade_count = Column(Integer, default=0)
    win_count = Column(Integer, default=0)
    loss_count = Column(Integer, default=0)

    # Drawdown tracking
    peak_balance = Column(Float, default=0.0)
    current_drawdown_pct = Column(Float, default=0.0)

    # Last trade info (for quick access)
    last_trade_pnl = Column(Float, nullable=True)
    last_trade_time = Column(DateTime, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
