"""Retail customer analytics with SQL (SQLite) + Python on the REAL UCI Online Retail dataset."""
import re, sqlite3, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.retail import load_raw, clean_sales

HERE = Path(__file__).parent
CH = HERE / "charts"; CH.mkdir(exist_ok=True)

sales = clean_sales(load_raw()).rename(columns={
    "InvoiceNo": "invoice_no", "StockCode": "stock_code", "Description": "description", "Quantity": "quantity",
    "InvoiceDate": "invoice_date", "UnitPrice": "unit_price", "CustomerID": "customer_id", "Country": "country",
    "Revenue": "revenue", "Month": "month"})
sales["invoice_date"] = sales["invoice_date"].dt.strftime("%Y-%m-%d %H:%M:%S")
db = HERE / "retail.db"
if db.exists(): db.unlink()
con = sqlite3.connect(db)
sales.to_sql("sales", con, index=False)
con.execute("CREATE INDEX ix_sales_customer ON sales(customer_id)")
con.execute("CREATE INDEX ix_sales_month ON sales(month)")

blocks = re.split(r"-- name: (\w+)\n", (HERE / "queries.sql").read_text())
Q = {blocks[i]: blocks[i + 1] for i in range(1, len(blocks), 2)}
R = {k: pd.read_sql_query(v, con) for k, v in Q.items()}
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})

# ---- monthly revenue ----
m = R["monthly"]
fig, ax = plt.subplots(figsize=(8, 4))
ax.bar(m["month"], m["revenue"] / 1000, color="#4b5563")
ax.set_ylabel("Revenue (£000)"); ax.set_title("Monthly revenue, Dec 2010 – Nov 2011 (UCI Online Retail)")
plt.setp(ax.get_xticklabels(), rotation=45, ha="right"); fig.tight_layout()
fig.savefig(CH / "monthly_revenue.png", dpi=150); plt.close(fig)

# ---- cohort retention ----
c = R["cohorts"].pivot(index="cohort", columns="months_since", values="customers")
ret = c.div(c[0], axis=0) * 100
fig, ax = plt.subplots(figsize=(8, 4.8))
im = ax.imshow(ret.values, cmap="Greys", vmin=0, vmax=60, aspect="auto")
ax.set_xticks(range(ret.shape[1])); ax.set_yticks(range(ret.shape[0])); ax.set_yticklabels(ret.index)
ax.set_xlabel("Months since first purchase"); ax.set_title("Customer retention by first-purchase cohort (%)")
for i in range(ret.shape[0]):
    for j in range(ret.shape[1]):
        v = ret.values[i, j]
        if not np.isnan(v): ax.text(j, i, f"{v:.0f}", ha="center", va="center", fontsize=7, color="white" if v > 35 else "black")
fig.colorbar(im, ax=ax, shrink=0.8); fig.tight_layout(); fig.savefig(CH / "cohort_retention.png", dpi=150); plt.close(fig)
avg_ret = ret.drop(columns=[0]).mean().round(1)

# ---- RFM segments ----
rfm = R["rfm"]
def seg(row):
    if row.r == 4 and row.f >= 3 and row.m >= 3: return "Champions"
    if row.f >= 3 and row.r >= 3:                return "Loyal"
    if row.f >= 3 and row.r <= 2:                return "At risk (were frequent)"
    if row.r == 4:                               return "Recent / new"
    if row.r == 1:                               return "Lost"
    return "Occasional"
rfm["segment"] = rfm.apply(seg, axis=1)
S = rfm.groupby("segment").agg(customers=("customer_id", "count"), revenue=("monetary", "sum")).sort_values("revenue", ascending=False)
S["pct_customers"] = 100 * S["customers"] / S["customers"].sum(); S["pct_revenue"] = 100 * S["revenue"] / S["revenue"].sum()
fig, ax = plt.subplots(figsize=(7, 4))
ax.barh(S.index[::-1], S["pct_revenue"][::-1], color="#4b5563", label="% of revenue")
ax.barh(S.index[::-1], S["pct_customers"][::-1], color="#d1d5db", height=0.4, label="% of customers")
ax.set_xlabel("%"); ax.set_title("RFM segments: share of customers vs. revenue"); ax.legend(frameon=False)
fig.tight_layout(); fig.savefig(CH / "rfm_segments.png", dpi=150); plt.close(fig)

# ---- Pareto of customer revenue ----
cust = rfm.sort_values("monetary", ascending=False).reset_index(drop=True)
cum = cust["monetary"].cumsum() / cust["monetary"].sum() * 100
n80 = int((cum < 80).sum() + 1); pct80 = 100 * n80 / len(cust)

# ---- findings ----
tot = float(sales["revenue"].sum()); uk = R["countries"].iloc[0]
top = R["top_products"].iloc[0]
nov, octo = m.set_index("month").loc["2011-11", "revenue"], m.set_index("month").loc["2011-10", "revenue"]
q3 = m.set_index("month").loc[["2011-01", "2011-02", "2011-03"], "revenue"].mean()
md = f"""# Findings (auto-generated from the real UCI Online Retail data)

- **Scale:** £{tot:,.0f} revenue from {sales['invoice_no'].nunique():,} invoices across {sales['country'].nunique()} countries (valid sale lines only, see the data-quality project for how "valid" is defined).
- **Seasonality:** November 2011 revenue (£{nov:,.0f}) was {nov / q3:.1f}x the Jan–Mar 2011 monthly average (£{q3:,.0f}).
- **Geography:** {uk['country']} accounts for {uk['pct_of_revenue']}% of revenue.
- **Top product:** {top['description']} (£{top['revenue']:,.0f}).
- **Retention:** on average, {avg_ret.get(1, float('nan')):.1f}% of a cohort buys again in month 1 and {avg_ret.get(6, float('nan')):.1f}% in month 6.
- **Concentration:** the top {pct80:.0f}% of identified customers ({n80:,} of {len(cust):,}) generate 80% of identified-customer revenue.
- **RFM:** Champions are {S.loc['Champions', 'pct_customers']:.0f}% of customers but {S.loc['Champions', 'pct_revenue']:.0f}% of revenue.

## Top products by revenue
{R['top_products'].to_markdown(index=False)}

## Top countries
{R['countries'].to_markdown(index=False)}

## RFM segments
{S.round(1).to_markdown()}
"""
(HERE / "findings.md").write_text(md)
print(md)
con.close(); db.unlink()
