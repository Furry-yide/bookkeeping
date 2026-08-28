from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.routers import transactions, categories, budgets, stats

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


@app.on_event("startup")
def on_startup():
    init_db()
    _seed_default_categories()


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


@app.get("/")
def root():
    return {"msg": "小猫的账本 API 运行中"}
