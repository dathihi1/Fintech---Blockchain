"""
WebSocket endpoints for real-time alerts
Provides real-time notification when behavioral alerts are detected
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, List
import json
import asyncio

router = APIRouter()


class ConnectionManager:
    """
    Manages WebSocket connections for real-time alerts.
    Tracks active connections per user for broadcasting alerts.
    """
    
    def __init__(self):
        # user_id -> list of active WebSocket connections
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        """Accept a new WebSocket connection for a user"""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        """Remove a WebSocket connection"""
        if user_id in self.active_connections:
            if websocket in self.active_connections[user_id]:
                self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
    
    async def send_personal_message(self, message: dict, user_id: str):
        """Send a message to all connections of a specific user"""
        if user_id in self.active_connections:
            dead_connections = []
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    dead_connections.append(connection)
            
            # Clean up dead connections
            for conn in dead_connections:
                self.disconnect(conn, user_id)
    
    async def broadcast(self, message: dict):
        """Broadcast a message to all connected users"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)
    
    def get_connection_count(self, user_id: str = None) -> int:
        """Get number of active connections"""
        if user_id:
            return len(self.active_connections.get(user_id, []))
        return sum(len(conns) for conns in self.active_connections.values())
    
    def is_user_connected(self, user_id: str) -> bool:
        """Check if a user has any active connections"""
        return user_id in self.active_connections and len(self.active_connections[user_id]) > 0


# Singleton manager instance
manager = ConnectionManager()


def get_websocket_manager() -> ConnectionManager:
    """Get the WebSocket manager singleton"""
    return manager


# ============ WebSocket Endpoints ============

@router.websocket("/ws/alerts/{user_id}")
async def websocket_alerts(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time behavioral alerts.
    
    Clients connect to receive alerts when:
    - A new trade is created with behavioral warnings
    - FOMO, Revenge Trading, or Tilt is detected
    - Critical alerts require immediate attention
    
    Message format:
    {
        "type": "alert",
        "alert": {
            "alert_type": "FOMO",
            "severity": "HIGH",
            "score": 75,
            "reasons": [...],
            "recommendation": "..."
        },
        "trade_id": 123,
        "timestamp": "2024-01-25T10:30:00"
    }
    """
    await manager.connect(websocket, user_id)
    
    # Send welcome message
    await websocket.send_json({
        "type": "connected",
        "message": f"Connected to alerts for user: {user_id}",
        "active_connections": manager.get_connection_count(user_id)
    })
    
    try:
        while True:
            # Keep connection alive and handle incoming messages
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0  # 30 second timeout for ping/pong
                )
                
                # Handle ping/pong for connection keepalive
                if data == "ping":
                    await websocket.send_text("pong")
                elif data == "status":
                    await websocket.send_json({
                        "type": "status",
                        "user_id": user_id,
                        "active_connections": manager.get_connection_count(user_id)
                    })
                    
            except asyncio.TimeoutError:
                # Send ping to check if connection is alive
                try:
                    await websocket.send_text("ping")
                except Exception:
                    break
                    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        manager.disconnect(websocket, user_id)


@router.websocket("/ws/trades/{user_id}")
async def websocket_trades(websocket: WebSocket, user_id: str):
    """
    WebSocket endpoint for real-time trade updates.
    
    Clients receive updates when:
    - New trade is created
    - Trade is closed/updated
    - P&L changes
    """
    await manager.connect(websocket, user_id)
    
    await websocket.send_json({
        "type": "connected",
        "channel": "trades",
        "user_id": user_id
    })
    
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception:
        manager.disconnect(websocket, user_id)


# ============ Helper Functions for Broadcasting ============

async def broadcast_alert(user_id: str, alert: dict, trade_id: int = None):
    """
    Broadcast a behavioral alert to a user.
    Called from trades.py when creating a trade with alerts.
    """
    from datetime import datetime
    
    message = {
        "type": "alert",
        "alert": alert,
        "trade_id": trade_id,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(message, user_id)


async def broadcast_trade_created(user_id: str, trade: dict):
    """Broadcast when a new trade is created"""
    from datetime import datetime
    
    message = {
        "type": "trade_created",
        "trade": trade,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(message, user_id)


async def broadcast_trade_closed(user_id: str, trade: dict):
    """Broadcast when a trade is closed"""
    from datetime import datetime
    
    message = {
        "type": "trade_closed",
        "trade": trade,
        "timestamp": datetime.utcnow().isoformat()
    }
    
    await manager.send_personal_message(message, user_id)
