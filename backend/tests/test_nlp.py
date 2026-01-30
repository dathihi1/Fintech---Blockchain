"""
Test NLP Engine
Tests for the NLP engine functionality
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import NLPEngine, get_nlp_engine


def test_nlp_engine_initialization():
    """Test NLP engine can be initialized"""
    engine = NLPEngine(use_gpu=False)
    assert engine is not None
    print("✅ NLP Engine initialized successfully")


def test_vietnamese_detection():
    """Test Vietnamese language detection"""
    engine = get_nlp_engine()
    
    # Vietnamese text
    vn_text = "Phải vào ngay kẻo lỡ cơ hội"
    result = engine.analyze(vn_text)
    assert result.language == "vi", f"Expected 'vi', got '{result.language}'"
    print(f"✅ Vietnamese detection: '{vn_text}' -> {result.language}")
    
    # English text
    en_text = "Must buy now, can't miss this opportunity"
    result = engine.analyze(en_text)
    assert result.language == "en", f"Expected 'en', got '{result.language}'"
    print(f"✅ English detection: '{en_text}' -> {result.language}")


def test_fomo_detection():
    """Test FOMO emotion detection"""
    engine = get_nlp_engine()
    
    # FOMO text Vietnamese
    fomo_text = "BTC breakout, phải vào ngay kẻo lỡ! All in luôn!"
    result = engine.analyze(fomo_text)
    
    fomo_emotions = [e for e in result.emotions if e.type == "FOMO"]
    assert len(fomo_emotions) > 0, "Should detect FOMO"
    assert "FOMO" in result.behavioral_flags
    print(f"✅ FOMO detection: Found {len(fomo_emotions)} FOMO indicators")
    print(f"   Keywords: {fomo_emotions[0].matched_keywords}")


def test_revenge_detection():
    """Test REVENGE emotion detection"""
    engine = get_nlp_engine()
    
    revenge_text = "Thua 3 lệnh rồi, phải gỡ gạc bằng được! Tăng size gấp đôi"
    result = engine.analyze(revenge_text)
    
    revenge_emotions = [e for e in result.emotions if e.type == "REVENGE"]
    assert len(revenge_emotions) > 0, "Should detect REVENGE"
    print(f"✅ REVENGE detection: Found {len(revenge_emotions)} REVENGE indicators")
    print(f"   Keywords: {revenge_emotions[0].matched_keywords}")


def test_rational_detection():
    """Test RATIONAL (positive) emotion detection"""
    engine = get_nlp_engine()
    
    rational_text = "Đã phân tích kỹ, RR 1:3, đặt stop loss chặt, theo kế hoạch"
    result = engine.analyze(rational_text)
    
    rational_emotions = [e for e in result.emotions if e.type == "RATIONAL"]
    assert len(rational_emotions) > 0, "Should detect RATIONAL"
    assert result.quality_score > 0.5, f"Quality score should be > 0.5, got {result.quality_score}"
    print(f"✅ RATIONAL detection: Quality score = {result.quality_score:.2f}")
    print(f"   Keywords: {rational_emotions[0].matched_keywords}")


def test_quality_scoring():
    """Test quality scoring"""
    engine = get_nlp_engine()
    
    # Low quality (emotional)
    low_quality = "FOMO quá, all in ngay đi!"
    result1 = engine.analyze(low_quality)
    
    # High quality (rational)
    high_quality = "Entry theo plan, SL 2%, TP 6%, RR 1:3"
    result2 = engine.analyze(high_quality)
    
    assert result1.quality_score < result2.quality_score, \
        f"Emotional text should have lower quality score: {result1.quality_score} vs {result2.quality_score}"
    
    print(f"✅ Quality scoring works:")
    print(f"   Low quality text: {result1.quality_score:.2f}")
    print(f"   High quality text: {result2.quality_score:.2f}")


def test_warnings_generation():
    """Test warning generation"""
    engine = get_nlp_engine()
    
    fomo_text = "Sợ lỡ quá, phải mua gấp ngay!"
    result = engine.analyze(fomo_text)
    
    assert len(result.warnings) > 0, "Should generate warnings"
    print(f"✅ Warnings generated:")
    for warning in result.warnings:
        print(f"   - {warning}")


def test_empty_text():
    """Test handling of empty text"""
    engine = get_nlp_engine()
    
    result = engine.analyze("")
    assert result.language == "unknown"
    assert result.sentiment_score == 0.0
    assert len(result.emotions) == 0
    print("✅ Empty text handled correctly")


def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 Running NLP Engine Tests")
    print("="*60 + "\n")
    
    tests = [
        test_nlp_engine_initialization,
        test_vietnamese_detection,
        test_fomo_detection,
        test_revenge_detection,
        test_rational_detection,
        test_quality_scoring,
        test_warnings_generation,
        test_empty_text,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__}: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"📊 Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
