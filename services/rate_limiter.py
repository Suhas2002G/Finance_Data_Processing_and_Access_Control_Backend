from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse
from fastapi import Request

# Limiter instance
limiter = Limiter(key_func=get_remote_address)  # API level Rate Limiter

# Custom handler
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={
            "message": "Too many requests",
            "detail": "Rate limit exceeded. Please try again later."
        },
    )