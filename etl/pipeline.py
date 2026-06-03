"""
Healthcare Data Engineering Project
Phase 2: ETL Pipeline
Extract from Oracle → Transform → Load to Staging
"""

import oracledb
import logging
import os
from datetime import datetime

# Logging Setup
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler(f"logs/etl_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN")
    )

# Create Staging Tables
def create_staging_tables(cursor):
    log.info("Creating staging tables...")

    staging_tables = [
        "DROP TABLE stg_sales_transactions",
        "DROP TABLE stg_prescription_fills",
        "DROP TABLE stg_inventory_levels",
        "DROP TABLE stg_customers",
        "DROP TABLE stg_products",
        "DROP TABLE stg_store_locations",
    ]

    for sql in staging_tables:
        try:
            cursor.execute(sql)
        except:
            pass

    cursor.execute("""
        CREATE TABLE stg_store_locations (
            store_id      VARCHAR2(10) PRIMARY KEY,
            store_name    VARCHAR2(100),
            city          VARCHAR2(50),
            state         VARCHAR2(5),
            zip_code      VARCHAR2(10),
            region        VARCHAR2(20),
            store_type    VARCHAR2(30),
            opened_date   DATE,
            manager_id    VARCHAR2(10),
            etl_load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            etl_status    VARCHAR2(20) DEFAULT 'VALID'
        )
    """)

    cursor.execute("""
        CREATE TABLE stg_products (
            product_id    VARCHAR2(10) PRIMARY KEY,
            product_name  VARCHAR2(100),
            category      VARCHAR2(50),
            brand         VARCHAR2(50),
            unit_price    NUMBER(10,2),
            cost_price    NUMBER(10,2),
            upc_code      VARCHAR2(20),
            supplier_id   VARCHAR2(10),
            etl_load_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            etl_status    VARCHAR2(20) DEFAULT 'VALID'
        )
    """)

    cursor.execute("""
        CREATE TABLE stg_customers (
            customer_id        VARCHAR2(10) PRIMARY KEY,
            loyalty_member     VARCHAR2(1),
            date_of_birth      DATE,
            gender             VARCHAR2(10),
            state              VARCHAR2(5),
            preferred_store    VARCHAR2(10),
            member_since       DATE,
            insurance_provider VARCHAR2(20),
            etl_load_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            etl_status         VARCHAR2(20) DEFAULT 'VALID'
        )
    """)

    cursor.execute("""
        CREATE TABLE stg_sales_transactions (
            transaction_id   VARCHAR2(15) PRIMARY KEY,
            store_id         VARCHAR2(10),
            customer_id      VARCHAR2(10),
            product_id       VARCHAR2(10),
            transaction_date TIMESTAMP,
            quantity         NUMBER(5),
            unit_price       NUMBER(10,2),
            discount_pct     NUMBER(5,2),
            total_amount     NUMBER(10,2),
            payment_method   VARCHAR2(20),
            cashier_id       VARCHAR2(10),
            return_flag      VARCHAR2(1),
            etl_load_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            etl_status       VARCHAR2(20) DEFAULT 'VALID'
        )
    """)

    cursor.execute("""
        CREATE TABLE stg_prescription_fills (
            rx_id               VARCHAR2(15) PRIMARY KEY,
            store_id            VARCHAR2(10),
            customer_id         VARCHAR2(10),
            drug_name           VARCHAR2(50),
            condition           VARCHAR2(50),
            fill_date           TIMESTAMP,
            days_supply         NUMBER(5),
            quantity_dispensed  NUMBER(5),
            prescriber_id       VARCHAR2(10),
            insurance_provider  VARCHAR2(20),
            copay_amount        NUMBER(10,2),
            retail_price        NUMBER(10,2),
            insurance_paid      NUMBER(10,2),
            refill_number       NUMBER(3),
            generic_flag        VARCHAR2(1),
            status              VARCHAR2(15),
            etl_load_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            etl_status          VARCHAR2(20) DEFAULT 'VALID'
        )
    """)

    cursor.execute("""
        CREATE TABLE stg_inventory_levels (
            inventory_id        VARCHAR2(25) PRIMARY KEY,
            store_id            VARCHAR2(10),
            product_id          VARCHAR2(10),
            snapshot_date       DATE,
            quantity_on_hand    NUMBER(10),
            reorder_point       NUMBER(10),
            reorder_quantity    NUMBER(10),
            units_sold_30d      NUMBER(10),
            units_received_30d  NUMBER(10),
            stockout_flag       VARCHAR2(1),
            low_stock_flag      VARCHAR2(1),
            last_restocked      TIMESTAMP,
            etl_load_date       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            etl_status          VARCHAR2(20) DEFAULT 'VALID'
        )
    """)

    log.info("✓ All staging tables created")

# ── EXTRACT ──────────────────────────────────────────────────────────────────
def extract(cursor, table):
    log.info(f"Extracting from {table}...")
    cursor.execute(f"SELECT * FROM {table}")
    columns = [col[0].lower() for col in cursor.description]
    rows    = cursor.fetchall()
    log.info(f"  → {len(rows)} rows extracted from {table}")
    return columns, rows

# ── TRANSFORM ────────────────────────────────────────────────────────────────
def transform_stores(columns, rows):
    log.info("Transforming store_locations...")
    valid, rejected = [], []
    seen = set()

    VALID_STATES  = {"FL","NY","TX","CA","IL","OH","PA","GA","NC","AZ"}
    VALID_REGIONS = {"Northeast","Southeast","Midwest","West","South"}

    for row in rows:
        r = dict(zip(columns, row))
        issues = []

        # Duplicate check
        if r["store_id"] in seen:
            issues.append("DUPLICATE_STORE_ID")
        seen.add(r["store_id"])

        # Null checks
        if not r["store_id"]:   issues.append("NULL_STORE_ID")
        if not r["store_name"]: issues.append("NULL_STORE_NAME")

        # State validation
        if r["state"] not in VALID_STATES:
            issues.append(f"INVALID_STATE:{r['state']}")

        # Region validation
        if r["region"] not in VALID_REGIONS:
            issues.append(f"INVALID_REGION:{r['region']}")

        if issues:
            rejected.append({**r, "issues": issues})
        else:
            valid.append(row)

    log.info(f"  → {len(valid)} valid | {len(rejected)} rejected")
    return valid, rejected

def transform_products(columns, rows):
    log.info("Transforming products...")
    valid, rejected = [], []
    seen = set()

    for row in rows:
        r = dict(zip(columns, row))
        issues = []

        if r["product_id"] in seen:
            issues.append("DUPLICATE_PRODUCT_ID")
        seen.add(r["product_id"])

        if not r["product_id"]:   issues.append("NULL_PRODUCT_ID")
        if not r["product_name"]: issues.append("NULL_PRODUCT_NAME")

        # Price validation
        if r["unit_price"] is None or r["unit_price"] <= 0:
            issues.append("INVALID_UNIT_PRICE")
        if r["cost_price"] is None or r["cost_price"] <= 0:
            issues.append("INVALID_COST_PRICE")

        # Cost should be less than unit price
        if r["unit_price"] and r["cost_price"]:
            if r["cost_price"] >= r["unit_price"]:
                issues.append("COST_EXCEEDS_PRICE")

        if issues:
            rejected.append({**r, "issues": issues})
        else:
            valid.append(row)

    log.info(f"  → {len(valid)} valid | {len(rejected)} rejected")
    return valid, rejected

def transform_customers(columns, rows):
    log.info("Transforming customers...")
    valid, rejected = [], []
    seen = set()

    VALID_GENDERS   = {"M", "F", "Other"}
    VALID_INSURANCE = {"Aetna","BlueCross","Cigna","UnitedHealth",
                       "Humana","Medicare","Medicaid","Self-Pay"}

    for row in rows:
        r = dict(zip(columns, row))
        issues = []

        if r["customer_id"] in seen:
            issues.append("DUPLICATE_CUSTOMER_ID")
        seen.add(r["customer_id"])

        if not r["customer_id"]: issues.append("NULL_CUSTOMER_ID")

        # Age validation (must be 18-120)
        if r["date_of_birth"]:
            age = (datetime.now() - r["date_of_birth"]).days // 365
            if age < 18: issues.append("UNDERAGE_CUSTOMER")
            if age > 120: issues.append("INVALID_AGE")
        else:
            issues.append("NULL_DATE_OF_BIRTH")

        if r["gender"] not in VALID_GENDERS:
            issues.append(f"INVALID_GENDER:{r['gender']}")

        if r["insurance_provider"] not in VALID_INSURANCE:
            issues.append(f"INVALID_INSURANCE:{r['insurance_provider']}")

        if issues:
            rejected.append({**r, "issues": issues})
        else:
            valid.append(row)

    log.info(f"  → {len(valid)} valid | {len(rejected)} rejected")
    return valid, rejected

def transform_sales(columns, rows):
    log.info("Transforming sales_transactions...")
    valid, rejected = [], []
    seen = set()

    VALID_PAYMENTS = {"Credit Card","Debit Card","Cash",
                      "CVS Rewards","Insurance"}

    for row in rows:
        r = dict(zip(columns, row))
        issues = []

        if r["transaction_id"] in seen:
            issues.append("DUPLICATE_TRANSACTION_ID")
        seen.add(r["transaction_id"])

        if not r["transaction_id"]: issues.append("NULL_TRANSACTION_ID")
        if not r["store_id"]:       issues.append("NULL_STORE_ID")
        if not r["product_id"]:     issues.append("NULL_PRODUCT_ID")

        # Quantity validation
        if r["quantity"] is None or r["quantity"] <= 0:
            issues.append("INVALID_QUANTITY")

        # Price validation
        if r["unit_price"] is None or r["unit_price"] <= 0:
            issues.append("INVALID_PRICE")

        # Total amount validation
        if r["total_amount"] is None or r["total_amount"] < 0:
            issues.append("INVALID_TOTAL_AMOUNT")

        # Future date check
        if r["transaction_date"] and r["transaction_date"] > datetime.now():
            issues.append("FUTURE_TRANSACTION_DATE")

        # Payment method validation
        if r["payment_method"] not in VALID_PAYMENTS:
            issues.append(f"INVALID_PAYMENT:{r['payment_method']}")

        # Discount validation
        if r["discount_pct"] and (r["discount_pct"] < 0 or r["discount_pct"] > 1):
            issues.append("INVALID_DISCOUNT")

        if issues:
            rejected.append({**r, "issues": issues})
        else:
            valid.append(row)

    log.info(f"  → {len(valid)} valid | {len(rejected)} rejected")
    return valid, rejected

def transform_prescriptions(columns, rows):
    log.info("Transforming prescription_fills...")
    valid, rejected = [], []
    seen = set()

    VALID_STATUS      = {"Filled", "Pending", "Cancelled"}
    VALID_DAYS_SUPPLY = {30, 60, 90}

    for row in rows:
        r = dict(zip(columns, row))
        issues = []

        if r["rx_id"] in seen:
            issues.append("DUPLICATE_RX_ID")
        seen.add(r["rx_id"])

        if not r["rx_id"]:      issues.append("NULL_RX_ID")
        if not r["store_id"]:   issues.append("NULL_STORE_ID")
        if not r["customer_id"]:issues.append("NULL_CUSTOMER_ID")
        if not r["drug_name"]:  issues.append("NULL_DRUG_NAME")

        # Future fill date check
        if r["fill_date"] and r["fill_date"] > datetime.now():
            issues.append("FUTURE_FILL_DATE")

        # Days supply validation
        if r["days_supply"] not in VALID_DAYS_SUPPLY:
            issues.append(f"INVALID_DAYS_SUPPLY:{r['days_supply']}")

        # Price validation
        if r["copay_amount"] is None or r["copay_amount"] < 0:
            issues.append("NEGATIVE_COPAY")
        if r["retail_price"] is None or r["retail_price"] <= 0:
            issues.append("INVALID_RETAIL_PRICE")

        # Copay cannot exceed retail price
        if r["copay_amount"] and r["retail_price"]:
            if r["copay_amount"] > r["retail_price"]:
                issues.append("COPAY_EXCEEDS_RETAIL")

        # Status validation
        if r["status"] not in VALID_STATUS:
            issues.append(f"INVALID_STATUS:{r['status']}")

        if issues:
            rejected.append({**r, "issues": issues})
        else:
            valid.append(row)

    log.info(f"  → {len(valid)} valid | {len(rejected)} rejected")
    return valid, rejected

def transform_inventory(columns, rows):
    log.info("Transforming inventory_levels...")
    valid, rejected = [], []
    seen = set()

    for row in rows:
        r = dict(zip(columns, row))
        issues = []

        if r["inventory_id"] in seen:
            issues.append("DUPLICATE_INVENTORY_ID")
        seen.add(r["inventory_id"])

        if not r["inventory_id"]: issues.append("NULL_INVENTORY_ID")
        if not r["store_id"]:     issues.append("NULL_STORE_ID")
        if not r["product_id"]:   issues.append("NULL_PRODUCT_ID")

        # Quantity validation
        if r["quantity_on_hand"] is None or r["quantity_on_hand"] < 0:
            issues.append("NEGATIVE_QUANTITY")
        if r["reorder_point"] is None or r["reorder_point"] < 0:
            issues.append("INVALID_REORDER_POINT")

        if issues:
            rejected.append({**r, "issues": issues})
        else:
            valid.append(row)

    log.info(f"  → {len(valid)} valid | {len(rejected)} rejected")
    return valid, rejected

# ── LOAD ─────────────────────────────────────────────────────────────────────
def load(cursor, table, rows, num_cols):
    if not rows:
        log.info(f"  No valid rows to load into {table}")
        return
    
    # Column maps for each staging table
    col_maps = {
        "stg_store_locations":    "store_id,store_name,city,state,zip_code,region,store_type,opened_date,manager_id",
        "stg_products":           "product_id,product_name,category,brand,unit_price,cost_price,upc_code,supplier_id",
        "stg_customers":          "customer_id,loyalty_member,date_of_birth,gender,state,preferred_store,member_since,insurance_provider",
        "stg_sales_transactions": "transaction_id,store_id,customer_id,product_id,transaction_date,quantity,unit_price,discount_pct,total_amount,payment_method,cashier_id,return_flag",
        "stg_prescription_fills": "rx_id,store_id,customer_id,drug_name,condition,fill_date,days_supply,quantity_dispensed,prescriber_id,insurance_provider,copay_amount,retail_price,insurance_paid,refill_number,generic_flag,status",
        "stg_inventory_levels":   "inventory_id,store_id,product_id,snapshot_date,quantity_on_hand,reorder_point,reorder_quantity,units_sold_30d,units_received_30d,stockout_flag,low_stock_flag,last_restocked",
    }

    cols         = col_maps[table]
    num_cols     = len(cols.split(","))
    placeholders = ",".join([f":{i+1}" for i in range(num_cols)])

    cursor.executemany(
        f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
        rows
    )
    log.info(f"  ✓ {len(rows)} rows loaded into {table}")
# ── MAIN ETL ─────────────────────────────────────────────────────────────────
def run_etl():
    log.info("=" * 60)
    log.info("HEALTHCARE ETL PIPELINE STARTED")
    log.info("=" * 60)

    start_time = datetime.now()
    conn = get_connection()
    cursor = conn.cursor()

    # Create staging tables
    create_staging_tables(cursor)
    conn.commit()

    total_valid    = 0
    total_rejected = 0

    # ── Stores ──
    cols, rows = extract(cursor, "store_locations")
    valid, rejected = transform_stores(cols, rows)
    load(cursor, "stg_store_locations", valid, 9)
    total_valid    += len(valid)
    total_rejected += len(rejected)

    # ── Products ──
    cols, rows = extract(cursor, "products")
    valid, rejected = transform_products(cols, rows)
    load(cursor, "stg_products", valid, 8)
    total_valid    += len(valid)
    total_rejected += len(rejected)

    # ── Customers ──
    cols, rows = extract(cursor, "customers")
    valid, rejected = transform_customers(cols, rows)
    load(cursor, "stg_customers", valid, 8)
    total_valid    += len(valid)
    total_rejected += len(rejected)

    # ── Sales ──
    cols, rows = extract(cursor, "sales_transactions")
    valid, rejected = transform_sales(cols, rows)
    load(cursor, "stg_sales_transactions", valid, 12)
    total_valid    += len(valid)
    total_rejected += len(rejected)

    # ── Prescriptions ──
    cols, rows = extract(cursor, "prescription_fills")
    valid, rejected = transform_prescriptions(cols, rows)
    load(cursor, "stg_prescription_fills", valid, 16)
    total_valid    += len(valid)
    total_rejected += len(rejected)

    # ── Inventory ──
    cols, rows = extract(cursor, "inventory_levels")
    valid, rejected = transform_inventory(cols, rows)
    load(cursor, "stg_inventory_levels", valid, 12)
    total_valid    += len(valid)
    total_rejected += len(rejected)

    conn.commit()
    cursor.close()
    conn.close()

    duration = (datetime.now() - start_time).seconds

    log.info("=" * 60)
    log.info("ETL PIPELINE COMPLETED")
    log.info(f"  Total valid records loaded : {total_valid:,}")
    log.info(f"  Total rejected records     : {total_rejected:,}")
    log.info(f"  Duration                   : {duration} seconds")
    log.info("=" * 60)

if __name__ == "__main__":
    run_etl()