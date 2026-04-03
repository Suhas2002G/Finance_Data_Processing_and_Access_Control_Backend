from fastapi import APIRouter, Request, Depends
from loguru import logger
from sqlalchemy.orm import Session, load_only

from services.rate_limiter import limiter
from core.db import get_db
from models.db_models import User
from utils.response_generator import success_response, error_response

user_router = APIRouter(tags=['Users'])


@user_router.get("/")
@limiter.limit("5/minute")
async def get_users(request: Request, db: Session = Depends(get_db)):
    users = db.query(User).options(load_only(User.id, User.name, User.email, User.role, User.is_active)).all()
    return success_response(
        data=users,
        message='All users are fetched',
    )