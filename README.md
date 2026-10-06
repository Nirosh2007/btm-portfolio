# BTM Portfolio

Projects built to practice the work done in Business Technology Management roles: data analytics, SQL, supply chain, project management, product management, and process improvement.

## Data transparency
- **Projects 1, 2, and 5 use REAL public data:** the UCI *Online Retail* dataset (541,909 transactions from a UK online retailer, 2010–2011). Citation is in [`common/retail.py`](common/retail.py).
- Cost inputs that aren't in that dataset (unit cost, order cost, lead time, etc.) are **stated assumptions**, labeled in each README.
- **Projects 3, 6, and 7 are case studies** with assumed numbers and hypotheses. **Project 4** uses illustrative assumptions. None contain real personal or company data.

| # | Project | Data | Skills | Stack |
|---|---|---|---|---|
| 1 | [Retail Customer Analytics](01-retail-customer-analytics-sql) | **Real** (541,909 lines) | SQL (CTEs, window functions), cohort retention, RFM segmentation | SQLite, Python, pandas |
| 2 | [Data Quality Audit](02-retail-data-quality-audit) | **Real** | Profiling, root-cause analysis, impact quantification, cleaning pipeline | Python, pandas |
| 3 | [Registration Process Improvement](03-mdba-registration-process-improvement) | Case study | Requirements, process mapping, user stories, RACI, KPIs | Markdown, Mermaid |
| 4 | [Rental Property Analyzer](04-ontario-rental-property-analyzer) | Assumptions | Financial modeling, sensitivity analysis, unit testing | Python |
| 5 | [Inventory Policy Backtest](05-inventory-optimization-real-demand) | **Real** demand + assumed costs | ABC/XYZ, safety stock, EOQ, train/holdout backtest | Python, pandas |
| 6 | [Project Management Plan](06-project-management-tournament-plan) | Case study | Charter, WBS, critical path, risk register, budget | Python, Markdown |
| 7 | [Product Management Case](07-product-management-concept) | Case study | Discovery, RICE, MVP scope, PRD, metrics | Markdown |

Every result is already saved in each project folder, so you can read the work without running anything.

## Run it (optional)
```bash
git clone <your-repo-url>
cd btm-portfolio
pip install -r requirements.txt
cd 01-retail-customer-analytics-sql && python analysis.py   # downloads the dataset on first run
```

## About
Business Technology Management student at Toronto Metropolitan University (Ted Rogers School of Management).
