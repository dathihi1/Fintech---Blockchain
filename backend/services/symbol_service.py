"""
Symbol Service - Fetch and cache trading symbols from Binance
"""

import httpx
import asyncio
from typing import List, Optional, Dict
from datetime import datetime, timedelta
from dataclasses import dataclass
import re


@dataclass
class Symbol:
    """Trading symbol with metadata"""
    symbol: str           # BTCUSDT
    base_asset: str       # BTC
    quote_asset: str      # USDT
    status: str           # TRADING
    
    def to_dict(self) -> dict:
        return {
            "symbol": self.symbol,
            "base_asset": self.base_asset,
            "quote_asset": self.quote_asset,
            "status": self.status,
            "display": f"{self.base_asset}/{self.quote_asset}"
        }


class SymbolCache:
    """In-memory cache for symbols with TTL"""
    
    def __init__(self, ttl_minutes: int = 5):
        self.symbols: List[Symbol] = []
        self.last_fetch: Optional[datetime] = None
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def is_valid(self) -> bool:
        if not self.last_fetch:
            return False
        return datetime.utcnow() - self.last_fetch < self.ttl
    
    def update(self, symbols: List[Symbol]):
        self.symbols = symbols
        self.last_fetch = datetime.utcnow()
    
    def get_all(self) -> List[Symbol]:
        return self.symbols


# Global cache
_symbol_cache = SymbolCache()


# Popular symbols for fallback
POPULAR_SYMBOLS = [
    Symbol("BTCUSDT", "BTC", "USDT", "TRADING"),
    Symbol("ETHUSDT", "ETH", "USDT", "TRADING"),
    Symbol("BNBUSDT", "BNB", "USDT", "TRADING"),
    Symbol("SOLUSDT", "SOL", "USDT", "TRADING"),
    Symbol("XRPUSDT", "XRP", "USDT", "TRADING"),
    Symbol("ADAUSDT", "ADA", "USDT", "TRADING"),
    Symbol("DOGEUSDT", "DOGE", "USDT", "TRADING"),
    Symbol("AVAXUSDT", "AVAX", "USDT", "TRADING"),
    Symbol("DOTUSDT", "DOT", "USDT", "TRADING"),
    Symbol("MATICUSDT", "MATIC", "USDT", "TRADING"),
    Symbol("LINKUSDT", "LINK", "USDT", "TRADING"),
    Symbol("LTCUSDT", "LTC", "USDT", "TRADING"),
    Symbol("ATOMUSDT", "ATOM", "USDT", "TRADING"),
    Symbol("UNIUSDT", "UNI", "USDT", "TRADING"),
    Symbol("APTUSDT", "APT", "USDT", "TRADING"),
    Symbol("ARBUSDT", "ARB", "USDT", "TRADING"),
    Symbol("OPUSDT", "OP", "USDT", "TRADING"),
    Symbol("NEARUSDT", "NEAR", "USDT", "TRADING"),
    Symbol("FILUSDT", "FIL", "USDT", "TRADING"),
    Symbol("INJUSDT", "INJ", "USDT", "TRADING"),
]


async def fetch_binance_symbols() -> List[Symbol]:
    """Fetch all trading symbols from Binance API"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("https://api.binance.com/api/v3/exchangeInfo")
            response.raise_for_status()
            data = response.json()
            
            symbols = []
            for s in data.get("symbols", []):
                # Only USDT pairs and active trading
                if s.get("quoteAsset") == "USDT" and s.get("status") == "TRADING":
                    symbols.append(Symbol(
                        symbol=s["symbol"],
                        base_asset=s["baseAsset"],
                        quote_asset=s["quoteAsset"],
                        status=s["status"]
                    ))
            
            return symbols
    except Exception as e:
        print(f"Failed to fetch Binance symbols: {e}")
        return POPULAR_SYMBOLS


async def get_symbols(force_refresh: bool = False) -> List[Symbol]:
    """Get symbols from cache or fetch from Binance"""
    global _symbol_cache
    
    if not force_refresh and _symbol_cache.is_valid():
        return _symbol_cache.get_all()
    
    symbols = await fetch_binance_symbols()
    _symbol_cache.update(symbols)
    
    return symbols


async def search_symbols(query: str, limit: int = 10) -> List[Symbol]:
    """
    Search symbols by prefix matching.
    Query can match symbol (BTCUSDT) or base asset (BTC).
    """
    if not query or len(query) < 1:
        # Return popular symbols if no query
        return POPULAR_SYMBOLS[:limit]
    
    query = query.upper().strip()
    symbols = await get_symbols()
    
    matches = []
    
    # Exact match first
    for s in symbols:
        if s.symbol == query or s.base_asset == query:
            matches.append(s)
    
    # Prefix match
    for s in symbols:
        if s not in matches:
            if s.symbol.startswith(query) or s.base_asset.startswith(query):
                matches.append(s)
    
    # Contains match
    for s in symbols:
        if s not in matches:
            if query in s.symbol or query in s.base_asset:
                matches.append(s)
    
    return matches[:limit]


async def get_user_symbols(user_id: str, db_session) -> List[str]:
    """Get symbols that a user has traded"""
    from models import Trade
    
    trades = (
        db_session.query(Trade.symbol)
        .filter(Trade.user_id == user_id)
        .distinct()
        .all()
    )
    
    return [t.symbol for t in trades]


# Singleton getter
def get_symbol_service():
    return {
        "search": search_symbols,
        "get_all": get_symbols,
        "get_user_symbols": get_user_symbols,
        "popular": POPULAR_SYMBOLS
    }
