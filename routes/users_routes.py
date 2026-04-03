from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import get_current_user, require_permission
from models.db_models import User
from models.pydantic_schemas import AdminCreateUser, UserUpdate
from services.rate_limiter import limiter
from services.security import hash_password
from utils.response_generator import error_response, success_response
from utils.roles import Permission, Role


user_router = APIRouter(tags=["Users"])


@user_router.get("/me", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_authenticated_user(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    return success_response(
        message="Authenticated user fetched successfully",
        data={"user": serialize_user(current_user)},
    )


@user_router.get("/", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_users(
    request: Request,
    role: Role | None = Query(default=None),
    is_active: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(User)

        if role is not None:
            query = query.filter(User.role == role.value)
        if is_active is not None:
            query = query.filter(User.is_active == is_active)

        users = (
            query.order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return success_response(
            message="Users fetched successfully",
            data={
                "items": [serialize_user(user) for user in users],
                "filters": {
                    "role": role.value if role else None,
                    "is_active": is_active,
                    "skip": skip,
                    "limit": limit,
                },
                "requested_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        logger.error(f"Get users error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to fetch users", str(exc)),
        ) from exc


@user_router.get("/{user_id}", status_code=status.HTTP_200_OK)
@limiter.limit("10/minute")
async def get_user_by_id(
    request: Request,
    user_id: int,
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        return success_response(
            message="User fetched successfully",
            data={
                "user": serialize_user(user),
                "requested_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        logger.error(f"Get user error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to fetch user", str(exc)),
        ) from exc


@user_router.post("/", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_user_by_admin(
    request: Request,
    payload: AdminCreateUser,
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    try:
        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists",
            )

        user = User(
            name=payload.name,
            email=payload.email,
            password_hash=hash_password(payload.password),
            role=payload.role.value,
            is_active=payload.is_active,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return success_response(
            message="User created successfully",
            data={
                "user": serialize_user(user),
                "created_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        db.rollback()
        logger.error(f"Create user error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to create user", str(exc)),
        ) from exc


@user_router.patch("/{user_id}", status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def update_user(
    request: Request,
    user_id: int,
    payload: UserUpdate,
    current_user: User = Depends(require_permission(Permission.MANAGE_USERS)),
    db: Session = Depends(get_db),
):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        updates = payload.model_dump(exclude_unset=True)

        if "role" in updates and user.id == current_user.id and updates["role"] != Role.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin users cannot remove their own admin role",
            )

        if updates.get("is_active") is False and user.id == current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Admin users cannot deactivate themselves",
            )

        if "password" in updates:
            user.password_hash = hash_password(updates.pop("password"))

        if "role" in updates:
            user.role = updates.pop("role").value

        for field, value in updates.items():
            setattr(user, field, value)

        db.commit()
        db.refresh(user)

        return success_response(
            message="User updated successfully",
            data={
                "user": serialize_user(user),
                "updated_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        db.rollback()
        logger.error(f"Update user error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to update user", str(exc)),
        ) from exc


def serialize_user(user: User) -> dict:
    return {
        "id": user.id,
        "name": user.name,
        "email": user.email,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
