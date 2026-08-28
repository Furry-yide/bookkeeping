from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.models import Base

SQLALCHEMY_DATABASE_URL = "sqlite:///./cat_ledger.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    Base.metadata.create_all(bind=engine)
    _migrate_db()


def _migrate_db():
    """补齐历史字段：category_id 允许为空，并新增 transfer_to_id 列。"""
    with engine.begin() as conn:
        info = conn.execute(text("PRAGMA table_info(transactions)")).fetchall()
        cols = [r[1] for r in info]
        cat_notnull = [r for r in info if r[1] == "category_id"][0][3]
        if cat_notnull == 0 and "transfer_to_id" in cols:
            return
        conn.execute(text("""
            CREATE TABLE transactions_new (
                id INTEGER PRIMARY KEY,
                amount FLOAT NOT NULL,
                type VARCHAR(10) NOT NULL,
                category_id INTEGER,
                payment_source_id INTEGER,
                transfer_to_id INTEGER,
                note TEXT,
                occurred_at DATETIME NOT NULL
            )
        """))
        existing = ", ".join(
            c for c in ["id", "amount", "type", "category_id", "payment_source_id", "note", "occurred_at"]
            if c in cols
        )
        conn.execute(text(f"INSERT INTO transactions_new ({existing}) SELECT {existing} FROM transactions"))
        conn.execute(text("DROP TABLE transactions"))
        conn.execute(text("ALTER TABLE transactions_new RENAME TO transactions"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
