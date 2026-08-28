from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, case

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/stats", tags=["stats"])


@router.get("/summary", response_model=schemas.StatsSummary)
def summary(month: str = Query(..., description="YYYY-MM"), db: Session = Depends(get_db)):
    q = db.query(models.Transaction).filter(
        func.strftime("%Y-%m", models.Transaction.occurred_at) == month
    )
    income = q.filter(models.Transaction.type == "income").with_entities(
        func.coalesce(func.sum(models.Transaction.amount), 0)
    ).scalar()
    expense = q.filter(models.Transaction.type == "expense").with_entities(
        func.coalesce(func.sum(models.Transaction.amount), 0)
    ).scalar()

    rows = (
        db.query(
            models.Category.id,
            models.Category.name,
            models.Category.icon,
            func.coalesce(func.sum(models.Transaction.amount), 0).label("total"),
        )
        .join(models.Transaction, models.Transaction.category_id == models.Category.id)
        .filter(
            func.strftime("%Y-%m", models.Transaction.occurred_at) == month,
            models.Transaction.type == "expense",
        )
        .group_by(models.Category.id)
        .order_by(func.sum(models.Transaction.amount).desc())
        .all()
    )
    by_category = [
        {"id": r.id, "name": r.name, "icon": r.icon, "total": float(r.total)}
        for r in rows
    ]
    return schemas.StatsSummary(
        month=month,
        total_income=float(income),
        total_expense=float(expense),
        balance=float(income) - float(expense),
        by_category=by_category,
    )


@router.get("/budget-progress")
def budget_progress(month: str = Query(..., description="YYYY-MM"), db: Session = Depends(get_db)):
    budget = db.query(models.Budget).filter(models.Budget.month == month).first()
    if not budget:
        return {"has_budget": False}
    spent = (
        db.query(func.coalesce(func.sum(models.Transaction.amount), 0))
        .filter(
            models.Transaction.type == "expense",
            func.strftime("%Y-%m", models.Transaction.occurred_at) == month,
        )
        .scalar()
    )
    spent = float(spent)
    limit = float(budget.limit_amount)
    return {
        "has_budget": True,
        "month": month,
        "limit_amount": limit,
        "spent": spent,
        "remaining": limit - spent,
        "percent": round(spent / limit * 100, 1) if limit else 0,
        "over": spent > limit,
    }


@router.get("/source-balances")
def source_balances(db: Session = Depends(get_db)):
    result = []
    for s in db.query(models.PaymentSource).order_by(models.PaymentSource.id).all():
        income = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
            models.Transaction.type == "income",
            models.Transaction.payment_source_id == s.id,
        ).scalar()
        expense = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
            models.Transaction.type == "expense",
            models.Transaction.payment_source_id == s.id,
        ).scalar()
        # 转账：转入视为收入，转出（payment_source_id）视为支出
        transfer_in = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
            models.Transaction.type == "transfer",
            models.Transaction.transfer_to_id == s.id,
        ).scalar()
        transfer_out = db.query(func.coalesce(func.sum(models.Transaction.amount), 0)).filter(
            models.Transaction.type == "transfer",
            models.Transaction.payment_source_id == s.id,
        ).scalar()
        inc = float(income) + float(transfer_in)
        exp = float(expense) + float(transfer_out)
        result.append({
            "id": s.id,
            "name": s.name,
            "icon": s.icon,
            "income": inc,
            "expense": exp,
            "balance": inc - exp,
        })
    return result
