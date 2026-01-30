"""
Rate Limiting Configuration
Uses slowapi for rate limiting API endpoints
"""

from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request

from .config import settings


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key - uses IP address.
    Can be extended to use user ID for authenticated requests.
    """
    return get_remote_address(request)


# Create limiter with IP-based rate limiting
limiter = Limiter(
    key_func=get_rate_limit_key,
    default_limits=[f"{settings.RATE_LIMIT_PER_MINUTE}/minute"]
)
