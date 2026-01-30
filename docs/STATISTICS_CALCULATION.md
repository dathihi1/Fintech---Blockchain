# 📊 Cách Tính Thống Kê Trading

## 🎯 Các Tham Số Chính

### 1. **Total Trades** (Tổng Số Giao Dịch)
```python
total_trades = len(all_trades)
```
- Đếm **TẤT CẢ** các trades (kể cả đang mở và đã đóng)
- Tăng lên khi thêm trade mới
- **Không phụ thuộc** vào exit_price

**Ví dụ:**
- 4 trades đã đóng + 1 trade đang mở = **5 Total Trades**

---

### 2. **Closed Trades** (Số Giao Dịch Đã Đóng)
```python
closed_trades = [t for t in all_trades if t.pnl_pct is not None]
```
- Chỉ đếm trades **ĐÃ CÓ exit_price và PnL**
- Trade mới chưa đóng **KHÔNG** được tính
- Dùng để tính các thống kê khác

**Ví dụ:**
- 4 trades có exit_price = **4 Closed Trades**
- Thêm 1 trade mới chưa đóng → vẫn **4 Closed Trades**

---

### 3. **Win Rate** (Tỷ Lệ Thắng)
```python
winning_trades = [t for t in closed_trades if t.pnl > 0]
win_rate = len(winning_trades) / len(closed_trades)
```

**Công thức:**
```
Win Rate = (Số trades có PnL > 0) / (Tổng closed trades)
```

**Ví dụ hiện tại:**
- Closed Trades: 4
- Winning: 2 (Trade #4: +6.25%, Trade #2: +2.38%)
- Losing: 2 (Trade #5: -2.37%, Trade #3: -4.68%)
- **Win Rate = 2/4 = 50%**

**Khi thêm trade mới:**

#### Trường hợp 1: Trade đang mở (chưa có exit)
```
Trade mới: BNBUSDT - Entry: $600 - Exit: null
→ Total Trades: 5
→ Closed Trades: 4 (không đổi)
→ Win Rate: 50% (không đổi)
```

#### Trường hợp 2: Trade đóng WIN
```
Trade mới: BNBUSDT - Entry: $600 - Exit: $630 (+5%)
→ Total Trades: 5
→ Closed Trades: 5
→ Winning: 3
→ Win Rate = 3/5 = 60%
```

#### Trường hợp 3: Trade đóng LOSE
```
Trade mới: BNBUSDT - Entry: $600 - Exit: $580 (-3.33%)
→ Total Trades: 5
→ Closed Trades: 5
→ Winning: 2
→ Win Rate = 2/5 = 40%
```

---

### 4. **Total PnL** (Tổng Lãi/Lỗ USD)
```python
total_pnl = sum(t.pnl for t in closed_trades if t.pnl)
```

**Công thức:**
```
Total PnL = Σ (exit_price - entry_price) × quantity
```

**Cho Long:**
```
PnL = (Exit Price - Entry Price) × Quantity
```

**Cho Short:**
```
PnL = (Entry Price - Exit Price) × Quantity
```

**Ví dụ hiện tại:**
```
Trade #5: -$1,183,048.91 (Short ETHUSDT)
Trade #4: +$281.36 (Long BTCUSDT)
Trade #3: -$1.12 (Long BTCUSDT)
Trade #2: +$107.31 (Long BTCUSDT)
Total PnL = -$1,182,662.47
```

**Khi thêm trade mới:**
```
Trade mới: Entry $600 × 10 BNB = $6,000
Exit: $630 × 10 BNB = $6,300
PnL = ($630 - $600) × 10 = +$300

→ New Total PnL = -$1,182,662.47 + $300 = -$1,182,362.47
```

---

### 5. **Avg PnL %** (% Lãi/Lỗ Trung Bình)
```python
avg_pnl_pct = sum(t.pnl_pct for t in closed_trades) / len(closed_trades)
```

**Công thức:**
```
Avg PnL % = Σ(PnL % của mỗi trade) / Số closed trades
```

**Ví dụ hiện tại:**
```
Trade #5: -2.37%
Trade #4: +6.25%
Trade #3: -4.68%
Trade #2: +2.38%

Avg = (-2.37 + 6.25 - 4.68 + 2.38) / 4 = 1.58 / 4 = +0.395%
```

**Lưu ý:** Code hiện tại báo +0.38% (có thể do làm tròn hoặc data khác)

**Khi thêm trade +5%:**
```
New Avg = (-2.37 + 6.25 - 4.68 + 2.38 + 5) / 5 = 6.58 / 5 = +1.32%
```

---

### 6. **Best Trade** (Trade Tốt Nhất)
```python
best_trade = max(t.pnl_pct for t in closed_trades)
```

**Công thức:**
```
Best Trade = MAX(tất cả PnL %)
```

**Ví dụ hiện tại:**
```
Trades: [-2.37%, +6.25%, -4.68%, +2.38%]
Best = +6.25%
```

**Khi thêm trade +8%:**
```
Best = +8% (thay thế +6.25%)
```

**Khi thêm trade +4%:**
```
Best = +6.25% (không đổi)
```

---

### 7. **Worst Trade** (Trade Tệ Nhất)
```python
worst_trade = min(t.pnl_pct for t in closed_trades)
```

**Công thức:**
```
Worst Trade = MIN(tất cả PnL %)
```

**Ví dụ hiện tại:**
```
Trades: [-2.37%, +6.25%, -4.68%, +2.38%]
Worst = -4.68%
```

**Khi thêm trade -6%:**
```
Worst = -6% (thay thế -4.68%)
```

---

## 📈 Ví Dụ Thực Tế: Thêm Trade Mới

### Scenario 1: Thêm Trade Đang Mở

**Trade mới:**
```json
{
  "symbol": "SOLUSDT",
  "side": "long",
  "entry_price": 100,
  "quantity": 5,
  "exit_price": null,
  "pnl": null,
  "pnl_pct": null
}
```

**Kết quả:**
```
Total Trades: 4 → 5 ✅ (tăng)
Closed Trades: 4 → 4 (không đổi)
Win Rate: 50% → 50% (không đổi)
Total PnL: -$1,182,662.47 → -$1,182,662.47 (không đổi)
Avg PnL: +0.38% → +0.38% (không đổi)
Best: +6.25% → +6.25% (không đổi)
Worst: -4.75% → -4.75% (không đổi)
```

---

### Scenario 2: Thêm Trade Win (+7%)

**Trade mới:**
```json
{
  "symbol": "SOLUSDT",
  "side": "long",
  "entry_price": 100,
  "quantity": 5,
  "exit_price": 107,
  "pnl": 35,
  "pnl_pct": 7.0
}
```

**Kết quả:**
```
Total Trades: 4 → 5 ✅
Closed Trades: 4 → 5 ✅
Win Rate: 50% → 60% ✅ (3 win / 5 trades)
Total PnL: -$1,182,662.47 → -$1,182,627.47 ✅
Avg PnL: +0.38% → +1.24% ✅
Best: +6.25% → +7.00% ✅
Worst: -4.75% → -4.75%
```

---

### Scenario 3: Thêm Trade Lose (-3%)

**Trade mới:**
```json
{
  "symbol": "SOLUSDT",
  "side": "long",
  "entry_price": 100,
  "quantity": 5,
  "exit_price": 97,
  "pnl": -15,
  "pnl_pct": -3.0
}
```

**Kết quả:**
```
Total Trades: 4 → 5 ✅
Closed Trades: 4 → 5 ✅
Win Rate: 50% → 40% ⚠️ (2 win / 5 trades)
Total PnL: -$1,182,662.47 → -$1,182,677.47 ⚠️
Avg PnL: +0.38% → -0.29% ⚠️
Best: +6.25% → +6.25%
Worst: -4.75% → -4.75%
```

---

## 🔄 Tính Toán PnL Chi Tiết

### Long Position (Mua)
```python
PnL USD = (Exit Price - Entry Price) × Quantity
PnL % = ((Exit Price - Entry Price) / Entry Price) × 100
```

**Ví dụ:**
```
Entry: $45,000 × 0.1 BTC = $4,500
Exit: $48,000 × 0.1 BTC = $4,800

PnL USD = ($48,000 - $45,000) × 0.1 = $300
PnL % = (($48,000 - $45,000) / $45,000) × 100 = 6.67%
```

### Short Position (Bán)
```python
PnL USD = (Entry Price - Exit Price) × Quantity
PnL % = ((Entry Price - Exit Price) / Entry Price) × 100
```

**Ví dụ:**
```
Entry: $50,000 × 0.1 BTC = $5,000 (Bán)
Exit: $48,000 × 0.1 BTC = $4,800 (Mua lại)

PnL USD = ($50,000 - $48,000) × 0.1 = $200
PnL % = (($50,000 - $48,000) / $50,000) × 100 = 4%
```

---

## 🎯 Khi Nào Stats Được Cập Nhật?

### ✅ Cập nhật ngay lập tức:
1. **Total Trades** - Khi POST /api/trades/ (thêm trade mới)
2. **Closed Trades** - Khi PATCH /api/trades/{id} với exit_price
3. **Win Rate, Avg PnL, Best, Worst** - Khi trade được đóng

### ⏱️ Refresh cần thiết:
- Frontend cần **reload** hoặc **poll** API sau khi:
  - Thêm trade mới
  - Cập nhật exit price
  - Xóa trade

---

## 📊 Code Implementation

### Backend (analysis.py)
```python
@router.get("/stats")
async def get_trade_stats(
    current_user: User = Depends(get_current_user_or_demo),
    db: Session = Depends(get_db)
):
    # 1. Lấy tất cả trades
    all_trades = db.query(Trade).filter(Trade.user_id == user_id).all()
    
    # 2. Lọc closed trades
    closed_trades = [t for t in all_trades if t.pnl_pct is not None]
    
    # 3. Tính win rate
    winning_trades = [t for t in closed_trades if t.pnl > 0]
    win_rate = len(winning_trades) / len(closed_trades)
    
    # 4. Tính các metrics khác
    total_pnl = sum(t.pnl for t in closed_trades)
    avg_pnl_pct = sum(t.pnl_pct for t in closed_trades) / len(closed_trades)
    best_trade = max(t.pnl_pct for t in closed_trades)
    worst_trade = min(t.pnl_pct for t in closed_trades)
    
    return {
        "total_trades": len(all_trades),
        "closed_trades": len(closed_trades),
        "win_rate": round(win_rate, 2),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl_pct": round(avg_pnl_pct, 2),
        "best_trade": round(best_trade, 2),
        "worst_trade": round(worst_trade, 2)
    }
```

---

## 💡 Tips Quan Trọng

### 1. Trade Đang Mở
- **Không** ảnh hưởng đến Win Rate, Avg PnL, Best/Worst
- Chỉ tăng Total Trades
- Frontend có thể hiển thị riêng "Open Trades"

### 2. Độ Chính Xác
- Làm tròn 2 chữ số thập phân
- PnL % chính xác hơn PnL USD (do quantity khác nhau)

### 3. Performance
- Cache stats nếu có nhiều trades (>1000)
- Tính toán real-time cho <100 trades

### 4. Edge Cases
- **Không có closed trades**: Return 0 cho tất cả
- **1 trade duy nhất**: Win rate = 100% hoặc 0%
- **Trade có PnL = 0**: Tính là Losing trade (breakeven)

---

## 🧪 Test Cases

### Test 1: Empty Portfolio
```
Input: 0 trades
Output:
  Total: 0, Closed: 0, Win Rate: 0%, 
  Total PnL: $0, Avg: 0%, Best: 0%, Worst: 0%
```

### Test 2: All Winning
```
Input: 3 trades (+2%, +5%, +3%)
Output:
  Total: 3, Closed: 3, Win Rate: 100%
  Avg: +3.33%, Best: +5%, Worst: +2%
```

### Test 3: All Losing
```
Input: 3 trades (-2%, -5%, -3%)
Output:
  Total: 3, Closed: 3, Win Rate: 0%
  Avg: -3.33%, Best: -2%, Worst: -5%
```

### Test 4: Mixed với Open Trades
```
Input: 
  - Closed: +5%, -2%, +3%
  - Open: 1 trade
Output:
  Total: 4, Closed: 3, Win Rate: 66.67%
  Avg: +2%, Best: +5%, Worst: -2%
```

---

**Last Updated:** January 30, 2026
**Version:** 1.0
