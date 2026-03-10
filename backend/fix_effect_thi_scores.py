"""One-time migration: randomize effect THI scores so they differ from parent.

2nd order effects: parent_score * random(0.6, 0.9)
3rd order effects (or child effects): parent_score * random(0.4, 0.75)
"""

import random
import sqlite3

random.seed(42)  # reproducible

conn = sqlite3.connect("tangentbook.db")
cur = conn.cursor()

# Get all theses with their THI scores
cur.execute("SELECT id, thi_score FROM theses")
theses = {row[0]: row[1] for row in cur.fetchall()}

# Get all effects
cur.execute('SELECT id, thesis_id, parent_effect_id, "order", thi_score FROM effects')
effects = cur.fetchall()

# Build a lookup: effect_id -> thi_score (will be updated)
effect_scores = {}

updated = 0
for eid, thesis_id, parent_effect_id, order, old_score in effects:
    if parent_effect_id is None:
        # 2nd order effect — derive from parent thesis
        parent_score = theses.get(thesis_id, 50.0)
        factor = random.uniform(0.6, 0.9)
    else:
        # 3rd order (child of another effect) — derive from parent effect
        parent_score = effect_scores.get(parent_effect_id, theses.get(thesis_id, 50.0))
        factor = random.uniform(0.4, 0.75)

    new_score = round(parent_score * factor, 1)
    new_score = max(5.0, min(95.0, new_score))  # clamp
    effect_scores[eid] = new_score

    cur.execute("UPDATE effects SET thi_score = ? WHERE id = ?", (new_score, eid))
    updated += 1
    print(f"  {eid[:40]:40s}  {old_score:5.1f} -> {new_score:5.1f}  (parent={parent_score:.1f}, factor={factor:.2f})")

conn.commit()
conn.close()
print(f"\nUpdated {updated} effects.")
