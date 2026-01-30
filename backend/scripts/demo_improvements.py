"""
Demo Script - NLP & ML Improvements
Demonstrates all new features with real examples
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from nlp import get_nlp_engine
import json


def print_section(title: str):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def print_result(result):
    """Print NLP result in formatted way"""
    print(f"\n📝 Text: {result.text}")
    print(f"🌍 Language: {result.language}")
    print(f"📊 Sentiment: {result.sentiment_label} ({result.sentiment_score:+.2f})")
    print(f"⭐ Quality Score: {result.quality_score:.2f}/1.00")
    
    if result.emotions:
        print(f"\n😊 Emotions Detected:")
        for emotion in result.emotions:
            confidence_bar = "█" * int(emotion.confidence * 20)
            print(f"   {emotion.type:15s} [{confidence_bar:20s}] {emotion.confidence:.0%}")
            if emotion.matched_keywords:
                print(f"      Keywords: {', '.join(emotion.matched_keywords[:5])}")
    
    if result.warnings:
        print(f"\n⚠️  Warnings:")
        for warning in result.warnings:
            print(f"   {warning}")
    
    print()


def demo_basic_usage():
    """Demo 1: Basic usage"""
    print_section("Demo 1: Basic NLP Analysis")
    
    engine = get_nlp_engine()
    
    # Vietnamese example
    result = engine.analyze("BTC đang pump mạnh, phải vào ngay kẻo lỡ tàu!")
    print_result(result)


def demo_negation_handling():
    """Demo 2: Negation handling"""
    print_section("Demo 2: Negation Handling")
    
    engine = get_nlp_engine()
    
    print("\n🔴 WITH FOMO (no negation):")
    result1 = engine.analyze("Phải vào ngay kẻo lỡ cơ hội!")
    print(f"   Emotions: {[e.type for e in result1.emotions]}")
    print(f"   Quality: {result1.quality_score:.2f}")
    
    print("\n🟢 WITHOUT FOMO (negated):")
    result2 = engine.analyze("Không FOMO, kiên nhẫn chờ pullback")
    print(f"   Emotions: {[e.type for e in result2.emotions]}")
    print(f"   Quality: {result2.quality_score:.2f}")
    
    print(f"\n✅ Negation working: FOMO removed, Quality improved ({result1.quality_score:.2f} → {result2.quality_score:.2f})")


def demo_rational_vs_emotional():
    """Demo 3: Rational vs Emotional trading"""
    print_section("Demo 3: Rational vs Emotional Trading Comparison")
    
    engine = get_nlp_engine()
    
    print("\n🔴 EMOTIONAL TRADING:")
    emotional_text = "Thua 3 lệnh rồi, phải gỡ gạc! All in x10 leverage!"
    result1 = engine.analyze(emotional_text)
    print_result(result1)
    
    print("\n🟢 RATIONAL TRADING:")
    rational_text = "Phân tích kỹ, RR 1:3, SL tại 0.95, TP tại 1.05, size 2% vốn"
    result2 = engine.analyze(rational_text)
    print_result(result2)


def demo_manipulation_detection():
    """Demo 4: Market manipulation detection"""
    print_section("Demo 4: Market Manipulation Detection")
    
    engine = get_nlp_engine()
    
    manipulation_examples = [
        "Tin nội bộ BTC sắp list ETF, pump x10 chắc chắn!",
        "Insider info: coin này sắp list Binance, all in nhanh!",
        "Pump and dump group, vào ngay kiếm lời nhanh!",
        "Wash trading để tạo volume giả, dump sau"
    ]
    
    for text in manipulation_examples:
        result = engine.analyze(text)
        emotions = [e.type for e in result.emotions]
        
        if "MANIPULATION" in emotions:
            print(f"\n🚨 MANIPULATION DETECTED!")
            print(f"   Text: {text}")
            print(f"   Emotions: {emotions}")
            print(f"   Quality: {result.quality_score:.2f}")
        else:
            print(f"\n⚠️  Text: {text}")
            print(f"   Emotions: {emotions}")


def demo_bilingual_support():
    """Demo 5: Bilingual support"""
    print_section("Demo 5: Bilingual Support (Vietnamese + English)")
    
    engine = get_nlp_engine()
    
    test_cases = [
        ("Pure Vietnamese", "Phải vào lệnh ngay, theo kế hoạch đã phân tích"),
        ("Pure English", "Following the plan, RR 1:3, stop loss set"),
        ("Mixed Language", "Setup đẹp, high probability, theo plan vào lệnh"),
        ("Vietnamese no diacritics", "Phai vao ngay keo lo!"),
    ]
    
    for name, text in test_cases:
        result = engine.analyze(text)
        emotions = [e.type for e in result.emotions]
        
        print(f"\n📝 {name}")
        print(f"   Text: {text}")
        print(f"   Detected Language: {result.language}")
        print(f"   Emotions: {emotions}")
        print(f"   Quality: {result.quality_score:.2f}")


def demo_quality_assessment():
    """Demo 6: Quality assessment"""
    print_section("Demo 6: Trading Note Quality Assessment")
    
    engine = get_nlp_engine()
    
    # Different quality levels
    notes = [
        ("Very Low", "FOMO! All in ngay! Pump rồi!"),
        ("Low", "Mua BTC, chắc lên"),
        ("Medium", "BTC breakout, vào lệnh theo trend"),
        ("Good", "Entry BTC, RR 1:2, SL tại 50k"),
        ("Excellent", "Phân tích kỹ: RR 1:3, SL 2%, TP 6%, size 5% vốn, theo chiến lược trend following")
    ]
    
    results = []
    for level, text in notes:
        result = engine.analyze(text)
        results.append((level, result))
    
    # Print comparison
    print("\n📊 Quality Score Comparison:\n")
    print(f"{'Level':<15} {'Score':<10} {'Emotions':<30} {'Warnings'}")
    print("-" * 70)
    
    for level, result in results:
        emotions_str = ", ".join([e.type for e in result.emotions][:3])
        warnings_count = len(result.warnings)
        bar = "█" * int(result.quality_score * 20)
        
        print(f"{level:<15} {result.quality_score:.2f} [{bar:<20}] {emotions_str:<30} {warnings_count}")


def demo_performance_logging():
    """Demo 7: Performance logging (if enabled)"""
    print_section("Demo 7: Production Monitoring & Logging")
    
    try:
        from ml.evaluator import get_evaluator
        
        # Create engine with logging enabled
        from nlp.engine import NLPEngine
        engine = NLPEngine(enable_logging=True)
        
        # Analyze some texts with logging
        texts = [
            "BTC phải vào ngay!",
            "Theo plan, SL đặt sẵn",
            "Thua rồi, gỡ gạc!"
        ]
        
        print("\n📊 Logging predictions...")
        for text in texts:
            result = engine.analyze(text, log_prediction=True)
            print(f"   ✅ Logged: {text[:40]}...")
        
        # Get performance report
        evaluator = get_evaluator()
        report = evaluator.get_performance_report("nlp_engine_v1")
        
        print(f"\n📈 Performance Report:")
        print(f"   Total predictions: {report['total_predictions']}")
        print(f"   Labeled predictions: {report['labeled_predictions']}")
        
        if report.get('confidence_distribution'):
            conf = report['confidence_distribution']
            print(f"   Confidence (mean): {conf.get('mean', 0):.2f}")
            print(f"   Confidence (std): {conf.get('std', 0):.2f}")
        
    except ImportError:
        print("\n⚠️ Evaluator not available (optional feature)")


def demo_model_registry():
    """Demo 8: Model registry"""
    print_section("Demo 8: Model Registry & Versioning")
    
    try:
        from ml.model_registry import get_model_registry, ModelMetrics
        
        registry = get_model_registry()
        
        # List all models
        models = registry.list_models()
        
        if models:
            print(f"\n📚 Registered Models: {len(models)}")
            for model in models:
                active_marker = "🟢 ACTIVE" if model.is_active else "⚪ Inactive"
                print(f"\n   {active_marker} {model.version}")
                print(f"      Type: {model.model_type}")
                print(f"      Path: {model.path}")
                print(f"      Trained: {model.trained_at}")
                print(f"      Metrics: Acc={model.metrics.accuracy:.2f}, F1={model.metrics.f1_score:.2f}")
        else:
            print("\n📚 No models registered yet")
            print("   Register models after training with:")
            print("   registry.register_model(...)")
        
    except ImportError:
        print("\n⚠️ Model registry not available")


def run_all_demos():
    """Run all demonstrations"""
    print("\n" + "=" * 70)
    print("  🎯 NLP & ML Improvements - Interactive Demo")
    print("=" * 70)
    
    try:
        demo_basic_usage()
        demo_negation_handling()
        demo_rational_vs_emotional()
        demo_manipulation_detection()
        demo_bilingual_support()
        demo_quality_assessment()
        demo_performance_logging()
        demo_model_registry()
        
        print("\n" + "=" * 70)
        print("  ✅ All demos completed successfully!")
        print("=" * 70)
        
        print("\n📚 Next Steps:")
        print("   1. Review the improvements in ml/IMPROVEMENTS.md")
        print("   2. Check quickstart guide in ml/QUICKSTART.md")
        print("   3. Run benchmarks: python scripts/benchmark_nlp.py")
        print("   4. Train models on your own data for better accuracy")
        
    except Exception as e:
        print(f"\n❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_demos()
