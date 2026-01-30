"""
Analysis API endpoints - Passive and Market analysis
Requires JWT authentication for passive analysis endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

from models import get_db, Trade, User
from analyzers import (
    get_passive_analyzer,
    get_market_analyzer,
    PassiveTrade,
    CandleStick
)
from core.auth import get_current_active_user, get_current_user_or_demo
from core.rate_limit import limiter

router = APIRouter(prefix="/analysis", tags=["Analysis"])


# ============ Request/Response Schemas ============

class PassiveAnalysisRequest(BaseModel):
    """Request for passive analysis"""
    limit: int = Field(default=100, ge=10, le=500)


class CandleInput(BaseModel):
    """Candlestick input data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float = 0.0


class MarketAnalysisRequest(BaseModel):
    """Request for market context analysis"""
    candles: List[CandleInput]
    current_price: Optional[float] = None


# ============ Endpoints ============

@router.post("/passive")
@limiter.limit("60/minute")
async def analyze_passive(
    http_request: Request,
    request: PassiveAnalysisRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Run passive analysis on authenticated user's trade history.

    Requires authentication.

    Analyzes:
    - Trade interval patterns (rushing after loss)
    - Position sizing patterns (revenge trading)
    - Hold duration patterns (loss aversion)
    - Time-based performance (best/worst hours)
    - Symbol performance (which coins to focus)

    Returns comprehensive report with recommendations.
    """
    user_id = str(current_user.id)

    # Fetch trades from database
    db_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .order_by(Trade.entry_time.desc())
        .limit(request.limit)
        .all()
    )

    if not db_trades:
        return {
            "error": "No trades found for this user",
            "user_id": user_id
        }
    
    # Convert to PassiveTrade format
    trades = []
    for t in db_trades:
        trades.append(PassiveTrade(
            id=t.id,
            symbol=t.symbol,
            side=t.side,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            quantity=t.quantity,
            pnl=t.pnl,
            pnl_pct=t.pnl_pct,
            entry_time=t.entry_time,
            exit_time=t.exit_time,
            hold_duration_minutes=t.hold_duration_minutes
        ))
    
    # Run analysis
    analyzer = get_passive_analyzer()
    report = analyzer.analyze(trades, user_id)

    return report.to_dict()


@router.get("/passive")
@limiter.limit("60/minute")
async def get_passive_analysis(
    request: Request,
    limit: int = 100,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get passive analysis for the authenticated user (GET method).

    Optional authentication (supports demo mode).
    """
    user_id = str(current_user.id)

    db_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .order_by(Trade.entry_time.desc())
        .limit(limit)
        .all()
    )

    if not db_trades:
        return {
            "error": "No trades found",
            "user_id": user_id
        }

    trades = [
        PassiveTrade(
            id=t.id,
            symbol=t.symbol,
            side=t.side,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            quantity=t.quantity,
            pnl=t.pnl,
            pnl_pct=t.pnl_pct,
            entry_time=t.entry_time,
            exit_time=t.exit_time,
            hold_duration_minutes=t.hold_duration_minutes
        )
        for t in db_trades
    ]

    analyzer = get_passive_analyzer()
    report = analyzer.analyze(trades, user_id)

    return report.to_dict()


@router.post("/market-context")
@limiter.limit("60/minute")
async def analyze_market_context(http_request: Request, request: MarketAnalysisRequest):
    """
    Analyze market context from candlestick data.

    This endpoint is public (no authentication required).

    Returns:
    - Technical indicators (RSI, MACD, SMA, EMA, ATR, Bollinger)
    - Candlestick patterns detected
    - Trend assessment
    - Volatility level
    - FOMO risk assessment
    """
    if len(request.candles) < 5:
        raise HTTPException(
            status_code=400,
            detail="At least 5 candles required for analysis"
        )

    # Convert to CandleStick objects
    candles = [
        CandleStick(
            timestamp=c.timestamp,
            open=c.open,
            high=c.high,
            low=c.low,
            close=c.close,
            volume=c.volume
        )
        for c in request.candles
    ]

    analyzer = get_market_analyzer()
    context = analyzer.analyze(candles, request.current_price)

    return context.to_dict()


@router.get("/intervals")
@limiter.limit("60/minute")
async def get_interval_analysis(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get interval analysis for the authenticated user.

    Requires authentication.
    """
    user_id = str(current_user.id)

    db_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .filter(Trade.exit_time.isnot(None))
        .order_by(Trade.entry_time.desc())
        .limit(100)
        .all()
    )

    if len(db_trades) < 3:
        return {"error": "Need at least 3 closed trades for interval analysis"}

    trades = [
        PassiveTrade(
            id=t.id, symbol=t.symbol, side=t.side,
            entry_price=t.entry_price, exit_price=t.exit_price,
            quantity=t.quantity, pnl=t.pnl, pnl_pct=t.pnl_pct,
            entry_time=t.entry_time, exit_time=t.exit_time,
            hold_duration_minutes=t.hold_duration_minutes
        )
        for t in db_trades
    ]

    analyzer = get_passive_analyzer()
    report = analyzer.analyze(trades, user_id)

    if report.interval_analysis:
        return report.interval_analysis.to_dict()
    return {"error": "Could not calculate interval analysis"}


@router.get("/sizing")
@limiter.limit("60/minute")
async def get_sizing_analysis(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get position sizing analysis for the authenticated user.

    Requires authentication.
    """
    user_id = str(current_user.id)

    db_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .filter(Trade.exit_time.isnot(None))
        .order_by(Trade.entry_time.desc())
        .limit(100)
        .all()
    )

    if len(db_trades) < 3:
        return {"error": "Need at least 3 closed trades for sizing analysis"}

    trades = [
        PassiveTrade(
            id=t.id, symbol=t.symbol, side=t.side,
            entry_price=t.entry_price, exit_price=t.exit_price,
            quantity=t.quantity, pnl=t.pnl, pnl_pct=t.pnl_pct,
            entry_time=t.entry_time, exit_time=t.exit_time,
            hold_duration_minutes=t.hold_duration_minutes
        )
        for t in db_trades
    ]

    analyzer = get_passive_analyzer()
    report = analyzer.analyze(trades, user_id)

    if report.sizing_analysis:
        return report.sizing_analysis.to_dict()
    return {"error": "Could not calculate sizing analysis"}


@router.get("/time-patterns")
@limiter.limit("60/minute")
async def get_time_analysis(
    request: Request,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Get time-based performance analysis for the authenticated user.

    Requires authentication.
    """
    user_id = str(current_user.id)

    db_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .filter(Trade.pnl_pct.isnot(None))
        .order_by(Trade.entry_time.desc())
        .limit(200)
        .all()
    )

    if len(db_trades) < 10:
        return {"error": "Need at least 10 closed trades for time analysis"}

    trades = [
        PassiveTrade(
            id=t.id, symbol=t.symbol, side=t.side,
            entry_price=t.entry_price, exit_price=t.exit_price,
            quantity=t.quantity, pnl=t.pnl, pnl_pct=t.pnl_pct,
            entry_time=t.entry_time, exit_time=t.exit_time,
            hold_duration_minutes=t.hold_duration_minutes
        )
        for t in db_trades
    ]

    analyzer = get_passive_analyzer()
    report = analyzer.analyze(trades, user_id)

    if report.time_analysis:
        return report.time_analysis.to_dict()
    return {"error": "Could not calculate time analysis"}


@router.get("/symbols")
@limiter.limit("60/minute")
async def get_symbol_analysis(
    request: Request,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get per-symbol performance analysis for the authenticated user.

    Optional authentication (supports demo mode).
    """
    user_id = str(current_user.id)

    db_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .filter(Trade.pnl_pct.isnot(None))
        .order_by(Trade.entry_time.desc())
        .limit(200)
        .all()
    )

    if len(db_trades) < 5:
        return {"error": "Need at least 5 closed trades for symbol analysis"}

    trades = [
        PassiveTrade(
            id=t.id, symbol=t.symbol, side=t.side,
            entry_price=t.entry_price, exit_price=t.exit_price,
            quantity=t.quantity, pnl=t.pnl, pnl_pct=t.pnl_pct,
            entry_time=t.entry_time, exit_time=t.exit_time,
            hold_duration_minutes=t.hold_duration_minutes
        )
        for t in db_trades
    ]

    analyzer = get_passive_analyzer()
    report = analyzer.analyze(trades, user_id)

    if report.symbol_analysis:
        return report.symbol_analysis.to_dict()
    return {"error": "Could not calculate symbol analysis"}


@router.get("/stats")
@limiter.limit("60/minute")
async def get_trade_stats(
    request: Request,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get trade statistics for the authenticated user.

    Optional authentication (supports demo mode).

    Returns:
    - total_trades: Total number of trades
    - closed_trades: Number of closed trades (with PnL)
    - win_rate: Percentage of winning trades
    - total_pnl: Sum of all PnL
    - avg_pnl_pct: Average PnL percentage
    - best_trade: Best trade PnL percentage
    - worst_trade: Worst trade PnL percentage
    """
    user_id = str(current_user.id)

    # Get all trades
    all_trades = (
        db.query(Trade)
        .filter(Trade.user_id == user_id)
        .all()
    )

    if not all_trades:
        return {
            "total_trades": 0,
            "closed_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl_pct": 0,
            "best_trade": 0,
            "worst_trade": 0
        }

    # Get closed trades (with PnL)
    closed_trades = [t for t in all_trades if t.pnl_pct is not None]

    if not closed_trades:
        return {
            "total_trades": len(all_trades),
            "closed_trades": 0,
            "win_rate": 0,
            "total_pnl": 0,
            "avg_pnl_pct": 0,
            "best_trade": 0,
            "worst_trade": 0
        }

    # Calculate statistics
    winning_trades = [t for t in closed_trades if t.pnl and t.pnl > 0]
    win_rate = len(winning_trades) / len(closed_trades) if closed_trades else 0

    total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
    avg_pnl_pct = sum(t.pnl_pct for t in closed_trades if t.pnl_pct) / len(closed_trades)

    pnl_pcts = [t.pnl_pct for t in closed_trades if t.pnl_pct]
    best_trade = max(pnl_pcts) if pnl_pcts else 0
    worst_trade = min(pnl_pcts) if pnl_pcts else 0

    return {
        "total_trades": len(all_trades),
        "closed_trades": len(closed_trades),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2) if total_pnl else 0,
        "avg_pnl_pct": round(avg_pnl_pct, 2),
        "best_trade": round(best_trade, 2),
        "worst_trade": round(worst_trade, 2)
    }
