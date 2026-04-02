from fastapi import APIRouter, Depends, HTTPException, Response, Request, status
from sqlalchemy.orm import Session
from loguru import logger

from core.db import get_db
from core.config import setting
from models.db_models import User
from models.pydantic_schemas import CreateUser, LoginRequest
from utils.response_generator import success_response, error_response
from services.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token
)

auth_router = APIRouter(tags=["Authentication"])

# -------------------------
# REGISTER
# -------------------------
@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: CreateUser, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(User).filter(User.email == payload.email).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role="viewer"
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return success_response("User created successfully")

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Register Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=error_response("Something went wrong", str(e))
        )


# -------------------------
# LOGIN
# -------------------------
@auth_router.post("/login", status_code=status.HTTP_200_OK)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == payload.email).first()

        if not user or not verify_password(payload.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        access_token = create_access_token({
            "user_id": user.id,
            "role": user.role
        })

        refresh_token = create_refresh_token({
            "user_id": user.id
        })

        # Cookies
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=setting.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        logger.info(f"User {user.email} logged in")

        return success_response("Login successful")

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Login Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=error_response("Something went wrong", str(e))
        )


# -------------------------
# REFRESH TOKEN
# -------------------------
@auth_router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_token(request: Request, response: Response):
    try:
        token = request.cookies.get("refresh_token")

        if not token:
            raise HTTPException(status_code=401, detail="Refresh token missing")

        payload = decode_token(token, is_refresh=True)

        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        new_access_token = create_access_token({
            "user_id": payload["user_id"]
        })

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=False,
            samesite="lax",
            max_age=setting.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )

        return success_response("Access token refreshed")

    except HTTPException as e:
        raise e

    except Exception as e:
        logger.error(f"Refresh Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=error_response("Something went wrong", str(e))
        )


# -------------------------
# LOGOUT
# -------------------------
@auth_router.post("/logout", status_code=status.HTTP_200_OK)
def logout(response: Response):
    try:
        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return success_response("Logged out successfully")

    except Exception as e:
        logger.error(f"Logout Error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=error_response("Something went wrong", str(e))
        )