"""
Test script to check NLP behavioral flags and risk score
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nlp.engine import NLPEngine
from analyzers.passive_analyzer import PassiveAnalyzer
from models import Trade
from datetime import datetime, timedelta

def test_nlp_flags():
    """Test if NLP engine detects behavioral flags"""
    print("=" * 60)
    print("TEST 1: NLP Behavioral Flags Detection")
    print("=" * 60)
    
    engine = NLPEngine(use_gpu=False, enable_ml_classifier=False)
    
    test_texts = [
        ("FOMO quá! Phải mua ngay không bỏ lỡ", "FOMO"),
        ("Thua rồi phải vào lại gấp đôi", "REVENGE"),
        ("Sợ quá, cắt lỗ đi", "FEAR"),
        ("Phân tích kỹ, setup tốt, vào lệnh", "RATIONAL"),
        ("Chắc chắn sẽ tăng, all-in!", "OVERCONFIDENCE"),
    ]
    
    for text, expected_flag in test_texts:
        result = engine.analyze(text)
        print(f"\nText: {text}")
        print(f"Expected: {expected_flag}")
        print(f"Behavioral Flags: {result.behavioral_flags}")
        print(f"Emotions: {[e.type for e in result.emotions]}")
        print(f"Quality Score: {result.quality_score}")
        
        if not result.behavioral_flags:
            print("❌ NO FLAGS DETECTED!")
        else:
            print(f"✅ Detected: {result.behavioral_flags}")

def test_risk_score():
    """Test if passive analyzer calculates risk score"""
    print("\n" + "=" * 60)
    print("TEST 2: Risk Score Calculation")
    print("=" * 60)
    
    analyzer = PassiveAnalyzer()
    
    # Create test trades with problematic patterns
    trades = []
    base_time = datetime.utcnow()
    
    # Pattern: Loss → Quick revenge trade → Another loss
    trades.append(Trade(
        id=1,
        user_id="1",
        symbol="BTCUSDT",
        side="long",
        entry_price=45000,
        exit_price=44000,  # Loss
        quantity=1.0,
        pnl=-1000,
        pnl_pct=-2.22,
        entry_time=base_time - timedelta(hours=2),
        exit_time=base_time - timedelta(hours=1, minutes=55),
        hold_duration_minutes=5
    ))
    
    # Quick revenge trade (5 minutes after loss)
    trades.append(Trade(
        id=2,
        user_id="1", 
        symbol="BTCUSDT",
        side="long",
        entry_price=44000,
        exit_price=43500,  # Another loss
        quantity=2.0,  # Doubled size!
        pnl=-1000,
        pnl_pct=-1.14,
        entry_time=base_time - timedelta(hours=1, minutes=50),
        exit_time=base_time - timedelta(hours=1, minutes=45),
        hold_duration_minutes=5
    ))
    
    # Normal trade after win
    trades.append(Trade(
        id=3,
        user_id="1",
        symbol="ETHUSDT",
        side="long",
        entry_price=3000,
        exit_price=3100,  # Win
        quantity=1.0,
        pnl=100,
        pnl_pct=3.33,
        entry_time=base_time - timedelta(hours=1),
        exit_time=base_time - timedelta(minutes=55),
        hold_duration_minutes=5
    ))
    
    # Convert to analyzer Trade format
    analyzer_trades = [
        analyzer.Trade(
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
        for t in trades
    ]
    
    try:
        report = analyzer.analyze(user_id="1", trades=analyzer_trades)
        
        print(f"\nTotal Trades: {report.total_trades}")
        print(f"Win Rate: {report.win_rate * 100:.1f}%")
        print(f"Risk Score: {report.risk_score}/100")
        
        if report.interval_analysis:
            print(f"\nInterval Analysis:")
            print(f"  Rushing after loss: {report.interval_analysis.rushing_after_loss}")
            print(f"  Rush ratio: {report.interval_analysis.rush_ratio:.2f}x")
        
        if report.sizing_analysis:
            print(f"\nSizing Analysis:")
            print(f"  Revenge pattern: {report.sizing_analysis.revenge_pattern_detected}")
            print(f"  Severity: {report.sizing_analysis.severity}")
        
        if report.hold_analysis:
            print(f"\nHold Analysis:")
            print(f"  Loss aversion: {report.hold_analysis.loss_aversion_detected}")
        
        print(f"\nRecommendations:")
        for rec in report.recommendations:
            print(f"  - {rec}")
        
        if report.risk_score == 0:
            print("\n❌ RISK SCORE IS 0 - NOT CALCULATING PROPERLY!")
        else:
            print(f"\n✅ Risk Score calculated: {report.risk_score}")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

def test_database_trades():
    """Test with real database trades"""
    print("\n" + "=" * 60)
    print("TEST 3: Database Trades Check")
    print("=" * 60)
    
    try:
        from models import get_db, Trade as DBTrade
        from sqlalchemy import inspect
        
        db = next(get_db())
        
        # Get first trade
        trade = db.query(DBTrade).first()
        
        if trade:
            print(f"\nTrade ID: {trade.id}")
            print(f"Symbol: {trade.symbol}")
            print(f"Notes: {trade.notes}")
            print(f"Behavioral Flags: {trade.behavioral_flags}")
            print(f"NLP Sentiment: {trade.nlp_sentiment}")
            print(f"NLP Quality Score: {trade.nlp_quality_score}")
            print(f"NLP Emotions: {trade.nlp_emotions}")
            
            if not trade.behavioral_flags or trade.behavioral_flags == []:
                print("\n❌ NO BEHAVIORAL FLAGS IN DATABASE!")
                print("Possible causes:")
                print("1. NLP engine not detecting flags")
                print("2. Flags not being saved to database")
                print("3. Empty notes (no text to analyze)")
            else:
                print(f"\n✅ Has flags: {trade.behavioral_flags}")
        else:
            print("No trades found in database")
            
        db.close()
        
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_nlp_flags()
    test_risk_score()
    test_database_trades()
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
Common Issues:
1. NLP flags not detected → Check keyword matching
2. Risk score = 0 → Need enough trades with loss patterns
3. Flags not in DB → Check if notes are provided when creating trade
    
To fix:
- Create trades with FOMO/REVENGE keywords in notes
- Need at least 3 trades with losses for risk calculation
- Check if behavioral flags are being saved properly
    """)
