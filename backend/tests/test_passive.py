"""
Test Passive Analyzer
Tests for behavioral pattern analysis
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.passive_analyzer import (
    PassiveAnalyzer,
    Trade,
    get_passive_analyzer
)


def create_sample_trades(count: int = 20):
    """Create sample trades for testing"""
    trades = []
    base_time = datetime.utcnow() - timedelta(days=7)
    
    for i in range(count):
        is_win = i % 3 != 0  # ~67% win rate
        pnl = 100 if is_win else -150
        pnl_pct = 2.0 if is_win else -3.0
        
        # After loss, enter faster (simulate revenge pattern)
        if i > 0 and trades[-1].pnl < 0:
            interval = timedelta(minutes=10)  # Fast entry after loss
            quantity = trades[-1].quantity * 1.5  # Increase size
        else:
            interval = timedelta(minutes=45)
            quantity = 1.0
        
        entry_time = base_time + timedelta(hours=i * 2) + interval
        hold_duration = 30 if is_win else 90  # Hold losers longer
        
        trades.append(Trade(
            id=i + 1,
            symbol="BTCUSDT" if i % 2 == 0 else "ETHUSDT",
            side="long",
            entry_price=40000 + i * 100,
            exit_price=40000 + i * 100 + (200 if is_win else -300),
            quantity=quantity,
            pnl=pnl,
            pnl_pct=pnl_pct,
            entry_time=entry_time,
            exit_time=entry_time + timedelta(minutes=hold_duration),
            hold_duration_minutes=hold_duration
        ))
    
    return trades


def test_passive_analyzer_initialization():
    """Test analyzer initialization"""
    analyzer = PassiveAnalyzer()
    assert analyzer is not None
    print("✅ Passive Analyzer initialized successfully")


def test_empty_trades():
    """Test with no trades"""
    analyzer = get_passive_analyzer()
    report = analyzer.analyze([], "user1")
    
    assert report.total_trades == 0
    assert len(report.recommendations) > 0
    print("✅ Empty trades handled correctly")


def test_basic_metrics():
    """Test basic metrics calculation"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    assert report.total_trades == 20
    assert 0 <= report.win_rate <= 1
    assert report.profit_factor >= 0
    print(f"✅ Basic metrics: win_rate={report.win_rate:.2%}, profit_factor={report.profit_factor}")


def test_interval_analysis():
    """Test trade interval pattern detection"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    if report.interval_analysis:
        ia = report.interval_analysis
        print(f"✅ Interval Analysis:")
        print(f"   Avg after loss: {ia.avg_interval_after_loss:.1f} min")
        print(f"   Avg after win: {ia.avg_interval_after_win:.1f} min")
        print(f"   Rushing after loss: {ia.rushing_after_loss}")
    else:
        print("⚠️ Interval analysis not available (need more trades)")


def test_sizing_analysis():
    """Test position sizing pattern detection"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    if report.sizing_analysis:
        sa = report.sizing_analysis
        print(f"✅ Sizing Analysis:")
        print(f"   Avg size increase after loss: {sa.avg_size_increase_after_loss:.2f}x")
        print(f"   Revenge pattern: {sa.revenge_pattern_detected}")
        print(f"   Severity: {sa.severity}")
    else:
        print("⚠️ Sizing analysis not available")


def test_hold_analysis():
    """Test hold duration pattern detection"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    if report.hold_analysis:
        ha = report.hold_analysis
        print(f"✅ Hold Analysis:")
        print(f"   Avg winning hold: {ha.avg_winning_hold_minutes:.1f} min")
        print(f"   Avg losing hold: {ha.avg_losing_hold_minutes:.1f} min")
        print(f"   Loss aversion ratio: {ha.loss_aversion_ratio:.2f}x")
        print(f"   Loss aversion detected: {ha.loss_aversion_detected}")
    else:
        print("⚠️ Hold analysis not available")


def test_time_analysis():
    """Test time-based performance analysis"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    if report.time_analysis:
        ta = report.time_analysis
        print(f"✅ Time Analysis:")
        print(f"   Best hours: {ta.best_hours}")
        print(f"   Worst hours: {ta.worst_hours}")
    else:
        print("⚠️ Time analysis not available (need more trades)")


def test_symbol_analysis():
    """Test per-symbol performance analysis"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    if report.symbol_analysis:
        sa = report.symbol_analysis
        print(f"✅ Symbol Analysis:")
        print(f"   Best symbols: {sa.best_symbols}")
        print(f"   Worst symbols: {sa.worst_symbols}")
        for symbol, stats in sa.symbol_stats.items():
            print(f"   {symbol}: win_rate={stats['win_rate']:.0%}, sharpe={stats['sharpe']}")
    else:
        print("⚠️ Symbol analysis not available")


def test_recommendations():
    """Test recommendation generation"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    assert len(report.recommendations) > 0
    print(f"✅ Recommendations ({len(report.recommendations)}):")
    for rec in report.recommendations[:3]:
        print(f"   → {rec[:60]}...")


def test_risk_score():
    """Test risk score calculation"""
    analyzer = get_passive_analyzer()
    trades = create_sample_trades(20)
    
    report = analyzer.analyze(trades, "test_user")
    
    assert 0 <= report.risk_score <= 100
    print(f"✅ Risk Score: {report.risk_score}/100")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Running Passive Analyzer Tests")
    print("="*60 + "\n")
    
    tests = [
        test_passive_analyzer_initialization,
        test_empty_trades,
        test_basic_metrics,
        test_interval_analysis,
        test_sizing_analysis,
        test_hold_analysis,
        test_time_analysis,
        test_symbol_analysis,
        test_recommendations,
        test_risk_score,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
            print()
        except Exception as e:
            print(f"❌ {test.__name__}: {e}\n")
            failed += 1
    
    print("="*60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
