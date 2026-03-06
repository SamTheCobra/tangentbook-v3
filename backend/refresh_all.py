"""Force-refresh all feeds and recalculate all THI scores."""

import asyncio
import logging
import sys

sys.path.insert(0, ".")

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

from database import SessionLocal
from models import Thesis, DataFeed
from services.feed_refresh import refresh_thesis_feeds, refresh_macro_header


async def main():
    db = SessionLocal()
    try:
        # Print before state
        theses = db.query(Thesis).all()
        print("\n═══ BEFORE ═══")
        for t in theses:
            print(f"  {t.id:42s} THI={t.thi_score:5.1f}  ev={t.evidence_score:5.1f}  mom={t.momentum_score:5.1f}  dq={t.conviction_data_score:5.1f}")

        # Refresh macro header
        print("\n═══ REFRESHING MACRO HEADER ═══")
        await refresh_macro_header(db)

        # Refresh each thesis
        print("\n═══ REFRESHING ALL THESIS FEEDS ═══")
        for t in theses:
            print(f"\n--- {t.title} ---")
            try:
                await refresh_thesis_feeds(t.id, db)
                db.refresh(t)
                print(f"  THI: {t.thi_score:.1f}  evidence: {t.evidence_score:.1f}  momentum: {t.momentum_score:.1f}")
            except Exception as e:
                print(f"  ERROR: {e}")

        # Print feed summary
        print("\n═══ FEED SUMMARY ═══")
        feeds = db.query(DataFeed).order_by(DataFeed.thesis_id).all()
        print(f"{'FEED':<40s} {'SOURCE':<8s} {'RAW VALUE':>12s} {'SCORE':>6s} {'STATUS':<10s}")
        print("─" * 82)
        for f in feeds:
            name = f.name.replace("Fred ", "").replace("Gtrends ", "")[:38]
            raw = f"{f.raw_value:.1f}" if f.raw_value else "——"
            score = f"{f.normalized_score:.0f}" if f.normalized_score is not None else "——"
            print(f"{name:<40s} {f.source:<8s} {raw:>12s} {score:>6s} {f.status:<10s}")

        # Print after state
        print("\n═══ AFTER ═══")
        for t in db.query(Thesis).all():
            print(f"  {t.id:42s} THI={t.thi_score:5.1f}  ev={t.evidence_score:5.1f}  mom={t.momentum_score:5.1f}  dq={t.conviction_data_score:5.1f}")

    finally:
        db.close()


if __name__ == "__main__":
    asyncio.run(main())
