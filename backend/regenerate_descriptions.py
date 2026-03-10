"""
Regenerate descriptions for all theses, equity bets, and startups using Claude.

Thesis: 2-3 casual sentences explaining why this thesis is smart.
Equity Bet: 1 sentence what the company does + 2 sentences why it's a smart play.
Startup: 1 sentence what the company does + 2 sentences why it's a smart play.
"""

import sys
import os
import json
import time

sys.path.insert(0, os.path.dirname(__file__))

import anthropic
from database import SessionLocal
from models import Thesis, Effect, EquityBet, StartupOpportunity
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL = "claude-sonnet-4-20250514"


def call_claude(prompt: str) -> str:
    resp = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def regenerate_thesis_descriptions(db):
    theses = db.query(Thesis).all()
    print(f"\n=== Regenerating {len(theses)} thesis descriptions ===\n")

    for t in theses:
        prompt = f"""Write a 2-3 sentence description for this investment thesis. Sound like a sharp investor explaining it to a friend over drinks — casual, colloquial, confident. No jargon, no press release tone. Just explain why this thesis is smart money.

Thesis title: {t.title}
Current subtitle: {t.subtitle}
Current description: {t.description}
Tags: {', '.join(t.tags or [])}
Time horizon: {t.time_horizon}

Return ONLY the 2-3 sentence description, nothing else."""

        try:
            new_desc = call_claude(prompt)
            t.description = new_desc
            print(f"  [THESIS] {t.title}")
            print(f"    -> {new_desc[:120]}...")
            time.sleep(0.5)
        except Exception as e:
            print(f"  [ERROR] {t.title}: {e}")

    db.commit()
    print(f"\nCommitted {len(theses)} thesis updates")


def regenerate_equity_bet_descriptions(db):
    bets = db.query(EquityBet).all()
    print(f"\n=== Regenerating {len(bets)} equity bet descriptions ===\n")

    for b in bets:
        # Get parent context
        parent_context = ""
        if b.effect_id:
            effect = db.query(Effect).filter(Effect.id == b.effect_id).first()
            if effect:
                thesis = db.query(Thesis).filter(Thesis.id == effect.thesis_id).first()
                parent_context = f"Parent thesis: {thesis.title if thesis else 'Unknown'}\nEffect: {effect.title}"
        elif b.thesis_id:
            thesis = db.query(Thesis).filter(Thesis.id == b.thesis_id).first()
            parent_context = f"Parent thesis: {thesis.title if thesis else 'Unknown'}"

        prompt = f"""Write a description for this equity bet in exactly this format:
- First sentence: What the company actually does, in plain English. No jargon.
- Second and third sentences: Why this is a smart play specifically under the parent thesis.

{parent_context}
Ticker: {b.ticker}
Company: {b.company_name}
Role: {b.role} (BENEFICIARY = wins if thesis plays out, HEADWIND = loses, CANARY = early warning signal)
Current rationale: {b.rationale}
Current company description: {b.company_description}

Return a JSON object with two fields:
{{"company_description": "1 sentence about what they do", "rationale": "2 sentences on why smart play"}}

Return ONLY the JSON, no markdown fences."""

        try:
            raw = call_claude(prompt)
            data = json.loads(raw)
            b.company_description = data["company_description"]
            b.rationale = data["rationale"]
            print(f"  [BET] {b.ticker} ({b.company_name})")
            print(f"    desc: {b.company_description[:100]}...")
            print(f"    rationale: {b.rationale[:100]}...")
            time.sleep(0.5)
        except json.JSONDecodeError:
            print(f"  [JSON ERROR] {b.ticker}: {raw[:200]}")
        except Exception as e:
            print(f"  [ERROR] {b.ticker}: {e}")

    db.commit()
    print(f"\nCommitted {len(bets)} equity bet updates")


def regenerate_startup_descriptions(db):
    opps = db.query(StartupOpportunity).all()
    print(f"\n=== Regenerating {len(opps)} startup descriptions ===\n")

    for o in opps:
        parent_context = ""
        if o.effect_id:
            effect = db.query(Effect).filter(Effect.id == o.effect_id).first()
            if effect:
                thesis = db.query(Thesis).filter(Thesis.id == effect.thesis_id).first()
                parent_context = f"Parent thesis: {thesis.title if thesis else 'Unknown'}\nEffect: {effect.title}"
        elif o.thesis_id:
            thesis = db.query(Thesis).filter(Thesis.id == o.thesis_id).first()
            parent_context = f"Parent thesis: {thesis.title if thesis else 'Unknown'}"

        prompt = f"""Write a description for this startup opportunity in exactly this format:
- First sentence: What the startup does, in plain English.
- Second and third sentences: Why this is a smart play specifically under the parent thesis.

{parent_context}
Startup name: {o.name}
Current one-liner: {o.one_liner}
Timing: {o.timing}

Return ONLY the 3 sentences as a single paragraph, nothing else."""

        try:
            new_liner = call_claude(prompt)
            o.one_liner = new_liner
            print(f"  [STARTUP] {o.name}")
            print(f"    -> {new_liner[:120]}...")
            time.sleep(0.5)
        except Exception as e:
            print(f"  [ERROR] {o.name}: {e}")

    db.commit()
    print(f"\nCommitted {len(opps)} startup updates")


def main():
    db = SessionLocal()
    try:
        regenerate_thesis_descriptions(db)
        regenerate_equity_bet_descriptions(db)
        regenerate_startup_descriptions(db)
        print("\n=== All descriptions regenerated ===")
    finally:
        db.close()


if __name__ == "__main__":
    main()
