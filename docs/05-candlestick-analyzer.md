# 5. Candlestick Analyzer - Phân Tích Mô Hình Nến

## 📋 Mô Tả Nghiệp Vụ

### Vấn đề cần giải quyết
Trader cần biết **bối cảnh kỹ thuật** tại thời điểm giao dịch:
- Có mô hình nến nào đang hình thành?
- Trade có align với tín hiệu nến không?

### Các mô hình nến nhận diện

| Pattern | Tín hiệu |
|---------|----------|
| Doji | ⚠️ Neutral |
| Hammer | 🟢 Bullish |
| Shooting Star | 🔴 Bearish |
| Engulfing | 🔄 Reversal |
| Morning/Evening Star | 🔄 Reversal |
| Three White Soldiers | 🟢 Bullish |
| Three Black Crows | 🔴 Bearish |

---

## 🔧 Xử Lý Kỹ Thuật

### Tech Stack
- **TA-Lib**: Pattern recognition
- **ccxt/yfinance**: OHLCV data
- **Redis**: Cache

### Implementation
```python
import talib
import numpy as np

class CandlestickAnalyzer:
    PATTERNS = {
        "DOJI": talib.CDLDOJI,
        "HAMMER": talib.CDLHAMMER,
        "ENGULFING": talib.CDLENGULFING,
        "MORNING_STAR": talib.CDLMORNINGSTAR,
        "EVENING_STAR": talib.CDLEVENINGSTAR,
    }
    
    def analyze(self, ohlcv) -> List[PatternDetection]:
        o, h, l, c = [np.array([x[i] for x in ohlcv]) for i in range(4)]
        patterns = []
        for name, func in self.PATTERNS.items():
            result = func(o, h, l, c)
            if result[-1] != 0:
                patterns.append(PatternDetection(
                    name=name,
                    signal="BULLISH" if result[-1] > 0 else "BEARISH"
                ))
        return patterns
    
    def check_alignment(self, trade_side: str, patterns) -> bool:
        """Check if trade aligns with dominant pattern signal"""
        dominant = self._get_dominant(patterns)
        return (trade_side == "BUY") == (dominant == "BULLISH")
```

### API Endpoints
```
GET  /api/candles/analyze/{symbol}
POST /api/candles/alignment
GET  /api/candles/stats/{user_id}
```
