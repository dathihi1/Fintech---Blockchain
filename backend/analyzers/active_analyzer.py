"""
Active Analyzer - Real-time behavioral analysis
Phân tích hành vi giao dịch theo thời gian thực
"""

from dataclasses import dataclass, field
from typing import Optional, List
from datetime import datetime

from .detectors import (
    FOMODetector,
    RevengeTradingDetector,
    TiltDetector,
    Alert,
    MarketContext,
    TradeInfo,
    RevengeSessionStats,
    TiltSessionStats
)


@dataclass
class ActiveAnalysisResult:
    """Result of active analysis"""
    alerts: List[Alert] = field(default_factory=list)
    has_critical: bool = False
    has_high: bool = False
    should_block_trade: bool = False
    overall_risk_score: int = 0
    
    def to_dict(self) -> dict:
        return {
            "alerts": [a.to_dict() for a in self.alerts],
            "has_critical": self.has_critical,
            "has_high": self.has_high,
            "should_block_trade": self.should_block_trade,
            "overall_risk_score": self.overall_risk_score
        }


@dataclass
class TradeContext:
    """Context for analyzing a trade"""
    user_id: str
    symbol: str
    side: str  # 'long' or 'short'
    entry_price: float
    quantity: float
    notes: Optional[str] = None
    entry_time: datetime = field(default_factory=datetime.utcnow)
    
    # Market context (optional)
    price_change_1h: float = 0.0
    price_change_24h: float = 0.0
    is_near_high: bool = False
    volume_ratio: float = 1.0
    
    # Session context (optional)
    last_trades: List[TradeInfo] = field(default_factory=list)
    avg_position_size: float = 0.0
    session_pnl: float = 0.0
    current_drawdown_pct: float = 0.0
    trade_count: int = 0
    win_count: int = 0
    loss_count: int = 0
    session_duration_hours: float = 0.0
    avg_trades_per_hour: float = 1.0
    trades_last_hour: int = 0


class ActiveAnalyzer:
    """
    Main Active Analyzer class.
    Orchestrates all detectors for real-time behavioral analysis.
    """
    
    def __init__(self):
        self.fomo_detector = FOMODetector()
        self.revenge_detector = RevengeTradingDetector()
        self.tilt_detector = TiltDetector()
    
    def analyze(self, context: TradeContext) -> ActiveAnalysisResult:
        """
        Analyze a trade for behavioral risks.
        
        Args:
            context: TradeContext with all relevant information
            
        Returns:
            ActiveAnalysisResult with alerts and risk assessment
        """
        alerts = []
        
        # Build market context
        market_context = MarketContext(
            price_change_pct_1h=context.price_change_1h,
            price_change_pct_24h=context.price_change_24h,
            is_near_local_high=context.is_near_high,
            volume_ratio=context.volume_ratio
        )
        
        # Build revenge session stats
        revenge_stats = RevengeSessionStats(
            last_trades=context.last_trades,
            avg_position_size=context.avg_position_size,
            session_pnl=context.session_pnl,
            current_drawdown_pct=context.current_drawdown_pct
        )
        
        # Build tilt session stats
        tilt_stats = TiltSessionStats(
            trade_count=context.trade_count,
            win_count=context.win_count,
            loss_count=context.loss_count,
            session_pnl=context.session_pnl,
            current_drawdown_pct=context.current_drawdown_pct,
            session_duration_hours=context.session_duration_hours,
            avg_trades_per_hour=context.avg_trades_per_hour,
            trades_last_hour=context.trades_last_hour
        )
        
        # Run FOMO detector
        fomo_alert = self.fomo_detector.detect(
            notes=context.notes,
            market_context=market_context,
            entry_price=context.entry_price
        )
        if fomo_alert:
            alerts.append(fomo_alert)
        
        # Run Revenge detector
        revenge_alert = self.revenge_detector.detect(
            notes=context.notes,
            current_quantity=context.quantity,
            entry_time=context.entry_time,
            session_stats=revenge_stats
        )
        if revenge_alert:
            alerts.append(revenge_alert)
        
        # Run Tilt detector
        tilt_alert = self.tilt_detector.detect(
            notes=context.notes,
            session_stats=tilt_stats
        )
        if tilt_alert:
            alerts.append(tilt_alert)
        
        # Calculate overall assessment
        has_critical = any(a.severity == "CRITICAL" for a in alerts)
        has_high = any(a.severity == "HIGH" for a in alerts)
        
        # Should block trade if any CRITICAL alert or multiple HIGH alerts
        should_block_trade = has_critical or sum(1 for a in alerts if a.severity == "HIGH") >= 2
        
        # Overall risk score (0-100)
        if alerts:
            overall_risk_score = min(100, sum(a.score for a in alerts) // len(alerts) + len(alerts) * 10)
        else:
            overall_risk_score = 0
        
        return ActiveAnalysisResult(
            alerts=alerts,
            has_critical=has_critical,
            has_high=has_high,
            should_block_trade=should_block_trade,
            overall_risk_score=overall_risk_score
        )
    
    def analyze_simple(
        self,
        notes: Optional[str] = None,
        price_change_1h: float = 0.0,
        recent_loss_pct: float = 0.0,
        current_drawdown: float = 0.0,
        trades_last_hour: int = 0
    ) -> ActiveAnalysisResult:
        """
        Simplified analysis with minimal context.
        Useful when full session data is not available.
        
        Args:
            notes: Trade notes
            price_change_1h: Price change in last hour (%)
            recent_loss_pct: Recent loss percentage (if any)
            current_drawdown: Current session drawdown (%)
            trades_last_hour: Number of trades in last hour
            
        Returns:
            ActiveAnalysisResult with alerts
        """
        alerts = []
        
        # FOMO check
        market_context = MarketContext(
            price_change_pct_1h=price_change_1h,
            is_near_local_high=price_change_1h > 5
        )
        fomo_alert = self.fomo_detector.detect(notes=notes, market_context=market_context)
        if fomo_alert:
            alerts.append(fomo_alert)
        
        # Simple revenge check based on notes
        if notes:
            note_lower = notes.lower()
            revenge_keywords = ["gỡ", "trả thù", "lấy lại", "revenge", "get back"]
            if any(kw in note_lower for kw in revenge_keywords) and recent_loss_pct > 1:
                alerts.append(Alert(
                    alert_type="REVENGE_TRADING",
                    severity="HIGH",
                    score=65,
                    reasons=["Phát hiện tâm lý revenge trading trong notes", f"Vừa thua {recent_loss_pct:.1f}%"],
                    recommendation="⚠️ Cảnh giác: Nghỉ 30 phút trước khi trade tiếp"
                ))
        
        # Simple tilt check
        tilt_stats = TiltSessionStats(
            current_drawdown_pct=current_drawdown,
            trades_last_hour=trades_last_hour,
            avg_trades_per_hour=2.0  # Assume average
        )
        tilt_alert = self.tilt_detector.detect(notes=notes, session_stats=tilt_stats)
        if tilt_alert:
            alerts.append(tilt_alert)
        
        # Build result
        has_critical = any(a.severity == "CRITICAL" for a in alerts)
        has_high = any(a.severity == "HIGH" for a in alerts)
        
        return ActiveAnalysisResult(
            alerts=alerts,
            has_critical=has_critical,
            has_high=has_high,
            should_block_trade=has_critical,
            overall_risk_score=sum(a.score for a in alerts) if alerts else 0
        )


# Singleton instance
_active_analyzer: Optional[ActiveAnalyzer] = None


def get_active_analyzer() -> ActiveAnalyzer:
    """Get or create Active Analyzer singleton"""
    global _active_analyzer
    if _active_analyzer is None:
        _active_analyzer = ActiveAnalyzer()
    return _active_analyzer
