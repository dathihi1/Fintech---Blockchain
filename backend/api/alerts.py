"""
Alerts API endpoints
Requires JWT authentication for all endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

from models import get_db, BehavioralAlert, User
from analyzers import get_active_analyzer
from core.auth import get_current_active_user, get_current_user_or_demo
from core.rate_limit import limiter

router = APIRouter(prefix="/alerts", tags=["Alerts"])


# ============ Request/Response Schemas ============

class AlertResponse(BaseModel):
    """Response schema for an alert"""
    id: int
    user_id: str
    trade_id: Optional[int]
    alert_type: str
    severity: str
    score: int
    reasons: List[str]
    recommendation: str
    acknowledged: bool
    acknowledged_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class AnalyzeRequest(BaseModel):
    """Request for quick behavioral analysis without creating trade"""
    notes: Optional[str] = None
    price_change_1h: float = 0.0
    recent_loss_pct: float = 0.0
    current_drawdown: float = 0.0
    trades_last_hour: int = 0


class AnalyzeResponse(BaseModel):
    """Response for behavioral analysis"""
    alerts: List[dict]
    has_critical: bool
    has_high: bool
    should_block_trade: bool
    overall_risk_score: int


# ============ Endpoints ============

@router.get("/", response_model=List[AlertResponse])
@limiter.limit("60/minute")
async def get_alerts(
    request: Request,
    active_only: bool = False,
    limit: int = 50,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get all alerts for the authenticated user.

    Optional authentication (supports demo mode).
    """
    query = db.query(BehavioralAlert).filter(
        BehavioralAlert.user_id == str(current_user.id)
    )

    if active_only:
        query = query.filter(BehavioralAlert.acknowledged == False)

    alerts = (
        query
        .order_by(BehavioralAlert.created_at.desc())
        .limit(limit)
        .all()
    )
    return alerts


@router.get("/active", response_model=List[AlertResponse])
@limiter.limit("60/minute")
async def get_active_alerts(
    request: Request,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get unacknowledged alerts for the authenticated user.

    Optional authentication (supports demo mode).
    """
    alerts = (
        db.query(BehavioralAlert)
        .filter(BehavioralAlert.user_id == str(current_user.id))
        .filter(BehavioralAlert.acknowledged == False)
        .order_by(BehavioralAlert.created_at.desc())
        .all()
    )
    return alerts


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
@limiter.limit("60/minute")
async def acknowledge_alert(
    request: Request,
    alert_id: int,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Acknowledge an alert.

    Requires authentication. Only acknowledges alerts owned by the authenticated user.
    """
    alert = db.query(BehavioralAlert).filter(
        BehavioralAlert.id == alert_id,
        BehavioralAlert.user_id == str(current_user.id)
    ).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.acknowledged = True
    alert.acknowledged_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)

    return alert


@router.post("/analyze", response_model=AnalyzeResponse)
@limiter.limit("60/minute")
async def analyze_behavior(request: Request, analyze_request: AnalyzeRequest):
    """
    Quick behavioral analysis without creating a trade.
    Useful for pre-trade check or real-time analysis.

    This endpoint is public (no authentication required).
    """
    analyzer = get_active_analyzer()

    result = analyzer.analyze_simple(
        notes=analyze_request.notes,
        price_change_1h=analyze_request.price_change_1h,
        recent_loss_pct=analyze_request.recent_loss_pct,
        current_drawdown=analyze_request.current_drawdown,
        trades_last_hour=analyze_request.trades_last_hour
    )

    return AnalyzeResponse(
        alerts=[a.to_dict() for a in result.alerts],
        has_critical=result.has_critical,
        has_high=result.has_high,
        should_block_trade=result.should_block_trade,
        overall_risk_score=result.overall_risk_score
    )


@router.get("/stats")
@limiter.limit("60/minute")
async def get_alert_stats(
    request: Request,
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    """
    Get alert statistics for the authenticated user.

    Optional authentication (supports demo mode).
    """
    all_alerts = (
        db.query(BehavioralAlert)
        .filter(BehavioralAlert.user_id == str(current_user.id))
        .all()
    )
    
    if not all_alerts:
        return {
            "total_alerts": 0,
            "by_type": {},
            "by_severity": {},
            "acknowledgement_rate": 0.0
        }
    
    # Count by type
    by_type = {}
    for alert in all_alerts:
        by_type[alert.alert_type] = by_type.get(alert.alert_type, 0) + 1
    
    # Count by severity
    by_severity = {}
    for alert in all_alerts:
        by_severity[alert.severity] = by_severity.get(alert.severity, 0) + 1
    
    # Acknowledgement rate
    acknowledged_count = sum(1 for a in all_alerts if a.acknowledged)
    ack_rate = acknowledged_count / len(all_alerts) if all_alerts else 0
    
    return {
        "total_alerts": len(all_alerts),
        "by_type": by_type,
        "by_severity": by_severity,
        "acknowledgement_rate": round(ack_rate, 2),
        "unacknowledged_count": len(all_alerts) - acknowledged_count
    }
