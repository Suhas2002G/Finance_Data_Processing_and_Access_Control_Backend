from fastapi import APIRouter
from loguru import logger

auth_router = APIRouter(prefix='/auth')

@auth_router.get("/orders")
async def get_orders():
    logger.debug("Fetching orders")
    return ["Order1", "Order2"]