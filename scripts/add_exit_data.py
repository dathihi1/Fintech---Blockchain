"""
Quick script to add exit prices to existing trades for testing
"""
import requests
import json
from datetime import datetime, timedelta

API_BASE = "http://localhost:8000/api"

def get_trades():
    """Get all trades"""
    response = requests.get(f"{API_BASE}/trades/", params={"limit": 50})
    if response.status_code == 200:
        return response.json()
    return []

def update_trade(trade_id, data):
    """Update a trade"""
    response = requests.patch(f"{API_BASE}/trades/{trade_id}", json=data)
    return response.json() if response.status_code == 200 else None

def main():
    print("🔄 Updating trades with exit data for testing...")
    print()
    
    trades = get_trades()
    
    if not trades:
        print("❌ No trades found!")
        return
    
    print(f"📊 Found {len(trades)} trades")
    print()
    
    updated = 0
    for trade in trades:
        # Skip if already has exit data
        if trade.get('exit_price'):
            print(f"⏭️  Trade #{trade['id']} already has exit data")
            continue
        
        # Generate realistic exit data
        entry_price = trade['entry_price']
        side = trade['side']
        
        # Simulate some wins and some losses
        import random
        is_win = random.choice([True, True, False])  # 66% win rate
        
        if is_win:
            # Winning trade: 2-8% profit
            pnl_pct = random.uniform(2, 8)
        else:
            # Losing trade: 2-5% loss
            pnl_pct = random.uniform(-5, -2)
        
        # Calculate exit price based on side
        if side == 'long':
            exit_price = entry_price * (1 + pnl_pct / 100)
        else:
            exit_price = entry_price * (1 - pnl_pct / 100)
        
        # Calculate PnL
        quantity = trade['quantity']
        if side == 'long':
            pnl = (exit_price - entry_price) * quantity
        else:
            pnl = (entry_price - exit_price) * quantity
        
        # Calculate hold duration (1-24 hours)
        hold_minutes = random.randint(60, 1440)
        
        # Update trade
        update_data = {
            'exit_price': round(exit_price, 2),
            'pnl': round(pnl, 2),
            'pnl_pct': round(pnl_pct, 2),
            'hold_duration_minutes': hold_minutes,
            'status': 'closed'
        }
        
        result = update_trade(trade['id'], update_data)
        
        if result:
            emoji = "✅" if pnl > 0 else "❌"
            print(f"{emoji} Trade #{trade['id']} ({trade['symbol']}): {pnl_pct:+.2f}% | PnL: ${pnl:+.2f}")
            updated += 1
        else:
            print(f"⚠️  Failed to update Trade #{trade['id']}")
    
    print()
    print(f"✅ Updated {updated} trades!")
    print()
    print("📊 Testing analytics now...")
    print()
    
    # Test stats endpoint
    response = requests.get(f"{API_BASE}/analysis/stats")
    if response.status_code == 200:
        stats = response.json()
        print("📈 Trade Statistics:")
        print(f"   Total Trades: {stats['total_trades']}")
        print(f"   Closed Trades: {stats['closed_trades']}")
        print(f"   Win Rate: {stats['win_rate']*100:.1f}%")
        print(f"   Total PnL: ${stats['total_pnl']:+.2f}")
        print(f"   Avg PnL: {stats['avg_pnl_pct']:+.2f}%")
        print(f"   Best Trade: {stats['best_trade']:+.2f}%")
        print(f"   Worst Trade: {stats['worst_trade']:+.2f}%")
    else:
        print("⚠️  Failed to get stats")
    
    print()
    print("✅ Done! Refresh dashboard and analytics pages to see updated data.")

if __name__ == "__main__":
    main()
