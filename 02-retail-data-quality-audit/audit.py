"""Data quality audit of the REAL UCI Online Retail dataset (541,909 line items).

Finds issues, quantifies their impact, shows where they concentrate, and builds a documented
cleaning waterfall. Nothing is guessed: rows are removed by explicit, countable rules.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.retail import load_raw, match_cancelled, PRODUCT_CODE

HERE = Path(__file__).parent
OUT = HERE / "output"; OUT.mkdir(exist_ok=True)
df = load_raw()
N = len(df)
df["value"] = df["Quantity"] * df["UnitPrice"]
is_cancel = df["InvoiceNo"].str.startswith("C")
nonproduct = ~df["StockCode"].str.match(PRODUCT_CODE)

# ---------------- 1. Issue inventory ----------------
issues = []
def add(name, mask, note):
    issues.append({"issue": name, "lines": int(mask.sum()), "pct_of_lines": round(100 * mask.mean(), 2), "note": note})
add("Missing CustomerID", df["CustomerID"].isna(), "Cannot be used for customer-level analysis (retention, RFM)")
add("Missing Description", df["Description"].isna(), "Product cannot be identified by name")
add("Cancellation lines (InvoiceNo starts with C)", is_cancel, "Negative quantities; must not be counted as sales")
add("Non-positive quantity, not a cancellation", ~is_cancel & (df["Quantity"] <= 0), "Stock adjustments, damaged or lost goods")
add("Non-positive unit price", df["UnitPrice"] <= 0, "Zero-price lines (often adjustments or free items)")
add("Non-product stock codes", nonproduct, "Postage, fees, manual entries, samples, not merchandise")
add("Exact duplicate rows", df.duplicated(keep="first"), "Identical on all 8 fields")
multi = df.dropna(subset=["Description"]).groupby("StockCode")["Description"].nunique()
add("Stock codes with >1 description", df["StockCode"].isin(multi[multi > 1].index), "Same product coded with different names")
issues = pd.DataFrame(issues)

# ---------------- 2. Cleaning waterfall ----------------
steps = []
keep = pd.Series(True, index=df.index)
def step(label, remove_mask):
    global keep
    removed = keep & remove_mask
    steps.append({"step": label, "lines_removed": int(removed.sum()), "revenue_removed": round(float(df.loc[removed, "value"].clip(lower=0).sum()))})
    keep &= ~remove_mask
step("Cancellation lines", is_cancel)
step("Non-positive quantity (adjustments)", df["Quantity"] <= 0)
step("Non-positive unit price", df["UnitPrice"] <= 0)
step("Non-product stock codes (postage, fees, manual)", nonproduct)
step("Exact duplicate rows", df.duplicated(keep="first"))
step("Originals later fully cancelled (matched by customer, product, qty)", df.index.isin(match_cancelled(df)))
W = pd.DataFrame(steps)
final = int(keep.sum())
raw_rev = float(df.loc[df["value"] > 0, "value"].sum()); final_rev = float(df.loc[keep, "value"].sum())

# ---------------- 3. Outliers ----------------
outl = df[df["Quantity"].abs() > 10000][["InvoiceNo", "StockCode", "Description", "Quantity", "UnitPrice", "CustomerID", "InvoiceDate"]].copy()
cancelled_idx = match_cancelled(df)
outl = outl[outl["Quantity"] > 0].copy()
outl["later_cancelled"] = outl.index.isin(cancelled_idx)

# ---------------- 4. Where do missing CustomerIDs concentrate? ----------------
df["missing_cust"] = df["CustomerID"].isna()
by_country = df.groupby("Country").agg(lines=("missing_cust", "size"), pct_missing=("missing_cust", "mean"))
by_country["pct_missing"] = (100 * by_country["pct_missing"]).round(1)
by_country = by_country[by_country["lines"] >= 1000].sort_values("pct_missing", ascending=False)
df["month"] = df["InvoiceDate"].dt.strftime("%Y-%m")
by_month = (100 * df.groupby("month")["missing_cust"].mean()).round(1)
rev_missing = df.loc[df["missing_cust"] & keep, "value"].sum() / df.loc[keep, "value"].sum() * 100
avg_line_known = df.loc[keep & ~df["missing_cust"], "value"].mean(); avg_line_missing = df.loc[keep & df["missing_cust"], "value"].mean()

# ---------------- Charts ----------------
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
fig, ax = plt.subplots(figsize=(8, 4))
labels = ["Raw lines"] + list(W["step"].str.replace(r" \(.*\)", "", regex=True)) + ["Analysis-ready"]
vals = [N] + [-v for v in W["lines_removed"]] + [final]
left = N; xs = []
ax.barh(0, N / 1000, color="#4b5563")
for i, v in enumerate(W["lines_removed"], 1):
    left -= v; ax.barh(i, v / 1000, left=left / 1000, color="#9ca3af")
ax.barh(len(W) + 1, final / 1000, color="#111827")
ax.set_yticks(range(len(labels))); ax.set_yticklabels(labels); ax.invert_yaxis(); ax.set_xlabel("Line items (thousands)")
ax.set_title("Cleaning waterfall: 541,909 raw lines to analysis-ready (UCI Online Retail)")
fig.tight_layout(); fig.savefig(OUT / "cleaning_waterfall.png", dpi=150); plt.close(fig)

fig, ax = plt.subplots(figsize=(8, 3.6))
ax.bar(by_month.index, by_month.values, color="#4b5563"); ax.set_ylabel("% of lines missing CustomerID")
ax.set_title("Missing CustomerID by month"); plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
fig.tight_layout(); fig.savefig(OUT / "missing_customerid_by_month.png", dpi=150); plt.close(fig)

# ---------------- Report ----------------
np_top = df[nonproduct].groupby("StockCode").agg(lines=("value", "size"), net_value=("value", "sum")).sort_values("lines", ascending=False).head(6).round(0)
report = f"""# Audit results (real data: UCI Online Retail, 541,909 lines)

## Issue inventory
{issues.to_markdown(index=False)}

## Cleaning waterfall
| Step | Lines removed | Positive revenue removed (£) |
|---|---:|---:|
""" + "\n".join(f"| {r.step} | {r.lines_removed:,} | {r.revenue_removed:,} |" for r in W.itertuples()) + f"""

**Result:** {final:,} analysis-ready lines ({100 * final / N:.1f}% of raw). Positive line value fell from £{raw_rev:,.0f} to £{final_rev:,.0f}, so **{100 * (1 - final_rev / raw_rev):.1f}% of apparent revenue was not real merchandise sales** (cancellations, fees, postage, and fully cancelled orders).

## Extreme quantities (qty > 10,000, sale lines only)
{outl.to_markdown(index=False)}

## Where missing CustomerIDs concentrate
- {100 * df['missing_cust'].mean():.1f}% of all lines have no CustomerID. They represent {rev_missing:.1f}% of analysis-ready revenue.
- Average value per line: £{avg_line_known:,.2f} with a CustomerID vs. £{avg_line_missing:,.2f} without.

{by_country.head(6).to_markdown()}

## Most frequent non-product stock codes
{np_top.to_markdown()}
"""
(OUT / "audit_report.md").write_text(report)
issues.to_csv(OUT / "issue_inventory.csv", index=False); W.to_csv(OUT / "cleaning_waterfall.csv", index=False)
print(report)
