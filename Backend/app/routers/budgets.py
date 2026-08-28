from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/api/budgets", tags=["budgets"])


@router.get("", response_model=list[schemas.BudgetOut])
def list_budgets(db: Session = Depends(get_db)):
    return db.query(models.Budget).order_by(models.Budget.month.desc()).all()


@router.post("", response_model=schemas.BudgetOut)
def create_budget(payload: schemas.BudgetCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Budget).filter(models.Budget.month == payload.month).first()
    if existing:
        raise HTTPException(400, "budget for this month already exists")
    obj = models.Budget(**payload.model_dump())
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@router.put("/{budget_id}", response_model=schemas.BudgetOut)
def update_budget(budget_id: int, payload: schemas.BudgetCreate, db: Session = Depends(get_db)):
    obj = db.get(models.Budget, budget_id)
    if not obj:
        raise HTTPException(404, "budget not found")
    for k, v in payload.model_dump().items():
        setattr(obj, k, v)
    db.commit()
    db.refresh(obj)
    return obj


@router.delete("/{budget_id}")
def delete_budget(budget_id: int, db: Session = Depends(get_db)):
    obj = db.get(models.Budget, budget_id)
    if not obj:
        raise HTTPException(404, "budget not found")
    db.delete(obj)
    db.commit()
    return {"ok": True}
