# Healthcare Data Engineering Project

An end-to-end data engineering project built for a retail pharmacy environment.

This project demonstrates production-grade data engineering skills across data ingestion, transformation, validation, analytics, CI/CD automation, and Power BI reporting.

## Project Overview

The goal of this project is to simulate a real healthcare and retail pharmacy data environment using Oracle 23ai, Python ETL pipelines, SQL analytics, automated testing, Azure DevOps CI/CD, and Power BI dashboards.

The project includes synthetic healthcare retail data, data quality validations, optimized SQL analytics, automated unit testing, and business intelligence reporting.

## Tech Stack

| Tool         | Purpose                                    |
| ------------ | ------------------------------------------ |
| Oracle 23ai  | Source database running in Docker          |
| Python       | ETL pipeline and synthetic data generation |
| oracledb     | Oracle database connection driver          |
| SQL / T-SQL  | Analytics and data transformation          |
| Azure DevOps | CI/CD pipeline automation                  |
| pytest       | Unit testing                               |
| Power BI     | Business intelligence dashboard            |
| Docker       | Oracle database containerization           |
| Git / GitHub | Version control                            |

## Project Phases

| Phase   | Description                                                                |
| ------- | -------------------------------------------------------------------------- |
| Phase 1 | Oracle 23ai setup and synthetic data generation                            |
| Phase 2 | ETL pipeline with 20+ data quality validation rules                        |
| Phase 3 | SQL analytics using window functions and business logic                    |
| Phase 4 | Azure DevOps CI/CD pipeline with automated unit testing                    |
| Phase 5 | Power BI dashboard with sales, pharmacy, inventory, and customer analytics |

## Dataset Overview

The project contains 8,570 synthetic records across 6 healthcare retail tables.

| Table              | Records | Description                     |
| ------------------ | ------: | ------------------------------- |
| store_locations    |      20 | Pharmacy store master data      |
| products           |      50 | Product catalog with pricing    |
| customers          |     500 | Customer loyalty profiles       |
| sales_transactions |   5,000 | Point-of-sale transaction data  |
| prescription_fills |   2,000 | Pharmacy prescription fill data |
| inventory_levels   |   1,000 | Store inventory snapshot data   |

## Key Achievements

* Loaded 8,570 records into Oracle 23ai running in Docker
* Built an ETL pipeline with 20+ data quality validation rules
* Created 15 optimized SQL analytics queries
* Implemented 29 pytest unit tests
* Built a 4-stage Azure DevOps CI/CD pipeline
* Created a Power BI dashboard with 4 report pages
* Added a full ETL audit trail with run timestamps and logging

## Data Quality Validation

The ETL pipeline includes validation rules across all 6 tables.

Examples of validations include:

* Null checks for required fields
* Duplicate record checks
* Price and quantity validation
* Inventory level validation
* Date range validation
* Foreign key relationship checks
* Loyalty member validation
* Prescription data consistency checks
* Transaction amount validation

## SQL Analytics

The project includes 15 optimized SQL queries for business analysis.

Key analytics include:

* Store revenue ranking using window functions
* Month-over-month revenue trends using `LAG()`
* Running revenue totals using `SUM() OVER()`
* Stockout rate by region
* Customer lifetime value analysis
* Prescription volume by drug name
* Revenue by state
* Insurance provider claim distribution
* Loyalty member vs non-member sales analysis

## Power BI Dashboard

The Power BI dashboard provides business insights across sales, pharmacy, inventory, and customer data.

### Page 1: Sales Overview

This page shows pharmacy store performance across the retail network.

Key visuals include:

* Total revenue KPI card
* Top stores by revenue
* Monthly revenue trend for 2024
* Revenue breakdown by state
* Insurance provider claim distribution

Key metric:

* Total revenue: **$735.37K**

### Page 2: Pharmacy & Inventory Analytics

This page focuses on pharmacy operations and inventory insights.

Key visuals include:

* Stockout alerts for products with zero inventory
* Prescription volume by drug name
* Total prescription count
* Loyalty member vs non-member transaction breakdown
* Insurance provider analysis

Key metric:

* Total prescriptions: **2,000**

## CI/CD Pipeline

The project uses Azure DevOps to automate quality checks, testing, build, and deployment on every GitHub push.

### Pipeline Stages

| Stage        | Description                     |
| ------------ | ------------------------------- |
| Code Quality | Runs flake8 linting             |
| Unit Tests   | Runs pytest test suite          |
| Build        | Packages project artifacts      |
| Deploy       | Simulates production deployment |

All 29 unit tests pass successfully.

```bash
29 passed in 0.10s
```

## Project Structure

```text
healthcare-data-engineering/
├── etl/
│   ├── phase1_oracle_loader.py      # Generates and loads synthetic data into Oracle
│   └── pipeline.py                  # ETL pipeline with validation rules
│
├── sql/
│   ├── analytics.sql                # 15 optimized SQL analytics queries
│   └── run_analytics.py             # Runs analytics queries
│
├── tests/
│   └── test_pipeline.py             # 29 unit tests
│
├── reports/
│   ├── export_for_powerbi.py        # Exports Oracle data for Power BI
│   └── dashboard_screenshots/       # Power BI dashboard screenshots
│
├── .env.example                     # Example environment file
├── .gitignore                       # Excludes sensitive and unnecessary files
├── azure-pipelines.yml              # Azure DevOps CI/CD pipeline
└── README.md                        # Project documentation
```

## How to Run Locally

### Prerequisites

Make sure the following tools are installed:

* Python 3.12+
* Docker Desktop
* Oracle 23ai Docker container
* Git

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Ramisanan/healthcare-data-engineering.git
cd healthcare-data-engineering
```

### 2. Create a Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

For Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install oracledb pandas sqlalchemy pytest python-dotenv
```

### 4. Start Oracle 23ai Docker Container

```bash
docker start oracle-healthcare
```

### 5. Create Environment File

```bash
cp .env.example .env
```

Then update the `.env` file with your Oracle database credentials.

Example:

```env
ORACLE_USER=your_username
ORACLE_PASSWORD=your_password
ORACLE_DSN=localhost:1521/FREEPDB1
```

## Running the Project

### Load Synthetic Data into Oracle

```bash
python3 etl/phase1_oracle_loader.py
```

### Run the ETL Pipeline

```bash
python3 etl/pipeline.py
```

### Run SQL Analytics

```bash
python3 sql/run_analytics.py
```

### Export Data for Power BI

```bash
python3 reports/export_for_powerbi.py
```

### Run Unit Tests

```bash
pytest tests/test_pipeline.py -v
```

## Sample Business Insights

This project helps answer questions such as:

* Which pharmacy stores generate the highest revenue?
* How does revenue trend month over month?
* Which regions have the highest stockout rate?
* Which drugs have the highest prescription volume?
* How do loyalty members compare with non-members?
* Which insurance providers contribute the most claims?

## Security Notes

Sensitive files are excluded from GitHub using `.gitignore`.

Examples of excluded files:

* `.env`
* Database credentials
* Local environment files
* Temporary files
* Python cache folders

Use `.env.example` as a template and never commit real credentials.

## Author

**Ramisa Anan**
Data Engineer
MS Data Science & Analytics, Florida Atlantic University
