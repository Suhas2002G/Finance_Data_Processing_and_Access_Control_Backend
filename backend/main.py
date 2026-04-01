# Standard library imports
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded

# Local application imports
from utils.logger import setup_logger
from models.db_models import *
from routes import auth_router, user_router, finance_router, dashboard_router
from core.config import setting
from services.rate_limiter import limiter, rate_limit_exceeded_handler


# Logger instance
logger = setup_logger()

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=setting.FRONTEND_URL,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Router Registration
app.include_router(auth_router, prefix="/auth")
app.include_router(user_router, prefix="/users")
app.include_router(finance_router, prefix="/finance")
app.include_router(dashboard_router, prefix="/dashboard")
# app.include_router(analyst_router, prefix="/relation_detection")
# app.include_router(viewer_router, prefix="/relation_detection")


@app.get("/")
def health_check():
    return {"status": "Finance Data API Running"}
