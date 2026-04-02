from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from loguru import logger
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import require_permission
from models.db_models import Transaction, User
from models.pydantic_schemas import TransactionCreate, TransactionUpdate
from services.rate_limiter import limiter
from utils.response_generator import error_response, success_response
from utils.roles import Permission


finance_router = APIRouter(tags=["Finance"])


@finance_router.get("/transactions")
@limiter.limit("5/minute")
async def fetch_all_transactions(
    request: Request,
    category: str | None = Query(default=None),
    transaction_type: str | None = Query(default=None, alias="type"),
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    current_user: User = Depends(require_permission(Permission.READ_TRANSACTIONS)),
    db: Session = Depends(get_db),
):
    try:
        query = db.query(Transaction)

        if category:
            query = query.filter(Transaction.category == category)
        if transaction_type:
            query = query.filter(Transaction.type == transaction_type)
        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = (
            query.order_by(Transaction.date.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

        return success_response(
            "Transactions fetched successfully",
            {
                "items": [serialize_transaction(transaction) for transaction in transactions],
                "filters": {
                    "category": category,
                    "type": transaction_type,
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                    "skip": skip,
                    "limit": limit,
                },
                "requested_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        logger.error(f"Fetch transactions error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to fetch transactions", str(exc)),
        ) from exc


@finance_router.get("/transactions/{transaction_id}")
@limiter.limit("5/minute")
async def get_transaction(
    request: Request,
    transaction_id: int,
    current_user: User = Depends(require_permission(Permission.READ_TRANSACTIONS)),
    db: Session = Depends(get_db),
):
    try:
        transaction = (
            db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        return success_response(
            "Transaction fetched successfully",
            {
                "transaction": serialize_transaction(transaction),
                "requested_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        logger.error(f"Get transaction error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to fetch transaction", str(exc)),
        ) from exc


@finance_router.post("/transactions", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_transaction(
    request: Request,
    payload: TransactionCreate,
    current_user: User = Depends(require_permission(Permission.CREATE_TRANSACTION)),
    db: Session = Depends(get_db),
):
    try:
        target_user_id = current_user.id
        user = db.query(User).filter(User.id == target_user_id).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target user not found",
            )

        transaction = Transaction(
            user_id=target_user_id,
            amount=payload.amount,
            type=payload.type,
            category=payload.category,
            note=payload.note,
            date=payload.date or datetime.now(timezone.utc),
        )

        db.add(transaction)
        db.commit()
        db.refresh(transaction)

        return success_response(
            "Transaction created successfully",
            {"transaction": serialize_transaction(transaction)},
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        db.rollback()
        logger.error(f"Create transaction error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to create transaction", str(exc)),
        ) from exc


@finance_router.put("/transactions/{transaction_id}")
@limiter.limit("5/minute")
async def update_transaction(
    request: Request,
    transaction_id: int,
    payload: TransactionUpdate,
    current_user: User = Depends(require_permission(Permission.UPDATE_TRANSACTION)),
    db: Session = Depends(get_db),
):
    try:
        transaction = (
            db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        updates = payload.model_dump(exclude_unset=True)
        target_user_id = updates.pop("user_id", None)

        if target_user_id is not None:
            user = db.query(User).filter(User.id == target_user_id).first()
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Target user not found",
                )
            transaction.user_id = target_user_id

        for field, value in updates.items():
            setattr(transaction, field, value)

        db.commit()
        db.refresh(transaction)

        return success_response(
            "Transaction updated successfully",
            {
                "transaction": serialize_transaction(transaction),
                "updated_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        db.rollback()
        logger.error(f"Update transaction error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to update transaction", str(exc)),
        ) from exc


@finance_router.delete("/transactions/{transaction_id}")
@limiter.limit("5/minute")
async def delete_transaction(
    request: Request,
    transaction_id: int,
    current_user: User = Depends(require_permission(Permission.DELETE_TRANSACTION)),
    db: Session = Depends(get_db),
):
    try:
        transaction = (
            db.query(Transaction)
            .filter(Transaction.id == transaction_id)
            .first()
        )

        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        deleted_transaction = serialize_transaction(transaction)
        db.delete(transaction)
        db.commit()

        return success_response(
            "Transaction deleted successfully",
            {
                "transaction": deleted_transaction,
                "deleted_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        db.rollback()
        logger.error(f"Delete transaction error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to delete transaction", str(exc)),
        ) from exc


def serialize_transaction(transaction: Transaction) -> dict:
    return {
        "id": transaction.id,
        "user_id": transaction.user_id,
        "amount": transaction.amount,
        "type": transaction.type,
        "category": transaction.category,
        "note": transaction.note,
        "date": transaction.date.isoformat() if transaction.date else None,
        "created_at": transaction.created_at.isoformat() if transaction.created_at else None,
    }
