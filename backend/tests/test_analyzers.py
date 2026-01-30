"""
Test Active Analyzer
Tests for FOMO, Revenge, and Tilt detectors
"""

import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers import (
    ActiveAnalyzer,
    get_active_analyzer,
    FOMODetector,
    RevengeTradingDetector,
    TiltDetector,
    DetectorMarketContext,  # Use detector's MarketContext
    TradeInfo
)
from analyzers.detectors.revenge_detector import SessionStats as RevengeSessionStats
from analyzers.detectors.tilt_detector import SessionStats as TiltSessionStats


def test_fomo_detector_keywords():
    """Test FOMO detection via keywords"""
    detector = FOMODetector()
    
    # FOMO keywords
    result = detector.detect(
        notes="Phải vào ngay kẻo lỡ! All in luôn!",
        market_context=None
    )
    
    assert result is not None, "Should detect FOMO from keywords"
    assert result.alert_type == "FOMO"
    print(f"✅ FOMO keywords detection: score={result.score}, severity={result.severity}")


def test_fomo_detector_price_pump():
    """Test FOMO detection via price pump"""
    detector = FOMODetector()

    # High price pump
    market_context = DetectorMarketContext(
        price_change_pct_1h=8.5,
        is_near_local_high=True
    )

    result = detector.detect(
        notes="BTC looking good",
        market_context=market_context
    )
    
    assert result is not None, "Should detect FOMO from price pump"
    assert result.score >= 50
    print(f"✅ FOMO price pump detection: score={result.score}")
    print(f"   Reasons: {result.reasons}")


def test_revenge_detector():
    """Test Revenge Trading detection"""
    detector = RevengeTradingDetector()
    
    # Setup: just lost -5%
    session_stats = RevengeSessionStats(
        last_trades=[
            TradeInfo(pnl=-100, pnl_pct=-5.0, quantity=1.0, exit_time=datetime.utcnow() - timedelta(minutes=5))
        ],
        avg_position_size=1.0,
        session_pnl=-100
    )
    
    result = detector.detect(
        notes="Phải gỡ lại ngay!",
        current_quantity=2.0,  # Doubled size
        entry_time=datetime.utcnow(),
        session_stats=session_stats
    )
    
    assert result is not None, "Should detect Revenge Trading"
    assert result.alert_type == "REVENGE_TRADING"
    assert result.severity in ["HIGH", "CRITICAL"]
    print(f"✅ Revenge Trading detection: score={result.score}, severity={result.severity}")
    print(f"   Reasons: {result.reasons}")


def test_tilt_detector():
    """Test Tilt detection"""
    detector = TiltDetector()
    
    # Setup: high drawdown, low win rate
    session_stats = TiltSessionStats(
        trade_count=10,
        win_count=2,
        loss_count=8,
        current_drawdown_pct=8.0,
        trades_last_hour=8,
        avg_trades_per_hour=2.0
    )
    
    result = detector.detect(
        notes="Frustrated! Market is rigged!",
        session_stats=session_stats
    )
    
    assert result is not None, "Should detect Tilt"
    assert result.alert_type == "TILT"
    print(f"✅ Tilt detection: score={result.score}, severity={result.severity}")
    print(f"   Reasons: {result.reasons}")


def test_active_analyzer_simple():
    """Test simplified Active Analyzer"""
    analyzer = get_active_analyzer()
    
    # Test FOMO scenario
    result = analyzer.analyze_simple(
        notes="Phải vào ngay! All in!",
        price_change_1h=7.0,
        recent_loss_pct=0.0,
        current_drawdown=0.0,
        trades_last_hour=1
    )
    
    assert len(result.alerts) > 0, "Should have alerts"
    print(f"✅ Active Analyzer simple: {len(result.alerts)} alerts")
    print(f"   Has critical: {result.has_critical}")
    print(f"   Should block: {result.should_block_trade}")
    print(f"   Risk score: {result.overall_risk_score}")


def test_no_alerts_for_rational():
    """Test no alerts for rational trading"""
    detector = FOMODetector()

    result = detector.detect(
        notes="Entry theo plan, SL 2%, TP 6%",
        market_context=DetectorMarketContext(price_change_pct_1h=1.0)
    )

    assert result is None, "Should not detect FOMO for rational trading"
    print("No false positive for rational notes")


def test_multiple_alerts():
    """Test detecting multiple issues at once"""
    analyzer = get_active_analyzer()
    
    # Scenario: FOMO + potential revenge
    result = analyzer.analyze_simple(
        notes="Phải gỡ lại! All in ngay kẻo lỡ!",
        price_change_1h=6.0,
        recent_loss_pct=3.0,
        current_drawdown=5.0,
        trades_last_hour=5
    )
    
    print(f"✅ Multiple alerts scenario:")
    print(f"   Total alerts: {len(result.alerts)}")
    for alert in result.alerts:
        print(f"   - {alert.alert_type}: {alert.severity} (score: {alert.score})")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Running Active Analyzer Tests")
    print("="*60 + "\n")
    
    tests = [
        test_fomo_detector_keywords,
        test_fomo_detector_price_pump,
        test_revenge_detector,
        test_tilt_detector,
        test_active_analyzer_simple,
        test_no_alerts_for_rational,
        test_multiple_alerts,
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
