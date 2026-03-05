import asyncio
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import validate_env, FEED_REFRESH_INTERVAL_MINUTES
from database import init_db, SessionLocal
from routers import theses, feeds
from seed import seed_database
from services.feed_refresh import refresh_all_theses

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)

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

scheduler = AsyncIOScheduler()


async def scheduled_refresh():
    """Background job to refresh all feeds."""
    db = SessionLocal()
    try:
        await refresh_all_theses(db)
    except Exception as e:
        logger.error(f"Scheduled refresh error: {e}")
    finally:
        db.close()


@app.on_event("startup")
async def startup():
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

    # Start background scheduler
    scheduler.add_job(
        scheduled_refresh,
        "interval",
        minutes=FEED_REFRESH_INTERVAL_MINUTES,
        id="feed_refresh",
        replace_existing=True,
    )
    scheduler.start()
    logger.info(f"Feed refresh scheduler started (interval: {FEED_REFRESH_INTERVAL_MINUTES}min)")


@app.on_event("shutdown")
async def shutdown():
    scheduler.shutdown(wait=False)


@app.get("/api/health")
def health():
    return {"status": "ok"}
