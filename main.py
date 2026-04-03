# Standard library imports
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException

# Third-party imports
from slowapi.errors import RateLimitExceeded

# Local application imports
from utils.logger import setup_logger
from models.db_models import *
from core.db import engine, Base
from routes import auth_router, user_router, finance_router, dashboard_router
from core.config import setting
from services.rate_limiter import limiter, rate_limit_exceeded_handler


# Logger instance
logger = setup_logger()

Base.metadata.create_all(bind=engine)

# Fastapi lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("[Startup] Application starting...")
    yield
    logger.info("[Shutdown] Application shutting down...")


# Fastapi App Initialization
app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter  # Attach limiter to app
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

# Router Registration
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/users")
app.include_router(finance_router, prefix="/finance")
app.include_router(dashboard_router, prefix="/dashboard")



@app.exception_handler(HTTPException)
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "message": exc.detail,
            "data": {},
            "error": None
        }
    )


@app.get("/")
def health_check():
    return {"status": "Finance Data API Running"}
