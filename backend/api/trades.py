"""
Trade API endpoints
Requires JWT authentication for all endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from models import get_db, Trade, NLPAnalysis, BehavioralAlert, User
from nlp import get_nlp_engine
from analyzers import get_active_analyzer
from core.auth import get_current_active_user, get_current_user_or_demo
from core.rate_limit import limiter

router = APIRouter(prefix="/trades", tags=["Trades"])


# ============ Request/Response Schemas ============

class TradeCreate(BaseModel):
    """Request schema for creating a trade"""
    symbol: str
    side: str = Field(..., pattern="^(long|short|BUY|SELL)$")
    entry_price: float = Field(..., gt=0)
    quantity: float = Field(..., gt=0)
    leverage: int = Field(default=1, ge=1, le=125)
    notes: Optional[str] = None


class TradeUpdate(BaseModel):
    """Request schema for updating/closing a trade"""
    exit_price: Optional[float] = None
    notes: Optional[str] = None


class TradeResponse(BaseModel):
    """Response schema for a trade"""
    id: int
    user_id: str
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    leverage: int
    pnl: Optional[float]
    pnl_pct: Optional[float]
    notes: Optional[str]
    nlp_sentiment: Optional[float]
    nlp_emotions: Optional[list]
    nlp_quality_score: Optional[float]
    behavioral_flags: Optional[list]
    entry_time: datetime
    exit_time: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class TradeWithAnalysis(BaseModel):
    """Response with trade and analysis results"""
    trade: TradeResponse
    nlp_analysis: Optional[dict] = None
    behavioral_alerts: list = []
    should_proceed: bool = True
    warnings: list = []


# ============ Endpoints ============

@router.post("/", response_model=TradeWithAnalysis)
@limiter.limit("60/minute")
async def create_trade(
    request: Request,
    trade_data: TradeCreate,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Create a new trade with NLP analysis and behavioral detection.

    Authentication optional in demo mode - uses demo_user if not authenticated.

    Returns trade data along with:
    - NLP analysis of notes (sentiment, emotions, quality)
    - Behavioral alerts (FOMO, Revenge Trading, Tilt)
    - Warnings and recommendations
    """
    nlp_engine = get_nlp_engine()
    active_analyzer = get_active_analyzer()

    # Normalize side
    side = trade_data.side.lower()
    if side in ("buy", "long"):
        side = "long"
    elif side in ("sell", "short"):
        side = "short"

    # Run NLP analysis on notes
    nlp_result = None
    if trade_data.notes:
        nlp_result = nlp_engine.analyze(trade_data.notes)

    # Run Active Analyzer
    analysis_result = active_analyzer.analyze_simple(
        notes=trade_data.notes,
        price_change_1h=0.0,  # Would need market data integration
        recent_loss_pct=0.0,
        current_drawdown=0.0,
        trades_last_hour=0
    )

    # Create trade in database using authenticated user's ID
    db_trade = Trade(
        user_id=str(current_user.id),
        symbol=trade_data.symbol.upper(),
        side=side,
        entry_price=trade_data.entry_price,
        quantity=trade_data.quantity,
        leverage=trade_data.leverage,
        notes=trade_data.notes,
        nlp_sentiment=nlp_result.sentiment_score if nlp_result else None,
        nlp_emotions=[e.to_dict() for e in nlp_result.emotions] if nlp_result else None,
        nlp_quality_score=nlp_result.quality_score if nlp_result else None,
        behavioral_flags=nlp_result.behavioral_flags if nlp_result else None
    )
    
    db.add(db_trade)
    db.commit()
    db.refresh(db_trade)
    
    # Save NLP analysis if exists
    if nlp_result:
        nlp_record = NLPAnalysis(
            trade_id=db_trade.id,
            language=nlp_result.language,
            sentiment_score=nlp_result.sentiment_score,
            sentiment_label=nlp_result.sentiment_label,
            emotions=[e.to_dict() for e in nlp_result.emotions],
            behavioral_flags=nlp_result.behavioral_flags,
            quality_score=nlp_result.quality_score,
            warnings=nlp_result.warnings
        )
        db.add(nlp_record)
    
    # Save behavioral alerts
    for alert in analysis_result.alerts:
        alert_record = BehavioralAlert(
            user_id=str(current_user.id),
            trade_id=db_trade.id,
            alert_type=alert.alert_type,
            severity=alert.severity,
            score=alert.score,
            reasons=alert.reasons,
            recommendation=alert.recommendation
        )
        db.add(alert_record)
    
    db.commit()
    
    # Build response
    warnings = nlp_result.warnings if nlp_result else []
    for alert in analysis_result.alerts:
        warnings.append(f"[{alert.severity}] {alert.alert_type}: {alert.recommendation}")
    
    return TradeWithAnalysis(
        trade=TradeResponse.model_validate(db_trade),
        nlp_analysis=nlp_result.to_dict() if nlp_result else None,
        behavioral_alerts=[a.to_dict() for a in analysis_result.alerts],
        should_proceed=not analysis_result.should_block_trade,
        warnings=warnings
    )


@router.get("/", response_model=List[TradeResponse])
@limiter.limit("60/minute")
async def get_trades(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get all trades for the authenticated user (or demo user in demo mode).

    Authentication optional in demo mode.
    """
    trades = (
        db.query(Trade)
        .filter(Trade.user_id == str(current_user.id))
        .order_by(Trade.created_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return trades


@router.get("/{trade_id}", response_model=TradeResponse)
@limiter.limit("60/minute")
async def get_trade(
    request: Request,
    trade_id: int,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get a specific trade by ID.

    Authentication optional in demo mode. Only returns trades owned by the user.
    """
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == str(current_user.id)
    ).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    return trade


@router.patch("/{trade_id}", response_model=TradeResponse)
@limiter.limit("60/minute")
async def update_trade(
    request: Request,
    trade_id: int,
    update_data: TradeUpdate,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Update or close a trade.

    Authentication optional in demo mode. Only updates trades owned by the user.
    """
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == str(current_user.id)
    ).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")
    
    # Update fields
    if update_data.exit_price is not None:
        trade.exit_price = update_data.exit_price
        trade.exit_time = datetime.utcnow()
        
        # Calculate P&L
        if trade.side == "long":
            trade.pnl_pct = ((update_data.exit_price - trade.entry_price) / trade.entry_price) * 100 * trade.leverage
        else:
            trade.pnl_pct = ((trade.entry_price - update_data.exit_price) / trade.entry_price) * 100 * trade.leverage
        
        trade.pnl = trade.quantity * trade.entry_price * (trade.pnl_pct / 100)
        
        # Calculate hold duration
        if trade.entry_time:
            hold_delta = trade.exit_time - trade.entry_time
            trade.hold_duration_minutes = int(hold_delta.total_seconds() / 60)
    
    if update_data.notes is not None:
        trade.notes = update_data.notes
        
        # Re-run NLP analysis
        nlp_engine = get_nlp_engine()
        nlp_result = nlp_engine.analyze(update_data.notes)
        trade.nlp_sentiment = nlp_result.sentiment_score
        trade.nlp_emotions = [e.to_dict() for e in nlp_result.emotions]
        trade.nlp_quality_score = nlp_result.quality_score
        trade.behavioral_flags = nlp_result.behavioral_flags
    
    db.commit()
    db.refresh(trade)
    
    return trade


@router.delete("/{trade_id}")
@limiter.limit("60/minute")
async def delete_trade(
    request: Request,
    trade_id: int,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Delete a trade.

    Authentication optional in demo mode. Only deletes trades owned by the user.
    """
    trade = db.query(Trade).filter(
        Trade.id == trade_id,
        Trade.user_id == str(current_user.id)
    ).first()
    if not trade:
        raise HTTPException(status_code=404, detail="Trade not found")

    db.delete(trade)
    db.commit()

    return {"message": "Trade deleted successfully"}
