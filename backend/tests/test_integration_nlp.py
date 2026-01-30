"""
Integration Tests for Enhanced NLP & ML
Tests all improvements working together
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import NLPEngine
import json


def test_full_pipeline():
    """Test complete NLP pipeline with all improvements"""
    print("\n" + "=" * 60)
    print("🧪 Full Pipeline Integration Test")
    print("=" * 60)
    
    # Initialize engine with all features
    engine = NLPEngine(
        use_gpu=False,
        enable_ml_classifier=False,  # Set True if model trained
        enable_logging=False  # Disable for testing
    )
    
    test_cases = [
        # Vietnamese - FOMO detection with word boundary
        {
            "text": "BTC đang pump, phải vào ngay kẻo lỡ tàu!",
            "checks": {
                "language": "vi",
                "has_fomo": True,
                "has_warnings": True,
                "quality_low": True
            }
        },
        
        # Vietnamese - Negation handling
        {
            "text": "Không FOMO, kiên nhẫn chờ pullback theo kế hoạch",
            "checks": {
                "language": "vi",
                "has_fomo": False,  # Should NOT detect FOMO (negated)
                "has_discipline": True,
                "quality_high": True
            }
        },
        
        # Vietnamese - Rational trading
        {
            "text": "Phân tích kỹ, RR 1:3, SL tại 0.95, TP tại 1.05",
            "checks": {
                "language": "vi",
                "has_rational": True,
                "quality_high": True,
                "sentiment_positive": True
            }
        },
        
        # Vietnamese - Revenge trading
        {
            "text": "Thua 3 lệnh rồi, phải gỡ gạc! Tăng size x2",
            "checks": {
                "language": "vi",
                "has_revenge": True,
                "quality_low": True,
                "has_warnings": True
            }
        },
        
        # Vietnamese - Manipulation detection
        {
            "text": "Tin nội bộ sắp list Binance, pump x10 chắc chắn",
            "checks": {
                "language": "vi",
                "has_manipulation": True,
                "has_greed": True,
                "quality_low": True
            }
        },
        
        # English - FOMO
        {
            "text": "BTC pumping hard, must buy now before too late!",
            "checks": {
                "language": "en",
                "has_fomo": True,
                "quality_low": True
            }
        },
        
        # English - Negation
        {
            "text": "No fear of missing out, waiting for confirmation",
            "checks": {
                "language": "en",
                "has_fomo": False,
                "has_discipline": True
            }
        },
        
        # Mixed language
        {
            "text": "Setup đẹp, high probability trade, theo plan",
            "checks": {
                "language": "vi",  # Majority Vietnamese
                "has_rational": True,
                "has_confident": True
            }
        }
    ]
    
    passed = 0
    failed = 0
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'=' * 60}")
        print(f"Test Case {i}: {test['text'][:50]}...")
        print(f"{'=' * 60}")
        
        result = engine.analyze(test["text"])
        
        # Check results
        checks = test["checks"]
        test_passed = True
        
        # Language check
        if "language" in checks:
            if result.language == checks["language"]:
                print(f"✅ Language: {result.language}")
            else:
                print(f"❌ Language: expected {checks['language']}, got {result.language}")
                test_passed = False
        
        # Emotion checks
        detected_emotions = {e.type for e in result.emotions}
        
        if checks.get("has_fomo"):
            if "FOMO" in detected_emotions:
                print(f"✅ FOMO detected")
            else:
                print(f"❌ FOMO not detected")
                test_passed = False
        
        if checks.get("has_fomo") == False:  # Explicitly False
            if "FOMO" not in detected_emotions:
                print(f"✅ FOMO correctly NOT detected (negation working)")
            else:
                print(f"❌ FOMO incorrectly detected (negation failed)")
                test_passed = False
        
        if checks.get("has_revenge"):
            if "REVENGE" in detected_emotions:
                print(f"✅ REVENGE detected")
            else:
                print(f"❌ REVENGE not detected")
                test_passed = False
        
        if checks.get("has_rational"):
            if "RATIONAL" in detected_emotions:
                print(f"✅ RATIONAL detected")
            else:
                print(f"❌ RATIONAL not detected")
                test_passed = False
        
        if checks.get("has_discipline"):
            if "DISCIPLINE" in detected_emotions:
                print(f"✅ DISCIPLINE detected")
            else:
                print(f"❌ DISCIPLINE not detected")
                test_passed = False
        
        if checks.get("has_confident"):
            if "CONFIDENT" in detected_emotions:
                print(f"✅ CONFIDENT detected")
            else:
                print(f"❌ CONFIDENT not detected")
                test_passed = False
        
        if checks.get("has_manipulation"):
            if "MANIPULATION" in detected_emotions:
                print(f"✅ MANIPULATION detected")
            else:
                print(f"❌ MANIPULATION not detected")
                test_passed = False
        
        if checks.get("has_greed"):
            if "GREED" in detected_emotions:
                print(f"✅ GREED detected")
            else:
                print(f"❌ GREED not detected")
                test_passed = False
        
        # Quality checks
        if checks.get("quality_low"):
            if result.quality_score < 0.5:
                print(f"✅ Quality low: {result.quality_score:.2f}")
            else:
                print(f"❌ Quality should be low, got {result.quality_score:.2f}")
                test_passed = False
        
        if checks.get("quality_high"):
            if result.quality_score >= 0.5:
                print(f"✅ Quality high: {result.quality_score:.2f}")
            else:
                print(f"❌ Quality should be high, got {result.quality_score:.2f}")
                test_passed = False
        
        # Sentiment checks
        if checks.get("sentiment_positive"):
            if result.sentiment_score > 0:
                print(f"✅ Sentiment positive: {result.sentiment_score:.2f}")
            else:
                print(f"❌ Sentiment should be positive, got {result.sentiment_score:.2f}")
                test_passed = False
        
        # Warnings check
        if checks.get("has_warnings"):
            if len(result.warnings) > 0:
                print(f"✅ Warnings generated: {len(result.warnings)}")
            else:
                print(f"❌ No warnings generated")
                test_passed = False
        
        # Print detailed results
        print(f"\n📊 Full Results:")
        print(f"   Sentiment: {result.sentiment_label} ({result.sentiment_score:.2f})")
        print(f"   Emotions: {detected_emotions}")
        print(f"   Quality: {result.quality_score:.2f}")
        print(f"   Warnings: {len(result.warnings)}")
        
        if result.emotions:
            print(f"\n🔍 Emotion Details:")
            for emotion in result.emotions:
                print(f"   - {emotion.type}: {emotion.confidence:.2f} ({', '.join(emotion.matched_keywords[:3])})")
        
        if result.warnings:
            print(f"\n⚠️ Warnings:")
            for warning in result.warnings:
                print(f"   - {warning}")
        
        # Track results
        if test_passed:
            print(f"\n✅ TEST PASSED")
            passed += 1
        else:
            print(f"\n❌ TEST FAILED")
            failed += 1
    
    # Summary
    print("\n" + "=" * 60)
    print(f"📊 Test Summary")
    print("=" * 60)
    print(f"Total tests: {len(test_cases)}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 All integration tests passed!")
    else:
        print(f"\n⚠️ {failed} test(s) failed - review needed")


if __name__ == "__main__":
    test_full_pipeline()
