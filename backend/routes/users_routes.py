from fastapi import APIRouter, Request
from services.rate_limiter import limiter
from loguru import logger

user_router = APIRouter(tags=['Users'])


@user_router.get("/")
@limiter.limit("5/minute")
async def get_users(request: Request):
    return {"users": ["Suhas", "Admin"]}