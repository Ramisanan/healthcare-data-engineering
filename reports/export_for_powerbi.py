"""
Healthcare Data Engineering Project
Export staging tables from Oracle to CSV for Power BI
"""

import oracledb
import csv
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

os.makedirs("reports/powerbi_data", exist_ok=True)

conn = oracledb.connect(
    user=os.getenv("ORACLE_USER"),
    password=os.getenv("ORACLE_PASSWORD"),
    dsn=os.getenv("ORACLE_DSN")
)
cursor = conn.cursor()

queries = {
    "sales_by_store": """
        SELECT
            s.store_id,
            sl.store_name,
            sl.state,
            sl.region,
            COUNT(s.transaction_id)       AS total_transactions,
            ROUND(SUM(s.total_amount), 2) AS total_revenue,
            ROUND(AVG(s.total_amount), 2) AS avg_transaction
        FROM stg_sales_transactions s
        JOIN stg_store_locations sl ON s.store_id = sl.store_id
        GROUP BY s.store_id, sl.store_name, sl.state, sl.region
    """,
    "monthly_sales": """
        SELECT
            TO_CHAR(transaction_date, 'YYYY-MM') AS sale_month,
            COUNT(transaction_id)                AS total_transactions,
            ROUND(SUM(total_amount), 2)          AS monthly_revenue
        FROM stg_sales_transactions
        GROUP BY TO_CHAR(transaction_date, 'YYYY-MM')
        ORDER BY sale_month
    """,
    "prescription_by_drug": """
        SELECT
            drug_name,
            condition,
            COUNT(rx_id)                   AS total_prescriptions,
            ROUND(AVG(copay_amount), 2)    AS avg_copay,
            ROUND(AVG(retail_price), 2)    AS avg_retail_price,
            SUM(CASE WHEN generic_flag = 'Y' THEN 1 ELSE 0 END) AS generic_count,
            SUM(CASE WHEN generic_flag = 'N' THEN 1 ELSE 0 END) AS brand_count
        FROM stg_prescription_fills
        GROUP BY drug_name, condition
        ORDER BY total_prescriptions DESC
    """,
    "insurance_analysis": """
        SELECT
            insurance_provider,
            COUNT(rx_id)                    AS total_claims,
            ROUND(SUM(retail_price), 2)     AS total_retail_value,
            ROUND(SUM(copay_amount), 2)     AS total_copay,
            ROUND(SUM(insurance_paid), 2)   AS total_insurance_paid,
            ROUND(AVG(copay_amount), 2)     AS avg_copay
        FROM stg_prescription_fills
        GROUP BY insurance_provider
        ORDER BY total_claims DESC
    """,
    "inventory_status": """
        SELECT
            i.store_id,
            sl.store_name,
            sl.region,
            p.product_name,
            p.category,
            i.quantity_on_hand,
            i.reorder_point,
            i.units_sold_30d,
            i.stockout_flag,
            i.low_stock_flag
        FROM stg_inventory_levels i
        JOIN stg_store_locations sl ON i.store_id  = sl.store_id
        JOIN stg_products        p  ON i.product_id = p.product_id
    """,
    "customer_loyalty": """
        SELECT
            c.loyalty_member,
            c.state,
            c.insurance_provider,
            COUNT(DISTINCT s.customer_id)        AS total_customers,
            COUNT(s.transaction_id)              AS total_transactions,
            ROUND(SUM(s.total_amount), 2)        AS total_revenue,
            ROUND(AVG(s.total_amount), 2)        AS avg_transaction
        FROM stg_sales_transactions s
        JOIN stg_customers c ON s.customer_id = c.customer_id
        WHERE s.customer_id != 'GUEST'
        GROUP BY c.loyalty_member, c.state, c.insurance_provider
    """
}

print("\n── Exporting Oracle data for Power BI ──\n")

for name, query in queries.items():
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows    = cursor.fetchall()
    path    = f"reports/powerbi_data/{name}.csv"

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(columns)
        writer.writerows(rows)

    print(f"  ✓ {name}.csv  →  {len(rows)} rows")

cursor.close()
conn.close()

print(f"\n── Done! Files saved to reports/powerbi_data/ ──\n")