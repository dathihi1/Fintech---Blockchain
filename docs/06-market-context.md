# 6. Market Context Enricher - Làm Giàu Bối Cảnh Thị Trường

## 📋 Mô Tả Nghiệp Vụ

### Vấn đề cần giải quyết
Mỗi giao dịch cần được gắn với **bối cảnh thị trường** lúc đó:
- Giá đã tăng/giảm bao nhiêu % trong 1h, 4h, 24h trước?
- RSI, MACD đang ở vùng nào?
- Volume có bất thường không?
- Market dominance (BTC.D) như thế nào?

### Các metrics cần enrich

| Metric | Mô tả | Ý nghĩa |
|--------|-------|---------|
| Price Change % | 1h, 4h, 24h | Entry sau pump hay dip |
| RSI | Relative Strength Index | Overbought/Oversold |
| MACD | Trend momentum | Trend direction |
| Volume Ratio | So với avg 20 periods | Có volume surge không |
| Volatility | ATR-based | Thị trường calm hay volatile |
| BTC Dominance | BTC.D tại thời điểm | Altcoin season hay không |

---

## 🔧 Xử Lý Kỹ Thuật

### Tech Stack
- **ccxt**: Exchange data (Binance, Bybit)
- **yfinance**: Traditional markets
- **pandas-ta**: Technical indicators
- **Redis**: OHLCV cache

### Implementation
```python
import ccxt
import pandas_ta as ta

class MarketContextEnricher:
    def __init__(self):
        self.exchange = ccxt.binance()
        
    async def enrich(self, symbol: str, timestamp: datetime) -> MarketContext:
        ohlcv = await self._fetch_ohlcv(symbol, timestamp)
        df = pd.DataFrame(ohlcv, columns=['ts','o','h','l','c','v'])
        
        # Calculate indicators
        df['rsi'] = ta.rsi(df['c'], length=14)
        macd = ta.macd(df['c'])
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        df['atr'] = ta.atr(df['h'], df['l'], df['c'])
        
        last = df.iloc[-1]
        return MarketContext(
            price_change_1h=self._calc_change(df, 1),
            price_change_24h=self._calc_change(df, 24),
            rsi=last['rsi'],
            macd=last['macd'],
            volume_ratio=last['v'] / df['v'].rolling(20).mean().iloc[-1],
            volatility=last['atr'] / last['c'] * 100
        )
```

### Output Schema
```python
@dataclass
class MarketContext:
    price_change_1h: float
    price_change_4h: float
    price_change_24h: float
    rsi: float
    macd: float
    macd_signal: float
    volume_ratio: float
    volatility: float  # ATR %
    trend: str  # "UPTREND", "DOWNTREND", "SIDEWAYS"
```

### API Endpoints
```
GET /api/market/{symbol}/context
GET /api/market/{symbol}/indicators
```
