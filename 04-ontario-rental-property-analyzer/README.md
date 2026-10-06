# Project 4: Ontario Rental Property & BRRRR Analyzer (Python)

A small, tested tool that evaluates a rental property the way an investor would: cash flow, cap rate, cash-on-cash return, DSCR, a BRRRR refinance scenario, break-even rent, and a rate/rent sensitivity table. It uses **Canadian mortgage conventions** (semi-annual compounding).

> **Assumptions note:** Every input in `example_scenario.json` is an **illustrative assumption**, not a market quote or financial advice. Replace them with real listing, lender, and municipal numbers. Lender refinance rules (LTV limits, etc.) change, so verify them.

## Run it
```bash
python analyzer.py                       # uses example_scenario.json
python analyzer.py my_property.json      # your own numbers
python -m unittest discover -s tests -v  # 6 tests
```

## Example output (illustrative scenario)
- Cap rate: **5.96%**, monthly cash flow: **+$298**, cash-on-cash: **1.79%**, DSCR: **1.09**
- **Break-even rent: $4,457** vs. $4,800 assumed
- BRRRR: refinancing at 80% of a $800k after-repair value pulls out **$80,000**, but **$120,500** stays in the deal, and post-refinance cash flow turns **negative (−$156/mo)**

| Mortgage rate \ Rent | $4,320 | $4,800 | $5,280 |
|---|---|---|---|
| 3.75% | 188 | 606 | 1,023 |
| 4.75% | -119 | 298 | 716 |
| 5.75% | -442 | -24 | 393 |
| 6.75% | -778 | -360 | 57 |

## What the example shows
The deal looks fine on the purchase mortgage but is **fragile**: a 1-point rate increase wipes out the cash flow, and the BRRRR refinance makes it negative. That is the point of running the numbers before buying.

## Limitations
Doesn't model appreciation, principal paydown, taxes on rental income, capital gains, or rent control rules. Those would be natural next features.
