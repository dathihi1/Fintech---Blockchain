# 📤 Exit Strategy - Khi Nào Người Dùng Exit?

## 🤔 Vấn Đề Hiện Tại

**Backend:** Có API `PATCH /api/trades/{id}` để update exit_price ✅  
**Frontend:** KHÔNG có UI để người dùng nhập exit_price ❌

### Quy Trình Mong Muốn
```
1. Người dùng vào lệnh thực tế trên sàn (Binance/...)
2. Tạo trade trong hệ thống (entry_price)
3. Trade đang mở (exit_price = null)
4. Khi đóng lệnh thực tế → Vào hệ thống UPDATE exit_price
5. Hệ thống tự tính PnL, cập nhật stats
```

---

## 🎯 Kịch Bản Sử Dụng

### Scenario 1: Trader Manual
```
09:00 - Vào lệnh Long BTCUSDT @ $45,000
      → Mở app, thêm trade mới

12:00 - Giá lên $48,000, quyết định chốt lời
      → Đóng lệnh trên Binance
      → Vào app, bấm nút "Close Trade"
      → Nhập Exit Price: $48,000
      → Hệ thống tính PnL: +6.67%
      → Dashboard cập nhật Win Rate: 60% → 66.67%
```

### Scenario 2: Copy Trading / Auto Bot
```
- Bot tự động vào/ra lệnh
- Người dùng sync dữ liệu sau mỗi trade
- Hoặc tích hợp API Binance (auto fetch exit_price)
```

### Scenario 3: Quên Update
```
- Trade đã đóng 1 tuần nhưng quên update
- Vào Trade Journal, tìm trade cũ
- Bấm "Close Trade", nhập exit_price
- Stats được tính lại ngay lập tức
```

---

## 🛠️ Implementation Plan

### Backend (Đã có sẵn) ✅
```python
# backend/api/trades.py
@router.patch("/{trade_id}")
async def update_trade(trade_id: int, update_data: TradeUpdate):
    # Update exit_price
    # Calculate PnL automatically
    # Update stats
```

### Frontend (CẦN BỔ SUNG) ❌

#### Option 1: Dialog Popup
```jsx
// Thêm dialog popup khi click vào row
<TableRow onClick={() => handleOpenCloseDialog(trade)}>
  ...
</TableRow>

// Dialog để nhập exit price
<Dialog open={closeDialogOpen}>
  <TextField label="Exit Price" />
  <Button onClick={handleCloseTrade}>Close Trade</Button>
</Dialog>
```

#### Option 2: Inline Edit
```jsx
// Thêm nút trong table row
<TableCell>
  {trade.exit_price ? (
    `$${trade.exit_price}`
  ) : (
    <Button size="small" onClick={() => openCloseForm(trade)}>
      Close Trade
    </Button>
  )}
</TableCell>
```

#### Option 3: Edit Page
```jsx
// Navigate to /trades/:id/edit
<IconButton onClick={() => navigate(`/trades/${trade.id}/edit`)}>
  <EditIcon />
</IconButton>
```

---

## 💡 Recommended Solution

### **Chọn Option 1: Dialog Popup** (Best UX)

**Lý do:**
- ✅ Nhanh gọn, không cần navigate
- ✅ Xác nhận trước khi đóng trade
- ✅ Có thể thêm notes khi exit
- ✅ Hiển thị preview PnL trước khi save

### UI Design:
```
┌─────────────────────────────────┐
│   Close Trade - BTCUSDT Long   │
├─────────────────────────────────┤
│ Entry Price: $45,000            │
│ Quantity: 0.1 BTC               │
│                                 │
│ Exit Price: [_______]  ← INPUT  │
│                                 │
│ 💰 Estimated P&L:               │
│    +$300 (+6.67%)               │
│                                 │
│ Exit Notes (optional):          │
│ [_______________________]       │
│                                 │
│  [Cancel]  [Close Trade] ← BTN  │
└─────────────────────────────────┘
```

---

## 📝 Code Implementation

### Step 1: Add Close Trade Function to API Service
```javascript
// frontend/src/services/api.js
export const closeTrade = async (tradeId, exitPrice, exitNotes = null) => {
    const response = await api.patch(`/trades/${tradeId}`, {
        exit_price: exitPrice,
        notes: exitNotes  // Optional: append exit notes
    });
    return response.data;
};
```

### Step 2: Add Dialog to TradeJournal.jsx
```jsx
const [closeDialog, setCloseDialog] = useState({
    open: false,
    trade: null,
    exitPrice: '',
    exitNotes: ''
});

const handleOpenCloseDialog = (trade) => {
    setCloseDialog({
        open: true,
        trade,
        exitPrice: '',
        exitNotes: ''
    });
};

const handleCloseTrade = async () => {
    const { trade, exitPrice } = closeDialog;
    
    try {
        await closeTrade(trade.id, parseFloat(exitPrice));
        
        // Update local state
        setTrades(prev => prev.map(t => 
            t.id === trade.id 
                ? { ...t, exit_price: parseFloat(exitPrice), pnl_pct: calculatePnL(t, exitPrice) }
                : t
        ));
        
        // Close dialog
        setCloseDialog({ open: false, trade: null, exitPrice: '', exitNotes: '' });
        
        // Refresh to get updated stats
        fetchTrades();
    } catch (err) {
        console.error('Failed to close trade:', err);
    }
};
```

### Step 3: Add Close Button to Table
```jsx
<TableCell>
    {trade.exit_price ? (
        <Typography>${trade.exit_price.toLocaleString()}</Typography>
    ) : (
        <Button
            size="small"
            variant="outlined"
            onClick={() => handleOpenCloseDialog(trade)}
        >
            Close
        </Button>
    )}
</TableCell>
```

### Step 4: Dialog Component
```jsx
<Dialog open={closeDialog.open} onClose={() => setCloseDialog({ ...closeDialog, open: false })}>
    <DialogTitle>
        Close Trade - {closeDialog.trade?.symbol} {closeDialog.trade?.side?.toUpperCase()}
    </DialogTitle>
    <DialogContent>
        <Box sx={{ mb: 2 }}>
            <Typography variant="body2" color="text.secondary">
                Entry Price: ${closeDialog.trade?.entry_price?.toLocaleString()}
            </Typography>
            <Typography variant="body2" color="text.secondary">
                Quantity: {closeDialog.trade?.quantity}
            </Typography>
        </Box>
        
        <TextField
            label="Exit Price"
            type="number"
            value={closeDialog.exitPrice}
            onChange={(e) => setCloseDialog({ ...closeDialog, exitPrice: e.target.value })}
            fullWidth
            required
            sx={{ mb: 2 }}
        />
        
        {closeDialog.exitPrice && (
            <Alert severity="info" sx={{ mb: 2 }}>
                💰 Estimated P&L: {calculateEstimatedPnL(closeDialog.trade, closeDialog.exitPrice)}
            </Alert>
        )}
        
        <TextField
            label="Exit Notes (optional)"
            value={closeDialog.exitNotes}
            onChange={(e) => setCloseDialog({ ...closeDialog, exitNotes: e.target.value })}
            multiline
            rows={2}
            fullWidth
        />
    </DialogContent>
    <DialogActions>
        <Button onClick={() => setCloseDialog({ ...closeDialog, open: false })}>
            Cancel
        </Button>
        <Button
            onClick={handleCloseTrade}
            variant="contained"
            disabled={!closeDialog.exitPrice}
        >
            Close Trade
        </Button>
    </DialogActions>
</Dialog>
```

---

## 🔄 Luồng Dữ Liệu

### Before Close (Trade đang mở)
```json
{
  "id": 5,
  "symbol": "BTCUSDT",
  "side": "long",
  "entry_price": 45000,
  "exit_price": null,
  "quantity": 0.1,
  "pnl": null,
  "pnl_pct": null
}
```

### After Close (Trade đã đóng)
```json
{
  "id": 5,
  "symbol": "BTCUSDT",
  "side": "long",
  "entry_price": 45000,
  "exit_price": 48000,  ← UPDATED
  "quantity": 0.1,
  "pnl": 300,           ← AUTO CALCULATED
  "pnl_pct": 6.67,      ← AUTO CALCULATED
  "exit_time": "2026-01-30T12:00:00"
}
```

### Stats Update (Backend tự động)
```
Before: 4 trades, Win Rate 50%, Avg +0.38%
After:  5 trades, Win Rate 60%, Avg +1.72%
```

---

## 🎨 Alternative: Quick Actions Menu

```jsx
// Thêm action menu cho mỗi trade
<TableCell>
    <IconButton onClick={(e) => handleMenuOpen(e, trade)}>
        <MoreVertIcon />
    </IconButton>
</TableCell>

<Menu anchorEl={menuAnchor}>
    <MenuItem onClick={handleCloseTrade}>
        <ExitToAppIcon /> Close Trade
    </MenuItem>
    <MenuItem onClick={handleEditTrade}>
        <EditIcon /> Edit
    </MenuItem>
    <MenuItem onClick={handleDeleteTrade}>
        <DeleteIcon /> Delete
    </MenuItem>
</Menu>
```

---

## 🚀 Next Steps

1. **Implement Close Trade Dialog** (cao nhất priority)
2. Add Edit Trade functionality (optional)
3. Add Delete Trade confirmation
4. Add bulk actions (close multiple trades)
5. **Future:** Auto-sync với Binance API

---

## 📊 Example Usage Timeline

```
Day 1 Morning:
  - Create Trade #1: BTCUSDT Long @ $45,000
  - Stats: 1 total, 0 closed, 0% win rate

Day 1 Evening:
  - Close Trade #1: Exit @ $48,000
  - Stats: 1 total, 1 closed, 100% win rate, +6.67% avg

Day 2:
  - Create Trade #2: ETHUSDT Short @ $3,000
  - Close Trade #2: Exit @ $2,900
  - Stats: 2 total, 2 closed, 100% win rate, +5.5% avg

Day 3:
  - Create Trade #3: SOLUSDT Long @ $100
  - Close Trade #3: Exit @ $95 (LOSS)
  - Stats: 3 total, 3 closed, 66.67% win rate, +2.2% avg

Day 4:
  - Create Trade #4: BNBUSDT Long @ $600
  - Still open (không close)
  - Stats: 4 total, 3 closed, 66.67% win rate (không đổi)
```

---

**Conclusion:** Cần bổ sung UI để người dùng có thể UPDATE exit_price khi đóng lệnh thực tế. Backend đã sẵn sàng, chỉ cần frontend implement dialog hoặc form để nhập exit price.

**Last Updated:** January 30, 2026
