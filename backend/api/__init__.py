from .auth import router as auth_router
from .trades import router as trades_router
from .nlp import router as nlp_router
from .alerts import router as alerts_router
from .analysis import router as analysis_router
from .websocket import router as websocket_router, get_websocket_manager
from .symbols import router as symbols_router

__all__ = [
    "auth_router",
    "trades_router",
    "nlp_router",
    "alerts_router",
    "analysis_router",
    "websocket_router",
    "get_websocket_manager",
    "symbols_router"
]

