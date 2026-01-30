"""
Vietnamese Trading Keywords Dictionary
Từ điển keywords giao dịch tiếng Việt cho phân tích NLP
"""

VIETNAMESE_TRADING_KEYWORDS = {
    # FOMO indicators - Sợ bỏ lỡ cơ hội
    "fomo": {
        "keywords": [
            "sợ lỡ", "phải vào ngay", "mua gấp", "không kịp",
            "đang bay", "pump rồi", "fomo", "all in", "chốt liền",
            "bắt đáy", "đuổi giá", "lỡ tàu", "sợ miss", "không thể bỏ lỡ",
            "phải mua", "vào ngay đi", "mau lên", "nhanh tay"
        ],
        "weight": -0.8,
        "emotion": "FOMO"
    },
    
    # Fear indicators - Sợ hãi
    "fear": {
        "keywords": [
            "sợ", "lo lắng", "hoang mang", "panic", "cắt lỗ ngay",
            "bán tháo", "dump", "sập", "crash", "liquidate",
            "thua hết", "mất sạch", "cháy tài khoản", "margin call",
            "không dám", "run rồi"
        ],
        "weight": -0.6,
        "emotion": "FEAR"
    },
    
    # Greed indicators - Tham lam
    "greed": {
        "keywords": [
            "x10", "x100", "moon", "rich", "giàu", "lời to",
            "all in", "leverage cao", "margin max", "full port",
            "lambo", "triệu phú", "đổi đời", "chắc thắng",
            "không thể thua", "dễ ăn"
        ],
        "weight": -0.5,
        "emotion": "GREED"
    },
    
    # Revenge indicators - Gỡ gạc, trả thù thị trường
    "revenge": {
        "keywords": [
            "gỡ gạc", "gỡ lại", "trả thù", "thua đủ rồi",
            "phải thắng", "không thể thua nữa", "lấy lại",
            "đòi lại", "bù lỗ", "phục hận", "quyết gỡ",
            "tăng size", "đánh lớn hơn"
        ],
        "weight": -0.9,
        "emotion": "REVENGE"
    },
    
    # Overconfidence indicators - Quá tự tin
    "overconfidence": {
        "keywords": [
            "chắc chắn thắng", "không thể sai", "dễ như ăn kẹo",
            "thắng rồi", "đỉnh cao", "bất bại", "siêu trader",
            "không cần stop loss", "all in được", "100% win",
            "ez game", "quá dễ", "chắc kèo", "ăn chắc",
            "thắng chắc", "win rate 100"
        ],
        "weight": -0.4,
        "emotion": "OVERCONFIDENCE"
    },
    
    # Manipulation indicators - Thao túng thị trường
    "manipulation": {
        "keywords": [
            "pump dump", "pnd", "dump trước khi pump", "fake volume",
            "wash trading", "tạo khối lượng ảo", "đẩy giá", "đánh sập",
            "tin nội bộ", "insider", "sắp list", "delist", "rug pull",
            "scam", "lừa đảo", "trap", "bẫy"
        ],
        "weight": -0.95,
        "emotion": "MANIPULATION"
    },
    
    # Rational indicators (positive) - Lý trí, kỷ luật
    "rational": {
        "keywords": [
            "phân tích", "theo kế hoạch", "RR", "stop loss",
            "take profit", "quản lý vốn", "size nhỏ", "test",
            "chờ xác nhận", "pullback", "retest", "risk management",
            "SL", "TP", "entry point", "theo chiến lược"
        ],
        "weight": 0.7,
        "emotion": "RATIONAL"
    },
    
    # Confident indicators (positive) - Tự tin có căn cứ
    "confident": {
        "keywords": [
            "tin tưởng", "setup đẹp", "high probability",
            "theo trend", "xác nhận rồi", "tín hiệu tốt",
            "backtest", "có edge", "tỷ lệ thắng cao"
        ],
        "weight": 0.5,
        "emotion": "CONFIDENT"
    },
    
    # Discipline indicators (positive) - Kỷ luật
    "discipline": {
        "keywords": [
            "theo plan", "kỷ luật", "đúng quy trình", "không tham",
            "cắt lỗ đúng điểm", "chờ signal", "patience", "kiên nhẫn",
            "không FOMO", "theo rules"
        ],
        "weight": 0.6,
        "emotion": "DISCIPLINE"
    }
}

# English keywords for bilingual support
ENGLISH_TRADING_KEYWORDS = {
    "fomo": {
        "keywords": [
            "fomo", "fear of missing out", "must buy now", "hurry", "missing out",
            "can't miss this", "pump", "moon", "going up fast",
            "buy before too late", "get in now", "buy now"
        ],
        "weight": -0.8,
        "emotion": "FOMO"
    },
    
    "fear": {
        "keywords": [
            "scared", "worried", "panic", "dump", "crash",
            "losing everything", "liquidated", "margin call",
            "stop out", "afraid", "fear", "panic sell"
        ],
        "weight": -0.6,
        "emotion": "FEAR"
    },
    
    "greed": {
        "keywords": [
            "x10", "x100", "moon", "lambo", "rich",
            "all in", "max leverage", "full port", "easy money",
            "guaranteed profit", "greed", "greedy"
        ],
        "weight": -0.5,
        "emotion": "GREED"
    },
    
    "revenge": {
        "keywords": [
            "revenge trade", "get it back", "must win",
            "can't lose again", "recover losses", "bigger position",
            "double down", "average down"
        ],
        "weight": -0.9,
        "emotion": "REVENGE"
    },
    
    "rational": {
        "keywords": [
            "analysis", "according to plan", "risk reward",
            "stop loss", "take profit", "position sizing",
            "risk management", "tested strategy", "high probability setup"
        ],
        "weight": 0.7,
        "emotion": "RATIONAL"
    },
    
    "confident": {
        "keywords": [
            "confident", "good setup", "trend following",
            "confirmed signal", "backtested", "edge",
            "high win rate", "proven strategy", "statistical edge"
        ],
        "weight": 0.5,
        "emotion": "CONFIDENT"
    },
    
    "discipline": {
        "keywords": [
            "following plan", "disciplined", "stick to rules",
            "patient", "waiting for signal", "no fomo",
            "proper risk management", "cutting losses"
        ],
        "weight": 0.6,
        "emotion": "DISCIPLINE"
    },
    
    "overconfidence": {
        "keywords": [
            "can't lose", "guaranteed win", "easy money",
            "100% sure", "no way to fail", "already won",
            "no stop needed", "risk free"
        ],
        "weight": -0.4,
        "emotion": "OVERCONFIDENCE"
    },
    
    "manipulation": {
        "keywords": [
            "pump and dump", "pnd", "wash trading", "fake volume",
            "insider info", "listing soon", "rug pull", "exit scam",
            "coordinated pump", "market maker manipulation", "spoofing"
        ],
        "weight": -0.95,
        "emotion": "MANIPULATION"
    }
}

# Negation words for both languages
NEGATION_WORDS = {
    "vi": ["không", "không phải", "chưa", "đừng", "chẳng", "chả"],
    "en": ["no", "not", "don't", "doesn't", "never", "won't", "can't"]
}


def get_all_keywords() -> dict:
    """Get combined keywords for both languages"""
    return {
        "vi": VIETNAMESE_TRADING_KEYWORDS,
        "en": ENGLISH_TRADING_KEYWORDS
    }
