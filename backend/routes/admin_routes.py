from fastapi import APIRouter
from loguru import logger

admin_router = APIRouter(tags=['Admin'])

@admin_router.get("/orders")
async def get_orders():
    logger.debug("Fetching orders")
    return ["Order1", "Order2"]