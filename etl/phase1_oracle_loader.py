"""
Healthcare Data Engineering Project
Phase 1: Generate synthetic data and load directly into Oracle Database
"""
import os
import oracledb
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    return oracledb.connect(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=os.getenv("ORACLE_DSN")
    )

cursor = conn.cursor()
print("✅ Connected to Oracle Database")

# ── Config ───────────────────────────────────────────────────────────────────
random.seed(42)
NUM_STORES        = 20
NUM_PRODUCTS      = 50
NUM_CUSTOMERS     = 500
NUM_SALES         = 5000
NUM_PRESCRIPTIONS = 2000

START_DATE = datetime(2024, 1, 1)
END_DATE   = datetime(2024, 12, 31)

def rand_date(start=START_DATE, end=END_DATE):
    delta = end - start
    return start + timedelta(
        days=random.randint(0, delta.days),
        hours=random.randint(0, 23),
        minutes=random.randint(0, 59)
    )

# ── Drop & Create Tables ─────────────────────────────────────────────────────
print("\n── Creating tables in Oracle ──")

tables = [
    "DROP TABLE sales_transactions",
    "DROP TABLE prescription_fills",
    "DROP TABLE inventory_levels",
    "DROP TABLE customers",
    "DROP TABLE products",
    "DROP TABLE store_locations",
]

# Drop tables if they exist (ignore errors if they don't)
for sql in tables:
    try:
        cursor.execute(sql)
    except:
        pass

# Create tables
cursor.execute("""
    CREATE TABLE store_locations (
        store_id      VARCHAR2(10)  PRIMARY KEY,
        store_name    VARCHAR2(100),
        city          VARCHAR2(50),
        state         VARCHAR2(5),
        zip_code      VARCHAR2(10),
        region        VARCHAR2(20),
        store_type    VARCHAR2(30),
        opened_date   DATE,
        manager_id    VARCHAR2(10)
    )
""")
print("  ✓ store_locations table created")

cursor.execute("""
    CREATE TABLE products (
        product_id    VARCHAR2(10)  PRIMARY KEY,
        product_name  VARCHAR2(100),
        category      VARCHAR2(50),
        brand         VARCHAR2(50),
        unit_price    NUMBER(10,2),
        cost_price    NUMBER(10,2),
        upc_code      VARCHAR2(20),
        supplier_id   VARCHAR2(10)
    )
""")
print("  ✓ products table created")

cursor.execute("""
    CREATE TABLE customers (
        customer_id        VARCHAR2(10)  PRIMARY KEY,
        loyalty_member     VARCHAR2(1),
        date_of_birth      DATE,
        gender             VARCHAR2(10),
        state              VARCHAR2(5),
        preferred_store    VARCHAR2(10),
        member_since       DATE,
        insurance_provider VARCHAR2(20)
    )
""")
print("  ✓ customers table created")

cursor.execute("""
    CREATE TABLE sales_transactions (
        transaction_id  VARCHAR2(15)  PRIMARY KEY,
        store_id        VARCHAR2(10),
        customer_id     VARCHAR2(10),
        product_id      VARCHAR2(10),
        transaction_date TIMESTAMP,
        quantity        NUMBER(5),
        unit_price      NUMBER(10,2),
        discount_pct    NUMBER(5,2),
        total_amount    NUMBER(10,2),
        payment_method  VARCHAR2(20),
        cashier_id      VARCHAR2(10),
        return_flag     VARCHAR2(1)
    )
""")
print("  ✓ sales_transactions table created")

cursor.execute("""
    CREATE TABLE prescription_fills (
        rx_id               VARCHAR2(15)  PRIMARY KEY,
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
        status              VARCHAR2(15)
    )
""")
print("  ✓ prescription_fills table created")

cursor.execute("""
    CREATE TABLE inventory_levels (
        inventory_id        VARCHAR2(25)  PRIMARY KEY,
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
        last_restocked      TIMESTAMP
    )
""")
print("  ✓ inventory_levels table created")

conn.commit()

# ── Generate & Insert Data ───────────────────────────────────────────────────
print("\n── Loading data into Oracle ──")

STATES     = ["FL","NY","TX","CA","IL","OH","PA","GA","NC","AZ"]
REGIONS    = ["Northeast","Southeast","Midwest","West","South"]
STORE_TYPES= ["Standalone","In-Store Clinic","Drive-Thru"]
CATEGORIES = ["OTC Medicine","Personal Care","Beauty","Vitamins",
               "Snacks","Baby Care","Household","Seasonal","Health Devices"]
INSURERS   = ["Aetna","BlueCross","Cigna","UnitedHealth",
               "Humana","Medicare","Medicaid","Self-Pay"]
PAYMENTS   = ["Credit Card","Debit Card","Cash","CVS Rewards","Insurance"]
DRUGS = [
    ("Lisinopril","Hypertension"), ("Metformin","Diabetes"),
    ("Atorvastatin","Cholesterol"), ("Amlodipine","Hypertension"),
    ("Omeprazole","GERD"), ("Metoprolol","Heart"),
    ("Levothyroxine","Thyroid"), ("Albuterol","Asthma"),
    ("Gabapentin","Nerve Pain"), ("Sertraline","Depression"),
    ("Amoxicillin","Antibiotic"), ("Fluoxetine","Depression"),
    ("Losartan","Hypertension"), ("Pantoprazole","GERD"),
    ("Montelukast","Asthma"), ("Escitalopram","Anxiety"),
    ("Rosuvastatin","Cholesterol"), ("Bupropion","Depression"),
    ("Trazodone","Sleep"), ("Hydrocodone","Pain"),
]

# 1. Stores
stores = []
for i in range(1, NUM_STORES + 1):
    sid = f"STR{i:04d}"
    stores.append((
        sid, f"CVS Pharmacy #{1000+i}", f"City_{i}",
        random.choice(STATES), f"{random.randint(10000,99999)}",
        random.choice(REGIONS), random.choice(STORE_TYPES),
        START_DATE - timedelta(days=random.randint(365,3650)),
        f"MGR{random.randint(100,999)}"
    ))

cursor.executemany("""
    INSERT INTO store_locations VALUES
    (:1,:2,:3,:4,:5,:6,:7,:8,:9)
""", stores)
print(f"  ✓ {len(stores)} stores loaded")

store_ids = [s[0] for s in stores]

# 2. Products
products = []
for i in range(1, NUM_PRODUCTS + 1):
    cat   = random.choice(CATEGORIES)
    price = round(random.uniform(1.99, 89.99), 2)
    products.append((
        f"PRD{i:04d}", f"{cat} Item {i}", cat,
        random.choice(["CVS Health","Generic","National Brand"]),
        price, round(price * random.uniform(0.4, 0.7), 2),
        f"{random.randint(100000000000,999999999999)}",
        f"SUP{random.randint(10,50):03d}"
    ))

cursor.executemany("""
    INSERT INTO products VALUES
    (:1,:2,:3,:4,:5,:6,:7,:8)
""", products)
print(f"  ✓ {len(products)} products loaded")

product_ids   = [p[0] for p in products]
product_prices= {p[0]: p[4] for p in products}

# 3. Customers
customers = []
for i in range(1, NUM_CUSTOMERS + 1):
    dob = START_DATE - timedelta(days=random.randint(365*18, 365*85))
    customers.append((
        f"CUST{i:05d}",
        random.choice(["Y","Y","Y","N"]),
        dob,
        random.choice(["M","F","Other"]),
        random.choice(STATES),
        random.choice(store_ids),
        START_DATE - timedelta(days=random.randint(30,1825)),
        random.choice(INSURERS)
    ))

cursor.executemany("""
    INSERT INTO customers VALUES
    (:1,:2,:3,:4,:5,:6,:7,:8)
""", customers)
print(f"  ✓ {len(customers)} customers loaded")

customer_ids = [c[0] for c in customers]

# 4. Sales Transactions
sales = []
for i in range(1, NUM_SALES + 1):
    pid   = random.choice(product_ids)
    price = product_prices[pid]
    qty   = random.randint(1, 6)
    disc  = round(random.uniform(0, 0.2), 2) if random.random() < 0.3 else 0.0
    sales.append((
        f"TXN{i:07d}",
        random.choice(store_ids),
        random.choice(customer_ids) if random.random() < 0.7 else "GUEST",
        pid,
        rand_date(),
        qty, price, disc,
        round(qty * price * (1 - disc), 2),
        random.choice(PAYMENTS),
        f"EMP{random.randint(1000,9999)}",
        "Y" if random.random() < 0.03 else "N"
    ))

cursor.executemany("""
    INSERT INTO sales_transactions VALUES
    (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12)
""", sales)
print(f"  ✓ {len(sales)} sales transactions loaded")

# 5. Prescriptions
prescriptions = []
for i in range(1, NUM_PRESCRIPTIONS + 1):
    drug, condition = random.choice(DRUGS)
    copay  = round(random.uniform(0, 75), 2)
    retail = round(random.uniform(copay + 5, copay + 300), 2)
    prescriptions.append((
        f"RX{i:07d}",
        random.choice(store_ids),
        random.choice(customer_ids),
        drug, condition,
        rand_date(),
        random.choice([30, 60, 90]),
        random.randint(30, 90),
        f"DR{random.randint(1000,9999)}",
        random.choice(INSURERS),
        copay, retail,
        round(retail - copay, 2),
        random.randint(0, 5),
        random.choice(["Y","Y","N"]),
        random.choice(["Filled","Filled","Filled","Pending","Cancelled"])
    ))

cursor.executemany("""
    INSERT INTO prescription_fills VALUES
    (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12,:13,:14,:15,:16)
""", prescriptions)
print(f"  ✓ {len(prescriptions)} prescriptions loaded")

# 6. Inventory
inventory = []
for store in stores:
    for prod in products:
        on_hand    = random.randint(0, 200)
        reorder_pt = random.randint(10, 40)
        inventory.append((
            f"INV{store[0]}_{prod[0]}",
            store[0], prod[0],
            END_DATE,
            on_hand, reorder_pt,
            random.randint(50, 200),
            random.randint(0, 150),
            random.randint(0, 200),
            "Y" if on_hand == 0 else "N",
            "Y" if 0 < on_hand <= reorder_pt else "N",
            rand_date(START_DATE + timedelta(days=300), END_DATE)
        ))

cursor.executemany("""
    INSERT INTO inventory_levels VALUES
    (:1,:2,:3,:4,:5,:6,:7,:8,:9,:10,:11,:12)
""", inventory)
print(f"  ✓ {len(inventory)} inventory records loaded")

conn.commit()
cursor.close()
conn.close()

total = (NUM_STORES + NUM_PRODUCTS + NUM_CUSTOMERS +
         NUM_SALES + NUM_PRESCRIPTIONS + NUM_STORES * NUM_PRODUCTS)
print(f"\n── Done! {total:,} total records loaded into Oracle ──")
print("── Database: FREEPDB1 | Host: localhost:1521 ──\n")