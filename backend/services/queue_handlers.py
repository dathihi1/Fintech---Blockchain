"""
Queue Message Handlers
Handles different types of messages from the trade queue
"""

from typing import Dict, Any
import structlog

from .queue_service import TradeQueue

logger = structlog.get_logger()


async def handle_trade_created(payload: Dict[str, Any]):
    """
    Handle trade created event.
    Runs behavioral analysis and broadcasts alerts via WebSocket.

    Expected payload:
    {
        "trade_id": int,
        "user_id": str,
        "notes": str,
        "symbol": str,
        "side": str,
        "price_change_1h": float,
        "recent_loss_pct": float,
        "current_drawdown": float,
        "trades_last_hour": int
    }
    """
    from api.websocket import broadcast_alert, broadcast_trade_created
    from analyzers import get_active_analyzer

    trade_id = payload.get("trade_id")
    user_id = payload.get("user_id")
    notes = payload.get("notes", "")

    logger.info("Processing trade created", trade_id=trade_id, user_id=user_id)

    try:
        # Run behavioral analysis
        analyzer = get_active_analyzer()
        result = analyzer.analyze_simple(
            notes=notes,
            price_change_1h=payload.get("price_change_1h", 0.0),
            recent_loss_pct=payload.get("recent_loss_pct", 0.0),
            current_drawdown=payload.get("current_drawdown", 0.0),
            trades_last_hour=payload.get("trades_last_hour", 0)
        )

        # Broadcast alerts via WebSocket
        if result.alerts:
            for alert in result.alerts:
                await broadcast_alert(user_id, alert.to_dict(), trade_id)
                logger.info(
                    "Alert broadcasted",
                    trade_id=trade_id,
                    alert_type=alert.alert_type,
                    severity=alert.severity
                )

        # Broadcast trade created event
        trade_data = {
            "id": trade_id,
            "symbol": payload.get("symbol"),
            "side": payload.get("side"),
            "has_alerts": len(result.alerts) > 0,
            "risk_score": result.overall_risk_score
        }
        await broadcast_trade_created(user_id, trade_data)

        logger.info(
            "Trade processing complete",
            trade_id=trade_id,
            alerts_count=len(result.alerts),
            risk_score=result.overall_risk_score
        )

    except Exception as e:
        logger.error(
            "Error processing trade created",
            trade_id=trade_id,
            error=str(e)
        )
        raise


async def handle_trade_closed(payload: Dict[str, Any]):
    """
    Handle trade closed event.
    Updates passive analysis data and broadcasts closure.

    Expected payload:
    {
        "trade_id": int,
        "user_id": str,
        "pnl": float,
        "pnl_pct": float,
        "hold_duration_minutes": int
    }
    """
    from api.websocket import broadcast_trade_closed

    trade_id = payload.get("trade_id")
    user_id = payload.get("user_id")

    logger.info("Processing trade closed", trade_id=trade_id, user_id=user_id)

    try:
        # Broadcast trade closed event
        await broadcast_trade_closed(user_id, payload)

        logger.info(
            "Trade closure processed",
            trade_id=trade_id,
            pnl=payload.get("pnl"),
            pnl_pct=payload.get("pnl_pct")
        )

    except Exception as e:
        logger.error(
            "Error processing trade closed",
            trade_id=trade_id,
            error=str(e)
        )
        raise


async def handle_analyze_request(payload: Dict[str, Any]):
    """
    Handle analysis request without creating a trade.
    Used for quick behavioral checks.

    Expected payload:
    {
        "user_id": str,
        "notes": str,
        "price_change_1h": float,
        "recent_loss_pct": float,
        "current_drawdown": float,
        "trades_last_hour": int
    }
    """
    from api.websocket import broadcast_alert
    from analyzers import get_active_analyzer

    user_id = payload.get("user_id")
    notes = payload.get("notes", "")

    logger.info("Processing analyze request", user_id=user_id)

    try:
        analyzer = get_active_analyzer()
        result = analyzer.analyze_simple(
            notes=notes,
            price_change_1h=payload.get("price_change_1h", 0.0),
            recent_loss_pct=payload.get("recent_loss_pct", 0.0),
            current_drawdown=payload.get("current_drawdown", 0.0),
            trades_last_hour=payload.get("trades_last_hour", 0)
        )

        # Broadcast alerts if any
        if result.alerts and user_id:
            for alert in result.alerts:
                await broadcast_alert(user_id, alert.to_dict())

        logger.info(
            "Analysis request processed",
            user_id=user_id,
            alerts_count=len(result.alerts)
        )

    except Exception as e:
        logger.error(
            "Error processing analyze request",
            user_id=user_id,
            error=str(e)
        )
        raise


def register_handlers(queue: TradeQueue):
    """
    Register all message handlers with the queue.

    Args:
        queue: TradeQueue instance to register handlers with
    """
    queue.register_handler("trade_created", handle_trade_created)
    queue.register_handler("trade_closed", handle_trade_closed)
    queue.register_handler("analyze_request", handle_analyze_request)

    logger.info("Queue handlers registered")
