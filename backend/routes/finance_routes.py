from fastapi import APIRouter, Request
from services.rate_limiter import limiter
from loguru import logger

finance_router = APIRouter(tags=['Finance'])

# APIs:
# POST /transactions
# GET /transactions (filtering)
# PUT /transactions/{id}
# DELETE /transactions/{id}

@finance_router.get("/transactions")
@limiter.limit("5/minute")
async def fecth_all_transactions(request: Request):
    pass

@finance_router.post("/transactions/{transaction_id}")
@limiter.limit("5/minute")
async def get_transactions(request: Request):
    pass

@finance_router.post("/transactions")
@limiter.limit("5/minute")
async def create_transactions(request: Request):
    pass

@finance_router.put("/transactions/{transaction_id}")
@limiter.limit("5/minute")
async def get_transactions(request: Request):
    pass

@finance_router.delete("/transactions/{transaction_id}")
@limiter.limit("5/minute")
async def get_transactions(request: Request):
    pass