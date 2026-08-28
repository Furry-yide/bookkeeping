from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app import models
from app.routers import transactions, categories, budgets, stats, paymentsources, auth, backup

app = FastAPI(title="小猫的账本 API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(categories.router)
app.include_router(transactions.router)
app.include_router(budgets.router)
app.include_router(stats.router)
app.include_router(paymentsources.router)
app.include_router(auth.router)
app.include_router(backup.router)


@app.on_event("startup")
def on_startup():
    init_db()
    _seed_default_categories()
    _seed_default_payment_sources()
    _seed_default_user()


def _seed_default_user():
    from app.database import SessionLocal
    from app import models
    from app.security import hash_password

    db = SessionLocal()
    try:
        if db.query(models.User).filter(models.User.username == "Furry-yide").count() == 0:
            db.add(models.User(
                username="Furry-yide",
                password_hash=hash_password("Dede200822"),
            ))
            db.commit()
    finally:
        db.close()


def _seed_default_categories():
    from app.database import SessionLocal
    from app import models

    db = SessionLocal()
    try:
        if db.query(models.Category).count() == 0:
            defaults = [
                ("餐饮", "expense", "🍚"),
                ("交通", "expense", "🚌"),
                ("购物", "expense", "🛍️"),
                ("居住", "expense", "🏠"),
                ("娱乐", "expense", "🎮"),
                ("医疗", "expense", "💊"),
                ("工资", "income", "💼"),
                ("理财", "income", "📈"),
                ("其他收入", "income", "✨"),
            ]
            for name, t, icon in defaults:
                db.add(models.Category(name=name, type=t, icon=icon))
            db.commit()
    finally:
        db.close()


def _seed_default_payment_sources():
    from app.database import SessionLocal

    db = SessionLocal()
    try:
        if db.query(models.PaymentSource).count() == 0:
            defaults = [
                ("微信支付", "💚"),
                ("支付宝", "🔵"),
                ("银行卡", "💳"),
                ("现金", "💵"),
                ("其他", "🪙"),
            ]
            for name, icon in defaults:
                db.add(models.PaymentSource(name=name, icon=icon))
            db.commit()
    finally:
        db.close()


@app.get("/")
def root():
    return {"msg": "小猫的账本 API 运行中"}
