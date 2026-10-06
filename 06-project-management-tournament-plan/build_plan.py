"""Schedule (critical path), risk register, and budget for a HYPOTHETICAL
12-team youth basketball tournament. All inputs are illustrative assumptions.
Writes markdown tables + a Mermaid Gantt chart to ./output.
"""
from datetime import date, timedelta
from pathlib import Path

OUT = Path(__file__).parent / "output"; OUT.mkdir(exist_ok=True)
START = date(2027, 3, 1)   # assumed project kickoff (Monday)

# ---- Tasks: id, name, duration (working days), predecessors ----
TASKS = [
    ("A", "Approve charter and budget",            3,  []),
    ("B", "Book gym and confirm date",             7,  ["A"]),
    ("C", "Open team registration",                2,  ["A"]),
    ("D", "Recruit referees and volunteers",      14,  ["B"]),
    ("E", "Collect registrations and fees",       21,  ["C"]),
    ("F", "Arrange insurance and first aid",       7,  ["B"]),
    ("G", "Order trophies and volunteer shirts",   5,  ["B"]),
    ("H", "Build game schedule and brackets",      5,  ["E"]),
    ("I", "Marketing and parent communications",  14,  ["C"]),
    ("J", "Volunteer briefing and training",       3,  ["D", "H"]),
    ("K", "Venue walkthrough and setup plan",      2,  ["F", "G"]),
    ("L", "Final readiness check (go/no-go)",      1,  ["J", "K", "I"]),
    ("M", "Run tournament (2 game days)",                2,  ["L"]),
    ("N", "Teardown, payments, and debrief",       3,  ["M"]),
]
byid = {t[0]: t for t in TASKS}

# ---- Critical Path Method ----
ES, EF = {}, {}
for tid, _, dur, preds in TASKS:                     # tasks are listed in dependency order
    ES[tid] = max([EF[p] for p in preds], default=0)
    EF[tid] = ES[tid] + dur
project_len = max(EF.values())
LS, LF = {}, {}
for tid, _, dur, preds in reversed(TASKS):
    succs = [t[0] for t in TASKS if tid in t[3]]
    LF[tid] = min([LS[s] for s in succs], default=project_len)
    LS[tid] = LF[tid] - dur
slack = {t: LS[t] - ES[t] for t in byid}
critical = [t[0] for t in TASKS if slack[t[0]] == 0]


def workday(offset):
    """Date of the Nth working day after START (skips Sat/Sun)."""
    d, n = START, 0
    while n < offset:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return d


rows = ["| ID | Task | Days | Depends on | Start | Finish | Slack (days) | Critical |", "|---|---|---|---|---|---|---|---|"]
for tid, name, dur, preds in TASKS:
    rows.append(f"| {tid} | {name} | {dur} | {', '.join(preds) or '-'} | {workday(ES[tid])} | {workday(EF[tid])} | {slack[tid]} | {'**Yes**' if tid in critical else ''} |")

gantt = ["```mermaid", "gantt", "    dateFormat YYYY-MM-DD", "    title Tournament plan (critical path in red)", "    axisFormat %b %d"]
for tid, name, dur, preds in TASKS:
    tag = "crit, " if tid in critical else ""
    gantt.append(f"    {name} :{tag}{tid.lower()}, {workday(ES[tid])}, {workday(EF[tid])}")
gantt.append("```")

path_names = " → ".join(f"{t} ({byid[t][1]})" for t in critical)
sched = f"""# Schedule and critical path (auto-generated)

Kickoff: **{START}** (assumed). Project length: **{project_len} working days**, finishing **{workday(project_len)}**.

**Critical path:** {path_names}

Any delay on a critical task delays the tournament day by the same amount. Non-critical tasks have slack shown below.

{chr(10).join(rows)}

{chr(10).join(gantt)}
"""
(OUT / "schedule.md").write_text(sched)

# ---- Risk register: likelihood (1-5) x impact (1-5) ----
RISKS = [
    ("R1", "Gym booking falls through or double-booked", 2, 5, "Book early; get written confirmation; identify a backup venue", "Operator"),
    ("R2", "Too few teams register",                      3, 4, "Early-bird discount; direct outreach to past teams; extend deadline once", "Operator"),
    ("R3", "Not enough referees or volunteers",           3, 4, "Recruit 20% extra; tiered schedule; back-up contact list", "Volunteer lead"),
    ("R4", "Injury during games",                         3, 5, "First-aid kit and certified attendant; insurance; emergency plan posted", "Safety lead"),
    ("R5", "Schedule runs behind on game day",            4, 3, "Fixed game clocks; buffer between rounds; dedicated schedule manager", "Operator"),
    ("R6", "Budget overrun",                              3, 3, "Contingency line; weekly budget check; approval for spend over $100", "Operator"),
    ("R7", "Trophy / shirt order arrives late",           2, 2, "Order 3 weeks early; confirm delivery date", "Operations"),
    ("R8", "Parent complaints about communication",       3, 2, "Single info page; reminders at 2 weeks, 1 week, 1 day", "Comms lead"),
]
risks = sorted(((*r, r[2] * r[3]) for r in RISKS), key=lambda x: -x[-1])
rr = ["| ID | Risk | Likelihood | Impact | Score | Rating | Response | Owner |", "|---|---|---|---|---|---|---|---|"]
for rid, txt, l, i, resp, own, sc in risks:
    rating = "High" if sc >= 12 else "Medium" if sc >= 6 else "Low"
    rr.append(f"| {rid} | {txt} | {l} | {i} | {sc} | {rating} | {resp} | {own} |")
(OUT / "risk_register.md").write_text("# Risk register (auto-generated)\n\nScore = Likelihood (1-5) x Impact (1-5). High >= 12, Medium 6-11, Low <= 5.\n\n" + "\n".join(rr) + "\n")

# ---- Budget ----
TEAMS, FEE = 12, 350
revenue = [("Team registration fees", TEAMS * FEE), ("Concession / sponsor income (assumed)", 900)]
costs = [("Gym rental (2 days)", 1600), ("Referees", 1200), ("Trophies and medals", 600), ("Volunteer shirts", 350),
         ("Insurance", 400), ("First-aid supplies", 120), ("Marketing and printing", 250), ("Admin / software", 100)]
sub = sum(c for _, c in costs); cont = round(0.10 * sub); tot_cost = sub + cont; tot_rev = sum(r for _, r in revenue)
b = ["| Item | Amount |", "|---|---:|"]
b += [f"| {n} | ${a:,} |" for n, a in revenue] + [f"| **Total revenue** | **${tot_rev:,}** |"]
b += [f"| {n} | ${a:,} |" for n, a in costs] + [f"| Contingency (10%) | ${cont:,} |", f"| **Total cost** | **${tot_cost:,}** |", f"| **Net** | **${tot_rev - tot_cost:,}** |"]
be = -(-tot_cost // FEE)    # ceiling division: teams needed ignoring concession income
(OUT / "budget.md").write_text(f"# Budget (auto-generated, illustrative)\n\n{chr(10).join(b)}\n\nBreak-even on registration fees alone: **{be} teams** at ${FEE} per team (concession income not counted).\n")
print(sched[:900]); print("critical:", critical, "len", project_len); print((OUT / "budget.md").read_text())
