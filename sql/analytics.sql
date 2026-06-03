/* ============================================================
   Healthcare Data Engineering Project
   Phase 3: SQL Analytics
   Database: Oracle 23ai | Schema: FREEPDB1
   ============================================================ */


/* ============================================================
   SECTION 1: SALES ANALYTICS
   ============================================================ */

-- Query 1: Total Revenue by Store with Ranking
-- Business Question: Which stores are generating the most revenue?
SELECT
    s.store_id,
    sl.store_name,
    sl.state,
    sl.region,
    COUNT(s.transaction_id)                          AS total_transactions,
    SUM(s.total_amount)                              AS total_revenue,
    ROUND(AVG(s.total_amount), 2)                    AS avg_transaction_value,
    RANK() OVER (ORDER BY SUM(s.total_amount) DESC)  AS revenue_rank
FROM
    stg_sales_transactions s
    JOIN stg_store_locations sl ON s.store_id = sl.store_id
GROUP BY
    s.store_id, sl.store_name, sl.state, sl.region
ORDER BY
    revenue_rank;


-- Query 2: Revenue by Store WITHIN Each Region
-- Business Question: Who is the top store in each region?
SELECT
    store_id,
    store_name,
    region,
    total_revenue,
    RANK() OVER (
        PARTITION BY region
        ORDER BY total_revenue DESC
    ) AS rank_in_region
FROM (
    SELECT
        s.store_id,
        sl.store_name,
        sl.region,
        SUM(s.total_amount) AS total_revenue
    FROM
        stg_sales_transactions s
        JOIN stg_store_locations sl ON s.store_id = sl.store_id
    GROUP BY
        s.store_id, sl.store_name, sl.region
)
ORDER BY
    region, rank_in_region;


-- Query 3: Monthly Sales Trend with Running Total
-- Business Question: How are sales trending month by month?
SELECT
    TO_CHAR(transaction_date, 'YYYY-MM')             AS sale_month,
    COUNT(transaction_id)                             AS total_transactions,
    ROUND(SUM(total_amount), 2)                       AS monthly_revenue,
    ROUND(AVG(total_amount), 2)                       AS avg_sale_value,
    ROUND(SUM(SUM(total_amount)) OVER (
        ORDER BY TO_CHAR(transaction_date, 'YYYY-MM')
    ), 2)                                             AS running_total_revenue,
    ROUND(SUM(total_amount) - LAG(SUM(total_amount)) OVER (
        ORDER BY TO_CHAR(transaction_date, 'YYYY-MM')
    ), 2)                                             AS revenue_vs_last_month
FROM
    stg_sales_transactions
GROUP BY
    TO_CHAR(transaction_date, 'YYYY-MM')
ORDER BY
    sale_month;


-- Query 4: Top 5 Product Categories by Revenue
-- Business Question: Which product categories drive the most sales?
SELECT
    p.category,
    COUNT(s.transaction_id)              AS total_transactions,
    SUM(s.quantity)                      AS total_units_sold,
    ROUND(SUM(s.total_amount), 2)        AS total_revenue,
    ROUND(AVG(s.total_amount), 2)        AS avg_sale_value,
    ROUND(SUM(s.total_amount) * 100 /
        SUM(SUM(s.total_amount)) OVER (), 2) AS revenue_pct
FROM
    stg_sales_transactions s
    JOIN stg_products p ON s.product_id = p.product_id
GROUP BY
    p.category
ORDER BY
    total_revenue DESC
FETCH FIRST 5 ROWS ONLY;


-- Query 5: Payment Method Breakdown
-- Business Question: How are customers paying?
SELECT
    payment_method,
    COUNT(transaction_id)                AS total_transactions,
    ROUND(SUM(total_amount), 2)          AS total_revenue,
    ROUND(AVG(total_amount), 2)          AS avg_transaction,
    ROUND(COUNT(transaction_id) * 100 /
        SUM(COUNT(transaction_id)) OVER (), 2) AS pct_of_transactions
FROM
    stg_sales_transactions
GROUP BY
    payment_method
ORDER BY
    total_transactions DESC;


/* ============================================================
   SECTION 2: PHARMACY ANALYTICS
   ============================================================ */

-- Query 6: Top 10 Most Prescribed Drugs
-- Business Question: Which drugs are dispensed the most?
SELECT
    drug_name,
    condition,
    COUNT(rx_id)                                     AS total_prescriptions,
    SUM(quantity_dispensed)                          AS total_units_dispensed,
    ROUND(AVG(copay_amount), 2)                      AS avg_copay,
    ROUND(AVG(retail_price), 2)                      AS avg_retail_price,
    ROUND(AVG(retail_price - copay_amount), 2)       AS avg_insurance_paid,
    RANK() OVER (ORDER BY COUNT(rx_id) DESC)         AS prescription_rank
FROM
    stg_prescription_fills
GROUP BY
    drug_name, condition
ORDER BY
    prescription_rank
FETCH FIRST 10 ROWS ONLY;


-- Query 7: Generic vs Brand Fill Rate
-- Business Question: What percentage of prescriptions are generic?
SELECT
    generic_flag,
    CASE generic_flag
        WHEN 'Y' THEN 'Generic'
        WHEN 'N' THEN 'Brand Name'
    END                                              AS drug_type,
    COUNT(rx_id)                                     AS total_prescriptions,
    ROUND(SUM(retail_price), 2)                      AS total_retail_value,
    ROUND(AVG(copay_amount), 2)                      AS avg_copay,
    ROUND(COUNT(rx_id) * 100 /
        SUM(COUNT(rx_id)) OVER (), 2)                AS fill_rate_pct
FROM
    stg_prescription_fills
GROUP BY
    generic_flag
ORDER BY
    generic_flag;


-- Query 8: Insurance Provider Analysis
-- Business Question: Which insurers cover the most prescriptions?
SELECT
    insurance_provider,
    COUNT(rx_id)                                     AS total_claims,
    ROUND(SUM(retail_price), 2)                      AS total_retail_value,
    ROUND(SUM(copay_amount), 2)                      AS total_copay_collected,
    ROUND(SUM(insurance_paid), 2)                    AS total_insurance_paid,
    ROUND(AVG(copay_amount), 2)                      AS avg_copay,
    RANK() OVER (ORDER BY COUNT(rx_id) DESC)         AS insurer_rank
FROM
    stg_prescription_fills
GROUP BY
    insurance_provider
ORDER BY
    insurer_rank;


-- Query 9: Prescription Volume by Month
-- Business Question: Are prescription volumes seasonal?
SELECT
    TO_CHAR(fill_date, 'YYYY-MM')                    AS fill_month,
    COUNT(rx_id)                                     AS total_prescriptions,
    COUNT(CASE WHEN generic_flag = 'Y' THEN 1 END)  AS generic_fills,
    COUNT(CASE WHEN generic_flag = 'N' THEN 1 END)  AS brand_fills,
    ROUND(SUM(retail_price), 2)                      AS total_retail_value,
    ROUND(SUM(insurance_paid), 2)                    AS total_insurance_paid,
    ROUND(SUM(SUM(retail_price)) OVER (
        ORDER BY TO_CHAR(fill_date, 'YYYY-MM')
    ), 2)                                            AS running_retail_total
FROM
    stg_prescription_fills
GROUP BY
    TO_CHAR(fill_date, 'YYYY-MM')
ORDER BY
    fill_month;


-- Query 10: Prescription Status Breakdown
-- Business Question: How many prescriptions are pending or cancelled?
SELECT
    status,
    COUNT(rx_id)                                     AS total_prescriptions,
    ROUND(SUM(retail_price), 2)                      AS total_retail_value,
    ROUND(COUNT(rx_id) * 100 /
        SUM(COUNT(rx_id)) OVER (), 2)                AS status_pct
FROM
    stg_prescription_fills
GROUP BY
    status
ORDER BY
    total_prescriptions DESC;


/* ============================================================
   SECTION 3: INVENTORY ANALYTICS
   ============================================================ */

-- Query 11: Stockout Rate by Store
-- Business Question: Which stores have the most stockouts?
SELECT
    i.store_id,
    sl.store_name,
    sl.region,
    COUNT(i.inventory_id)                            AS total_products,
    SUM(CASE WHEN i.stockout_flag = 'Y' THEN 1 ELSE 0 END)
                                                     AS stockout_count,
    SUM(CASE WHEN i.low_stock_flag = 'Y' THEN 1 ELSE 0 END)
                                                     AS low_stock_count,
    ROUND(SUM(CASE WHEN i.stockout_flag = 'Y'
        THEN 1 ELSE 0 END) * 100 / COUNT(i.inventory_id), 2)
                                                     AS stockout_rate_pct,
    RANK() OVER (
        ORDER BY SUM(CASE WHEN i.stockout_flag = 'Y'
        THEN 1 ELSE 0 END) DESC
    )                                                AS stockout_rank
FROM
    stg_inventory_levels i
    JOIN stg_store_locations sl ON i.store_id = sl.store_id
GROUP BY
    i.store_id, sl.store_name, sl.region
ORDER BY
    stockout_rank;


-- Query 12: Products That Need Reordering Right Now
-- Business Question: Which products are below reorder point?
SELECT
    i.store_id,
    i.product_id,
    p.product_name,
    p.category,
    i.quantity_on_hand,
    i.reorder_point,
    i.reorder_quantity,
    i.units_sold_30d,
    ROUND(i.quantity_on_hand / NULLIF(i.units_sold_30d, 0), 1)
                                                     AS days_of_stock_remaining,
    CASE
        WHEN i.stockout_flag  = 'Y' THEN 'CRITICAL - OUT OF STOCK'
        WHEN i.low_stock_flag = 'Y' THEN 'WARNING  - LOW STOCK'
        ELSE                              'OK'
    END                                              AS stock_status
FROM
    stg_inventory_levels i
    JOIN stg_products p ON i.product_id = p.product_id
WHERE
    i.stockout_flag  = 'Y'
    OR i.low_stock_flag = 'Y'
ORDER BY
    stockout_flag DESC,
    days_of_stock_remaining ASC;


-- Query 13: Stockout Rate by Region
-- Business Question: Which region has the worst inventory management?
SELECT
    sl.region,
    COUNT(i.inventory_id)                            AS total_products,
    SUM(CASE WHEN i.stockout_flag = 'Y' THEN 1 ELSE 0 END)
                                                     AS total_stockouts,
    ROUND(SUM(CASE WHEN i.stockout_flag = 'Y'
        THEN 1 ELSE 0 END) * 100 / COUNT(i.inventory_id), 2)
                                                     AS stockout_rate_pct,
    RANK() OVER (
        ORDER BY SUM(CASE WHEN i.stockout_flag = 'Y'
        THEN 1 ELSE 0 END) * 100 / COUNT(i.inventory_id) DESC
    )                                                AS worst_region_rank
FROM
    stg_inventory_levels i
    JOIN stg_store_locations sl ON i.store_id = sl.store_id
GROUP BY
    sl.region
ORDER BY
    worst_region_rank;


/* ============================================================
   SECTION 4: CUSTOMER ANALYTICS
   ============================================================ */

-- Query 14: Customer Lifetime Value (CLV)
-- Business Question: Who are our most valuable customers?
SELECT
    s.customer_id,
    c.loyalty_member,
    c.state,
    c.insurance_provider,
    COUNT(s.transaction_id)                          AS total_transactions,
    ROUND(SUM(s.total_amount), 2)                    AS total_spend,
    ROUND(AVG(s.total_amount), 2)                    AS avg_transaction_value,
    MIN(s.transaction_date)                          AS first_purchase,
    MAX(s.transaction_date)                          AS last_purchase,
    RANK() OVER (ORDER BY SUM(s.total_amount) DESC)  AS clv_rank
FROM
    stg_sales_transactions s
    JOIN stg_customers c ON s.customer_id = c.customer_id
WHERE
    s.customer_id != 'GUEST'
GROUP BY
    s.customer_id, c.loyalty_member,
    c.state, c.insurance_provider
ORDER BY
    clv_rank
FETCH FIRST 20 ROWS ONLY;


-- Query 15: Loyalty vs Non-Loyalty Customer Spend
-- Business Question: Do loyalty members spend more?
SELECT
    c.loyalty_member,
    CASE c.loyalty_member
        WHEN 'Y' THEN 'Loyalty Member'
        WHEN 'N' THEN 'Non-Member'
    END                                              AS member_type,
    COUNT(DISTINCT s.customer_id)                    AS total_customers,
    COUNT(s.transaction_id)                          AS total_transactions,
    ROUND(SUM(s.total_amount), 2)                    AS total_revenue,
    ROUND(AVG(s.total_amount), 2)                    AS avg_transaction_value,
    ROUND(SUM(s.total_amount) /
        COUNT(DISTINCT s.customer_id), 2)            AS avg_spend_per_customer
FROM
    stg_sales_transactions s
    JOIN stg_customers c ON s.customer_id = c.customer_id
WHERE
    s.customer_id != 'GUEST'
GROUP BY
    c.loyalty_member
ORDER BY
    total_revenue DESC;