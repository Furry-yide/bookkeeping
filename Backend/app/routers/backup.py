from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app import models
from app.routers.auth import require_auth
from app.routers import stats as stats_router

router = APIRouter(prefix="/api/backup", tags=["backup"])

FIELDS = {
    models.Category: ["id", "name", "type", "icon"],
    models.PaymentSource: ["id", "name", "icon"],
    models.Transaction: ["id", "amount", "type", "category_id", "payment_source_id", "note", "occurred_at"],
    models.Budget: ["id", "month", "category_id", "limit_amount", "note"],
}


def _dump(model, db):
    cols = FIELDS[model]
    return [{c: getattr(o, c) for c in cols} for o in db.query(model).all()]


@router.get("/export")
def export_data(db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    months = [
        r[0]
        for r in db.query(
            func.strftime("%Y-%m", models.Transaction.occurred_at)
        ).distinct().all()
        if r[0]
    ]
    monthly_stats = [
        stats_router.summary(month=m, db=db).model_dump() for m in sorted(months)
    ]
    return {
        "version": 1,
        "exported_at": datetime.utcnow().isoformat(),
        "categories": _dump(models.Category, db),
        "payment_sources": _dump(models.PaymentSource, db),
        "transactions": _dump(models.Transaction, db),
        "budgets": _dump(models.Budget, db),
        "monthly_stats": monthly_stats,
        "source_balances": stats_router.source_balances(db=db),
    }


@router.post("/import")
def import_data(payload: dict, db: Session = Depends(get_db), _auth: str = Depends(require_auth)):
    # 全量覆盖式迁移：先清空四张业务表，再按 JSON 写入
    db.query(models.Transaction).delete()
    db.query(models.Budget).delete()
    db.query(models.Category).delete()
    db.query(models.PaymentSource).delete()
    db.commit()

    for c in payload.get("categories", []) or []:
        db.add(models.Category(
            id=c["id"], name=c["name"], type=c["type"], icon=c.get("icon", "💰")
        ))
    for s in payload.get("payment_sources", []) or []:
        db.add(models.PaymentSource(id=s["id"], name=s["name"], icon=s.get("icon", "💳")))
    for t in payload.get("transactions", []) or []:
        occ = t.get("occurred_at")
        if isinstance(occ, str):
            occ = datetime.fromisoformat(occ)
        db.add(models.Transaction(
            id=t["id"], amount=t["amount"], type=t["type"],
            category_id=t["category_id"],
            payment_source_id=t.get("payment_source_id"),
            note=t.get("note", ""), occurred_at=occ,
        ))
    for b in payload.get("budgets", []) or []:
        db.add(models.Budget(
            id=b["id"], month=b["month"],
            category_id=b.get("category_id"),
            limit_amount=b["limit_amount"], note=b.get("note", ""),
        ))
    db.commit()

    return {
        "ok": True,
        "imported": {
            "categories": len(payload.get("categories", []) or []),
            "payment_sources": len(payload.get("payment_sources", []) or []),
            "transactions": len(payload.get("transactions", []) or []),
            "budgets": len(payload.get("budgets", []) or []),
        },
    }
