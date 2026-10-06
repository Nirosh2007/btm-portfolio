# Findings (auto-generated from the real UCI Online Retail data)

- **Scale:** £9,850,003 revenue from 19,636 invoices across 38 countries (valid sale lines only, see the data-quality project for how "valid" is defined).
- **Seasonality:** November 2011 revenue (£1,441,113) was 2.5x the Jan–Mar 2011 monthly average (£581,725).
- **Geography:** United Kingdom accounts for 84.8% of revenue.
- **Top product:** REGENCY CAKESTAND 3 TIER (£169,506).
- **Retention:** on average, 21.3% of a cohort buys again in month 1 and 26.8% in month 6.
- **Concentration:** the top 27% of identified customers (1,167 of 4,322) generate 80% of identified-customer revenue.
- **RFM:** Champions are 19% of customers but 57% of revenue.

## Top products by revenue
| stock_code   | description                        |   units |   revenue |
|:-------------|:-----------------------------------|--------:|----------:|
| 22423        | REGENCY CAKESTAND 3 TIER           |   13445 |    169506 |
| 47566        | PARTY BUNTING                      |   18090 |     98610 |
| 85123A       | WHITE HANGING HEART T-LIGHT HOLDER |   35117 |     97989 |
| 85099B       | JUMBO BAG RED RETROSPOT            |   47488 |     92642 |
| 23084        | RABBIT NIGHT LIGHT                 |   30709 |     66808 |
| 22086        | PAPER CHAIN KIT 50'S CHRISTMAS     |   18922 |     63835 |
| 84879        | ASSORTED COLOUR BIRD ORNAMENT      |   36333 |     58879 |
| 79321        | CHILLI LIGHTS                      |   10225 |     53762 |
| 22197        | SMALL POPCORN HOLDER               |   56673 |     51169 |
| 22502        | PICNIC BASKET WICKER SMALL         |    1868 |     51058 |

## Top countries
| country        |         revenue |   pct_of_revenue |
|:---------------|----------------:|-----------------:|
| United Kingdom |      8.3503e+06 |             84.8 |
| Netherlands    | 283480          |              2.9 |
| EIRE           | 261562          |              2.7 |
| Germany        | 203600          |              2.1 |
| France         | 182697          |              1.9 |
| Australia      | 137063          |              1.4 |
| Switzerland    |  52713          |              0.5 |
| Spain          |  51983          |              0.5 |

## RFM segments
| segment                 |   customers |          revenue |   pct_customers |   pct_revenue |
|:------------------------|------------:|-----------------:|----------------:|--------------:|
| Champions               |         807 |      4.77014e+06 |            18.7 |          57.2 |
| Loyal                   |         700 |      1.64404e+06 |            16.2 |          19.7 |
| At risk (were frequent) |         653 |      1.08225e+06 |            15.1 |          13   |
| Occasional              |        1048 | 449486           |            24.2 |           5.4 |
| Lost                    |         906 | 312326           |            21   |           3.7 |
| Recent / new            |         208 |  82163.6         |             4.8 |           1   |
