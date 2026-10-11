-- ============================================================
-- Retail Transaction Analytics
-- MySQL Analytics Queries
-- Database: retail_analytics
-- Table: transactions
-- ============================================================


-- ============================================================
-- 1. OVERALL BUSINESS KPIs
-- ============================================================

SELECT
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT stock_code) AS unique_products,
    COUNT(DISTINCT country) AS unique_countries,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue,
    AVG(transaction_value) AS average_transaction_value
FROM transactions;


-- ============================================================
-- 2. REVENUE BY COUNTRY
-- ============================================================

SELECT
    country,
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    COUNT(DISTINCT customer_id) AS unique_customers,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY country
ORDER BY total_revenue DESC;


-- ============================================================
-- 3. TOP 10 COUNTRIES BY REVENUE
-- ============================================================

SELECT
    country,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY country
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- 4. TOP 10 PRODUCTS BY REVENUE
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY stock_code
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- 5. TOP 10 PRODUCTS BY QUANTITY SOLD
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY stock_code
ORDER BY total_quantity DESC
LIMIT 10;


-- ============================================================
-- 6. CUSTOMER REVENUE RANKING
-- ============================================================

SELECT
    customer_id,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- 7. MONTHLY SALES TREND
-- ============================================================

SELECT
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY DATE_FORMAT(invoice_date, '%Y-%m')
ORDER BY month;


-- ============================================================
-- 8. MONTHLY AVERAGE ORDER VALUE
-- ============================================================

SELECT
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(transaction_value) AS total_revenue,
    SUM(transaction_value) / COUNT(DISTINCT invoice_no)
        AS average_order_value
FROM transactions
GROUP BY DATE_FORMAT(invoice_date, '%Y-%m')
ORDER BY month;


-- ============================================================
-- 9. YEARLY SALES TREND
-- ============================================================

SELECT
    YEAR(invoice_date) AS year,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY YEAR(invoice_date)
ORDER BY year;


-- ============================================================
-- 10. YEAR AND MONTH SALES TREND
-- ============================================================

SELECT
    YEAR(invoice_date) AS year,
    MONTH(invoice_date) AS month_number,
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY
    YEAR(invoice_date),
    MONTH(invoice_date),
    DATE_FORMAT(invoice_date, '%Y-%m')
ORDER BY year, month_number;


-- ============================================================
-- 11. SALES BY COUNTRY AND MONTH
-- ============================================================

SELECT
    country,
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue,
    COUNT(DISTINCT invoice_no) AS unique_invoices
FROM transactions
GROUP BY
    country,
    DATE_FORMAT(invoice_date, '%Y-%m')
ORDER BY
    country,
    month;


-- ============================================================
-- 12. PRODUCT PERFORMANCE BY MONTH
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY
    stock_code,
    DATE_FORMAT(invoice_date, '%Y-%m')
ORDER BY
    stock_code,
    month;


-- ============================================================
-- 13. PRODUCT PERFORMANCE SUMMARY
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    COUNT(DISTINCT invoice_no) AS order_count,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue,
    AVG(unit_price) AS average_unit_price
FROM transactions
GROUP BY stock_code
ORDER BY total_revenue DESC;


-- ============================================================
-- 14. PRODUCTS WITH NEGATIVE SALES QUANTITY
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue,
    SUM(
        CASE
            WHEN is_negative_quantity = 1 THEN 1
            ELSE 0
        END
    ) AS negative_quantity_records
FROM transactions
GROUP BY stock_code
HAVING negative_quantity_records > 0
ORDER BY negative_quantity_records DESC;


-- ============================================================
-- 15. CANCELLED-INVOICE SUMMARY
-- ============================================================

SELECT
    is_cancelled_invoice,
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY is_cancelled_invoice
ORDER BY is_cancelled_invoice;


-- ============================================================
-- 16. NEGATIVE-QUANTITY SUMMARY
-- ============================================================

SELECT
    is_negative_quantity,
    COUNT(*) AS transaction_records,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY is_negative_quantity
ORDER BY is_negative_quantity;


-- ============================================================
-- 17. ZERO-PRICE TRANSACTIONS
-- ============================================================

SELECT
    COUNT(*) AS zero_price_records,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity
FROM transactions
WHERE unit_price = 0;


-- ============================================================
-- 18. ZERO-PRICE TRANSACTIONS BY PRODUCT
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    COUNT(*) AS zero_price_records,
    SUM(quantity) AS total_quantity
FROM transactions
WHERE unit_price = 0
GROUP BY stock_code
ORDER BY zero_price_records DESC;


-- ============================================================
-- 19. TRANSACTIONS WITH MISSING CUSTOMER ID
-- ============================================================

SELECT
    COUNT(*) AS records_without_customer,
    COUNT(DISTINCT invoice_no) AS invoices_without_customer,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
WHERE customer_id IS NULL;


-- ============================================================
-- 20. CUSTOMER MONTHLY SPENDING
-- ============================================================

SELECT
    customer_id,
    DATE_FORMAT(invoice_date, '%Y-%m') AS month,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
WHERE customer_id IS NOT NULL
GROUP BY
    customer_id,
    DATE_FORMAT(invoice_date, '%Y-%m')
ORDER BY
    customer_id,
    month;


-- ============================================================
-- 21. TOP CUSTOMERS BY ORDER COUNT
-- ============================================================

SELECT
    customer_id,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(transaction_value) AS total_revenue
FROM transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY total_orders DESC
LIMIT 10;


-- ============================================================
-- 22. TOP CUSTOMERS BY REVENUE
-- ============================================================

SELECT
    customer_id,
    COUNT(DISTINCT invoice_no) AS total_orders,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
WHERE customer_id IS NOT NULL
GROUP BY customer_id
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- 23. AVERAGE ORDER VALUE
-- ============================================================

SELECT
    SUM(transaction_value)
        / COUNT(DISTINCT invoice_no) AS average_order_value
FROM transactions;


-- ============================================================
-- 24. ORDER-LEVEL SALES
-- ============================================================

SELECT
    invoice_no,
    MIN(invoice_date) AS invoice_date,
    MAX(customer_id) AS customer_id,
    MAX(country) AS country,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS order_value
FROM transactions
GROUP BY invoice_no
ORDER BY order_value DESC;


-- ============================================================
-- 25. TOP 10 ORDERS BY VALUE
-- ============================================================

SELECT
    invoice_no,
    MIN(invoice_date) AS invoice_date,
    MAX(customer_id) AS customer_id,
    MAX(country) AS country,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS order_value
FROM transactions
GROUP BY invoice_no
ORDER BY order_value DESC
LIMIT 10;


-- ============================================================
-- 26. DAILY REVENUE TREND
-- ============================================================

SELECT
    DATE(invoice_date) AS sales_date,
    COUNT(DISTINCT invoice_no) AS unique_invoices,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue
FROM transactions
GROUP BY DATE(invoice_date)
ORDER BY sales_date;


-- ============================================================
-- 27. COUNTRY SALES SHARE
-- ============================================================

SELECT
    country,
    SUM(transaction_value) AS total_revenue,
    ROUND(
        SUM(transaction_value) /
        (
            SELECT SUM(transaction_value)
            FROM transactions
        ) * 100,
        2
    ) AS revenue_percentage
FROM transactions
GROUP BY country
ORDER BY total_revenue DESC;


-- ============================================================
-- 28. PRODUCT REVENUE SHARE
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    SUM(transaction_value) AS total_revenue,
    ROUND(
        SUM(transaction_value) /
        (
            SELECT SUM(transaction_value)
            FROM transactions
        ) * 100,
        2
    ) AS revenue_percentage
FROM transactions
GROUP BY stock_code
ORDER BY total_revenue DESC
LIMIT 10;


-- ============================================================
-- 29. PRODUCTS WITH DECLINING SALES
-- ============================================================
-- Compare the first and last available month for each product.

WITH monthly_product_sales AS (
    SELECT
        stock_code,
        DATE_FORMAT(invoice_date, '%Y-%m') AS month,
        SUM(transaction_value) AS monthly_revenue
    FROM transactions
    GROUP BY
        stock_code,
        DATE_FORMAT(invoice_date, '%Y-%m')
),

product_periods AS (
    SELECT
        stock_code,
        MIN(month) AS first_month,
        MAX(month) AS last_month
    FROM monthly_product_sales
    GROUP BY stock_code
)

SELECT
    p.stock_code,
    MAX(t.description) AS description,
    p.first_month,
    p.last_month,

    MAX(
        CASE
            WHEN m.month = p.first_month
            THEN m.monthly_revenue
        END
    ) AS first_month_revenue,

    MAX(
        CASE
            WHEN m.month = p.last_month
            THEN m.monthly_revenue
        END
    ) AS last_month_revenue

FROM product_periods p
JOIN monthly_product_sales m
    ON p.stock_code = m.stock_code
JOIN transactions t
    ON p.stock_code = t.stock_code

GROUP BY
    p.stock_code,
    p.first_month,
    p.last_month

HAVING last_month_revenue < first_month_revenue

ORDER BY
    (last_month_revenue - first_month_revenue) ASC
LIMIT 20;


-- ============================================================
-- 30. UNUSUAL TRANSACTION PATTERNS
-- ============================================================

SELECT
    stock_code,
    MAX(description) AS description,
    COUNT(*) AS transaction_records,
    SUM(quantity) AS total_quantity,
    SUM(transaction_value) AS total_revenue,
    SUM(
        CASE
            WHEN quantity < 0 THEN 1
            ELSE 0
        END
    ) AS negative_quantity_records,
    SUM(
        CASE
            WHEN unit_price = 0 THEN 1
            ELSE 0
        END
    ) AS zero_price_records
FROM transactions
GROUP BY stock_code
HAVING
    negative_quantity_records > 0
    OR zero_price_records > 0
ORDER BY
    negative_quantity_records DESC,
    zero_price_records DESC
LIMIT 20;


-- ============================================================
-- 31. DATA QUALITY SUMMARY
-- ============================================================

SELECT
    COUNT(*) AS total_records,

    SUM(
        CASE
            WHEN description IS NULL THEN 1
            ELSE 0
        END
    ) AS missing_description,

    SUM(
        CASE
            WHEN customer_id IS NULL THEN 1
            ELSE 0
        END
    ) AS missing_customer_id,

    SUM(
        CASE
            WHEN quantity < 0 THEN 1
            ELSE 0
        END
    ) AS negative_quantity,

    SUM(
        CASE
            WHEN unit_price = 0 THEN 1
            ELSE 0
        END
    ) AS zero_price,

    SUM(
        CASE
            WHEN is_cancelled_invoice = 1 THEN 1
            ELSE 0
        END
    ) AS cancelled_invoice_records

FROM transactions;


-- ============================================================
-- 32. DATASET DATE RANGE
-- ============================================================

SELECT
    MIN(invoice_date) AS earliest_transaction,
    MAX(invoice_date) AS latest_transaction,
    DATEDIFF(
        MAX(invoice_date),
        MIN(invoice_date)
    ) AS dataset_days
FROM transactions;