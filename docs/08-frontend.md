# 8. Frontend UI - React Dashboard

## 📋 Mô Tả Nghiệp Vụ

### Các màn hình chính

| Screen | Chức năng |
|--------|-----------|
| **Dashboard** | Overview: P&L, win rate, alerts |
| **Trade Journal** | Nhập và xem lịch sử trades |
| **Analytics** | Charts, behavioral patterns |
| **Alerts** | Real-time warnings |
| **Settings** | API keys, preferences |

### UI Components

```
┌────────────────────────────────────────────────────────┐
│ 🏠 Dashboard                                           │
├──────────────┬──────────────┬──────────────────────────┤
│ Total P&L    │ Win Rate     │ Sharpe Ratio            │
│ +$1,234      │ 62%          │ 1.45                    │
├──────────────┴──────────────┴──────────────────────────┤
│ 📊 P&L Chart (TradingView)                            │
│ ▁▂▃▄▅▆▇█▇▆▅▄▃▂▁▂▃▄▅▆▇                                │
├────────────────────────────────────────────────────────┤
│ ⚠️ Active Alerts                                       │
│ 🔴 FOMO detected - BTC entry after 8% pump           │
│ 🟡 Overtrading - 12 trades today                      │
├────────────────────────────────────────────────────────┤
│ 📋 Recent Trades                                       │
│ BTC  | BUY  | +2.3% | 🟢 Aligned with Hammer         │
│ ETH  | SELL | -1.1% | 🔴 Revenge trade detected       │
└────────────────────────────────────────────────────────┘
```

---

## 🔧 Xử Lý Kỹ Thuật

### Tech Stack
- **Framework**: React + Vite
- **Charts**: TradingView Lightweight Charts
- **Styling**: CSS with dark mode
- **State**: React Query
- **WebSocket**: Native WS for alerts

### Project Structure
```
frontend/
├── src/
│   ├── App.jsx
│   ├── index.css
│   ├── pages/
│   │   ├── Dashboard.jsx
│   │   ├── TradeJournal.jsx
│   │   └── Analytics.jsx
│   ├── components/
│   │   ├── TradeForm.jsx
│   │   ├── TradeTable.jsx
│   │   ├── AlertFeed.jsx
│   │   ├── PnLChart.jsx
│   │   └── BehavioralHeatmap.jsx
│   └── hooks/
│       ├── useAlerts.js
│       └── useTrades.js
└── package.json
```

### Key Components

#### Dashboard
```jsx
export function Dashboard() {
  const { data: stats } = useQuery('stats', fetchStats);
  const { alerts } = useAlerts();
  
  return (
    <div className="dashboard">
      <StatsCards stats={stats} />
      <PnLChart />
      <AlertFeed alerts={alerts} />
      <RecentTrades limit={5} />
    </div>
  );
}
```

#### Real-time Alerts Hook
```jsx
export function useAlerts() {
  const [alerts, setAlerts] = useState([]);
  
  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/alerts/${userId}`);
    ws.onmessage = (e) => {
      const alert = JSON.parse(e.data);
      setAlerts(prev => [alert, ...prev]);
      showNotification(alert);
    };
    return () => ws.close();
  }, []);
  
  return { alerts };
}
```

### Design System
- Dark theme by default
- Glassmorphism cards
- Color coding: 🟢 profit, 🔴 loss, 🟡 warning
- Smooth animations
