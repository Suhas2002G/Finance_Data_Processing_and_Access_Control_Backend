# Standard library imports
from contextlib import asynccontextmanager

# Third-party imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Local application imports
from utils.logger import setup_logger
from routes import auth_router, admin_router
from core.config import setting

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
print(setting.FRONTEND_URL)

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
app.include_router(admin_router, prefix="/admin")
# app.include_router(analyst_router, prefix="/relation_detection")
# app.include_router(viewer_router, prefix="/relation_detection")


@app.get("/")
def health_check():
    return {"status": "Finance Data API Running"}
