# SubsTrack — CDC + SCD Type 2 Data Pipeline

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Snowflake](https://img.shields.io/badge/snowflake-✓-success.svg)](https://www.snowflake.com/)
[![dbt](https://img.shields.io/badge/dbt-1.8.5-orange.svg)](https://www.getdbt.com/)
[![FastAPI](https://img.shields.io/badge/fastapi-✓-informational.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

**Track customer plan changes from source to dashboard — with full historical accuracy.**

SubsTrack is an end-to-end data pipeline that captures customer plan changes (upgrades, downgrades, cancellations) from a SQLite source database, streams them into Snowflake via Change Data Capture (CDC), preserves every historical version using Slowly Changing Dimension Type 2 (SCD2), and visualizes the results in a real-time dashboard.

---

## Table of Contents

- [Architecture](#architecture)
- [The Problem This Solves](#the-problem-this-solves)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Pipeline Walkthrough](#pipeline-walkthrough)
- [dbt Models](#dbt-models)
- [Dashboard Pages](#dashboard-pages)
- [End-to-End Test Sequence](#end-to-end-test-sequence)
- [Key Concepts Explained](#key-concepts-explained)
- [Verification Queries](#verification-queries)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture

```
SQLite (Source)
    │
    │  CDC Extraction (watermark-based)
    ▼
CSV Files (timestamped, append-only)
    │
    │  PUT to Snowflake Stage
    ▼
┌────────────────────────────────────────────────┐
│              SNOWFLAKE DATA CLOUD              │
│                                                │
│  @RAW_STAGE  ──► Snowpipe ──► RAW.CUSTOMERS    │
│   (landing)     (auto-load)   (append-only)    │
│                                    │           │
│                                    ▼           │
│                             CUSTOMERS_STREAM   │
│                              (change log)      │
│                                    │           │
│                             TASK (MERGE)       │
│                                    │           │
│                             STAGING.CUSTOMERS   │
│                             (current state)    │
│                                    │           │
│                        ┌───────────┴───────────┐
│                        ▼                       ▼
│                 SNAPSHOTS                  MARTS
│              (SCD2 history)          (business-ready)
│                        │                       │
│                        └───────────┬───────────┘
│                                    │
└────────────────────────────────────┼───────────┘
                                     │
                                     ▼
                            FastAPI Dashboard
                         (4 pages, live queries)
```

### Data Flow Summary

```
Source → Extract → Stage → Load → Stream → Merge → Snapshot → Model → Dashboard
         (CDC)           (Snowpipe)     (Task)   (dbt)     (dbt)   (FastAPI)
```

---

## The Problem This Solves

### Without This Pipeline

Your production database has customers changing plans. You need to answer:

> "What plan was Alice on when she purchased in February?"

If you only store the **current** state, you'd answer **"Premium"** — which is **wrong**. Alice was on Basic in February. She upgraded to Premium in June.

### How SubsTrack Fixes It

1. **CDC** captures every change at the source (via `updated_at` timestamps)
2. **SCD2** preserves every version (Alice has 2 versions: Basic + Premium)
3. **Temporal joins** link purchases to the historically correct version
4. **Dashboard** visualizes the difference — "Plan when bought" vs "Current plan"

### Business Impact

| Question | Wrong Answer | Right Answer |
|---|---|---|
| What plan drove February revenue? | Premium ($79) | Basic ($29) |
| How long was Alice on Basic? | 0 days | 5 months |
| Which plan has highest retention? | Unknown | Tracked via SCD2 |

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Source Database** | SQLite 3 | Simulates production database (zero-config) |
| **Change Data Capture** | Python + Pandas | Watermark-based incremental extraction |
| **Data Warehouse** | Snowflake | Cloud storage, compute, and transformation |
| **Orchestration** | Snowpipe + Stream + Task | Serverless loading and processing |
| **Transformation** | dbt 1.8.5 | SCD2 snapshots, cleansing, mart models |
| **Dashboard** | FastAPI + Jinja2 + Plotly | Real-time visualization |
| **Package Manager** | pip | Dependency management |
| **Version Control** | Git | Source code tracking |

---

## Project Structure

```
substrack/
│
├── source/                          # Simulated production database
│   ├── create_db.py                 # Creates SQLite database schema
│   ├── seed_data.py                 # Seeds initial customers & purchases
│   └── simulate_changes.py          # Simulates plan upgrades/downgrades
│
├── pipeline/                        # CDC extraction and upload
│   ├── cdc_extract.py               # Reads watermark, extracts changes, writes CSVs
│   ├── upload_to_stage.py           # Uploads CSVs to Snowflake, triggers pipes & tasks
│   ├── watermark.json               # Tracks last processed timestamp
│   └── output/                      # Generated CSV files (gitignored)
│
├── snowflake/                       # Snowflake SQL setup scripts
│   ├── 01_setup.sql                 # Warehouse, database, schemas, stage, file format
│   ├── 02_raw_tables.sql            # RAW layer tables (append-only)
│   ├── 03_staging_tables.sql        # STAGING layer tables (current state)
│   ├── 04_snowpipe.sql              # Snowpipe definitions (serverless COPY)
│   ├── 05_streams.sql               # Stream definitions (change logs)
│   └── 06_tasks.sql                 # Task definitions (MERGE logic)
│
├── dbt_project/                     # dbt transformation project
│   ├── dbt_project.yml              # dbt configuration
│   ├── profiles.yml                 # Snowflake connection profile
│   ├── macros/
│   │   └── generate_schema_name.sql # Custom schema naming macro
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml          # Source table definitions
│   │   │   ├── schema.yml           # Tests (unique, not_null, accepted_values)
│   │   │   ├── stg_customers.sql    # Cleaned customer data
│   │   │   └── stg_purchases.sql    # Cleaned purchase data
│   │   └── marts/
│   │       ├── schema.yml           # Tests (relationships, etc.)
│   │       ├── dim_customer.sql     # Enriched customer dimension
│   │       └── fct_purchases.sql    # Purchase facts with temporal join
│   └── snapshots/
│       └── dim_customer_snapshot.sql # SCD2 snapshot configuration
│
├── streamlit/                       # FastAPI dashboard
│   ├── app.py                       # FastAPI application (4 routes)
│   ├── requirements.txt             # Python dependencies
│   ├── templates/
│   │   ├── base.html               # Base layout with navigation
│   │   ├── overview.html           # Pipeline status page
│   │   ├── customers.html          # Customer SCD2 history page
│   │   ├── purchases.html          # Purchase temporal analysis page
│   │   └── distribution.html       # Plan distribution page
│   └── static/                     # Static assets (CSS, JS)
│
├── .env                             # Snowflake credentials (gitignored)
├── .gitignore                       # Git exclusion rules
└── requirements.txt                 # Python dependencies
```

---

## Quick Start

### Prerequisites

```bash
python --version    # 3.8+
pip --version       # Latest
```

### 1. Clone and Install

```bash
git clone <repo-url> substrack
cd substrack
pip install -r requirements.txt
```

### 2. Configure Snowflake Credentials

Create `.env` in the project root:

```env
SNOWFLAKE_ACCOUNT=your_account_here
SNOWFLAKE_USER=your_username
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_WAREHOUSE=SUBSTRACK_WH
SNOWFLAKE_DATABASE=SUBSTRACK_DB
SNOWFLAKE_ROLE=SYSADMIN
```

### 3. Set Up Snowflake Infrastructure

```bash
python -c "from dotenv import load_dotenv; load_dotenv()"
python snowflake/01_setup.sql    # Run each SQL file in order through Snowflake
python snowflake/02_raw_tables.sql
python snowflake/03_staging_tables.sql
python snowflake/04_snowpipe.sql
python snowflake/05_streams.sql
python snowflake/06_tasks.sql
```

### 4. Seed Source Data

```bash
python source/create_db.py
python source/seed_data.py
```

### 5. Run the Pipeline

```bash
python pipeline/upload_to_stage.py
```

### 6. Run dbt Transformations

```bash
cd dbt_project
dbt snapshot
dbt run
dbt test
```

### 7. Start the Dashboard

```bash
cd ..
python streamlit/app.py
# Open http://127.0.0.1:8000
```

---

## Pipeline Walkthrough

### Phase 1: Source Data (`source/`)

The SQLite database simulates a production system. It contains two tables:

**`customers`** — The key column is `updated_at`. Every time a row changes, this timestamp updates. This is the **cursor** for CDC.

| Column | Example | Purpose |
|---|---|---|
| `customer_id` | CUST_001 | Primary key |
| `plan` | basic | Current plan tier |
| `plan_price` | 29.00 | Monthly price |
| `status` | active | Account status |
| `updated_at` | 2024-01-01 00:00:00 | **CDC cursor** — changes on every update |

**`purchases`** — Append-only. A purchase never changes once created.

### Phase 2: CDC Extraction (`pipeline/cdc_extract.py`)

Uses the **watermark pattern** — a JSON file stores the last processed timestamp.

```python
# Simplified logic
watermark = read_watermark()                          # "last checked at 2024-01-01"
changes = query("SELECT * WHERE updated_at > ?", watermark)  # Only what's NEW
write_csv(changes, f"{table}_{timestamp}.csv")        # Timestamped filename
save_watermark(current_time)                          # Update AFTER success
```

**Key design decisions:**
- Watermark saved **after** processing (at-least-once semantics)
- Filenames include timestamps (Snowpipe deduplication)
- `_change_type` column added (UPSERT/INSERT) for MERGE logic
- ORDER BY updated_at ensures chronological processing

### Phase 3: Snowflake Loading (`pipeline/upload_to_stage.py`)

```python
PUT file://customers.csv @RAW_STAGE/customers/    # Upload to stage
ALTER PIPE CUSTOMERS_PIPE REFRESH                  # Trigger Snowpipe
EXECUTE TASK PROCESS_CUSTOMERS_TASK                # Merge into staging
```

The pipeline is **on-demand** — no polling, no idle checks.

### Phase 4: Snowflake Objects

| Object | Function |
|---|---|
| **Stage** | Landing zone for CSV files |
| **File Format** | CSV parsing rules (headers, quoting, nulls) |
| **Snowpipe** | Serverless COPY INTO RAW tables |
| **Stream** | Change log on RAW tables (append-only) |
| **Task** | Executes MERGE from stream to staging |

### Phase 5: dbt Transformations

See [dbt Models](#dbt-models) section for detailed explanation.

### Phase 6: Dashboard

See [Dashboard Pages](#dashboard-pages) section.

---

## dbt Models

### Model Dependency Graph

```
STAGING.CUSTOMERS (source table)
    │
    │  stg_customers.sql (view)
    │    → Clean data, add plan_rank, days_since_signup
    │
    ├── dim_customer_snapshot.sql (snapshot)
    │     → SCD2: preserve every version
    │     → Adds: dbt_scd_id, dbt_valid_from, dbt_valid_to
    │
    │         │
    │         ▼
    │   dim_customer.sql (table)
    │     → Enrich: plan_tier, is_current, days_on_plan, estimated_revenue
    │
    ├── stg_purchases.sql (view)
    │     → Clean data, add purchase_month, purchase_year
    │
    └── fct_purchases.sql (table)
          → Temporal join: purchase_date BETWEEN valid_from AND valid_to
          → Output: plan_at_purchase (historically correct)
```

### Staging Models

**`stg_customers.sql`**
- Converts strings to proper types (dates, numbers)
- Lowercases and trims emails, plans, and statuses
- Derives `plan_rank` (free=0, basic=1, premium=2, enterprise=3)
- Calculates `days_since_signup`
- Excludes soft-deleted records (`_is_deleted = FALSE`)

**`stg_purchases.sql`**
- Trims product names
- Casts amounts and dates to proper types
- Derives `purchase_month` and `purchase_year`

### Snapshot Model

**`dim_customer_snapshot.sql`**

The core SCD2 configuration:

```sql
{% snapshot dim_customer_snapshot %}
{{
    config(
        target_schema='SNAPSHOTS',
        unique_key='customer_id',
        strategy='timestamp',
        updated_at='updated_at',
        invalidate_hard_deletes=True
    )
}}
SELECT * FROM {{ source('staging', 'customers') }}
{% endsnapshot %}
```

What dbt adds automatically:

| Column | Purpose |
|---|---|
| `dbt_scd_id` | Surrogate key (hash of customer_id + valid_from) |
| `dbt_updated_at` | Copy of updated_at that triggered this version |
| `dbt_valid_from` | When this version became active |
| `dbt_valid_to` | When this version ended (NULL = current) |

### Mart Models

**`dim_customer.sql`**
- Enriches snapshot with `plan_tier` (Starter/Growth/Enterprise)
- Adds `is_current` flag (NULL valid_to = TRUE)
- Calculates `days_on_plan` and `estimated_revenue_this_period`

**`fct_purchases.sql`** — The **temporal join**:

```sql
SELECT p.*, c.plan AS plan_at_purchase
FROM purchases p
LEFT JOIN dim_customer c
  ON p.customer_id = c.customer_id
 AND p.purchase_date >= c.valid_from::DATE
 AND p.purchase_date < COALESCE(c.valid_to::DATE, '9999-12-31')
```

This is the query that answers: *"What plan was the customer on WHEN they made this purchase?"*

### Data Tests

16 tests across all models:

| Test | Count | Purpose |
|---|---|---|
| `unique` | 4 | No duplicate primary/surrogate keys |
| `not_null` | 8 | Mandatory fields have values |
| `accepted_values` | 3 | Plans match valid tiers, statuses match valid states |
| `relationships` | 1 | Foreign key integrity (customer_sk → dim_customer) |

---

## Dashboard Pages

The dashboard is a FastAPI application with 4 routes. All data is queried live from Snowflake MARTS tables.

### Page 1: Pipeline Overview (`/`)

Displays:
- **Raw Records**: Total rows in RAW.CUSTOMERS (append-only log)
- **Staging Customers**: Current unique customers in STAGING
- **SCD2 Versions**: Total rows in SNAPSHOTS (all historical versions)
- **Total Purchases**: Purchases in MARTS.FCT_PURCHASES
- **Plan Distribution**: Bar chart of current customer plan counts

### Page 2: Customer History (`/customers`)

Features:
- Dropdown selector for each customer (from dim_customer)
- Plan timeline chart (colored bars per plan version)
- Historical version table with valid_from, valid_to, days_on_plan
- Shows `is_current` flag for active versions

### Page 3: Purchase Analysis (`/purchases`)

The **money page** — proves the temporal join works:
- Table with purchase details and **plan_at_purchase** vs **current_plan**
- Color-coded **DIFFERENT** (red) / **SAME** (green) labels
- Revenue by plan bar chart
- Purchase count by plan pie chart

### Page 4: Plan Distribution (`/distribution`)

Shows:
- Current plan distribution pie chart
- Monthly revenue by plan bar chart
- SCD2 versions per customer table (Alice: 2, Dave: 2, etc.)

### Running the Dashboard

```bash
python streamlit/app.py
# Visit http://127.0.0.1:8000
```

---

## End-to-End Test Sequence

### Full Test Run

```bash
# Step 1: Create fresh source data
python source/create_db.py
python source/seed_data.py

# Step 2: Run CDC pipeline (initial load)
python pipeline/upload_to_stage.py

# Step 3: Run dbt snapshot (capture version 1)
cd dbt_project
dbt snapshot
dbt run
dbt test

# Step 4: Simulate plan changes
python -c "
from source.simulate_changes import *
alice_upgrades_to_premium()
bob_downgrades_to_basic()
carol_cancels()
dave_upgrades_to_basic()
"

# Step 5: Run pipeline again (capture changes)
python pipeline/upload_to_stage.py

# Step 6: Run dbt snapshot (creates version 2)
cd dbt_project
dbt snapshot
dbt run
dbt test

# Step 7: View the proof
python pipeline/verify_temporal.py
python streamlit/app.py  # Open http://127.0.0.1:8000
```

### Expected Results

```
dbt test: 16/16 PASS

Temporal join:
  PUR_001 | Alice | Feb purchase | Plan: Basic  | Now: Premium | DIFFERENT ✓
  PUR_003 | Alice | May purchase | Plan: Basic  | Now: Premium | DIFFERENT ✓
  PUR_002 | Bob   | Feb purchase | Plan: Premium | Now: Basic   | DIFFERENT ✓
  PUR_004 | Dave  | Apr purchase | Plan: Free    | Now: Basic   | DIFFERENT ✓
  PUR_005 | Carol | Mar purchase | Plan: Enterprise | Now: Enterprise | SAME
```

---

## Key Concepts Explained

### Change Data Capture (CDC)

CDC identifies what changed in a database since you last checked. Instead of copying the entire table every time (slow and expensive), you only move what's new.

**Our approach: Watermark**
1. Store "last processed timestamp" in a JSON file
2. Query `WHERE updated_at > watermark`
3. Save new watermark after successful processing

**Safety guarantee**: At-least-once semantics. If the script crashes mid-way, the next run reprocesses the same batch. No data loss.

### SCD Type 2 (Slowly Changing Dimension Type 2)

SCD2 preserves every version of a record. When a customer changes plans, the old version is "closed" (given an end date) and a new version is "opened" (given a start date).

**Without SCD2**: You only know the current state. Historical questions are impossible.

**With SCD2**: You can answer "What was true at any point in time?"

| Version | Customer | Plan | Valid From | Valid To | Status |
|---|---|---|---|---|---|
| 1 | Alice | Basic | 2024-01-01 | 2026-06-05 | Closed |
| 2 | Alice | Premium | 2026-06-05 | NULL | Current |

### Temporal Join

A temporal join links two tables using time ranges. It answers: "What was the state of dimension X when fact Y occurred?"

```sql
SELECT purchase.*, customer.plan
FROM purchase
JOIN customer
  ON purchase.customer_id = customer.customer_id
 AND purchase.date BETWEEN customer.valid_from AND customer.valid_to
```

This is the core analytical pattern for historical accuracy.

### Medallion Architecture

| Layer | Name | Description |
|---|---|---|
| Bronze | RAW | Raw data as-is from source |
| Silver | STAGING + SNAPSHOTS | Cleaned, typed, historically preserved |
| Gold | MARTS | Business-ready, denormalized, tested |

---

## Verification Queries

Run these in Snowflake to validate the pipeline:

### 1. Alice's Plan History (2 versions expected)

```sql
SELECT customer_id, full_name, plan, valid_from, valid_to, is_current
FROM SUBSTRACK_DB.MARTS.DIM_CUSTOMER
WHERE customer_id = 'CUST_001'
ORDER BY valid_from;
```

### 2. Dave's Plan History (2 versions expected)

```sql
SELECT customer_id, full_name, plan, valid_from, valid_to, is_current
FROM SUBSTRACK_DB.MARTS.DIM_CUSTOMER
WHERE customer_id = 'CUST_004'
ORDER BY valid_from;
```

### 3. Temporal Join Proof

```sql
SELECT
    f.purchase_id,
    f.customer_name,
    f.purchase_date,
    f.amount,
    f.plan_at_purchase,    -- Historically accurate plan
    c.plan AS current_plan  -- Current plan (may be different)
FROM SUBSTRACK_DB.MARTS.FCT_PURCHASES f
JOIN SUBSTRACK_DB.MARTS.DIM_CUSTOMER c
    ON f.customer_id = c.customer_id AND c.is_current = TRUE
WHERE f.customer_id = 'CUST_001'
ORDER BY f.purchase_date;
```

### 4. No Overlapping Date Ranges (Data Quality)

```sql
SELECT a.customer_id, a.valid_from, a.valid_to, b.valid_from, b.valid_to
FROM SUBSTRACK_DB.MARTS.DIM_CUSTOMER a
JOIN SUBSTRACK_DB.MARTS.DIM_CUSTOMER b
    ON a.customer_id = b.customer_id
    AND a.customer_sk != b.customer_sk
    AND a.valid_from < COALESCE(b.valid_to, '9999-12-31')
    AND b.valid_from < COALESCE(a.valid_to, '9999-12-31');
-- Expected: 0 rows (no overlaps)
```

### 5. Pipeline Counts

```sql
SELECT 'RAW.CUSTOMERS' AS table_name, COUNT(*) FROM SUBSTRACK_DB.RAW.CUSTOMERS
UNION ALL
SELECT 'STAGING.CUSTOMERS', COUNT(*) FROM SUBSTRACK_DB.STAGING.CUSTOMERS
UNION ALL
SELECT 'SNAPSHOTS.DIM_CUSTOMER_SNAPSHOT', COUNT(*) FROM SUBSTRACK_DB.SNAPSHOTS.DIM_CUSTOMER_SNAPSHOT
UNION ALL
SELECT 'MARTS.DIM_CUSTOMER', COUNT(*) FROM SUBSTRACK_DB.MARTS.DIM_CUSTOMER
UNION ALL
SELECT 'MARTS.FCT_PURCHASES', COUNT(*) FROM SUBSTRACK_DB.MARTS.FCT_PURCHASES;
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Commit Convention

We use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: new feature
fix: bug fix
docs: documentation
refactor: code change without behavior change
test: adding tests
chore: maintenance
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for learning, designed for production.*
