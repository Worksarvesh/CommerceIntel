-- CommerceIntel Analytics Platform - Analytical Queries

-- 1. Monthly revenue trend
SELECT
    strftime('%Y-%m', order_date) AS year_month,
    SUM(order_total) AS total_revenue,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS active_customers
FROM orders
GROUP BY year_month
ORDER BY year_month;

-- 2. Top 20 products by revenue
SELECT
    p.stock_code,
    p.description,
    p.category,
    SUM(t.revenue) AS total_revenue,
    SUM(t.quantity) AS total_quantity
FROM transactions t
JOIN products p ON t.stock_code = p.stock_code
GROUP BY p.stock_code, p.description, p.category
ORDER BY total_revenue DESC
LIMIT 20;

-- 3. Top 20 customers by lifetime value
SELECT
    c.customer_id,
    c.country,
    COUNT(DISTINCT o.order_id) AS total_orders,
    SUM(o.order_total) AS customer_lifetime_value
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.country
ORDER BY customer_lifetime_value DESC
LIMIT 20;

-- 4. Category performance
SELECT
    category,
    SUM(revenue) AS total_revenue,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT stock_code) AS unique_products
FROM transactions
WHERE category IS NOT NULL
GROUP BY category
ORDER BY total_revenue DESC;

-- 5. Customer purchase frequency distribution
SELECT
    order_bucket,
    COUNT(*) AS customer_count
FROM (
    SELECT
        customer_id,
        CASE
            WHEN total_orders = 1 THEN '1 order'
            WHEN total_orders BETWEEN 2 AND 3 THEN '2-3 orders'
            WHEN total_orders BETWEEN 4 AND 6 THEN '4-6 orders'
            ELSE '7+ orders'
        END AS order_bucket
    FROM (
        SELECT customer_id, COUNT(DISTINCT order_id) AS total_orders
        FROM orders
        GROUP BY customer_id
    )
)
GROUP BY order_bucket;

-- 6. Average order value by country
SELECT
    country,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(AVG(order_total), 2) AS avg_order_value,
    ROUND(SUM(order_total), 2) AS total_revenue
FROM orders
GROUP BY country
ORDER BY total_revenue DESC;

-- 7. Repeat purchase rate
SELECT
    ROUND(
        100.0 * SUM(CASE WHEN total_orders > 1 THEN 1 ELSE 0 END) / COUNT(*),
        2
    ) AS repeat_customer_rate_pct
FROM (
    SELECT customer_id, COUNT(DISTINCT order_id) AS total_orders
    FROM orders
    GROUP BY customer_id
);

-- 8. Revenue by day of week
SELECT
    CASE CAST(strftime('%w', order_date) AS INTEGER)
        WHEN 0 THEN 'Sunday'
        WHEN 1 THEN 'Monday'
        WHEN 2 THEN 'Tuesday'
        WHEN 3 THEN 'Wednesday'
        WHEN 4 THEN 'Thursday'
        WHEN 5 THEN 'Friday'
        WHEN 6 THEN 'Saturday'
    END AS day_of_week,
    SUM(order_total) AS total_revenue
FROM orders
GROUP BY strftime('%w', order_date)
ORDER BY strftime('%w', order_date);
