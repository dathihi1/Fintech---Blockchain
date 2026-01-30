"""
Demo Script - Quick Demo of NLP and Active Analyzer
Chạy demo nhanh các tính năng chính
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import get_nlp_engine
from analyzers import get_active_analyzer


def demo_nlp():
    """Demo NLP Engine"""
    print("\n" + "="*60)
    print("🧠 NLP ENGINE DEMO")
    print("="*60)
    
    nlp = get_nlp_engine()
    
    # Test cases
    test_cases = [
        {
            "name": "FOMO Trade",
            "text": "BTC breakout! Phải vào ngay kẻo lỡ! All in luôn!"
        },
        {
            "name": "Revenge Trade",
            "text": "Thua 3 lệnh rồi, phải gỡ gạc bằng được. Tăng size x2!"
        },
        {
            "name": "Rational Trade",
            "text": "Entry theo plan, RR 1:3, đặt SL 2%, theo trend lớn."
        },
        {
            "name": "Fear/Panic",
            "text": "Sợ quá! Cắt lỗ ngay đi, thị trường sập rồi!"
        },
        {
            "name": "English FOMO",
            "text": "Must buy now! Can't miss this pump, all in!"
        }
    ]
    
    for tc in test_cases:
        print(f"\n📝 {tc['name']}")
        print(f"   Input: \"{tc['text']}\"")
        
        result = nlp.analyze(tc['text'])
        
        print(f"   Language: {result.language}")
        print(f"   Sentiment: {result.sentiment_label} ({result.sentiment_score:.2f})")
        print(f"   Quality Score: {result.quality_score:.2f}")
        
        if result.emotions:
            emotions_str = ", ".join([f"{e.type}({e.confidence:.0%})" for e in result.emotions])
            print(f"   Emotions: {emotions_str}")
        
        if result.behavioral_flags:
            print(f"   ⚠️ Flags: {result.behavioral_flags}")
        
        if result.warnings:
            for w in result.warnings[:2]:  # Show max 2 warnings
                print(f"   {w}")


def demo_active_analyzer():
    """Demo Active Analyzer"""
    print("\n\n" + "="*60)
    print("🔍 ACTIVE ANALYZER DEMO")
    print("="*60)
    
    analyzer = get_active_analyzer()
    
    scenarios = [
        {
            "name": "Normal Trading",
            "notes": "Following my strategy, small size test",
            "price_change_1h": 1.0,
            "recent_loss_pct": 0.0,
            "current_drawdown": 0.0,
            "trades_last_hour": 2
        },
        {
            "name": "FOMO Scenario",
            "notes": "Phải vào ngay! Pump quá mạnh!",
            "price_change_1h": 8.0,
            "recent_loss_pct": 0.0,
            "current_drawdown": 0.0,
            "trades_last_hour": 2
        },
        {
            "name": "Revenge Trading",
            "notes": "Gỡ lại thôi! Tăng size lên!",
            "price_change_1h": 0.0,
            "recent_loss_pct": 5.0,
            "current_drawdown": 5.0,
            "trades_last_hour": 4
        },
        {
            "name": "Tilt Scenario",
            "notes": "Frustrated! Thị trường điên quá!",
            "price_change_1h": 0.0,
            "recent_loss_pct": 3.0,
            "current_drawdown": 10.0,
            "trades_last_hour": 10
        }
    ]
    
    for sc in scenarios:
        print(f"\n📊 {sc['name']}")
        print(f"   Notes: \"{sc['notes']}\"")
        print(f"   Context: price_change={sc['price_change_1h']}%, drawdown={sc['current_drawdown']}%")
        
        result = analyzer.analyze_simple(
            notes=sc["notes"],
            price_change_1h=sc["price_change_1h"],
            recent_loss_pct=sc["recent_loss_pct"],
            current_drawdown=sc["current_drawdown"],
            trades_last_hour=sc["trades_last_hour"]
        )
        
        if result.alerts:
            print(f"   🚨 Alerts: {len(result.alerts)}")
            for alert in result.alerts:
                print(f"      [{alert.severity}] {alert.alert_type}: score={alert.score}")
                print(f"      → {alert.recommendation[:60]}...")
        else:
            print("   ✅ No alerts - Safe to trade")
        
        if result.should_block_trade:
            print("   ⛔ RECOMMENDATION: SHOULD NOT TRADE!")
        
        print(f"   Risk Score: {result.overall_risk_score}/100")


def main():
    """Run all demos"""
    print("\n" + "🎉 " * 20)
    print("SMART TRADING JOURNAL - FEATURE DEMO")
    print("🎉 " * 20)
    
    demo_nlp()
    demo_active_analyzer()
    
    print("\n\n" + "="*60)
    print("✅ Demo complete! Try the API at http://localhost:8000/docs")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
