"""
NLP Benchmark and Testing Utility
Compares performance before/after improvements
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import NLPEngine
import time
from typing import List, Dict
import json


# Test cases for Vietnamese
VIETNAMESE_TEST_CASES = [
    {
        "text": "BTC breakout, phải vào ngay kẻo lỡ! All in luôn!",
        "expected_emotions": ["FOMO", "GREED"],
        "expected_quality": "low",
        "description": "FOMO + Greed pattern"
    },
    {
        "text": "Đã phân tích kỹ, RR 1:3, đặt stop loss tại 0.95, theo kế hoạch",
        "expected_emotions": ["RATIONAL", "DISCIPLINE"],
        "expected_quality": "high",
        "description": "Rational trading with plan"
    },
    {
        "text": "Thua 3 lệnh rồi, phải gỡ gạc bằng được! Tăng size gấp đôi",
        "expected_emotions": ["REVENGE"],
        "expected_quality": "low",
        "description": "Revenge trading"
    },
    {
        "text": "Không FOMO nữa, chờ xác nhận setup trước khi vào",
        "expected_emotions": ["DISCIPLINE", "RATIONAL"],
        "expected_quality": "high",
        "description": "Negated FOMO (discipline)"
    },
    {
        "text": "Tin nội bộ BTC sắp list ETF, pump x10 chắc luôn",
        "expected_emotions": ["MANIPULATION", "GREED"],
        "expected_quality": "low",
        "description": "Market manipulation indicator"
    },
    {
        "text": "Setup đẹp theo trend lớn, size nhỏ test trước",
        "expected_emotions": ["CONFIDENT", "DISCIPLINE"],
        "expected_quality": "high",
        "description": "Confident but disciplined"
    },
    {
        "text": "Panic rồi, sợ cháy tài khoản, cắt lỗ ngay!",
        "expected_emotions": ["FEAR"],
        "expected_quality": "low",
        "description": "Fear and panic"
    },
    {
        "text": "Chắc chắn thắng 100%, không thể sai được, ez game",
        "expected_emotions": ["OVERCONFIDENCE"],
        "expected_quality": "low",
        "description": "Overconfidence"
    }
]

# Test cases for English
ENGLISH_TEST_CASES = [
    {
        "text": "BTC breaking out, must buy now before it's too late!",
        "expected_emotions": ["FOMO"],
        "expected_quality": "low",
        "description": "FOMO pattern"
    },
    {
        "text": "Following my plan, RR 1:3, stop loss set at $50k",
        "expected_emotions": ["RATIONAL"],
        "expected_quality": "high",
        "description": "Rational with risk management"
    },
    {
        "text": "Lost 3 trades, need to get it back now. Doubling position size",
        "expected_emotions": ["REVENGE"],
        "expected_quality": "low",
        "description": "Revenge trading"
    },
    {
        "text": "No FOMO this time, waiting for confirmation",
        "expected_emotions": ["DISCIPLINE"],
        "expected_quality": "high",
        "description": "Negated FOMO"
    }
]


def benchmark_language_detection(engine: NLPEngine):
    """Test language detection accuracy"""
    print("\n" + "=" * 60)
    print("🌍 Language Detection Benchmark")
    print("=" * 60)
    
    correct = 0
    total = 0
    
    for test in VIETNAMESE_TEST_CASES:
        result = engine.analyze(test["text"])
        if result.language == "vi":
            correct += 1
        else:
            print(f"❌ Misdetected Vietnamese: {test['text'][:50]}...")
        total += 1
    
    for test in ENGLISH_TEST_CASES:
        result = engine.analyze(test["text"])
        if result.language == "en":
            correct += 1
        else:
            print(f"❌ Misdetected English: {test['text'][:50]}...")
        total += 1
    
    accuracy = correct / total
    print(f"\n✅ Language Detection Accuracy: {accuracy:.2%} ({correct}/{total})")


def benchmark_emotion_detection(engine: NLPEngine):
    """Test emotion detection accuracy"""
    print("\n" + "=" * 60)
    print("😊 Emotion Detection Benchmark")
    print("=" * 60)
    
    all_tests = VIETNAMESE_TEST_CASES + ENGLISH_TEST_CASES
    
    total_expected = 0
    total_detected = 0
    correct_detections = 0
    
    for test in all_tests:
        result = engine.analyze(test["text"])
        detected_types = [e.type for e in result.emotions]
        
        expected = set(test["expected_emotions"])
        detected = set(detected_types)
        
        # Calculate precision/recall per test
        true_positives = len(expected & detected)
        
        total_expected += len(expected)
        total_detected += len(detected)
        correct_detections += true_positives
        
        # Print results
        print(f"\n📝 {test['description']}")
        print(f"   Text: {test['text'][:60]}...")
        print(f"   Expected: {expected}")
        print(f"   Detected: {detected}")
        
        if expected == detected:
            print(f"   ✅ Perfect match!")
        elif true_positives > 0:
            print(f"   ⚠️ Partial match ({true_positives}/{len(expected)})")
        else:
            print(f"   ❌ No match")
    
    precision = correct_detections / total_detected if total_detected > 0 else 0
    recall = correct_detections / total_expected if total_expected > 0 else 0
    f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
    
    print(f"\n📊 Overall Emotion Detection:")
    print(f"   Precision: {precision:.2%}")
    print(f"   Recall: {recall:.2%}")
    print(f"   F1 Score: {f1:.2%}")


def benchmark_negation_handling(engine: NLPEngine):
    """Test negation handling"""
    print("\n" + "=" * 60)
    print("🚫 Negation Handling Benchmark")
    print("=" * 60)
    
    negation_tests = [
        {
            "text": "Không FOMO nữa, kiên nhẫn chờ signal",
            "should_not_detect": ["FOMO"],
            "should_detect": ["DISCIPLINE"]
        },
        {
            "text": "Không all in, quản lý vốn cẩn thận",
            "should_not_detect": ["GREED"],
            "should_detect": ["DISCIPLINE"]
        },
        {
            "text": "No fear of missing out, waiting patiently",
            "should_not_detect": ["FOMO"],
            "should_detect": ["DISCIPLINE"]
        },
        {
            "text": "Don't panic sell, stick to the plan",
            "should_not_detect": ["FEAR"],
            "should_detect": ["DISCIPLINE"]
        }
    ]
    
    correct = 0
    total = 0
    
    for test in negation_tests:
        result = engine.analyze(test["text"])
        detected_types = [e.type for e in result.emotions]
        
        # Check if negated emotions are NOT detected
        negated_correct = all(
            emotion not in detected_types
            for emotion in test["should_not_detect"]
        )
        
        # Check if positive emotions ARE detected
        positive_correct = any(
            emotion in detected_types
            for emotion in test["should_detect"]
        )
        
        test_passed = negated_correct and positive_correct
        
        print(f"\n📝 {test['text'][:60]}...")
        print(f"   Should NOT detect: {test['should_not_detect']}")
        print(f"   Should detect: {test['should_detect']}")
        print(f"   Detected: {detected_types}")
        print(f"   {'✅ PASS' if test_passed else '❌ FAIL'}")
        
        if test_passed:
            correct += 1
        total += 1
    
    accuracy = correct / total
    print(f"\n✅ Negation Handling Accuracy: {accuracy:.2%} ({correct}/{total})")


def benchmark_performance(engine: NLPEngine):
    """Benchmark inference speed"""
    print("\n" + "=" * 60)
    print("⚡ Performance Benchmark")
    print("=" * 60)
    
    test_texts = [test["text"] for test in VIETNAMESE_TEST_CASES + ENGLISH_TEST_CASES]
    
    # Warm up
    for text in test_texts[:2]:
        engine.analyze(text)
    
    # Benchmark
    start_time = time.time()
    for text in test_texts:
        engine.analyze(text)
    end_time = time.time()
    
    total_time = end_time - start_time
    avg_time = total_time / len(test_texts) * 1000  # Convert to ms
    
    print(f"\n✅ Inference Performance:")
    print(f"   Total samples: {len(test_texts)}")
    print(f"   Total time: {total_time:.3f}s")
    print(f"   Average time: {avg_time:.1f}ms per sample")
    print(f"   Target: <500ms {'✅ PASS' if avg_time < 500 else '❌ FAIL'}")


def run_all_benchmarks():
    """Run all benchmarks"""
    print("\n" + "=" * 60)
    print("🧪 NLP Engine Comprehensive Benchmark")
    print("=" * 60)
    
    # Initialize engine
    print("\n🔧 Initializing NLP Engine...")
    engine = NLPEngine(use_gpu=False, enable_ml_classifier=False, enable_logging=False)
    print("✅ Engine initialized (keyword-based mode)")
    
    # Run benchmarks
    benchmark_language_detection(engine)
    benchmark_emotion_detection(engine)
    benchmark_negation_handling(engine)
    benchmark_performance(engine)
    
    print("\n" + "=" * 60)
    print("✅ All benchmarks complete!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_benchmarks()
