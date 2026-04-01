from fastapi import APIRouter, Request
from services.rate_limiter import limiter
from loguru import logger

dashboard_router = APIRouter(tags=['Dashboard'])


@dashboard_router.get("/")
@limiter.limit("5/minute")
async def get_users(request: Request):
    return {"users": ["Suhas", "Admin"]}