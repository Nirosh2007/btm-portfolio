"""Inventory policy BACKTEST on REAL demand (UCI Online Retail, valid sales, cancellations netted).

Parameters are estimated from a training window and then tested on a later holdout window the
policy has never seen. That matters here: the holdout contains the Nov 2011 holiday peak.

ASSUMED (not in the data): unit cost, order cost, holding rate, supplier lead time, stockout penalty.
The dataset has selling prices and quantities only.
"""
import sys
from pathlib import Path
from statistics import NormalDist
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from common.retail import load_raw, clean_sales

HERE = Path(__file__).parent
OUT = HERE / "output"; OUT.mkdir(exist_ok=True)

# ---------------- Assumptions ----------------
COST_PCT_OF_PRICE = 0.60   # unit cost = 60% of median selling price
ORDER_COST = 40.0          # £ per purchase order
HOLD_RATE = 0.22           # annual holding cost, % of unit cost
LEAD_WEEKS = 2             # supplier lead time (weeks)
STOCKOUT_PCT = 0.50        # penalty per unit short, % of unit cost
N_SKU = 150                # top products by training revenue
TRAIN_WEEKS = 40
SERVICE = {"A": 0.98, "B": 0.95, "C": 0.90}

# ---------------- Weekly demand per product ----------------
sales = clean_sales(load_raw())
sales["week"] = sales["InvoiceDate"].dt.to_period("W-SUN").dt.start_time
weeks = pd.date_range(sales["week"].min(), sales["week"].max(), freq="W-MON")
weeks = weeks[weeks < pd.Timestamp("2011-12-05")]            # drop the partial final week
demand = sales.pivot_table(index="StockCode", columns="week", values="Quantity", aggfunc="sum", fill_value=0).reindex(columns=weeks, fill_value=0)
price = sales.groupby("StockCode")["UnitPrice"].median()
rev_train = (sales[sales["week"].isin(weeks[:TRAIN_WEEKS])].assign(rev=lambda d: d["Quantity"] * d["UnitPrice"]).groupby("StockCode")["rev"].sum())
skus = rev_train.sort_values(ascending=False).head(N_SKU).index
D = demand.loc[skus]; train, test = D.iloc[:, :TRAIN_WEEKS], D.iloc[:, TRAIN_WEEKS:]
unit_cost = (price.loc[skus] * COST_PCT_OF_PRICE)
n_test = test.shape[1]

# ---------------- ABC / XYZ on the training window ----------------
tab = pd.DataFrame({"mu": train.mean(axis=1), "sigma": train.std(axis=1, ddof=1)})
tab["cv"] = tab["sigma"] / tab["mu"]
tab["train_value"] = rev_train.loc[skus]
tab = tab.sort_values("train_value", ascending=False)
share = 100 * tab["train_value"] / tab["train_value"].sum(); prior = share.cumsum() - share
tab["abc"] = np.where(prior < 80, "A", np.where(prior < 95, "B", "C"))
tab["xyz"] = np.where(tab["cv"] < 1.0, "X", np.where(tab["cv"] < 2.0, "Y", "Z"))
tab["unit_cost"] = unit_cost.loc[tab.index]
nd = NormalDist()
tab["z"] = tab["abc"].map(lambda c: nd.inv_cdf(SERVICE[c]))
tab["eoq"] = np.ceil(np.sqrt(2 * tab["mu"] * 52 * ORDER_COST / (HOLD_RATE * tab["unit_cost"])))


def simulate(sku, policy):
    """Weekly-review (s, S) policy with lost sales. Returns metrics for the holdout window."""
    d_all = D.loc[sku].values; c = tab.loc[sku, "unit_cost"]
    hist_mu, hist_sd = tab.loc[sku, "mu"], tab.loc[sku, "sigma"]
    z, eoq = tab.loc[sku, "z"], tab.loc[sku, "eoq"]
    on_hand = None; pipeline = []; filled = short = orders = 0; inv_sum = 0.0
    for t in range(TRAIN_WEEKS, TRAIN_WEEKS + n_test):
        if policy == "adaptive":                                  # re-estimate from the latest 12 weeks
            w = d_all[t - 12:t]; mu, sd = w.mean(), w.std(ddof=1)
        else:
            mu, sd = hist_mu, hist_sd
        if policy == "naive":
            s_pt = mu * LEAD_WEEKS; big_s = s_pt + 4 * mu          # no safety stock, order up to 4 weeks of demand
        else:
            ss = z * sd * np.sqrt(LEAD_WEEKS + 1)
            s_pt = mu * LEAD_WEEKS + ss; big_s = s_pt + max(eoq, mu)
        if on_hand is None: on_hand = big_s
        on_hand += sum(q for a, q in pipeline if a == t); pipeline = [(a, q) for a, q in pipeline if a > t]
        f = min(d_all[t], on_hand); on_hand -= f; filled += f; short += d_all[t] - f
        pos = on_hand + sum(q for _, q in pipeline)
        if pos <= s_pt:
            pipeline.append((t + LEAD_WEEKS, big_s - pos)); orders += 1
        inv_sum += on_hand
    avg_inv = inv_sum / n_test
    return dict(sku=sku, abc=tab.loc[sku, "abc"], policy=policy, filled=filled, short=short, orders=orders, avg_inv_units=avg_inv,
                avg_inv_value=avg_inv * c, order_cost=orders * ORDER_COST, hold_cost=avg_inv * c * HOLD_RATE * n_test / 52,
                short_value=short * c)


rows = [simulate(s, p) for s in tab.index for p in ("naive", "static", "adaptive")]
R = pd.DataFrame(rows)
G = R.groupby("policy").agg(filled=("filled", "sum"), short=("short", "sum"), inv=("avg_inv_value", "sum"), orders=("orders", "sum"),
                            order_cost=("order_cost", "sum"), hold_cost=("hold_cost", "sum"), short_value=("short_value", "sum"))
G["fill_rate"] = 100 * G["filled"] / (G["filled"] + G["short"])
for pen in (STOCKOUT_PCT,):
    G["stockout_cost"] = G["short_value"] * pen
G["total_cost"] = G["order_cost"] + G["hold_cost"] + G["stockout_cost"]
order = ["naive", "static", "adaptive"]; G = G.loc[order]
names = {"naive": "Naive (no safety stock)", "static": "Optimized, static (trained once)", "adaptive": "Optimized, adaptive (12-wk rolling)"}
by_abc = R.groupby(["abc", "policy"]).apply(lambda g: 100 * g["filled"].sum() / (g["filled"].sum() + g["short"].sum()), include_groups=False).unstack()[order].round(1)

# ---------------- How different is the holdout from training? ----------------
tr_mean = train.sum(axis=0).mean(); te_mean = test.sum(axis=0).mean()
shift = pd.DataFrame({"train_mu": tab["mu"], "test_mu": test.mean(axis=1)}).loc[tab.index]
pct_up = 100 * (shift["test_mu"] > shift["train_mu"]).mean()

# ---------------- Sensitivity ----------------
sens = []
for pen in (0.0, 0.10, 0.25, 0.50, 1.00):
    tot = (G["order_cost"] + G["hold_cost"] + G["short_value"] * pen)
    sens.append([f"{int(pen * 100)}%"] + [f"£{tot[p]:,.0f}" for p in order] + [names[tot.idxmin()]])
sens = pd.DataFrame(sens, columns=["Stockout penalty (% of unit cost)"] + [names[p] for p in order] + ["Cheapest"])

# ---------------- Charts ----------------
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "font.size": 10})
wk = D.sum(axis=0)
fig, ax = plt.subplots(figsize=(8, 3.8))
ax.plot(wk.index, wk.values / 1000, color="black"); ax.axvline(weeks[TRAIN_WEEKS], color="gray", ls="--")
ax.text(weeks[TRAIN_WEEKS], ax.get_ylim()[1] * 0.92, "  holdout starts", fontsize=9)
ax.set_ylabel("Units per week (000s), top 150 products"); ax.set_title("Weekly demand: training window vs. holdout (real data)")
fig.tight_layout(); fig.savefig(OUT / "demand_train_vs_holdout.png", dpi=150); plt.close(fig)

fig, axs = plt.subplots(1, 2, figsize=(10, 4))
cols = ["#9ca3af", "#4b5563", "#111827"]
axs[0].bar([names[p].split(" (")[0] for p in order], G["fill_rate"], color=cols); axs[0].set_ylim(60, 100); axs[0].set_title("Holdout fill rate (%), axis starts at 60")
for i, p in enumerate(order): axs[0].text(i, G.loc[p, "fill_rate"] + 0.5, f"{G.loc[p, 'fill_rate']:.1f}", ha="center")
axs[1].bar([names[p].split(" (")[0] for p in order], G["inv"] / 1000, color=cols); axs[1].set_title("Average inventory value (£000, assumed unit cost)")
for a in axs: a.tick_params(axis="x", labelrotation=12)
fig.tight_layout(); fig.savefig(OUT / "policy_comparison.png", dpi=150); plt.close(fig)

tab.round(2).to_csv(OUT / "sku_policy_parameters.csv")
R.round(2).to_csv(OUT / "backtest_by_sku.csv", index=False)

cls = tab.groupby("abc").agg(skus=("mu", "size"), value_pct=("train_value", lambda v: 100 * v.sum() / tab["train_value"].sum())).round(1)
md = f"""# Backtest results (auto-generated; REAL demand, assumed costs)

Training: first {TRAIN_WEEKS} weeks (Dec 2010 – Sep 2011). Holdout: next {n_test} weeks (to early Dec 2011, includes the holiday peak). {N_SKU} top products.

## Did demand change between training and holdout?
Average weekly units (top {N_SKU} products): **{tr_mean:,.0f}** in training vs. **{te_mean:,.0f}** in holdout ({te_mean / tr_mean:.1f}x). {pct_up:.0f}% of products sold faster in the holdout than in training.

## ABC classification (training window)
{cls.to_markdown()}

## Policy comparison on the holdout
| Metric | {names['naive']} | {names['static']} | {names['adaptive']} |
|---|---|---|---|
| Fill rate | {G.loc['naive','fill_rate']:.1f}% | {G.loc['static','fill_rate']:.1f}% | {G.loc['adaptive','fill_rate']:.1f}% |
| Avg inventory value | £{G.loc['naive','inv']:,.0f} | £{G.loc['static','inv']:,.0f} | £{G.loc['adaptive','inv']:,.0f} |
| Orders placed | {G.loc['naive','orders']:,.0f} | {G.loc['static','orders']:,.0f} | {G.loc['adaptive','orders']:,.0f} |
| Ordering cost | £{G.loc['naive','order_cost']:,.0f} | £{G.loc['static','order_cost']:,.0f} | £{G.loc['adaptive','order_cost']:,.0f} |
| Holding cost | £{G.loc['naive','hold_cost']:,.0f} | £{G.loc['static','hold_cost']:,.0f} | £{G.loc['adaptive','hold_cost']:,.0f} |
| Stockout cost | £{G.loc['naive','stockout_cost']:,.0f} | £{G.loc['static','stockout_cost']:,.0f} | £{G.loc['adaptive','stockout_cost']:,.0f} |
| **Total cost** | **£{G.loc['naive','total_cost']:,.0f}** | **£{G.loc['static','total_cost']:,.0f}** | **£{G.loc['adaptive','total_cost']:,.0f}** |

## Fill rate by ABC class (%)
{by_abc.rename(columns=names).to_markdown()}

## Sensitivity to the stockout-penalty assumption
{sens.to_markdown(index=False)}
"""
(OUT / "results.md").write_text(md)
print(md)
