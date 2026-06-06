# Healthcare Data Engineering Project

End-to-end data engineering pipeline for a retail pharmacy environment.
Built to demonstrate production-grade data engineering skills across
ingestion, transformation, analytics, CI/CD, and reporting.

## Tech Stack

| Tool | Purpose |
|---|---|
| Oracle 23ai | Source database (Docker) |
| Python | ETL pipeline, data generation |
| oracledb | Oracle database driver |
| SQL / T-SQL | Analytics and optimization |
| Azure DevOps | CI/CD pipeline (4 stages) |
| pytest | Unit testing (29 tests) |
| Power BI | Business intelligence dashboard |
| Docker | Oracle database containerization |
| Git / GitHub | Version control |

## Project Phases

| Phase | Description | Status |
|---|---|---|
| Phase 1 | Oracle 23ai setup + synthetic data generation (8,570 records) | ✅ Complete |
| Phase 2 | ETL pipeline with 20+ data quality validation rules | ✅ Complete |
| Phase 3 | SQL analytics with window functions and business insights | ✅ Complete |
| Phase 4 | Azure DevOps CI/CD pipeline + 29 unit tests | ✅ Complete |
| Phase 5 | Power BI dashboard with 4 report pages | ✅ Complete |

## Dataset Overview

| Table | Records | Description |
|---|---|---|
| store_locations | 20 | Pharmacy store master data |
| products | 50 | Product catalog with pricing |
| customers | 500 | Customer loyalty profiles |
| sales_transactions | 5,000 | Point-of-sale transactions |
| prescription_fills | 2,000 | Pharmacy prescription data |
| inventory_levels | 1,000 | Store inventory snapshots |

## Key Achievements

- 8,570 records loaded into Oracle 23ai running in Docker
- 20+ data quality validation rules across 6 tables
- 29 unit tests — all passing in 0.10 seconds
- 4-stage CI/CD pipeline — fully automated on every push
- Power BI dashboard with sales, pharmacy, inventory and customer analytics
- Full audit trail — every ETL run logged with timestamps

## Power BI Dashboard

[View Live Dashboard](ADD-YOUR-POWERBI-LINK-HERE)

### Dashboard Pages
- **Page 1:** Sales Overview — revenue by store, monthly trends, payment methods
- **Page 2:** Pharmacy Analytics — drug prescriptions, insurance breakdown
- **Page 3:** Inventory Intelligence — stockout alerts, low stock warnings
- **Page 4:** Customer Loyalty — loyalty vs non-loyalty spend analysis

## SQL Analytics

15 optimized queries covering:
- Revenue ranking with window functions
- Month-over-month trends with LAG()
- Running totals with SUM() OVER()
- Stockout rate by region
- Customer lifetime value

## CI/CD Pipeline

4 automated stages on every GitHub push:
1. **Code Quality** — flake8 linting
2. **Unit Tests** — pytest (29 tests)
3. **Build** — artifact packaging
4. **Deploy** — production deployment

## Project Structure
'''
healthcare-data-engineering/
├── etl/
│   ├── phase1_oracle_loader.py  ← generates and loads data into Oracle
│   └── pipeline.py              ← ETL pipeline with validation rules
├── sql/
│   ├── analytics.sql            ← 15 optimized SQL queries
│   └── run_analytics.py         ← analytics runner
├── tests/
│   └── test_pipeline.py         ← 29 unit tests
├── reports/
│   ├── export_for_powerbi.py    ← exports Oracle data for Power BI
│   └── dashboard_screenshots/   ← Power BI dashboard screenshots
├── .env                         ← credentials (not in GitHub)
├── .gitignore                   ← excludes sensitive files
├── azure-pipelines.yml          ← Azure DevOps CI/CD pipeline
└── README.md                    ← this file
'''

How to Run Locally
Prerequisites

Python 3.12+
Docker Desktop
Oracle 23ai container running

### Setup
1. Clone the repo
git clone https://github.com/Ramisanan/healthcare-data-engineering.git
cd healthcare-data-engineering
2. Create virtual environment
python3 -m venv venv
source venv/bin/activate
3. Install dependencies
pip install oracledb pandas sqlalchemy pytest python-dotenv
4. Start Oracle in Docker
docker start oracle-healthcare
5. Create .env file
echo "ORACLE_USER=system" > .env
echo "ORACLE_PASSWORD=Health123" >> .env
echo "ORACLE_DSN=localhost:1521/FREEPDB1" >> .env
Run the Pipeline
Load data into Oracle
python3 etl/phase1_oracle_loader.py
Run ETL pipeline
python3 etl/pipeline.py
Run SQL analytics
python3 sql/run_analytics.py
Export data for Power BI
python3 reports/export_for_powerbi.py
Run unit tests
pytest tests/test_pipeline.py -v

### Author
Ramisa Anan
Data Engineer | MS Data Science & Analytics, Florida Atlantic University
LinkedIn
GitHub
EOF