"""
Clean all equity bet descriptions:
1. Strip prepended company name from company_description
2. Strip "— TICKER" patterns
3. Strip "positioned in ..." boilerplate
4. For bets with garbage/stub descriptions, regenerate via Claude
"""

import sys
import os
import re
import json
import time

sys.path.insert(0, os.path.dirname(__file__))

import anthropic
from database import SessionLocal
from models import EquityBet, Effect, Thesis
from config import ANTHROPIC_API_KEY

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
MODEL = "claude-sonnet-4-20250514"


def strip_name_prefix(name: str, desc: str) -> str:
    """Remove company name prefix like 'CompanyName — rest' or 'CompanyName — TICKER...'"""
    if not desc or not name:
        return desc

    # Pattern: "CompanyName — rest..." or "CompanyName — TICKER..."
    if desc.startswith(name):
        rest = desc[len(name):].lstrip()
        # Strip leading dash/em-dash
        rest = re.sub(r'^[\u2014\u2013—–-]+\s*', '', rest)
        # Strip ticker if it follows: "TICKER..." or "TICKER —"
        rest = re.sub(r'^[A-Z]{1,5}[\s.…]*', '', rest, count=1) if re.match(r'^[A-Z]{1,5}[\s.…]', rest) else rest
        rest = rest.lstrip(' .…-—')
        return rest if rest else desc

    return desc


def is_stub(desc: str) -> bool:
    """Check if description is a stub/boilerplate that needs regeneration."""
    if not desc or len(desc) < 20:
        return True
    stubs = [
        "positioned as beneficiary",
        "positioned as headwind",
        "positioned as canary",
        "positioned in ",
        "broad market benchmark",
    ]
    lower = desc.lower()
    return any(s in lower for s in stubs)


def get_parent_context(bet, db):
    """Get thesis and effect context for a bet."""
    thesis_title = ""
    effect_title = ""
    if bet.effect_id:
        effect = db.query(Effect).filter(Effect.id == bet.effect_id).first()
        if effect:
            effect_title = effect.title
            thesis = db.query(Thesis).filter(Thesis.id == effect.thesis_id).first()
            if thesis:
                thesis_title = thesis.title
    elif bet.thesis_id:
        thesis = db.query(Thesis).filter(Thesis.id == bet.thesis_id).first()
        if thesis:
            thesis_title = thesis.title
    return thesis_title, effect_title


def regenerate_bet(bet, thesis_title, effect_title):
    """Call Claude to generate proper description + rationale."""
    context = f"Parent thesis: {thesis_title}"
    if effect_title:
        context += f"\nEffect: {effect_title}"

    prompt = f"""Write a description for this equity bet. Return a JSON object with exactly two fields:

1. "company_description": One plain-English sentence about what this company actually does. Do NOT start with the company name. Do NOT include the ticker. Just describe the business.
2. "rationale": Two sentences explaining why this is a smart play under the parent thesis. Be specific about the causal link.

{context}
Ticker: {bet.ticker}
Company: {bet.company_name}
Role: {bet.role}
Current description: {bet.company_description}
Current rationale: {bet.rationale}

Return ONLY valid JSON, no markdown fences."""

    resp = client.messages.create(
        model=MODEL,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    return json.loads(resp.content[0].text.strip())


def main():
    db = SessionLocal()
    bets = db.query(EquityBet).all()
    print(f"Processing {len(bets)} equity bets...\n")

    cleaned = 0
    regenerated = 0
    errors = 0

    for b in bets:
        name = b.company_name or ""
        desc = b.company_description or ""
        rat = b.rationale or ""

        # Step 1: Strip name prefix from description
        new_desc = strip_name_prefix(name, desc)

        # Step 2: Check if it's a stub that needs regeneration
        if is_stub(new_desc):
            thesis_title, effect_title = get_parent_context(b, db)
            try:
                data = regenerate_bet(b, thesis_title, effect_title)
                b.company_description = data["company_description"]
                b.rationale = data["rationale"]
                regenerated += 1
                print(f"  [REGEN] {b.ticker} ({name})")
                print(f"    desc: {b.company_description[:100]}")
                print(f"    rationale: {b.rationale[:100]}")
                time.sleep(0.3)
            except Exception as e:
                errors += 1
                print(f"  [ERROR] {b.ticker}: {e}")
                # Still apply the basic name-strip
                if new_desc != desc:
                    b.company_description = new_desc
                    cleaned += 1
        elif new_desc != desc:
            b.company_description = new_desc
            cleaned += 1
            print(f"  [STRIP] {b.ticker}: {new_desc[:80]}")

    db.commit()
    print(f"\nDone: {cleaned} stripped, {regenerated} regenerated, {errors} errors")
    print(f"Total: {cleaned + regenerated} bets updated out of {len(bets)}")

    # Verify
    print("\n=== Verification: first 20 bets ===\n")
    bets = db.query(EquityBet).limit(20).all()
    for b in bets:
        print(f"{b.ticker:8s} | {(b.company_description or '')[:90]}")
        print(f"{'':8s} | {(b.rationale or '')[:90]}")
        print()

    db.close()


if __name__ == "__main__":
    main()
