"""Calculate EFS for all equity bets and STS for all startups."""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from database import SessionLocal, init_db
from models import EquityBet, StartupOpportunity, Thesis, Effect
from services.efs_service import calculate_efs, calculate_sts, THESIS_KEYWORDS


async def main():
    init_db()
    db = SessionLocal()

    print("=" * 100)
    print("EQUITY FIT SCORE — FULL CALCULATION")
    print("=" * 100)

    # Calculate EFS for all equity bets
    bets = db.query(EquityBet).all()
    print(f"\nProcessing {len(bets)} equity bets...\n")

    results = []
    for i, bet in enumerate(bets):
        # Determine thesis context
        thesis_id = bet.thesis_id
        thesis_title = ""
        if thesis_id:
            thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
            thesis_title = thesis.title[:20] if thesis else ""
        elif bet.effect_id:
            effect = db.query(Effect).filter(Effect.id == bet.effect_id).first()
            if effect:
                thesis_id = effect.thesis_id
                thesis = db.query(Thesis).filter(Thesis.id == thesis_id).first()
                thesis_title = thesis.title[:20] if thesis else ""

        if not thesis_id:
            continue

        keywords = THESIS_KEYWORDS.get(thesis_id, [])
        if not keywords and thesis:
            keywords = (thesis.tags or []) + thesis.title.lower().split()

        try:
            efs = await calculate_efs(bet, thesis_id, keywords, db)
            results.append({
                "ticker": bet.ticker,
                "thesis": thesis_title,
                "revenue": efs.revenue_alignment_score,
                "beta": efs.thesis_beta_score,
                "momentum": efs.momentum_alignment_score,
                "valuation": efs.valuation_buffer_score,
                "purity": efs.signal_purity_score,
                "efs": efs.efs_score,
                "direction": efs.momentum_direction,
            })

            if (i + 1) % 10 == 0:
                print(f"  Processed {i + 1}/{len(bets)} bets...")
        except Exception as e:
            print(f"  ERROR: {bet.ticker} — {e}")

    # Print results table
    print(f"\n{'='*100}")
    print(f"{'Ticker':<8} {'Thesis':<22} {'Rev%':>6} {'Beta':>6} {'Mom':>6} {'Val':>6} {'Pure':>6} {'EFS':>6} {'Dir':<12}")
    print(f"{'-'*100}")
    results.sort(key=lambda x: x["efs"], reverse=True)
    for r in results:
        print(f"{r['ticker']:<8} {r['thesis']:<22} {r['revenue']:>6.1f} {r['beta']:>6.1f} {r['momentum']:>6.1f} {r['valuation']:>6.1f} {r['purity']:>6.1f} {r['efs']:>6.1f} {r['direction'] or '':<12}")

    print(f"\n{'='*100}")
    print(f"Total: {len(results)} equity bets scored")
    print(f"Average EFS: {sum(r['efs'] for r in results) / len(results):.1f}" if results else "No results")

    # Calculate STS for all startups
    print(f"\n{'='*100}")
    print("STARTUP TIMING SCORE — FULL CALCULATION")
    print(f"{'='*100}")

    opps = db.query(StartupOpportunity).all()
    print(f"\nProcessing {len(opps)} startup opportunities...\n")

    sts_results = []
    for i, opp in enumerate(opps):
        try:
            sts = await calculate_sts(opp, db)
            sts_results.append({
                "name": opp.name[:25],
                "sts": sts.sts_score,
                "timing": sts.timing_label,
                "thi": sts.thi_alignment_score,
                "velocity": sts.thi_velocity_score,
                "competition": sts.competition_density_score,
            })
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(opps)} startups...")
        except Exception as e:
            print(f"  ERROR: {opp.name} — {e}")

    print(f"\n{'='*100}")
    print(f"{'Name':<27} {'STS':>5} {'THI':>5} {'Vel':>5} {'Comp':>5} {'Timing':<14}")
    print(f"{'-'*100}")
    sts_results.sort(key=lambda x: x["sts"], reverse=True)
    for r in sts_results[:50]:  # top 50
        print(f"{r['name']:<27} {r['sts']:>5.1f} {r['thi']:>5.1f} {r['velocity']:>5.1f} {r['competition']:>5.1f} {r['timing']:<14}")

    print(f"\n{'='*100}")
    print(f"Total: {len(sts_results)} startups scored")
    print(f"Average STS: {sum(r['sts'] for r in sts_results) / len(sts_results):.1f}" if sts_results else "No results")

    db.close()


if __name__ == "__main__":
    asyncio.run(main())
