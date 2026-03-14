from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    Base.metadata.create_all(bind=engine)

    with engine.connect() as conn:
        for table, col, col_type, default in [
            ("effects", "causal_mechanism", "TEXT", None),
            ("effects", "time_horizon", "TEXT", None),
            ("effects", "suggested_signals", "TEXT", None),
            ("equity_bets", "source", "TEXT", "'ai'"),
        ]:
            try:
                stmt = f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"
                if default is not None:
                    stmt += f" DEFAULT {default}"
                conn.execute(
                    __import__("sqlalchemy").text(stmt)
                )
                conn.commit()
            except Exception:
                pass
