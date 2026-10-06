"""Shared loader and cleaning rules for the UCI "Online Retail" dataset.

Source: UCI Machine Learning Repository, "Online Retail" (donated by Dr. Daqing Chen).
541,909 line items from a UK-based online gift retailer, 2010-12-01 to 2011-12-09.
Cite: Chen, D., Sain, S.L., & Guo, K. (2012). Data mining for the online retail industry:
A case study of RFM model-based customer segmentation using data mining. Journal of Database
Marketing & Customer Strategy Management, 19(3), 197-208. doi:10.1057/dbm.2012.17

If you don't have the data locally, load_raw() downloads a copy from the 'onlineretail' R package
on GitHub (which includes the data with the donor's permission) and caches it in ./data/.
You can also download the original from the UCI page and save it as data/online_retail.csv.gz.
"""
from pathlib import Path
import re
import tarfile
import tempfile
import urllib.request

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CSV = DATA / "online_retail.csv.gz"
MIRROR = "https://codeload.github.com/allanvc/onlineretail/tar.gz/HEAD"
PRODUCT_CODE = re.compile(r"^\d{5}[A-Za-z]*$")   # real products are 5 digits + optional letter


def download() -> None:
    import pyreadr  # pip install pyreadr
    DATA.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        tgz = Path(tmp) / "repo.tgz"
        urllib.request.urlretrieve(MIRROR, tgz)
        with tarfile.open(tgz) as t:
            t.extractall(tmp)
        rda = next(Path(tmp).rglob("onlineretail.rda"))
        df = list(pyreadr.read_r(str(rda)).values())[0]
    df.to_csv(CSV, index=False, compression="gzip")


def load_raw() -> pd.DataFrame:
    if not CSV.exists():
        download()
    return pd.read_csv(CSV, dtype={"InvoiceNo": str, "StockCode": str}, parse_dates=["InvoiceDate"])


def match_cancelled(df: pd.DataFrame) -> pd.Index:
    """Index of original sale lines that were fully cancelled later.

    A cancellation (InvoiceNo starting with 'C') is matched to an earlier sale by the same customer,
    same product, and the same quantity. Partial returns are NOT matched.
    """
    known = df["CustomerID"].notna()
    cancels = df[known & df["InvoiceNo"].str.startswith("C")].copy()
    sales = df[known & ~df["InvoiceNo"].str.startswith("C") & (df["Quantity"] > 0)].copy()
    cancels["qty"] = -cancels["Quantity"]
    key = ["CustomerID", "StockCode"]
    need = cancels.groupby(key + ["qty"]).size().rename("n_cancel").reset_index()
    sales = sales.merge(need, left_on=key + ["Quantity"], right_on=key + ["qty"], how="left")
    sales.index = df[known & ~df["InvoiceNo"].str.startswith("C") & (df["Quantity"] > 0)].index
    sales = sales[sales["n_cancel"].notna()].sort_values("InvoiceDate")
    sales["rank"] = sales.groupby(key + ["Quantity"]).cumcount() + 1
    return sales[sales["rank"] <= sales["n_cancel"]].index


def clean_sales(df: pd.DataFrame, net_cancellations: bool = True) -> pd.DataFrame:
    """Valid sale lines: not a cancellation, positive quantity and price, real product code,
    and (optionally) not later fully cancelled."""
    ok = (
        ~df["InvoiceNo"].str.startswith("C")
        & (df["Quantity"] > 0)
        & (df["UnitPrice"] > 0)
        & df["StockCode"].str.match(PRODUCT_CODE)
    )
    out = df[ok & ~df.duplicated(keep="first")].copy()        # exact duplicates first, same order as the audit
    if net_cancellations:
        out = out.drop(index=match_cancelled(df).intersection(out.index))
    out["Revenue"] = out["Quantity"] * out["UnitPrice"]
    out["Month"] = out["InvoiceDate"].dt.strftime("%Y-%m")
    return out
