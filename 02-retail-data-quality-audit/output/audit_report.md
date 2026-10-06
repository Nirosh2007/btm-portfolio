# Audit results (real data: UCI Online Retail, 541,909 lines)

## Issue inventory
| issue                                        |   lines |   pct_of_lines | note                                                        |
|:---------------------------------------------|--------:|---------------:|:------------------------------------------------------------|
| Missing CustomerID                           |  135080 |          24.93 | Cannot be used for customer-level analysis (retention, RFM) |
| Missing Description                          |    1454 |           0.27 | Product cannot be identified by name                        |
| Cancellation lines (InvoiceNo starts with C) |    9288 |           1.71 | Negative quantities; must not be counted as sales           |
| Non-positive quantity, not a cancellation    |    1336 |           0.25 | Stock adjustments, damaged or lost goods                    |
| Non-positive unit price                      |    2517 |           0.46 | Zero-price lines (often adjustments or free items)          |
| Non-product stock codes                      |    2995 |           0.55 | Postage, fees, manual entries, samples, not merchandise     |
| Exact duplicate rows                         |    5268 |           0.97 | Identical on all 8 fields                                   |
| Stock codes with >1 description              |  112742 |          20.8  | Same product coded with different names                     |

## Cleaning waterfall
| Step | Lines removed | Positive revenue removed (£) |
|---|---:|---:|
| Cancellation lines | 9,288 | 0 |
| Non-positive quantity (adjustments) | 1,336 | 0 |
| Non-positive unit price | 1,181 | 0 |
| Non-product stock codes (postage, fees, manual) | 2,379 | 395,650 |
| Exact duplicate rows | 5,221 | 24,214 |
| Originals later fully cancelled (matched by customer, product, qty) | 3,075 | 396,817 |

**Result:** 519,429 analysis-ready lines (95.9% of raw). Positive line value fell from £10,666,685 to £9,850,003, so **7.7% of apparent revenue was not real merchandise sales** (cancellations, fees, postage, and fully cancelled orders).

## Extreme quantities (qty > 10,000, sale lines only)
|   InvoiceNo |   StockCode | Description                    |   Quantity |   UnitPrice |   CustomerID | InvoiceDate         | later_cancelled   |
|------------:|------------:|:-------------------------------|-----------:|------------:|-------------:|:--------------------|:------------------|
|      541431 |       23166 | MEDIUM CERAMIC TOP STORAGE JAR |      74215 |        1.04 |        12346 | 2011-01-18 10:01:00 | True              |
|      578841 |       84826 | ASSTD DESIGN 3D PAPER STICKERS |      12540 |        0    |        13256 | 2011-11-25 15:57:00 | False             |
|      581483 |       23843 | PAPER CRAFT , LITTLE BIRDIE    |      80995 |        2.08 |        16446 | 2011-12-09 09:15:00 | True              |

## Where missing CustomerIDs concentrate
- 24.9% of all lines have no CustomerID. They represent 15.3% of analysis-ready revenue.
- Average value per line: £21.49 with a CustomerID vs. £11.49 without.

| Country        |   lines |   pct_missing |
|:---------------|--------:|--------------:|
| United Kingdom |  495478 |          27   |
| EIRE           |    8196 |           8.7 |
| Switzerland    |    2002 |           6.2 |
| Portugal       |    1519 |           2.6 |
| France         |    8557 |           0.8 |
| Belgium        |    2069 |           0   |

## Most frequent non-product stock codes
| StockCode   |   lines |   net_value |
|:------------|--------:|------------:|
| POST        |    1256 |       66231 |
| DOT         |     710 |      206245 |
| M           |     571 |      -68674 |
| C2          |     144 |        6986 |
| D           |      77 |       -5696 |
| S           |      63 |       -3049 |
