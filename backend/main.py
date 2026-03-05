from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import validate_env
from database import init_db, SessionLocal
from routers import theses, feeds
from seed import seed_database

validate_env()

app = FastAPI(title="TangentBook v3", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["Content-Type"],
)

app.include_router(theses.router)
app.include_router(feeds.router)


@app.on_event("startup")
def startup():
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}
