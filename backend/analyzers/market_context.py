"""
Market Context Analyzer - Phân tích bối cảnh thị trường
Sử dụng các indicator kỹ thuật để enrich trade data
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import math


@dataclass
class CandleStick:
    """OHLCV candlestick data"""
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


@dataclass
class MarketIndicators:
    """Technical indicators at a point in time"""
    # Trend
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_12: Optional[float] = None
    ema_26: Optional[float] = None
    
    # Momentum
    rsi_14: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    macd_histogram: Optional[float] = None
    
    # Volatility
    atr_14: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None
    bollinger_width: Optional[float] = None
    
    # Volume
    volume_sma_20: Optional[float] = None
    volume_ratio: Optional[float] = None  # current / average
    
    def to_dict(self) -> dict:
        return {k: v for k, v in self.__dict__.items() if v is not None}


@dataclass
class CandlePattern:
    """Detected candlestick pattern"""
    name: str
    type: str  # 'bullish', 'bearish', 'neutral'
    reliability: str  # 'low', 'medium', 'high'
    description: str
    
    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "type": self.type,
            "reliability": self.reliability,
            "description": self.description
        }


@dataclass
class MarketContext:
    """Complete market context at entry time"""
    symbol: str
    timestamp: datetime
    price: float
    
    # Price changes
    price_change_1h: float = 0.0
    price_change_24h: float = 0.0
    price_change_7d: float = 0.0
    
    # Position relative to range
    distance_from_high_24h: float = 0.0  # percentage below 24h high
    distance_from_low_24h: float = 0.0   # percentage above 24h low
    is_near_high: bool = False
    is_near_low: bool = False
    
    # Technical indicators
    indicators: Optional[MarketIndicators] = None
    
    # Candlestick patterns
    patterns: List[CandlePattern] = field(default_factory=list)
    
    # Market regime
    trend: str = "neutral"  # 'uptrend', 'downtrend', 'neutral', 'ranging'
    volatility: str = "normal"  # 'low', 'normal', 'high', 'extreme'
    
    # Risk assessment
    fomo_risk: str = "low"  # 'low', 'medium', 'high'
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "price": self.price,
            "price_change_1h": self.price_change_1h,
            "price_change_24h": self.price_change_24h,
            "price_change_7d": self.price_change_7d,
            "distance_from_high_24h": self.distance_from_high_24h,
            "distance_from_low_24h": self.distance_from_low_24h,
            "is_near_high": self.is_near_high,
            "is_near_low": self.is_near_low,
            "indicators": self.indicators.to_dict() if self.indicators else None,
            "patterns": [p.to_dict() for p in self.patterns],
            "trend": self.trend,
            "volatility": self.volatility,
            "fomo_risk": self.fomo_risk
        }


class MarketContextAnalyzer:
    """
    Market Context Analyzer - Calculates technical indicators and detects patterns.
    """
    
    def __init__(self):
        pass
    
    def analyze(
        self,
        candles: List[CandleStick],
        current_price: Optional[float] = None
    ) -> MarketContext:
        """
        Analyze market context from candlestick data.
        
        Args:
            candles: List of OHLCV candles (most recent last)
            current_price: Current market price (optional)
            
        Returns:
            MarketContext with indicators and patterns
        """
        if not candles:
            return self._empty_context()
        
        latest = candles[-1]
        price = current_price or latest.close
        
        # Calculate price changes
        price_change_1h = self._calc_price_change(candles, 1)
        price_change_24h = self._calc_price_change(candles, 24)
        price_change_7d = self._calc_price_change(candles, 168)  # 7 * 24
        
        # Calculate distance from high/low
        high_24h = max(c.high for c in candles[-24:]) if len(candles) >= 24 else max(c.high for c in candles)
        low_24h = min(c.low for c in candles[-24:]) if len(candles) >= 24 else min(c.low for c in candles)
        
        dist_from_high = ((high_24h - price) / high_24h) * 100 if high_24h > 0 else 0
        dist_from_low = ((price - low_24h) / low_24h) * 100 if low_24h > 0 else 0
        
        is_near_high = dist_from_high < 2  # Within 2% of 24h high
        is_near_low = dist_from_low < 2
        
        # Calculate indicators
        indicators = self._calculate_indicators(candles)
        
        # Detect patterns
        patterns = self._detect_patterns(candles[-10:])
        
        # Determine trend
        trend = self._determine_trend(candles, indicators)
        
        # Determine volatility
        volatility = self._determine_volatility(candles, indicators)
        
        # Assess FOMO risk
        fomo_risk = self._assess_fomo_risk(price_change_1h, price_change_24h, is_near_high, indicators)
        
        return MarketContext(
            symbol=getattr(candles[0], 'symbol', 'UNKNOWN'),
            timestamp=datetime.utcnow(),
            price=price,
            price_change_1h=round(price_change_1h, 2),
            price_change_24h=round(price_change_24h, 2),
            price_change_7d=round(price_change_7d, 2),
            distance_from_high_24h=round(dist_from_high, 2),
            distance_from_low_24h=round(dist_from_low, 2),
            is_near_high=is_near_high,
            is_near_low=is_near_low,
            indicators=indicators,
            patterns=patterns,
            trend=trend,
            volatility=volatility,
            fomo_risk=fomo_risk
        )
    
    def _calc_price_change(self, candles: List[CandleStick], hours: int) -> float:
        """Calculate price change over given hours"""
        if len(candles) < hours:
            hours = len(candles)
        if hours < 1:
            return 0.0
        
        current = candles[-1].close
        past = candles[-hours].close if len(candles) >= hours else candles[0].close
        
        return ((current - past) / past) * 100 if past > 0 else 0.0
    
    def _calculate_indicators(self, candles: List[CandleStick]) -> MarketIndicators:
        """Calculate technical indicators"""
        closes = [c.close for c in candles]
        highs = [c.high for c in candles]
        lows = [c.low for c in candles]
        volumes = [c.volume for c in candles]
        
        indicators = MarketIndicators()
        
        # SMAs
        if len(closes) >= 20:
            indicators.sma_20 = round(sum(closes[-20:]) / 20, 2)
        if len(closes) >= 50:
            indicators.sma_50 = round(sum(closes[-50:]) / 50, 2)
        
        # EMAs
        if len(closes) >= 12:
            indicators.ema_12 = round(self._calc_ema(closes, 12), 2)
        if len(closes) >= 26:
            indicators.ema_26 = round(self._calc_ema(closes, 26), 2)
        
        # RSI
        if len(closes) >= 15:
            indicators.rsi_14 = round(self._calc_rsi(closes, 14), 2)
        
        # MACD
        if indicators.ema_12 and indicators.ema_26:
            indicators.macd = round(indicators.ema_12 - indicators.ema_26, 4)
            # Signal line (9-period EMA of MACD) - simplified
            indicators.macd_signal = round(indicators.macd * 0.8, 4)  # Approximation
            indicators.macd_histogram = round(indicators.macd - indicators.macd_signal, 4)
        
        # ATR
        if len(candles) >= 14:
            indicators.atr_14 = round(self._calc_atr(candles, 14), 2)
        
        # Bollinger Bands
        if len(closes) >= 20:
            sma = sum(closes[-20:]) / 20
            std = (sum((p - sma) ** 2 for p in closes[-20:]) / 20) ** 0.5
            indicators.bollinger_upper = round(sma + 2 * std, 2)
            indicators.bollinger_lower = round(sma - 2 * std, 2)
            indicators.bollinger_width = round((indicators.bollinger_upper - indicators.bollinger_lower) / sma * 100, 2)
        
        # Volume
        if len(volumes) >= 20:
            indicators.volume_sma_20 = round(sum(volumes[-20:]) / 20, 2)
            indicators.volume_ratio = round(volumes[-1] / indicators.volume_sma_20, 2) if indicators.volume_sma_20 > 0 else 1.0
        
        return indicators
    
    def _calc_ema(self, prices: List[float], period: int) -> float:
        """Calculate EMA"""
        if len(prices) < period:
            return prices[-1]
        
        multiplier = 2 / (period + 1)
        ema = sum(prices[:period]) / period  # Start with SMA
        
        for price in prices[period:]:
            ema = (price * multiplier) + (ema * (1 - multiplier))
        
        return ema
    
    def _calc_rsi(self, prices: List[float], period: int = 14) -> float:
        """Calculate RSI"""
        if len(prices) < period + 1:
            return 50.0
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def _calc_atr(self, candles: List[CandleStick], period: int = 14) -> float:
        """Calculate Average True Range"""
        if len(candles) < period + 1:
            return 0.0
        
        true_ranges = []
        for i in range(1, len(candles)):
            tr = max(
                candles[i].high - candles[i].low,
                abs(candles[i].high - candles[i-1].close),
                abs(candles[i].low - candles[i-1].close)
            )
            true_ranges.append(tr)
        
        return sum(true_ranges[-period:]) / period
    
    def _detect_patterns(self, candles: List[CandleStick]) -> List[CandlePattern]:
        """Detect candlestick patterns"""
        if len(candles) < 3:
            return []
        
        patterns = []
        
        # Get last 3 candles
        c1, c2, c3 = candles[-3], candles[-2], candles[-1]
        
        # Doji
        body = abs(c3.close - c3.open)
        range_size = c3.high - c3.low
        if range_size > 0 and body / range_size < 0.1:
            patterns.append(CandlePattern(
                name="Doji",
                type="neutral",
                reliability="medium",
                description="Thị trường đang phân vân, có thể đảo chiều"
            ))
        
        # Hammer (bullish)
        if c3.close > c3.open:
            lower_shadow = min(c3.open, c3.close) - c3.low
            upper_shadow = c3.high - max(c3.open, c3.close)
            if lower_shadow > body * 2 and upper_shadow < body * 0.5:
                patterns.append(CandlePattern(
                    name="Hammer",
                    type="bullish",
                    reliability="medium",
                    description="Tín hiệu đảo chiều tăng sau downtrend"
                ))
        
        # Engulfing patterns
        if len(candles) >= 2:
            # Bullish Engulfing
            if c2.close < c2.open and c3.close > c3.open:  # Red then green
                if c3.open < c2.close and c3.close > c2.open:
                    patterns.append(CandlePattern(
                        name="Bullish Engulfing",
                        type="bullish",
                        reliability="high",
                        description="Nến xanh bao trùm nến đỏ - tín hiệu tăng mạnh"
                    ))
            
            # Bearish Engulfing
            if c2.close > c2.open and c3.close < c3.open:  # Green then red
                if c3.open > c2.close and c3.close < c2.open:
                    patterns.append(CandlePattern(
                        name="Bearish Engulfing",
                        type="bearish",
                        reliability="high",
                        description="Nến đỏ bao trùm nến xanh - tín hiệu giảm mạnh"
                    ))
        
        # Three consecutive green/red
        if all(c.close > c.open for c in candles[-3:]):
            patterns.append(CandlePattern(
                name="Three White Soldiers",
                type="bullish",
                reliability="high",
                description="3 nến xanh liên tiếp - uptrend mạnh"
            ))
        elif all(c.close < c.open for c in candles[-3:]):
            patterns.append(CandlePattern(
                name="Three Black Crows",
                type="bearish",
                reliability="high",
                description="3 nến đỏ liên tiếp - downtrend mạnh"
            ))
        
        return patterns
    
    def _determine_trend(self, candles: List[CandleStick], indicators: MarketIndicators) -> str:
        """Determine current market trend"""
        if not indicators.sma_20 or not indicators.sma_50:
            return "neutral"
        
        current_price = candles[-1].close
        
        if current_price > indicators.sma_20 > indicators.sma_50:
            return "uptrend"
        elif current_price < indicators.sma_20 < indicators.sma_50:
            return "downtrend"
        elif indicators.bollinger_width and indicators.bollinger_width < 5:
            return "ranging"
        else:
            return "neutral"
    
    def _determine_volatility(self, candles: List[CandleStick], indicators: MarketIndicators) -> str:
        """Determine current volatility level"""
        if not indicators.atr_14 or not indicators.sma_20:
            return "normal"
        
        # ATR as percentage of price
        atr_pct = (indicators.atr_14 / indicators.sma_20) * 100
        
        if atr_pct > 5:
            return "extreme"
        elif atr_pct > 3:
            return "high"
        elif atr_pct < 1:
            return "low"
        else:
            return "normal"
    
    def _assess_fomo_risk(
        self,
        price_change_1h: float,
        price_change_24h: float,
        is_near_high: bool,
        indicators: MarketIndicators
    ) -> str:
        """Assess FOMO risk based on market conditions"""
        risk_score = 0
        
        # Strong recent pump
        if price_change_1h > 8:
            risk_score += 3
        elif price_change_1h > 5:
            risk_score += 2
        elif price_change_1h > 3:
            risk_score += 1
        
        # Near 24h high
        if is_near_high:
            risk_score += 2
        
        # Overbought RSI
        if indicators.rsi_14 and indicators.rsi_14 > 70:
            risk_score += 2
        elif indicators.rsi_14 and indicators.rsi_14 > 60:
            risk_score += 1
        
        # High volume spike
        if indicators.volume_ratio and indicators.volume_ratio > 3:
            risk_score += 1
        
        if risk_score >= 5:
            return "high"
        elif risk_score >= 3:
            return "medium"
        else:
            return "low"
    
    def _empty_context(self) -> MarketContext:
        """Return empty context"""
        return MarketContext(
            symbol="UNKNOWN",
            timestamp=datetime.utcnow(),
            price=0.0
        )


# Singleton
_market_analyzer: Optional[MarketContextAnalyzer] = None

def get_market_analyzer() -> MarketContextAnalyzer:
    """Get or create Market Context Analyzer singleton"""
    global _market_analyzer
    if _market_analyzer is None:
        _market_analyzer = MarketContextAnalyzer()
    return _market_analyzer
