# 7. API Layer - FastAPI Backend

## 📋 Mô Tả Nghiệp Vụ

### Endpoints cần thiết

| Category | Endpoint | Method | Mô tả |
|----------|----------|--------|-------|
| **Trades** | `/api/trades` | POST | Thêm giao dịch mới |
| | `/api/trades` | GET | Lấy lịch sử giao dịch |
| | `/api/trades/{id}` | GET | Chi tiết 1 trade |
| **Analysis** | `/api/analysis/passive` | GET | Phân tích thụ động |
| | `/api/analysis/active` | GET | Alerts hiện tại |
| **NLP** | `/api/nlp/analyze` | POST | Phân tích text |
| **Candles** | `/api/candles/{symbol}` | GET | Mô hình nến |
| **Market** | `/api/market/{symbol}` | GET | Bối cảnh thị trường |
| **WebSocket** | `/ws/alerts` | WS | Real-time alerts |

---

## 🔧 Xử Lý Kỹ Thuật

### Project Structure
```
backend/
├── main.py              # FastAPI app
├── config.py            # Settings
├── routers/
│   ├── trades.py
│   ├── analysis.py
│   ├── nlp.py
│   └── market.py
├── models/
│   ├── trade.py
│   └── analysis.py
├── services/
│   ├── trade_service.py
│   └── analysis_service.py
└── ws/
    └── alerts.py
```

### Main App
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Smart Trading Journal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(trades.router, prefix="/api/trades")
app.include_router(analysis.router, prefix="/api/analysis")
app.include_router(nlp.router, prefix="/api/nlp")
app.include_router(market.router, prefix="/api/market")
```

### Trade Model
```python
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TradeCreate(BaseModel):
    symbol: str
    side: str  # "BUY" or "SELL"
    entry_price: float
    quantity: float
    notes: Optional[str] = None

class Trade(TradeCreate):
    id: str
    user_id: str
    entry_time: datetime
    exit_price: Optional[float]
    exit_time: Optional[datetime]
    pnl: Optional[float]
    nlp_analysis: Optional[dict]
    market_context: Optional[dict]
```

### WebSocket Alerts
```python
from fastapi import WebSocket

@app.websocket("/ws/alerts/{user_id}")
async def alert_stream(user_id: str, ws: WebSocket):
    await ws.accept()
    async for alert in alert_channel.subscribe(user_id):
        await ws.send_json(alert.dict())
```
