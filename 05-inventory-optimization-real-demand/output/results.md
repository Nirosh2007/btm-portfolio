# Backtest results (auto-generated; REAL demand, assumed costs)

Training: first 40 weeks (Dec 2010 – Sep 2011). Holdout: next 13 weeks (to early Dec 2011, includes the holiday peak). 150 top products.

## Did demand change between training and holdout?
Average weekly units (top 150 products): **24,522** in training vs. **35,068** in holdout (1.4x). 66% of products sold faster in the holdout than in training.

## ABC classification (training window)
| abc   |   skus |   value_pct |
|:------|-------:|------------:|
| A     |    100 |        80.4 |
| B     |     37 |        14.9 |
| C     |     13 |         4.7 |

## Policy comparison on the holdout
| Metric | Naive (no safety stock) | Optimized, static (trained once) | Optimized, adaptive (12-wk rolling) |
|---|---|---|---|
| Fill rate | 80.0% | 93.9% | 97.4% |
| Avg inventory value | £101,519 | £328,627 | £334,911 |
| Orders placed | 409 | 194 | 216 |
| Ordering cost | £16,360 | £7,760 | £8,640 |
| Holding cost | £5,584 | £18,074 | £18,420 |
| Stockout cost | £74,041 | £21,238 | £10,866 |
| **Total cost** | **£95,985** | **£47,072** | **£37,926** |

## Fill rate by ABC class (%)
| abc   |   Naive (no safety stock) |   Optimized, static (trained once) |   Optimized, adaptive (12-wk rolling) |
|:------|--------------------------:|-----------------------------------:|--------------------------------------:|
| A     |                      84.3 |                               97.1 |                                  98.8 |
| B     |                      61.8 |                               79.3 |                                  91.4 |
| C     |                      82   |                               97.6 |                                  98.1 |

## Sensitivity to the stockout-penalty assumption
| Stockout penalty (% of unit cost)   | Naive (no safety stock)   | Optimized, static (trained once)   | Optimized, adaptive (12-wk rolling)   | Cheapest                            |
|:------------------------------------|:--------------------------|:-----------------------------------|:--------------------------------------|:------------------------------------|
| 0%                                  | £21,944                   | £25,834                            | £27,060                               | Naive (no safety stock)             |
| 10%                                 | £36,752                   | £30,082                            | £29,233                               | Optimized, adaptive (12-wk rolling) |
| 25%                                 | £58,964                   | £36,453                            | £32,493                               | Optimized, adaptive (12-wk rolling) |
| 50%                                 | £95,985                   | £47,072                            | £37,926                               | Optimized, adaptive (12-wk rolling) |
| 100%                                | £170,026                  | £68,310                            | £48,792                               | Optimized, adaptive (12-wk rolling) |
