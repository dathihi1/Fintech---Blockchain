"""
Symbols API - Symbol search and autocomplete
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from models import get_db, Trade
from services.symbol_service import search_symbols, get_symbols, POPULAR_SYMBOLS

router = APIRouter(prefix="/symbols", tags=["Symbols"])


@router.get("/search")
async def search_symbol(
    q: str = Query("", description="Search query (symbol or base asset)"),
    limit: int = Query(10, ge=1, le=50)
):
    """
    Search for trading symbols.
    
    Examples:
    - `/api/symbols/search?q=BTC` → BTCUSDT, BTCBUSD, etc.
    - `/api/symbols/search?q=ETH` → ETHUSDT, ETHBUSD, etc.
    """
    results = await search_symbols(q, limit)
    return [s.to_dict() for s in results]


@router.get("/popular")
async def get_popular_symbols(limit: int = Query(20, ge=1, le=50)):
    """Get most popular trading symbols"""
    return [s.to_dict() for s in POPULAR_SYMBOLS[:limit]]


@router.get("/all")
async def get_all_symbols():
    """Get all available symbols (cached from Binance)"""
    symbols = await get_symbols()
    return [s.to_dict() for s in symbols]


@router.get("/user/{user_id}")
async def get_user_traded_symbols(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Get symbols that a user has traded"""
    trades = (
        db.query(Trade.symbol)
        .filter(Trade.user_id == user_id)
        .distinct()
        .all()
    )
    
    user_symbols = [t.symbol for t in trades]
    
    # Also return popular symbols not yet traded
    traded_set = set(user_symbols)
    suggestions = [s.symbol for s in POPULAR_SYMBOLS if s.symbol not in traded_set]
    
    return {
        "traded": user_symbols,
        "suggestions": suggestions[:10]
    }
