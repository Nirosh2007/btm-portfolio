"""RICE prioritization for a HYPOTHETICAL product. All inputs are estimates to be validated.
RICE = (Reach x Impact x Confidence) / Effort
Reach: families per quarter | Impact: 0.25 minimal, 0.5 low, 1 medium, 2 high, 3 massive
Confidence: 0-1 | Effort: person-weeks
"""
from pathlib import Path
FEATURES = [
    # name, reach, impact, confidence, effort
    ("Online registration + payment",        400, 3.0, 0.8, 6),
    ("Automatic schedule + reminders",       400, 2.0, 0.8, 4),
    ("Parent-facing team page (games, map)", 400, 1.0, 0.8, 3),
    ("Attendance tracking for coaches",      120, 1.0, 0.5, 3),
    ("Volunteer shift sign-up",              150, 1.0, 0.5, 4),
    ("Live scores and standings",            300, 0.5, 0.5, 5),
    ("Photo / video sharing",                200, 0.25, 0.5, 6),
    ("Player stats and progress",            100, 0.5, 0.3, 8),
]
rows = sorted(((n, r, i, c, e, r * i * c / e) for n, r, i, c, e in FEATURES), key=lambda x: -x[-1])
md = ["| Rank | Feature | Reach | Impact | Confidence | Effort (wks) | RICE score |", "|---|---|---|---|---|---|---|"]
for k, (n, r, i, c, e, s) in enumerate(rows, 1):
    md.append(f"| {k} | {n} | {r} | {i} | {int(c*100)}% | {e} | **{s:,.0f}** |")
out = Path(__file__).parent / "rice_prioritization.md"
out.write_text("# RICE prioritization (auto-generated; estimates are assumptions)\n\n" + "\n".join(md) + "\n")
print(out.read_text())
