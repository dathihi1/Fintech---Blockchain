"""
Test Market Context Analyzer
Tests for technical indicators and pattern detection
"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from analyzers.market_context import (
    MarketContextAnalyzer,
    CandleStick,
    get_market_analyzer
)


def create_sample_candles(count: int = 50, trend: str = "up"):
    """Create sample candlestick data"""
    candles = []
    base_time = datetime.utcnow() - timedelta(hours=count)
    base_price = 40000.0
    
    for i in range(count):
        if trend == "up":
            price_change = i * 50 + (100 if i % 3 == 0 else -30)
        elif trend == "down":
            price_change = -i * 50 + (-100 if i % 3 == 0 else 30)
        else:
            price_change = (i % 5 - 2) * 50
        
        open_price = base_price + price_change
        close_price = open_price + (50 if i % 2 == 0 else -30)
        high_price = max(open_price, close_price) + 20
        low_price = min(open_price, close_price) - 20
        volume = 1000000 + i * 10000
        
        candles.append(CandleStick(
            timestamp=base_time + timedelta(hours=i),
            open=open_price,
            high=high_price,
            low=low_price,
            close=close_price,
            volume=volume
        ))
    
    return candles


def test_analyzer_initialization():
    """Test analyzer initialization"""
    analyzer = MarketContextAnalyzer()
    assert analyzer is not None
    print("✅ Market Context Analyzer initialized successfully")


def test_empty_candles():
    """Test with no candles"""
    analyzer = get_market_analyzer()
    context = analyzer.analyze([])
    
    assert context.symbol == "UNKNOWN"
    assert context.price == 0.0
    print("✅ Empty candles handled correctly")


def test_price_changes():
    """Test price change calculations"""
    analyzer = get_market_analyzer()
    candles = create_sample_candles(30, "up")
    
    context = analyzer.analyze(candles)
    
    print(f"✅ Price Changes:")
    print(f"   1h change: {context.price_change_1h:.2f}%")
    print(f"   24h change: {context.price_change_24h:.2f}%")


def test_technical_indicators():
    """Test technical indicator calculations"""
    analyzer = get_market_analyzer()
    candles = create_sample_candles(50, "up")
    
    context = analyzer.analyze(candles)
    indicators = context.indicators
    
    print("✅ Technical Indicators:")
    if indicators:
        if indicators.sma_20:
            print(f"   SMA 20: {indicators.sma_20:.2f}")
        if indicators.sma_50:
            print(f"   SMA 50: {indicators.sma_50:.2f}")
        if indicators.rsi_14:
            print(f"   RSI 14: {indicators.rsi_14:.2f}")
        if indicators.macd:
            print(f"   MACD: {indicators.macd:.4f}")
        if indicators.atr_14:
            print(f"   ATR 14: {indicators.atr_14:.2f}")
        if indicators.bollinger_width:
            print(f"   BB Width: {indicators.bollinger_width:.2f}%")


def test_pattern_detection():
    """Test candlestick pattern detection"""
    analyzer = get_market_analyzer()
    
    # Create candles with potential patterns
    candles = create_sample_candles(20, "neutral")
    context = analyzer.analyze(candles)
    
    print(f"✅ Pattern Detection:")
    if context.patterns:
        for pattern in context.patterns:
            print(f"   {pattern.name} ({pattern.type}): {pattern.description}")
    else:
        print("   No patterns detected")


def test_trend_detection():
    """Test trend detection"""
    analyzer = get_market_analyzer()
    
    # Uptrend
    candles_up = create_sample_candles(50, "up")
    context_up = analyzer.analyze(candles_up)
    
    # Downtrend
    candles_down = create_sample_candles(50, "down")
    context_down = analyzer.analyze(candles_down)
    
    print(f"✅ Trend Detection:")
    print(f"   Uptrend candles: {context_up.trend}")
    print(f"   Downtrend candles: {context_down.trend}")


def test_volatility_detection():
    """Test volatility level detection"""
    analyzer = get_market_analyzer()
    candles = create_sample_candles(30, "up")
    
    context = analyzer.analyze(candles)
    
    print(f"✅ Volatility: {context.volatility}")


def test_fomo_risk():
    """Test FOMO risk assessment"""
    analyzer = get_market_analyzer()
    
    # Create candles with strong pump (should trigger FOMO)
    candles = []
    base_time = datetime.utcnow() - timedelta(hours=30)
    base_price = 40000.0
    
    for i in range(30):
        # Strong pump in last few candles
        if i > 25:
            price_change = (i - 25) * 500  # 10%+ pump
        else:
            price_change = i * 20
        
        open_price = base_price + price_change
        close_price = open_price + 100
        
        candles.append(CandleStick(
            timestamp=base_time + timedelta(hours=i),
            open=open_price,
            high=close_price + 50,
            low=open_price - 30,
            close=close_price,
            volume=2000000 if i > 25 else 1000000
        ))
    
    context = analyzer.analyze(candles)
    
    print(f"✅ FOMO Risk Assessment:")
    print(f"   Price change 1h: {context.price_change_1h:.2f}%")
    print(f"   Near 24h high: {context.is_near_high}")
    print(f"   FOMO Risk: {context.fomo_risk}")


def test_context_to_dict():
    """Test serialization"""
    analyzer = get_market_analyzer()
    candles = create_sample_candles(20, "up")
    
    context = analyzer.analyze(candles)
    context_dict = context.to_dict()
    
    assert "price" in context_dict
    assert "indicators" in context_dict
    assert "patterns" in context_dict
    assert "trend" in context_dict
    assert "fomo_risk" in context_dict
    
    print("✅ Context serialization works correctly")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Running Market Context Analyzer Tests")
    print("="*60 + "\n")
    
    tests = [
        test_analyzer_initialization,
        test_empty_candles,
        test_price_changes,
        test_technical_indicators,
        test_pattern_detection,
        test_trend_detection,
        test_volatility_detection,
        test_fomo_risk,
        test_context_to_dict,
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
