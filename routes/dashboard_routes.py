from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from loguru import logger
from sqlalchemy import func
from sqlalchemy.orm import Session

from core.db import get_db
from core.deps import require_permission
from models.db_models import Transaction, User
from services.rate_limiter import limiter
from utils.response_generator import error_response, success_response
from utils.roles import Permission


dashboard_router = APIRouter(tags=["Dashboard"])


@dashboard_router.get("/")
@limiter.limit("5/minute")
async def get_dashboard_summary(
    request: Request,
    start_date: datetime | None = Query(default=None),
    end_date: datetime | None = Query(default=None),
    current_user: User = Depends(require_permission(Permission.READ_DASHBOARD)),
    db: Session = Depends(get_db),
):
    try:
        filtered_query = db.query(Transaction)

        if start_date:
            filtered_query = filtered_query.filter(Transaction.date >= start_date)
        if end_date:
            filtered_query = filtered_query.filter(Transaction.date <= end_date)

        income_total = (
            filtered_query
            .filter(Transaction.type == "income")
            .with_entities(func.coalesce(func.sum(Transaction.amount), 0.0))
            .scalar()
        )
        expense_total = (
            filtered_query
            .filter(Transaction.type == "expense")
            .with_entities(func.coalesce(func.sum(Transaction.amount), 0.0))
            .scalar()
        )

        category_totals = (
            filtered_query
            .with_entities(
                Transaction.category,
                Transaction.type,
                func.coalesce(func.sum(Transaction.amount), 0.0).label("total"),
            )
            .group_by(Transaction.category, Transaction.type)
            .order_by(func.sum(Transaction.amount).desc())
            .all()
        )

        recent_activity = (
            filtered_query
            .order_by(Transaction.date.desc())
            .limit(5)
            .all()
        )

        monthly_trends = (
            filtered_query
            .with_entities(
                func.strftime("%Y-%m", Transaction.date).label("month"),
                Transaction.type,
                func.coalesce(func.sum(Transaction.amount), 0.0).label("total"),
            )
            .group_by(func.strftime("%Y-%m", Transaction.date), Transaction.type)
            .order_by(func.strftime("%Y-%m", Transaction.date).asc())
            .all()
        )

        return success_response(
            "Dashboard summary fetched successfully",
            {
                "summary": {
                    "total_income": float(income_total or 0.0),
                    "total_expenses": float(expense_total or 0.0),
                    "net_balance": float((income_total or 0.0) - (expense_total or 0.0)),
                },
                "category_totals": [
                    {
                        "category": item.category,
                        "type": item.type,
                        "total": float(item.total),
                    }
                    for item in category_totals
                ],
                "recent_activity": [
                    serialize_transaction(transaction)
                    for transaction in recent_activity
                ],
                "monthly_trends": [
                    {
                        "month": item.month,
                        "type": item.type,
                        "total": float(item.total),
                    }
                    for item in monthly_trends
                ],
                "filters": {
                    "start_date": start_date.isoformat() if start_date else None,
                    "end_date": end_date.isoformat() if end_date else None,
                },
                "requested_by": current_user.email,
            },
        )
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        logger.error(f"Dashboard summary error: {str(exc)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_response("Failed to fetch dashboard summary", str(exc)),
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
