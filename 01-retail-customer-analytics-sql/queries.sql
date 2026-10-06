-- name: monthly
-- Monthly revenue, orders, and active customers (Dec 2011 is partial, so it is excluded)
SELECT month,
       ROUND(SUM(revenue)) AS revenue,
       COUNT(DISTINCT invoice_no) AS orders,
       COUNT(DISTINCT customer_id) AS customers
FROM sales
WHERE month < '2011-12'
GROUP BY month
ORDER BY month;

-- name: top_products
SELECT stock_code,
       MAX(description) AS description,
       SUM(quantity) AS units,
       ROUND(SUM(revenue)) AS revenue
FROM sales
GROUP BY stock_code
ORDER BY revenue DESC
LIMIT 10;

-- name: countries
SELECT country,
       ROUND(SUM(revenue)) AS revenue,
       ROUND(100.0 * SUM(revenue) / (SELECT SUM(revenue) FROM sales), 1) AS pct_of_revenue
FROM sales
GROUP BY country
ORDER BY revenue DESC
LIMIT 8;

-- name: cohorts
-- Cohort retention: customers grouped by the month of their first purchase,
-- then counted by how many months later they bought again.
WITH first_purchase AS (
    SELECT customer_id, MIN(month) AS cohort
    FROM sales WHERE customer_id IS NOT NULL
    GROUP BY customer_id
),
activity AS (
    SELECT DISTINCT customer_id, month
    FROM sales WHERE customer_id IS NOT NULL AND month < '2011-12'
)
SELECT f.cohort,
       (CAST(substr(a.month, 1, 4) AS INT) * 12 + CAST(substr(a.month, 6, 2) AS INT))
     - (CAST(substr(f.cohort, 1, 4) AS INT) * 12 + CAST(substr(f.cohort, 6, 2) AS INT)) AS months_since,
       COUNT(DISTINCT a.customer_id) AS customers
FROM first_purchase f
JOIN activity a USING (customer_id)
WHERE f.cohort < '2011-12'
GROUP BY f.cohort, months_since
ORDER BY f.cohort, months_since;

-- name: rfm
-- RFM scoring: Recency (days since last order), Frequency (orders), Monetary (revenue),
-- each scored 1-4 using NTILE window functions.
WITH base AS (
    SELECT customer_id,
           MAX(date(invoice_date)) AS last_date,
           COUNT(DISTINCT invoice_no) AS frequency,
           SUM(revenue) AS monetary
    FROM sales
    WHERE customer_id IS NOT NULL
    GROUP BY customer_id
)
SELECT customer_id, frequency, ROUND(monetary, 2) AS monetary,
       CAST(julianday('2011-12-10') - julianday(last_date) AS INT) AS recency_days,
       NTILE(4) OVER (ORDER BY julianday(last_date)) AS r,
       NTILE(4) OVER (ORDER BY frequency, monetary) AS f,
       NTILE(4) OVER (ORDER BY monetary) AS m
FROM base;
