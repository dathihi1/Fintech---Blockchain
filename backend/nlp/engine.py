"""
NLP Engine for Trading Journal
Phân tích sentiment và emotions từ ghi chú giao dịch
"""

from typing import List, Dict, Optional
from dataclasses import dataclass, field, asdict
import re
import os
import torch

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    HAS_TRANSFORMERS = True
except ImportError:
    HAS_TRANSFORMERS = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_VADER = True
except ImportError:
    HAS_VADER = False

try:
    from langdetect import detect, LangDetectException
    HAS_LANGDETECT = True
except ImportError:
    HAS_LANGDETECT = False

from .vietnamese_keywords import VIETNAMESE_TRADING_KEYWORDS, ENGLISH_TRADING_KEYWORDS, NEGATION_WORDS

# Import emotion classifier and evaluator (optional)
try:
    from ml.emotion_classifier import get_emotion_predictor
    HAS_EMOTION_CLASSIFIER = True
except ImportError:
    HAS_EMOTION_CLASSIFIER = False

try:
    from ml.evaluator import get_evaluator
    HAS_EVALUATOR = True
except ImportError:
    HAS_EVALUATOR = False


@dataclass
class Emotion:
    """Detected emotion from text"""
    type: str  # "FOMO", "FEAR", "GREED", "REVENGE", "RATIONAL", "CONFIDENT"
    confidence: float  # 0 to 1
    matched_keywords: List[str] = field(default_factory=list)
    weight: float = 0.0
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NLPResult:
    """Result of NLP analysis"""
    text: str
    language: str  # "vi" or "en"
    sentiment_score: float  # -1 to 1
    sentiment_label: str  # "positive", "negative", "neutral"
    emotions: List[Emotion] = field(default_factory=list)
    behavioral_flags: List[str] = field(default_factory=list)
    quality_score: float = 0.5  # 0 to 1
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        result = asdict(self)
        result["emotions"] = [e.to_dict() if isinstance(e, Emotion) else e for e in self.emotions]
        return result


class NLPEngine:
    """
    NLP Engine for analyzing trading notes.
    Supports Vietnamese and English with FinBERT + PhoBERT + VADER + keyword matching.
    Features:
    - Lazy loading of models
    - Word boundary matching for keywords
    - Negation handling
    - Improved language detection
    - Fine-tuned model support
    """
    
    def __init__(self, use_gpu: bool = False, enable_ml_classifier: bool = True, enable_logging: bool = True):
        self.use_gpu = use_gpu
        self.device = 0 if use_gpu and torch.cuda.is_available() else -1
        self.enable_ml_classifier = enable_ml_classifier
        self.enable_logging = enable_logging
        
        # Lazy-loaded models (None until first use)
        self._finbert = None
        self._phobert_model = None
        self._phobert_tokenizer = None
        self._vader = None
        self._emotion_predictor = None
        self._evaluator = None
        
        # Load keyword dictionaries
        self.vn_keywords = VIETNAMESE_TRADING_KEYWORDS
        self.en_keywords = ENGLISH_TRADING_KEYWORDS
        self.negation_words = NEGATION_WORDS
    
    @property
    def emotion_predictor(self):
        """Lazy load emotion predictor"""
        if self._emotion_predictor is None and HAS_EMOTION_CLASSIFIER and self.enable_ml_classifier:
            try:
                self._emotion_predictor = get_emotion_predictor(use_gpu=self.use_gpu)
            except Exception as e:
                print(f"Warning: Could not load emotion predictor: {e}")
        return self._emotion_predictor
    
    @property
    def evaluator(self):
        """Lazy load performance evaluator"""
        if self._evaluator is None and HAS_EVALUATOR and self.enable_logging:
            try:
                self._evaluator = get_evaluator()
            except Exception as e:
                print(f"Warning: Could not load evaluator: {e}")
        return self._evaluator
    
    @property
    def finbert(self):
        """Lazy load FinBERT model"""
        if self._finbert is None and HAS_TRANSFORMERS:
            try:
                # Try to load fine-tuned model first
                model_path = "ml/models/finbert_trading_vi"
                if os.path.exists(model_path):
                    print(f"Loading fine-tuned FinBERT from {model_path}")
                    self._finbert = pipeline(
                        "sentiment-analysis",
                        model=model_path,
                        device=self.device,
                        return_all_scores=True
                    )
                else:
                    # Fallback to base model
                    print("Loading base FinBERT model")
                    self._finbert = pipeline(
                        "sentiment-analysis",
                        model="ProsusAI/finbert",
                        device=self.device,
                        return_all_scores=True
                    )
            except Exception as e:
                print(f"Warning: Could not load FinBERT: {e}")
        return self._finbert
    
    @property
    def phobert(self):
        """Lazy load PhoBERT model for Vietnamese"""
        if self._phobert_model is None and HAS_TRANSFORMERS:
            try:
                model_path = "ml/models/phobert_trading_vi"
                if os.path.exists(model_path):
                    print(f"Loading fine-tuned PhoBERT from {model_path}")
                    self._phobert_tokenizer = AutoTokenizer.from_pretrained(model_path)
                    self._phobert_model = AutoModelForSequenceClassification.from_pretrained(model_path)
                    if self.device >= 0:
                        self._phobert_model = self._phobert_model.to("cuda")
            except Exception as e:
                print(f"Warning: Could not load PhoBERT: {e}")
        return self._phobert_model, self._phobert_tokenizer
    
    @property
    def vader(self):
        """Lazy load VADER analyzer"""
        if self._vader is None and HAS_VADER:
            self._vader = SentimentIntensityAnalyzer()
        return self._vader
    
    def analyze(self, text: str, log_prediction: bool = False) -> NLPResult:
        """
        Analyze trading note text.
        
        Args:
            text: The trading note to analyze
            log_prediction: Whether to log this prediction for performance monitoring
            
        Returns:
            NLPResult with sentiment, emotions, and quality score
        """
        if not text or not text.strip():
            return self._empty_result()
        
        text = text.strip()
        
        # Detect language
        language = self._detect_language(text)
        
        # Get sentiment score
        if language == "vi":
            sentiment = self._analyze_vietnamese(text)
        else:
            sentiment = self._analyze_english(text)
        
        # Detect emotions - try ML classifier first, fallback to keywords
        emotions = self._detect_emotions_hybrid(text, language)
        
        # Extract behavioral flags
        behavioral_flags = [e.type for e in emotions if e.weight < 0]
        
        # Assess quality of reasoning
        quality_score = self._assess_quality(text, emotions)
        
        # Generate warnings
        warnings = self._generate_warnings(emotions)
        
        result = NLPResult(
            text=text,
            language=language,
            sentiment_score=sentiment["score"],
            sentiment_label=sentiment["label"],
            emotions=emotions,
            behavioral_flags=behavioral_flags,
            quality_score=quality_score,
            warnings=warnings
        )
        
        # Log prediction for performance monitoring
        if log_prediction and self.evaluator:
            try:
                self.evaluator.log_prediction(
                    model_id="nlp_engine_v1",
                    input_text=text,
                    prediction=sentiment["label"],
                    confidence=abs(sentiment["score"])
                )
            except Exception as e:
                print(f"Warning: Could not log prediction: {e}")
        
        return result
    
    def _detect_emotions_hybrid(self, text: str, language: str) -> List[Emotion]:
        """
        Hybrid emotion detection: ML classifier + keyword matching.
        ML classifier provides calibrated confidence, keywords provide explainability.
        """
        emotions_dict = {}  # type -> Emotion
        
        # Try ML-based emotion prediction first
        if self.emotion_predictor:
            try:
                ml_emotions = self.emotion_predictor.predict(text, threshold=0.3)
                for emotion_type, confidence in ml_emotions:
                    emotions_dict[emotion_type] = Emotion(
                        type=emotion_type,
                        confidence=confidence,
                        matched_keywords=["ML prediction"],
                        weight=self._get_emotion_weight(emotion_type)
                    )
            except Exception as e:
                print(f"ML emotion prediction failed: {e}")
        
        # Keyword-based detection (for explainability and fallback)
        keyword_emotions = self._detect_emotions(text, language)
        
        # Merge: Use ML confidence if available, otherwise use keyword confidence
        for kw_emotion in keyword_emotions:
            if kw_emotion.type in emotions_dict:
                # Update keywords but keep ML confidence
                emotions_dict[kw_emotion.type].matched_keywords = kw_emotion.matched_keywords
            else:
                # Use keyword-based emotion
                emotions_dict[kw_emotion.type] = kw_emotion
        
        return list(emotions_dict.values())
    
    def _get_emotion_weight(self, emotion_type: str) -> float:
        """Get weight for an emotion type"""
        weight_map = {
            "FOMO": -0.8,
            "FEAR": -0.6,
            "GREED": -0.5,
            "REVENGE": -0.9,
            "OVERCONFIDENCE": -0.4,
            "MANIPULATION": -0.95,
            "RATIONAL": 0.7,
            "CONFIDENT": 0.5,
            "DISCIPLINE": 0.6
        }
        return weight_map.get(emotion_type, 0.0)
    
    def _detect_language(self, text: str) -> str:
        """
        Detect if text is Vietnamese or English using langdetect.
        Fallback to heuristic-based detection if langdetect is not available.
        """
        # Try langdetect first (more accurate)
        if HAS_LANGDETECT:
            try:
                lang = detect(text)
                # Map to vi/en
                if lang == "vi":
                    return "vi"
                else:
                    return "en"  # Default to English for other languages
            except LangDetectException:
                pass  # Fall through to heuristic method
        
        # Fallback: Heuristic-based detection
        # Create Vietnamese charset (avoid modifying set during iteration)
        vn_lower = "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
        vn_upper = vn_lower.upper()
        vietnamese_chars = set(vn_lower + vn_upper)
        
        vn_char_count = sum(1 for c in text if c in vietnamese_chars)
        
        # If more than 3% of characters are Vietnamese diacritics (reduced threshold)
        if vn_char_count > len(text) * 0.03:
            return "vi"
        
        # Check for common Vietnamese words
        vn_words = ["và", "là", "của", "có", "được", "trong", "cho", "với", "không", "này", 
                    "thì", "đã", "sẽ", "phải", "như", "nếu", "khi", "để", "còn", "đang"]
        text_lower = text.lower()
        vn_word_matches = sum(1 for word in vn_words if f" {word} " in f" {text_lower} ")
        
        if vn_word_matches >= 2:  # At least 2 Vietnamese words
            return "vi"
        
        return "en"
    
    def _analyze_vietnamese(self, text: str) -> Dict:
        """
        Analyze Vietnamese text sentiment.
        Uses PhoBERT fine-tuned model if available, otherwise falls back to keyword-based.
        """
        # Try PhoBERT model first
        model, tokenizer = self.phobert
        if model is not None and tokenizer is not None:
            try:
                inputs = tokenizer(text[:256], return_tensors="pt", truncation=True, padding=True)
                if self.device >= 0:
                    inputs = {k: v.to("cuda") for k, v in inputs.items()}
                
                with torch.no_grad():
                    outputs = model(**inputs)
                    probs = torch.softmax(outputs.logits, dim=-1)
                    pred_label = torch.argmax(probs, dim=-1).item()
                    confidence = probs[0][pred_label].item()
                
                # Map label to sentiment
                label_map = {0: "negative", 1: "neutral", 2: "positive"}
                score_map = {0: -confidence, 1: 0, 2: confidence}
                
                return {
                    "score": score_map.get(pred_label, 0),
                    "label": label_map.get(pred_label, "neutral")
                }
            except Exception as e:
                print(f"PhoBERT inference failed: {e}")
        
        # Fallback to keyword-based approach
        score = 0.0
        text_lower = text.lower()
        
        # Score based on Vietnamese keywords
        for category, data in self.vn_keywords.items():
            matched = self._match_keywords_with_boundary(text_lower, data["keywords"])
            if matched:
                # Adjust score based on number of matches
                score += data["weight"] * min(len(matched) * 0.3, 1.0)
        
        # Normalize score to -1 to 1
        score = max(-1, min(1, score))
        
        # Determine label
        if score > 0.2:
            label = "positive"
        elif score < -0.2:
            label = "negative"
        else:
            label = "neutral"
        
        return {"score": score, "label": label}
    
    def _analyze_english(self, text: str) -> Dict:
        """Analyze English text sentiment using FinBERT or VADER"""
        # Try FinBERT first
        if self.finbert:
            try:
                results = self.finbert(text[:512])[0]  # Limit to 512 chars for BERT
                label_to_score = {"positive": 1, "negative": -1, "neutral": 0}
                best = max(results, key=lambda x: x["score"])
                return {
                    "score": label_to_score.get(best["label"], 0) * best["score"],
                    "label": best["label"]
                }
            except Exception:
                pass
        
        # Fallback to VADER
        if self.vader:
            scores = self.vader.polarity_scores(text)
            compound = scores["compound"]
            if compound > 0.05:
                label = "positive"
    def _analyze_english(self, text: str) -> Dict:
        """Analyze English text sentiment using FinBERT or VADER"""
        # Try FinBERT first
        if self.finbert:
            try:
                results = self.finbert(text[:512])[0]  # Limit to 512 chars for BERT
                label_to_score = {"positive": 1, "negative": -1, "neutral": 0}
                best = max(results, key=lambda x: x["score"])
                return {
                    "score": label_to_score.get(best["label"], 0) * best["score"],
                    "label": best["label"]
                }
            except Exception as e:
                print(f"FinBERT inference failed: {e}")
        
        # Fallback to VADER
        if self.vader:
            scores = self.vader.polarity_scores(text)
            compound = scores["compound"]
            if compound > 0.05:
                label = "positive"
            elif compound < -0.05:
                label = "negative"
            else:
                label = "neutral"
            return {"score": compound, "label": label}
        
        # No analyzer available
        return {"score": 0.0, "label": "neutral"}
    
    def _match_keywords_with_boundary(self, text: str, keywords: List[str]) -> List[str]:
        """
        Match keywords with word boundary support to avoid false positives.
        
        Args:
            text: Lowercase text to search in
            keywords: List of keywords to match
            
        Returns:
            List of matched keywords
        """
        matched = []
        
        for kw in keywords:
            kw_words = kw.split()
            
            # Single word - use word boundary
            if len(kw_words) == 1:
                # Use word boundary regex
                pattern = rf'\b{re.escape(kw)}\b'
                if re.search(pattern, text):
                    matched.append(kw)
            else:
                # Multi-word phrase - simple substring match
                if kw in text:
                    matched.append(kw)
        
        return matched
    
    def _check_negation(self, text: str, keyword: str, language: str) -> bool:
        """
        Check if a keyword is negated by nearby negation words.
        
        Args:
            text: The full text (lowercase)
            keyword: The keyword to check
            language: "vi" or "en"
            
        Returns:
            True if keyword is negated, False otherwise
        """
        negation_list = self.negation_words.get(language, [])
        
        # Build pattern: negation word followed by 0-4 words, then keyword or its variations
        # More flexible to catch "no fear of missing out", "không all in"
        negation_pattern = '|'.join([re.escape(neg) for neg in negation_list])
        
        # Escape keyword for regex
        kw_escaped = re.escape(keyword)
        
        # Pattern: negation + up to 4 words + keyword
        pattern = rf'({negation_pattern})\s+(?:\w+\s+){{0,4}}{kw_escaped}'
        
        if re.search(pattern, text, re.IGNORECASE):
            return True
        
        # Also check for keyword + negation (less common)
        # E.g., "FOMO không còn nữa"
        reverse_pattern = rf'{kw_escaped}\s+(?:\w+\s+){{0,2}}({negation_pattern})'
        if re.search(reverse_pattern, text, re.IGNORECASE):
            return True
        
        return False
    
    def _detect_emotions(self, text: str, language: str) -> List[Emotion]:
        """
        Detect emotions from text based on keywords with negation handling.
        """
        emotions = []
        text_lower = text.lower()
        
        # Choose keyword dictionary based on language
        keywords_dict = self.vn_keywords if language == "vi" else self.en_keywords
        
        # Also check the other language keywords (many traders mix languages)
        other_dict = self.en_keywords if language == "vi" else self.vn_keywords
        other_lang = "en" if language == "vi" else "vi"
        
        # Primary language detection
        for category, data in keywords_dict.items():
            matched = self._match_keywords_with_boundary(text_lower, data["keywords"])
            
            # Filter out negated keywords
            matched = [kw for kw in matched if not self._check_negation(text_lower, kw, language)]
            
            if matched:
                # Calculate confidence based on keyword count and strength
                base_confidence = min(len(matched) * 0.3, 1.0)
                # Boost confidence for critical emotions
                if data["emotion"] in ["FOMO", "REVENGE", "MANIPULATION"]:
                    confidence = min(base_confidence * 1.2, 1.0)
                else:
                    confidence = base_confidence
                    
                emotions.append(Emotion(
                    type=data["emotion"],
                    confidence=confidence,
                    matched_keywords=matched,
                    weight=data["weight"]
                ))
        
        # Secondary language detection (mixed language text)
        for category, data in other_dict.items():
            # Skip if we already detected this emotion
            if any(e.type == data["emotion"] for e in emotions):
                continue
            
            matched = self._match_keywords_with_boundary(text_lower, data["keywords"])
            
            # Filter out negated keywords
            matched = [kw for kw in matched if not self._check_negation(text_lower, kw, other_lang)]
            
            if matched:
                confidence = min(len(matched) * 0.2, 0.9)  # Slightly lower confidence for secondary language
                emotions.append(Emotion(
                    type=data["emotion"],
                    confidence=confidence,
                    matched_keywords=matched,
                    weight=data["weight"]
                ))
        
        return emotions
    
    def _assess_quality(self, text: str, emotions: List[Emotion]) -> float:
        """
        Assess the quality of trading reasoning.
        
        High quality = evidence of planning, risk management
        Low quality = emotional, impulsive language
        """
        score = 0.5  # Baseline
        text_lower = text.lower()
        
        # Positive indicators (evidence of planning)
        positive_keywords = [
            "stop loss", "sl", "take profit", "tp",
            "rr", "risk reward", "quản lý vốn", "risk management",
            "kế hoạch", "plan", "chiến lược", "strategy",
            "phân tích", "analysis", "backtest",
            "entry point", "điểm vào", "target"
        ]
        
        for kw in positive_keywords:
            if kw in text_lower:
                score += 0.08
        
        # Negative indicators from emotions
        for emotion in emotions:
            if emotion.type in ["FOMO", "REVENGE", "GREED"]:
                score -= 0.15 * emotion.confidence
            elif emotion.type == "FEAR":
                score -= 0.08 * emotion.confidence
            elif emotion.type == "OVERCONFIDENCE":
                score -= 0.1 * emotion.confidence
            elif emotion.type in ["RATIONAL", "DISCIPLINE", "CONFIDENT"]:
                score += 0.1 * emotion.confidence
        
        # Clamp to 0-1
        return max(0.0, min(1.0, score))
    
    def _generate_warnings(self, emotions: List[Emotion]) -> List[str]:
        """Generate warning messages based on detected emotions"""
        warnings = []
        
        for emotion in emotions:
            if emotion.confidence < 0.3:
                continue
                
            if emotion.type == "FOMO":
                warnings.append("⚠️ CẢNH BÁO FOMO: Hãy kiểm tra lại lý do vào lệnh. Đợi pullback?")
            elif emotion.type == "REVENGE":
                warnings.append("🛑 CẢNH BÁO REVENGE: Nghỉ ngơi ít nhất 30 phút trước khi trade tiếp!")
            elif emotion.type == "GREED":
                warnings.append("⚠️ CẢNH BÁO GREED: Consider giảm position size 50%")
            elif emotion.type == "FEAR":
                warnings.append("📊 Phát hiện FEAR: Stick to your plan, avoid panic selling")
            elif emotion.type == "OVERCONFIDENCE":
                warnings.append("⚠️ CẢNH BÁO: Quá tự tin có thể dẫn đến sai lầm. Double-check analysis.")
            elif emotion.type == "MANIPULATION":
                warnings.append("🚨 CẢNH BÁO MANIPULATION: Có dấu hiệu thao túng thị trường. Kiểm tra nguồn thông tin!")
        
        return warnings
    
    def _empty_result(self) -> NLPResult:
        """Return empty result for empty input"""
        return NLPResult(
            text="",
            language="unknown",
            sentiment_score=0.0,
            sentiment_label="neutral",
            emotions=[],
            behavioral_flags=[],
            quality_score=0.5,
            warnings=[]
        )


# Singleton instance
_nlp_engine: Optional[NLPEngine] = None


def get_nlp_engine(use_gpu: bool = False) -> NLPEngine:
    """Get or create NLP engine singleton"""
    global _nlp_engine
    if _nlp_engine is None:
        _nlp_engine = NLPEngine(use_gpu=use_gpu)
    return _nlp_engine
