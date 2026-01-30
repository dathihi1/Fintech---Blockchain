"""
Smart Trading Journal API
AI-powered trading journal with behavioral analysis
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import structlog
import asyncio
import json

from core.config import settings
from core.rate_limit import limiter
from models import init_db
from api import trades_router, nlp_router, alerts_router, analysis_router, symbols_router, auth_router
from services.queue_service import get_trade_queue
from services.queue_handlers import register_handlers

# Setup logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer()
    ],
    wrapper_class=structlog.stdlib.BoundLogger,
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown"""
    # Startup
    logger.info("Starting up Smart Trading Journal API...")

    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")

    # Skip NLP model pre-loading to speed up startup (will lazy load on first use)
    logger.info("NLP engine will be lazy loaded on first use")

    # Start trade queue
    try:
        queue = get_trade_queue()
        register_handlers(queue)
        await queue.start(num_workers=3)
        logger.info("Trade queue started")
    except Exception as e:
        logger.warning(f"Trade queue initialization skipped: {e}")

    logger.info("Startup complete!")

    yield  # Application runs here

    # Shutdown
    logger.info("Shutting down Smart Trading Journal API...")

    # Stop trade queue
    try:
        queue = get_trade_queue()
        await queue.stop()
        logger.info("Trade queue stopped")
    except Exception as e:
        logger.warning(f"Trade queue shutdown error: {e}")

    logger.info("Shutdown complete!")


# Create FastAPI app
app = FastAPI(
    title="Smart Trading Journal API",
    description="""
## AI-powered Trading Journal with Behavioral Analysis

### Features:
- **NLP Analysis**: Analyze trading notes for sentiment and emotions
- **FOMO Detection**: Detect Fear of Missing Out behavior
- **Revenge Trading Detection**: Identify emotional revenge trading
- **Tilt Detection**: Detect when trader is tilted/emotional
- **Real-time Alerts**: Get warnings before making bad trades
- **JWT Authentication**: Secure user authentication

### Supported Emotions:
- FOMO, FEAR, GREED, REVENGE (negative)
- RATIONAL, CONFIDENT, DISCIPLINE (positive)
    """,
    version="1.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware - configure CORS_ORIGINS in environment for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)


# ============ Include Routers ============

app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(trades_router, prefix=settings.API_PREFIX)
app.include_router(nlp_router, prefix=settings.API_PREFIX)
app.include_router(alerts_router, prefix=settings.API_PREFIX)
app.include_router(analysis_router, prefix=settings.API_PREFIX)
app.include_router(symbols_router, prefix=settings.API_PREFIX)


# ============ WebSocket Connections ============

class ConnectionManager:
    """Manage WebSocket connections"""
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket connected for user {user_id}")
    
    def disconnect(self, websocket: WebSocket, user_id: str):
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket disconnected for user {user_id}")
    
    async def send_alert(self, user_id: str, alert: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(alert)
                except Exception as e:
                    logger.error(f"Failed to send WebSocket message: {e}")
    
    async def broadcast(self, message: dict):
        for user_id, connections in self.active_connections.items():
            for connection in connections:
                try:
                    await connection.send_json(message)
                except Exception:
                    pass

manager = ConnectionManager()


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str, token: str = None):
    """
    WebSocket endpoint for real-time alerts.

    Connect: ws://localhost:8000/ws/{user_id}?token={jwt_token}

    Requires authentication via token query parameter.
    Receives real-time alerts when behavioral issues are detected.
    """
    from core.auth import verify_token

    # Validate authentication
    if not token:
        await websocket.close(code=4001, reason="Missing authentication token")
        return

    payload = verify_token(token)
    if not payload:
        await websocket.close(code=4003, reason="Invalid token")
        return

    # Verify token belongs to the requested user
    token_user_id = payload.get("sub")
    if token_user_id != user_id:
        await websocket.close(code=4003, reason="Token does not match user ID")
        return

    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive and receive messages
            data = await websocket.receive_text()

            # Echo back or process commands
            try:
                message = json.loads(data)
                if message.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                elif message.get("type") == "analyze":
                    # Quick analysis request via WebSocket
                    from analyzers import get_active_analyzer
                    analyzer = get_active_analyzer()
                    result = analyzer.analyze_simple(
                        notes=message.get("notes"),
                        trades_last_hour=message.get("trades_last_hour", 0)
                    )
                    await websocket.send_json({
                        "type": "analysis_result",
                        "data": result.to_dict()
                    })
            except json.JSONDecodeError:
                await websocket.send_json({"error": "Invalid JSON"})

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


# ============ Root Endpoints ============

@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "Smart Trading Journal API",
        "version": "1.1.0",
        "docs": "/docs",
        "health": "/health",
        "websocket": "/ws/{user_id}",
        "endpoints": {
            "auth": f"{settings.API_PREFIX}/auth",
            "trades": f"{settings.API_PREFIX}/trades",
            "nlp": f"{settings.API_PREFIX}/nlp",
            "alerts": f"{settings.API_PREFIX}/alerts",
            "analysis": f"{settings.API_PREFIX}/analysis"
        }
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "demo_mode": settings.DEMO_MODE,
        "nlp_model": settings.NLP_MODEL_NAME
    }


# ============ Run directly ============

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",  # Use string import to avoid multiprocessing issues
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False
    )
