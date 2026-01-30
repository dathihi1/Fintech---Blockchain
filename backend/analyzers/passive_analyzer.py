"""
Passive Analyzer - Phân tích thụ động từ lịch sử giao dịch
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from statistics import mean, stdev
import math


@dataclass
class Trade:
    """Trade data for analysis"""
    id: int
    symbol: str
    side: str
    entry_price: float
    exit_price: Optional[float]
    quantity: float
    pnl: Optional[float]
    pnl_pct: Optional[float]
    entry_time: datetime
    exit_time: Optional[datetime]
    hold_duration_minutes: Optional[int] = None


@dataclass 
class IntervalAnalysis:
    """Trade interval analysis results"""
    avg_interval_after_loss: float  # minutes
    avg_interval_after_win: float
    rushing_after_loss: bool
    rush_ratio: float  # how much faster after loss
    recommendation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "avg_interval_after_loss": self.avg_interval_after_loss,
            "avg_interval_after_win": self.avg_interval_after_win,
            "rushing_after_loss": self.rushing_after_loss,
            "rush_ratio": self.rush_ratio,
            "recommendation": self.recommendation
        }


@dataclass
class SizingAnalysis:
    """Position sizing analysis results"""
    avg_size_increase_after_loss: float
    avg_size_increase_after_win: float
    revenge_pattern_detected: bool
    severity: str  # 'LOW', 'MEDIUM', 'HIGH'
    recommendation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "avg_size_increase_after_loss": self.avg_size_increase_after_loss,
            "avg_size_increase_after_win": self.avg_size_increase_after_win,
            "revenge_pattern_detected": self.revenge_pattern_detected,
            "severity": self.severity,
            "recommendation": self.recommendation
        }


@dataclass
class HoldAnalysis:
    """Hold duration analysis results"""
    avg_winning_hold_minutes: float
    avg_losing_hold_minutes: float
    loss_aversion_ratio: float
    loss_aversion_detected: bool
    recommendation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "avg_winning_hold_minutes": self.avg_winning_hold_minutes,
            "avg_losing_hold_minutes": self.avg_losing_hold_minutes,
            "loss_aversion_ratio": self.loss_aversion_ratio,
            "loss_aversion_detected": self.loss_aversion_detected,
            "recommendation": self.recommendation
        }


@dataclass
class TimeAnalysis:
    """Time-based performance analysis"""
    best_hours: List[int]  # Hours with highest win rate
    worst_hours: List[int]
    best_days: List[str]  # Day names
    worst_days: List[str]
    hourly_stats: Dict[int, Dict]  # {hour: {win_rate, avg_pnl, trade_count}}
    recommendation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "best_hours": self.best_hours,
            "worst_hours": self.worst_hours,
            "best_days": self.best_days,
            "worst_days": self.worst_days,
            "hourly_stats": self.hourly_stats,
            "recommendation": self.recommendation
        }


@dataclass
class SymbolAnalysis:
    """Per-symbol performance analysis"""
    symbol_stats: Dict[str, Dict]  # {symbol: {win_rate, avg_pnl, trade_count, sharpe}}
    best_symbols: List[str]
    worst_symbols: List[str]
    recommendation: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "symbol_stats": self.symbol_stats,
            "best_symbols": self.best_symbols,
            "worst_symbols": self.worst_symbols,
            "recommendation": self.recommendation
        }


@dataclass
class PassiveAnalysisReport:
    """Complete passive analysis report"""
    user_id: str
    period: str
    generated_at: datetime
    
    # Basic metrics
    total_trades: int
    win_rate: float
    profit_factor: float
    avg_pnl_pct: float
    max_drawdown: float
    
    # Behavioral patterns
    interval_analysis: Optional[IntervalAnalysis] = None
    sizing_analysis: Optional[SizingAnalysis] = None
    hold_analysis: Optional[HoldAnalysis] = None
    time_analysis: Optional[TimeAnalysis] = None
    symbol_analysis: Optional[SymbolAnalysis] = None
    
    # Summary
    recommendations: List[str] = field(default_factory=list)
    risk_score: float = 0.0  # 0-100
    
    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "period": self.period,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "total_trades": self.total_trades,
            "win_rate": self.win_rate,
            "profit_factor": self.profit_factor,
            "avg_pnl_pct": self.avg_pnl_pct,
            "max_drawdown": self.max_drawdown,
            "interval_analysis": self.interval_analysis.to_dict() if self.interval_analysis else None,
            "sizing_analysis": self.sizing_analysis.to_dict() if self.sizing_analysis else None,
            "hold_analysis": self.hold_analysis.to_dict() if self.hold_analysis else None,
            "time_analysis": self.time_analysis.to_dict() if self.time_analysis else None,
            "symbol_analysis": self.symbol_analysis.to_dict() if self.symbol_analysis else None,
            "recommendations": self.recommendations,
            "risk_score": self.risk_score
        }


class PassiveAnalyzer:
    """
    Passive Analyzer - Analyzes historical trades for behavioral patterns.
    """
    
    def __init__(self):
        pass
    
    def analyze(self, trades: List[Trade], user_id: str = "unknown") -> PassiveAnalysisReport:
        """
        Run full passive analysis on trade history.
        
        Args:
            trades: List of trades sorted by entry_time
            user_id: User identifier
            
        Returns:
            PassiveAnalysisReport with all analysis results
        """
        if not trades:
            return self._empty_report(user_id)
        
        # Sort trades by entry time
        trades = sorted(trades, key=lambda t: t.entry_time)
        
        # Calculate basic metrics
        total_trades = len(trades)
        closed_trades = [t for t in trades if t.pnl is not None]
        
        wins = [t for t in closed_trades if t.pnl > 0]
        losses = [t for t in closed_trades if t.pnl < 0]
        
        win_rate = len(wins) / len(closed_trades) if closed_trades else 0
        
        total_profit = sum(t.pnl for t in wins) if wins else 0
        total_loss = abs(sum(t.pnl for t in losses)) if losses else 1
        profit_factor = total_profit / total_loss if total_loss > 0 else 0
        
        avg_pnl_pct = mean([t.pnl_pct for t in closed_trades if t.pnl_pct]) if closed_trades else 0
        
        max_drawdown = self._calculate_max_drawdown(closed_trades)
        
        # Run analyses
        interval_analysis = self._analyze_intervals(closed_trades)
        sizing_analysis = self._analyze_sizing(closed_trades)
        hold_analysis = self._analyze_hold_duration(closed_trades)
        time_analysis = self._analyze_time_patterns(closed_trades)
        symbol_analysis = self._analyze_symbols(closed_trades)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            interval_analysis, sizing_analysis, hold_analysis, 
            time_analysis, symbol_analysis
        )
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(
            interval_analysis, sizing_analysis, hold_analysis
        )
        
        return PassiveAnalysisReport(
            user_id=user_id,
            period=f"last_{total_trades}_trades",
            generated_at=datetime.utcnow(),
            total_trades=total_trades,
            win_rate=round(win_rate, 4),
            profit_factor=round(profit_factor, 2),
            avg_pnl_pct=round(avg_pnl_pct, 2),
            max_drawdown=round(max_drawdown, 2),
            interval_analysis=interval_analysis,
            sizing_analysis=sizing_analysis,
            hold_analysis=hold_analysis,
            time_analysis=time_analysis,
            symbol_analysis=symbol_analysis,
            recommendations=recommendations,
            risk_score=round(risk_score, 1)
        )
    
    def _analyze_intervals(self, trades: List[Trade]) -> Optional[IntervalAnalysis]:
        """Analyze time intervals between trades"""
        if len(trades) < 3:
            return None
        
        intervals_after_loss = []
        intervals_after_win = []
        
        for i in range(1, len(trades)):
            prev_trade = trades[i - 1]
            curr_trade = trades[i]
            
            if prev_trade.exit_time and curr_trade.entry_time:
                interval_minutes = (curr_trade.entry_time - prev_trade.exit_time).total_seconds() / 60
                
                if interval_minutes >= 0:  # Valid interval
                    if prev_trade.pnl and prev_trade.pnl < 0:
                        intervals_after_loss.append(interval_minutes)
                    elif prev_trade.pnl and prev_trade.pnl > 0:
                        intervals_after_win.append(interval_minutes)
        
        if not intervals_after_loss or not intervals_after_win:
            return None
        
        avg_after_loss = mean(intervals_after_loss)
        avg_after_win = mean(intervals_after_win)
        
        rush_ratio = avg_after_loss / avg_after_win if avg_after_win > 0 else 1
        rushing = rush_ratio < 0.5  # Trading 2x faster after loss
        
        recommendation = None
        if rushing:
            recommendation = f"⚠️ Bạn vào lệnh nhanh hơn {(1-rush_ratio)*100:.0f}% sau khi thua. Hãy chờ ít nhất 30 phút sau loss."
        
        return IntervalAnalysis(
            avg_interval_after_loss=round(avg_after_loss, 1),
            avg_interval_after_win=round(avg_after_win, 1),
            rushing_after_loss=rushing,
            rush_ratio=round(rush_ratio, 2),
            recommendation=recommendation
        )
    
    def _analyze_sizing(self, trades: List[Trade]) -> Optional[SizingAnalysis]:
        """Analyze position sizing patterns"""
        if len(trades) < 3:
            return None
        
        size_changes_after_loss = []
        size_changes_after_win = []
        
        for i in range(1, len(trades)):
            prev_trade = trades[i - 1]
            curr_trade = trades[i]
            
            if prev_trade.quantity and curr_trade.quantity:
                size_ratio = curr_trade.quantity / prev_trade.quantity
                
                if prev_trade.pnl and prev_trade.pnl < 0:
                    size_changes_after_loss.append(size_ratio)
                elif prev_trade.pnl and prev_trade.pnl > 0:
                    size_changes_after_win.append(size_ratio)
        
        if not size_changes_after_loss:
            return None
        
        avg_after_loss = mean(size_changes_after_loss)
        avg_after_win = mean(size_changes_after_win) if size_changes_after_win else 1.0
        
        revenge_detected = avg_after_loss > 1.3  # >30% increase after loss
        
        if avg_after_loss > 1.5:
            severity = "HIGH"
        elif avg_after_loss > 1.3:
            severity = "MEDIUM"
        else:
            severity = "LOW"
        
        recommendation = None
        if revenge_detected:
            recommendation = f"🛑 Phát hiện REVENGE PATTERN: Size tăng {(avg_after_loss-1)*100:.0f}% sau loss. Hãy giữ size cố định!"
        
        return SizingAnalysis(
            avg_size_increase_after_loss=round(avg_after_loss, 2),
            avg_size_increase_after_win=round(avg_after_win, 2),
            revenge_pattern_detected=revenge_detected,
            severity=severity,
            recommendation=recommendation
        )
    
    def _analyze_hold_duration(self, trades: List[Trade]) -> Optional[HoldAnalysis]:
        """Analyze hold duration patterns"""
        winning_holds = [t.hold_duration_minutes for t in trades if t.pnl and t.pnl > 0 and t.hold_duration_minutes]
        losing_holds = [t.hold_duration_minutes for t in trades if t.pnl and t.pnl < 0 and t.hold_duration_minutes]
        
        if not winning_holds or not losing_holds:
            return None
        
        avg_win_hold = mean(winning_holds)
        avg_loss_hold = mean(losing_holds)
        
        ratio = avg_loss_hold / avg_win_hold if avg_win_hold > 0 else 1
        loss_aversion = ratio > 2  # Holding losers 2x longer than winners
        
        recommendation = None
        if loss_aversion:
            recommendation = f"⚠️ Loss Aversion: Giữ lệnh lỗ gấp {ratio:.1f}x lệnh lời. Hãy cắt lỗ nhanh hơn!"
        
        return HoldAnalysis(
            avg_winning_hold_minutes=round(avg_win_hold, 1),
            avg_losing_hold_minutes=round(avg_loss_hold, 1),
            loss_aversion_ratio=round(ratio, 2),
            loss_aversion_detected=loss_aversion,
            recommendation=recommendation
        )
    
    def _analyze_time_patterns(self, trades: List[Trade]) -> Optional[TimeAnalysis]:
        """Analyze performance by time of day and day of week"""
        if len(trades) < 10:
            return None
        
        hourly_data = {}  # {hour: [pnl_pct, ...]}
        daily_data = {}   # {day_name: [pnl_pct, ...]}
        
        for trade in trades:
            if trade.pnl_pct is None:
                continue
                
            hour = trade.entry_time.hour
            day = trade.entry_time.strftime("%A")
            
            if hour not in hourly_data:
                hourly_data[hour] = []
            hourly_data[hour].append(trade.pnl_pct)
            
            if day not in daily_data:
                daily_data[day] = []
            daily_data[day].append(trade.pnl_pct)
        
        # Calculate hourly stats
        hourly_stats = {}
        for hour, pnls in hourly_data.items():
            wins = sum(1 for p in pnls if p > 0)
            hourly_stats[hour] = {
                "win_rate": round(wins / len(pnls), 2) if pnls else 0,
                "avg_pnl": round(mean(pnls), 2) if pnls else 0,
                "trade_count": len(pnls)
            }
        
        # Find best/worst hours
        sorted_hours = sorted(hourly_stats.items(), key=lambda x: x[1]["win_rate"], reverse=True)
        best_hours = [h for h, _ in sorted_hours[:3] if hourly_stats[h]["trade_count"] >= 3]
        worst_hours = [h for h, _ in sorted_hours[-3:] if hourly_stats[h]["trade_count"] >= 3]
        
        # Find best/worst days
        daily_win_rates = {}
        for day, pnls in daily_data.items():
            wins = sum(1 for p in pnls if p > 0)
            daily_win_rates[day] = wins / len(pnls) if pnls else 0
        
        sorted_days = sorted(daily_win_rates.items(), key=lambda x: x[1], reverse=True)
        best_days = [d for d, _ in sorted_days[:2]]
        worst_days = [d for d, _ in sorted_days[-2:]]
        
        recommendation = None
        if worst_hours and best_hours:
            recommendation = f"📊 Trade nhiều vào {best_hours[0]}h-{best_hours[-1]}h, tránh {worst_hours[0]}h-{worst_hours[-1]}h"
        
        return TimeAnalysis(
            best_hours=best_hours,
            worst_hours=worst_hours,
            best_days=best_days,
            worst_days=worst_days,
            hourly_stats=hourly_stats,
            recommendation=recommendation
        )
    
    def _analyze_symbols(self, trades: List[Trade]) -> Optional[SymbolAnalysis]:
        """Analyze performance by trading symbol"""
        if len(trades) < 5:
            return None
        
        symbol_data = {}
        
        for trade in trades:
            if trade.pnl_pct is None:
                continue
                
            symbol = trade.symbol
            if symbol not in symbol_data:
                symbol_data[symbol] = []
            symbol_data[symbol].append(trade.pnl_pct)
        
        symbol_stats = {}
        for symbol, pnls in symbol_data.items():
            if len(pnls) < 2:
                continue
                
            wins = sum(1 for p in pnls if p > 0)
            avg_pnl = mean(pnls)
            
            # Simple Sharpe approximation
            if len(pnls) > 1:
                try:
                    std = stdev(pnls)
                    sharpe = avg_pnl / std if std > 0 else 0
                except:
                    sharpe = 0
            else:
                sharpe = 0
            
            symbol_stats[symbol] = {
                "win_rate": round(wins / len(pnls), 2),
                "avg_pnl": round(avg_pnl, 2),
                "trade_count": len(pnls),
                "sharpe": round(sharpe, 2)
            }
        
        if not symbol_stats:
            return None
        
        # Sort by Sharpe
        sorted_symbols = sorted(symbol_stats.items(), key=lambda x: x[1]["sharpe"], reverse=True)
        best_symbols = [s for s, _ in sorted_symbols[:3] if symbol_stats[s]["trade_count"] >= 3]
        worst_symbols = [s for s, _ in sorted_symbols[-3:] if symbol_stats[s]["trade_count"] >= 3]
        
        recommendation = None
        if best_symbols and worst_symbols and best_symbols[0] != worst_symbols[-1]:
            recommendation = f"💡 Focus vào {best_symbols[0]} (Sharpe={symbol_stats[best_symbols[0]]['sharpe']}), tránh {worst_symbols[-1]}"
        
        return SymbolAnalysis(
            symbol_stats=symbol_stats,
            best_symbols=best_symbols,
            worst_symbols=worst_symbols,
            recommendation=recommendation
        )
    
    def _calculate_max_drawdown(self, trades: List[Trade]) -> float:
        """Calculate maximum drawdown from trade history"""
        if not trades:
            return 0.0
        
        cumulative = 0.0
        peak = 0.0
        max_dd = 0.0
        
        for trade in trades:
            if trade.pnl_pct:
                cumulative += trade.pnl_pct
                if cumulative > peak:
                    peak = cumulative
                dd = peak - cumulative
                if dd > max_dd:
                    max_dd = dd
        
        return max_dd
    
    def _generate_recommendations(
        self,
        interval: Optional[IntervalAnalysis],
        sizing: Optional[SizingAnalysis],
        hold: Optional[HoldAnalysis],
        time: Optional[TimeAnalysis],
        symbol: Optional[SymbolAnalysis]
    ) -> List[str]:
        """Compile all recommendations"""
        recs = []
        
        if interval and interval.recommendation:
            recs.append(interval.recommendation)
        if sizing and sizing.recommendation:
            recs.append(sizing.recommendation)
        if hold and hold.recommendation:
            recs.append(hold.recommendation)
        if time and time.recommendation:
            recs.append(time.recommendation)
        if symbol and symbol.recommendation:
            recs.append(symbol.recommendation)
        
        if not recs:
            recs.append("✅ Không phát hiện vấn đề nghiêm trọng. Tiếp tục duy trì kỷ luật!")
        
        return recs
    
    def _calculate_risk_score(
        self,
        interval: Optional[IntervalAnalysis],
        sizing: Optional[SizingAnalysis],
        hold: Optional[HoldAnalysis]
    ) -> float:
        """Calculate overall behavioral risk score (0-100)"""
        score = 0.0
        
        if interval and interval.rushing_after_loss:
            score += 25
        
        if sizing and sizing.revenge_pattern_detected:
            if sizing.severity == "HIGH":
                score += 35
            elif sizing.severity == "MEDIUM":
                score += 25
            else:
                score += 15
        
        if hold and hold.loss_aversion_detected:
            score += 20
        
        return min(100, score)
    
    def _empty_report(self, user_id: str) -> PassiveAnalysisReport:
        """Return empty report when no trades available"""
        return PassiveAnalysisReport(
            user_id=user_id,
            period="no_trades",
            generated_at=datetime.utcnow(),
            total_trades=0,
            win_rate=0.0,
            profit_factor=0.0,
            avg_pnl_pct=0.0,
            max_drawdown=0.0,
            recommendations=["📊 Chưa có dữ liệu giao dịch để phân tích"],
            risk_score=0.0
        )


# Singleton
_passive_analyzer: Optional[PassiveAnalyzer] = None

def get_passive_analyzer() -> PassiveAnalyzer:
    """Get or create Passive Analyzer singleton"""
    global _passive_analyzer
    if _passive_analyzer is None:
        _passive_analyzer = PassiveAnalyzer()
    return _passive_analyzer
