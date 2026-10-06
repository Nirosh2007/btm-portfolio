"""Rental property & BRRRR analyzer (Canadian mortgage conventions).

Every number in `example_scenario.json` is an ILLUSTRATIVE ASSUMPTION, not a
market quote. Replace with real listing / lender / municipal figures.
"""
from __future__ import annotations
import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path


def monthly_payment(principal: float, annual_rate: float, years: int = 25) -> float:
    """Canadian fixed-rate mortgages compound semi-annually, not monthly."""
    if principal <= 0:
        return 0.0
    monthly_rate = (1 + annual_rate / 2) ** (2 / 12) - 1
    n = years * 12
    if monthly_rate == 0:
        return principal / n
    return principal * monthly_rate / (1 - (1 + monthly_rate) ** -n)


@dataclass
class Property:
    purchase_price: float
    down_payment_pct: float
    mortgage_rate: float          # e.g. 0.05 for 5%
    amortization_years: int
    monthly_rent: float           # total rent across all units
    vacancy_pct: float            # e.g. 0.05
    annual_property_tax: float
    annual_insurance: float
    monthly_maintenance_pct: float  # % of gross rent set aside, e.g. 0.08
    monthly_utilities: float        # landlord-paid
    closing_costs_pct: float = 0.015  # legal, LTT, etc. (rough)
    rehab_cost: float = 0.0
    after_repair_value: float = 0.0   # used for BRRRR refinance
    refinance_ltv: float = 0.80       # lenders cap refinance LTV (verify current rules)


def analyze(p: Property) -> dict:
    down = p.purchase_price * p.down_payment_pct
    loan = p.purchase_price - down
    pmt = monthly_payment(loan, p.mortgage_rate, p.amortization_years)

    gross_annual_rent = p.monthly_rent * 12
    effective_rent = gross_annual_rent * (1 - p.vacancy_pct)
    maintenance = gross_annual_rent * p.monthly_maintenance_pct
    opex = p.annual_property_tax + p.annual_insurance + maintenance + p.monthly_utilities * 12
    noi = effective_rent - opex
    debt_service = pmt * 12
    cash_flow = noi - debt_service

    cash_invested = down + p.purchase_price * p.closing_costs_pct + p.rehab_cost
    result = {
        "cash_invested": round(cash_invested),
        "monthly_mortgage_payment": round(pmt, 2),
        "noi_annual": round(noi),
        "cap_rate_pct": round(100 * noi / p.purchase_price, 2),
        "annual_cash_flow": round(cash_flow),
        "monthly_cash_flow": round(cash_flow / 12),
        "cash_on_cash_return_pct": round(100 * cash_flow / cash_invested, 2) if cash_invested else None,
        "dscr": round(noi / debt_service, 2) if debt_service else None,
    }

    if p.after_repair_value > 0:   # BRRRR: refinance, pull cash out
        new_loan = p.after_repair_value * p.refinance_ltv
        cash_out = new_loan - loan
        left_in = cash_invested - cash_out
        new_pmt = monthly_payment(new_loan, p.mortgage_rate, p.amortization_years)
        post_cf = noi - new_pmt * 12
        result["brrrr"] = {
            "refinance_loan": round(new_loan),
            "cash_pulled_out": round(cash_out),
            "cash_left_in_deal": round(max(left_in, 0)),
            "post_refi_monthly_cash_flow": round(post_cf / 12),
            "post_refi_cash_on_cash_pct": round(100 * post_cf / left_in, 2) if left_in > 0 else "infinite (all cash recovered)",
        }
    return result


def break_even_rent(p: Property) -> float:
    """Monthly rent needed for $0 monthly cash flow (solved by bisection)."""
    lo, hi = 0.0, p.monthly_rent * 5
    for _ in range(60):
        mid = (lo + hi) / 2
        q = Property(**{**asdict(p), "monthly_rent": mid})
        if analyze(q)["annual_cash_flow"] < 0:
            lo = mid
        else:
            hi = mid
    return round(hi)


def sensitivity(p: Property, rates: list[float], rents: list[float]) -> list[list]:
    """Monthly cash flow across mortgage-rate and rent scenarios."""
    grid = []
    for r in rates:
        row = []
        for rent in rents:
            q = Property(**{**asdict(p), "mortgage_rate": r, "monthly_rent": rent})
            row.append(analyze(q)["monthly_cash_flow"])
        grid.append(row)
    return grid


def main(path: str) -> None:
    p = Property(**json.loads(Path(path).read_text()))
    res = analyze(p)
    print(json.dumps(res, indent=2))
    print(f"\nBreak-even monthly rent (cash flow = $0): ${break_even_rent(p):,}  vs. assumed ${p.monthly_rent:,.0f}")
    rates = [p.mortgage_rate + d for d in (-0.01, 0, 0.01, 0.02)]
    rents = [p.monthly_rent * f for f in (0.90, 1.0, 1.10)]
    grid = sensitivity(p, rates, rents)
    print("\nMonthly cash flow sensitivity (rows = mortgage rate, cols = monthly rent)")
    print("rate \\ rent | " + " | ".join(f"${x:,.0f}" for x in rents))
    for r, row in zip(rates, grid):
        print(f"{r*100:>5.2f}%     | " + " | ".join(f"{v:>7,}" for v in row))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(Path(__file__).parent / "example_scenario.json"))
