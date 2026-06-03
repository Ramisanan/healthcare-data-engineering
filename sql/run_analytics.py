"""
Healthcare Data Engineering Project
Phase 3: Run SQL Analytics against Oracle
"""

import oracledb
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN")
    )

conn = get_connection()
cursor = conn.cursor()

queries = {
    "Top 5 Stores by Revenue": """
        SELECT
            s.store_id,
            sl.store_name,
            sl.region,
            ROUND(SUM(s.total_amount), 2) AS total_revenue,
            RANK() OVER (ORDER BY SUM(s.total_amount) DESC) AS rank
        FROM stg_sales_transactions s
        JOIN stg_store_locations sl ON s.store_id = sl.store_id
        GROUP BY s.store_id, sl.store_name, sl.region
        ORDER BY rank
        FETCH FIRST 5 ROWS ONLY
    """,
    "Generic vs Brand Fill Rate": """
        SELECT
            CASE generic_flag
                WHEN 'Y' THEN 'Generic'
                WHEN 'N' THEN 'Brand Name'
            END AS drug_type,
            COUNT(rx_id) AS total_prescriptions,
            ROUND(COUNT(rx_id) * 100 /
                SUM(COUNT(rx_id)) OVER (), 2) AS fill_rate_pct
        FROM stg_prescription_fills
        GROUP BY generic_flag
        ORDER BY generic_flag
    """,
    "Stockout Rate by Region": """
        SELECT
            sl.region,
            COUNT(i.inventory_id) AS total_products,
            SUM(CASE WHEN i.stockout_flag = 'Y' THEN 1 ELSE 0 END) AS stockouts,
            ROUND(SUM(CASE WHEN i.stockout_flag = 'Y'
                THEN 1 ELSE 0 END) * 100 / COUNT(i.inventory_id), 2) AS stockout_pct
        FROM stg_inventory_levels i
        JOIN stg_store_locations sl ON i.store_id = sl.store_id
        GROUP BY sl.region
        ORDER BY stockout_pct DESC
    """,
    "Loyalty vs Non-Loyalty Spend": """
        SELECT
            CASE c.loyalty_member
                WHEN 'Y' THEN 'Loyalty Member'
                WHEN 'N' THEN 'Non-Member'
            END AS member_type,
            COUNT(DISTINCT s.customer_id) AS total_customers,
            ROUND(SUM(s.total_amount), 2) AS total_revenue,
            ROUND(SUM(s.total_amount) /
                COUNT(DISTINCT s.customer_id), 2) AS avg_spend_per_customer
        FROM stg_sales_transactions s
        JOIN stg_customers c ON s.customer_id = c.customer_id
        WHERE s.customer_id != 'GUEST'
        GROUP BY c.loyalty_member
        ORDER BY total_revenue DESC
    """
}

print("\n" + "=" * 60)
print("HEALTHCARE ANALYTICS REPORT")
print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

for title, query in queries.items():
    print(f"\n── {title} ──")
    cursor.execute(query)
    columns = [col[0] for col in cursor.description]
    rows    = cursor.fetchall()
    print("  " + " | ".join(f"{col:<25}" for col in columns))
    print("  " + "-" * (27 * len(columns)))
    for row in rows:
        print("  " + " | ".join(f"{str(val):<25}" for val in row))

print("\n" + "=" * 60)
cursor.close()
conn.close()