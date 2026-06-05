# SubsTrack — CDC + SCD Type 2 Data Pipeline

[![Python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Snowflake](https://img.shields.io/badge/snowflake-✓-success.svg)](https://www.snowflake.com/)
[![dbt](https://img.shields.io/badge/dbt-1.8.5-orange.svg)](https://www.getdbt.com/)
[![FastAPI](https://img.shields.io/badge/fastapi-✓-informational.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

---

**Track customer plan changes from source to dashboard — with full historical accuracy, at scale.**

SubsTrack captures plan changes from **1,000+ customers** across **7 interconnected source tables** (customers, purchases, subscriptions, billing invoices, payment methods, usage events, support tickets), streams them into Snowflake via CDC, preserves every historical version using SCD Type 2, and visualizes everything in a **6-page live dashboard**.

---

## Scale

| Metric | Count |
|---|---|
| Customers | **1,000** |
| Source Tables | **7** |
| Purchases | ~2,000 |
| Subscriptions | ~1,100 |
| Billing Invoices | ~6,000 |
| Usage Events | ~4,000 |
| Support Tickets | ~2,000 |
| **Total Pipeline Records** | **~16,000+** |
| SCD2 Snapshots | **4** |
| Dashboard Pages | **6** |
| dbt Tests | **25+** |

---

## Table of Contents

- [Architecture](#architecture)
- [The Problem This Solves](#the-problem-this-solves)
- [Entity Relationship Diagram](#entity-relationship-diagram)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Pipeline Walkthrough](#pipeline-walkthrough)
- [dbt Models](#dbt-models)
- [Dashboard Pages](#dashboard-pages)
- [Key Concepts Explained](#key-concepts-explained)
- [Verification Queries](#verification-queries)
- [Contributing](#contributing)
- [License](#license)

---

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────┐
│                     LAYER 1: SOURCE & INGESTION                          │
│                                                                          │
│  ┌─────────────────────┐    ┌──────────────────┐    ┌───────────────┐   │
│  │      SQLite DB       │    │  CDC Engine       │    │ @RAW_STAGE    │   │
│  │  ┌───────┐ 1,000 rr │───→│  watermark.json   │───→│  /customers/  │   │
│  │  │customers│         │    │  SELECT * WHERE   │    │  /purchases/  │   │
│  │  ├────────┤         │    │  updated_at > ?    │    │  /subs/       │   │
│  │  │purchases│ 2,000   │    │  ─→ CSV files     │    │  /invoices/   │   │
│  │  ├────────┤         │    └──────────────────┘    │  /payments/   │   │
│  │  │subs     │ 1,100   │                           │  /usage/      │   │
│  │  ├────────┤         │                           │  /tickets/    │   │
│  │  │invoices │ 6,000   │                           └───────┬───────┘   │
│  │  ├────────┤         │                                   │           │
│  │  │payments │ 1,060   │                                   │ PUT file  │
│  │  ├────────┤         │                                   ▼           │
│  │  │usage    │ 4,000   │                           ALTER PIPE REFRESH │
│  │  ├────────┤         │                                   │           │
│  │  │tickets  │ 2,000   │                                   ▼           │
│  │  └───────┘          │                           ┌──────────────┐   │
│  └─────────────────────┘                           │  Snowpipe    │   │
│                                                     │ (7 pipes)    │   │
│                                                     └──────┬───────┘   │
└─────────────────────────────────────────────────────────────┼──────────┘
                                                               │
┌─────────────────────────────────────────────────────────────┼──────────┐
│                     LAYER 2: SNOWFLAKE PROCESSING           │          │
│                                                             ▼          │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                     RAW TABLES (append-only)                  │     │
│  │   RAW.CUSTOMERS (all 1,000+ versions stacked)                │     │
│  │   RAW.PURCHASES │ RAW.SUBSCRIPTIONS │ RAW.BILLING_INVOICES   │     │
│  │   RAW.PAYMENT_METHODS │ RAW.USAGE_EVENTS │ RAW.SUPPORT_TICKETS│     │
│  └──────────────────────────────────────────────────────────────┘     │
│                              │                                         │
│                              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │              STREAMS (change logs, APPEND_ONLY)              │     │
│  │   7 streams — one per RAW table — capture new rows           │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                              │                                         │
│                              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │              TASKS (manual MERGE, NO SCHEDULE)               │     │
│  │   7 tasks — MERGE FROM stream INTO STAGING tables            │     │
│  │   EXECUTE TASK PROCESS_CUSTOMERS_TASK (manual trigger)       │     │
│  └──────────────────────────────────────────────────────────────┘     │
│                              │                                         │
│                              ▼                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │            STAGING TABLES (1 row per entity = current state)  │     │
│  │   STAGING.CUSTOMERS (1,000 rows), STAGING.PURCHASES, etc.    │     │
│  └──────────────────────────────────────────────────────────────┘     │
└───────────────────────────────────────────────────────────────────────┘
                              │
                              │ dbt snapshot + run
                              ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     LAYER 3: dbt TRANSFORMATIONS                      │
│                                                                       │
│  ┌──────────────┐    ┌──────────────────┐    ┌──────────────────┐    │
│  │   STAGING    │    │    SCD2          │    │     MARTS        │    │
│  │   MODELS     │───→│   SNAPSHOTS      │───→│    MODELS        │    │
│  │  (7 views)   │    │   (4 snapshots)  │    │   (6 tables)     │    │
│  │              │    │                  │    │                  │    │
│  │ plan_rank    │    │ customers:       │    │ dim_customer     │    │
│  │ days_since   │    │   Alice v1:Basic │    │ dim_subscription │    │
│  │ purchase_mth │    │   Alice v2:Prm   │    │ dim_support_tkt  │    │
│  │ event_cat    │    │ subscriptions    │    │ fct_purchases ✦  │    │
│  │ is_paid      │    │ payment_methods  │    │ fct_invoices     │    │
│  │ ticket_age   │    │ support_tickets  │    │ fct_usage_events │    │
│  └──────────────┘    └──────────────────┘    └──────────────────┘    │
│                                                           │          │
│                                              ✦ temporal join:       │
│                                           purchase_date BETWEEN     │
│                                           valid_from AND valid_to   │
└───────────────────────────────────────────────────────────────────────┘
                              │
                              │ FastAPI live queries
                              ▼
┌───────────────────────────────────────────────────────────────────────┐
│                     LAYER 4: DASHBOARD                                │
│                                                                       │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐                              │
│  │Overview  │ │Customers │ │Purchases │                              │
│  │8 metrics │ │SCD2      │ │DIFFERENT │                              │
│  │plan chart│ │timeline  │ │/SAME     │                              │
│  ├──────────┤ ├──────────┤ ├──────────┤                              │
│  │Subscript.│ │Billing   │ │Usage     │                              │
│  │active/   │ │revenue   │ │by cat.   │                              │
│  │cancelled │ │chart     │ │per cust. │                              │
│  └──────────┘ └──────────┘ └──────────┘                              │
└───────────────────────────────────────────────────────────────────────┘
```

### Data Flow Summary

```
SQLite (7 tables) → CDC (watermark extract) → Snowflake Stage
  → Snowpipe (7, auto COPY) → RAW (append-only)
  → Stream (7, capture deltas) → Task (7, manual MERGE)
  → Staging (current state) → dbt (staging → SCD2 snapshots → marts)
  → FastAPI Dashboard (6 pages, live)
```

---

## The Problem This Solves

### Without This Pipeline

Your production database has customers changing plans. You need to answer:

> "What plan was Alice on when she purchased in February?"

If you only store the **current** state, you'd answer **"Premium"** — which is **wrong**. Alice was on Basic in February. She upgraded to Premium in June.

Now imagine this across **1,000 customers** with **2,000 purchases** and **6,000 invoices**. Without SCD2, every historical report is wrong.

### How SubsTrack Fixes It

1. **CDC** captures every change across all 7 tables (via `updated_at` timestamps)
2. **SCD2** preserves every version — 4 snapshots track customers, subscriptions, payment methods, and support ticket status
3. **Temporal joins** link every fact to the historically correct dimension version
4. **Dashboard** visualizes the difference — "Plan when bought" vs "Current plan"

### Business Impact

| Question | Wrong Answer | Right Answer |
|---|---|---|
| What plan drove February revenue? | Premium ($79) | Basic ($29) |
| How long was Alice on Basic? | 0 days | 5 months |
| Which plan has highest retention? | Unknown | Tracked via SCD2 |
| How many invoices were overdue? | Unknown | Tracked via billing mart |
| Which customers use the most API calls? | Unknown | Tracked via usage mart |

---

## Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────────┐       ┌──────────────────┐
│  customers   │──1:N──│    purchases     │       │  usage_events    │
│  (1,000)     │       │    (~2,000)      │       │  (~4,000)        │
└──────┬───────┘       └──────────────────┘       └──────────────────┘
       │
       │──1:N──┌──────────────────┐       ┌──────────────────┐
       │       │  subscriptions   │       │  payment_methods │
       │       │  (~1,100)        │       │  (~1,060)        │
       │       └──────────────────┘       └──────────────────┘
       │
       │──1:N──┌──────────────────┐       ┌──────────────────┐
       │       │ billing_invoices │       │ support_tickets  │
       │       │  (~6,000)        │       │  (~2,000)        │
               └──────────────────┘       └──────────────────┘
```

---

## Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Source Database** | SQLite 3 | Zero-config, seeded with 1,000+ customers |
| **Change Data Capture** | Python | Watermark-based, 7-table dynamic extraction |
| **Data Warehouse** | Snowflake | Medallion architecture (RAW → STAGING → SNAPSHOTS → MARTS) |
| **Orchestration** | Snowpipe + Stream + Task | 7 pipes, 7 streams, 7 tasks — all manual |
| **Transformation** | dbt 1.8.5 + dbt_utils | 7 staging models + 4 SCD2 snapshots + 6 mart models |
| **Data Tests** | dbt built-in | 25+ tests: unique, not_null, accepted_values, relationships |
| **Dashboard** | FastAPI + Jinja2 + Plotly | 6 pages, live queries to Snowflake |
| **Version Control** | Git | Conventional commits |

---

## Project Structure

```
substrack/
│
├── source/                       # Simulated production database
│   ├── create_db.py              # 7-table schema creation
│   ├── seed_data.py              # Seeds 1,000+ customers with full SaaS data
│   └── simulate_changes.py       # Batch simulation functions (plan changes, cancellations, tickets, etc.)
│
├── pipeline/                     # CDC extraction and upload
│   ├── cdc_extract.py            # Dynamic CDC — TABLE_CONFIGS dict drives all 7 tables
│   ├── upload_to_stage.py        # Uploads CSVs, triggers pipes + tasks (no hardcoded tables)
│   ├── watermark.json            # Tracks last processed timestamp per table
│   └── output/                   # Generated CSV files (gitignored)
│
├── snowflake/                    # Snowflake SQL setup scripts
│   ├── 01_setup.sql              # Warehouse, database, 4 schemas, stage, file format
│   ├── 02_raw_tables.sql         # 7 RAW tables (append-only with _loaded_at)
│   ├── 03_staging_tables.sql     # 7 STAGING tables (current state with type casting)
│   ├── 04_snowpipe.sql           # 7 Snowpipe definitions (AUTO_INGEST = FALSE)
│   ├── 05_streams.sql            # 7 Streams (APPEND_ONLY = TRUE)
│   └── 06_tasks.sql              # 7 Tasks (NO SCHEDULE — manual MERGE logic)
│
├── dbt_project/                  # dbt transformation project
│   ├── dbt_project.yml           # Config with model paths, schema mapping
│   ├── profiles.yml              # Snowflake connection (env var pattern)
│   ├── packages.yml              # dbt_utils dependency
│   ├── macros/
│   │   └── generate_schema_name.sql
│   ├── models/
│   │   ├── staging/
│   │   │   ├── sources.yml       # 7 source table definitions
│   │   │   ├── schema.yml        # 25+ tests across all staging models
│   │   │   ├── stg_customers.sql
│   │   │   ├── stg_purchases.sql
│   │   │   ├── stg_subscriptions.sql
│   │   │   ├── stg_billing_invoices.sql
│   │   │   ├── stg_payment_methods.sql
│   │   │   ├── stg_usage_events.sql
│   │   │   └── stg_support_tickets.sql
│   │   └── marts/
│   │       ├── schema.yml        # Mart-level tests
│   │       ├── dim_customer.sql  # SCD2-enriched customer dimension
│   │       ├── dim_subscription.sql # Subscription dimension
│   │       ├── dim_support_ticket.sql # Ticket history dimension
│   │       ├── fct_purchases.sql # Temporal join proof
│   │       ├── fct_billing_invoices.sql # Revenue tracking
│   │       └── fct_usage_events.sql # Usage analytics
│   └── snapshots/
│       ├── dim_customer_snapshot.sql    # SCD2 — timestamp strategy
│       ├── dim_subscription_snapshot.sql
│       ├── dim_payment_method_snapshot.sql
│       └── dim_support_ticket_snapshot.sql
│
├── streamlit/                    # FastAPI dashboard
│   ├── app.py                    # 6 routes, live Snowflake queries
│   └── templates/
│       ├── base.html             # Nav with 7 links
│       ├── overview.html         # 8 metric cards + plan chart
│       ├── customers.html        # SCD2 timeline per customer
│       ├── purchases.html        # DIFFERENT/SAME temporal proof
│       ├── subscriptions.html    # Active vs cancelled breakdown
│       ├── billing.html          # Revenue and invoice status
│       ├── usage.html            # Usage category + per-customer
│       └── distribution.html     # Plan distribution analytics
│
├── .env                          # Snowflake credentials (gitignored)
├── .gitignore
├── requirements.txt
├── README.md
└── ARCHITECTURE-POSTER.md        # Midjourney/DALL-E prompt for architecture visual
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

Run each SQL file through Snowflake (Snowsight or SnowSQL):

```bash
snowsql -f snowflake/01_setup.sql
snowsql -f snowflake/02_raw_tables.sql
snowsql -f snowflake/03_staging_tables.sql
snowsql -f snowflake/04_snowpipe.sql
snowsql -f snowflake/05_streams.sql
snowsql -f snowflake/06_tasks.sql
```

### 4. Seed Source Data (1,000+ customers)

```bash
python source/create_db.py
python source/seed_data.py     # Generates ~16,000 records deterministic
```

### 5. Run the Pipeline

```bash
python pipeline/upload_to_stage.py   # Extracts, uploads, triggers pipes + tasks
```

### 6. Run dbt Transformations

```bash
cd dbt_project
dbt deps             # Install dbt_utils
dbt snapshot         # Create SCD2 versions
dbt run              # Build mart models
dbt test             # 25+ tests
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

The SQLite database contains **7 tables** with **~16,000 total records**:

**`customers` (1,000 rows)** — The key column is `updated_at`. Every time a row changes, this timestamp updates. This is the **cursor** for CDC.

| Column | Example | Purpose |
|---|---|---|
| `customer_id` | CUST_0001 | Primary key |
| `plan` | basic | Current plan tier |
| `plan_price` | 29.00 | Monthly price |
| `status` | active | Account status |
| `updated_at` | 2024-01-01 00:00:00 | **CDC cursor** |

**All 7 tables** have `updated_at` or `created_at` timestamps that serve as CDC cursors. The CDC engine dynamically discovers which cursor field to use from a central configuration dictionary.

### Phase 2: CDC Extraction (`pipeline/cdc_extract.py`)

Uses the **watermark pattern** with a dynamic `TABLE_CONFIGS` dict:

```python
TABLE_CONFIGS = {
    "customers": {"cursor_field": "updated_at", "change_type": "UPSERT", ...},
    "purchases": {"cursor_field": "created_at", "change_type": "INSERT", ...},
    "subscriptions": {"cursor_field": "updated_at", "change_type": "UPSERT", ...},
    # ... all 7 tables defined here
}
```

**Key design decisions:**
- Watermark saved **after** processing (at-least-once semantics)
- No hardcoded table names — adding a new table = 1 entry in TABLE_CONFIGS
- `_change_type` column (UPSERT/INSERT) for MERGE logic
- ORDER BY cursor ensures chronological processing

### Phase 3: Snowflake Loading (`pipeline/upload_to_stage.py`)

Dynamic pipeline loops over all 7 tables with data:

```python
for t in TABLE_CONFIGS:
    if file_exists:
        upload_file_to_stage(table_file, stage_path)
        trigger_snowpipe(pipe_name)

time.sleep(5)  # Wait for Snowpipe

for t in tables_with_data:
    execute_task(task_name)
```

### Phase 4: Snowflake Objects (7 of each)

| Object | Count | Function |
|---|---|---|
| **Stage** | 1 | Landing zone for all 7 table CSVs |
| **File Format** | 1 | CSV parsing rules |
| **Snowpipe** | 7 | Serverless COPY INTO RAW tables |
| **Stream** | 7 | Change log on each RAW table |
| **Task** | 7 | MERGE from stream to staging |

All tasks: **NO SCHEDULE** — run only via `EXECUTE TASK` after `ALTER PIPE REFRESH`.

### Phase 5: dbt Transformations

7 staging models → 4 SCD2 snapshots → 6 mart models. See [dbt Models](#dbt-models).

### Phase 6: Dashboard

6-page FastAPI app with live Snowflake queries. See [Dashboard Pages](#dashboard-pages).

---

## dbt Models

### Model Dependency Graph

```
STAGING schema (7 source tables)
    │
    ├── stg_customers.sql ──→ dim_customer_snapshot ──→ dim_customer
    ├── stg_subscriptions.sql ──→ dim_subscription_snapshot ──→ dim_subscription
    ├── stg_support_tickets.sql ──→ dim_support_ticket_snapshot ──→ dim_support_ticket
    ├── stg_payment_methods.sql ──→ dim_payment_method_snapshot
    ├── stg_purchases.sql ──→ fct_purchases (temporal join with dim_customer)
    ├── stg_billing_invoices.sql ──→ fct_billing_invoices (join with dim_customer)
    └── stg_usage_events.sql ──→ fct_usage_events (join with dim_customer)
```

### Staging Models (7 views)

Each staging model cleans, types, and enriches source data:

| Model | Enrichments |
|---|---|
| `stg_customers` | `plan_rank` (0-3), `days_since_signup` |
| `stg_purchases` | `purchase_month`, `purchase_year` |
| `stg_subscriptions` | `plan_rank`, `is_active` |
| `stg_billing_invoices` | `is_paid`, `days_to_pay` |
| `stg_payment_methods` | `is_valid`, `expiration_date` |
| `stg_usage_events` | `event_category`, `event_date`, `event_month` |
| `stg_support_tickets` | `priority_rank`, `ticket_age_days`, `is_resolved` |

### SCD2 Snapshots (4 snapshots)

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

Applied to: `customers`, `subscriptions`, `payment_methods`, `support_tickets`.

What dbt adds automatically:

| Column | Purpose |
|---|---|
| `dbt_scd_id` | Surrogate key (hash of entity_id + valid_from) |
| `dbt_updated_at` | Copy of the cursor timestamp |
| `dbt_valid_from` | When this version became active |
| `dbt_valid_to` | When this version ended (NULL = current) |

### Mart Models (6 tables)

| Model | Type | Key Logic |
|---|---|---|
| `dim_customer` | Table | `plan_tier`, `is_current`, `days_on_plan`, `estimated_revenue` |
| `dim_subscription` | Table | `plan_tier`, `total_subscription_days`, subscription lifecycle |
| `dim_support_ticket` | Table | SCD2-enriched ticket status history |
| `fct_purchases` | Table | **Temporal join**: `purchase_date BETWEEN dbt_valid_from AND COALESCE(dbt_valid_to, '9999-12-31')` |
| `fct_billing_invoices` | Table | `collected_revenue`, `outstanding_revenue` |
| `fct_usage_events` | Table | Usage per customer with plan context |

The temporal join in `fct_purchases` is the core analytical pattern:

```sql
SELECT p.*, c.plan AS plan_at_purchase, c.plan_tier AS plan_tier_at_purchase
FROM stg_purchases p
LEFT JOIN dim_customer c
    ON p.customer_id = c.customer_id
    AND p.purchase_date >= c.dbt_valid_from::DATE
    AND p.purchase_date < COALESCE(c.dbt_valid_to::DATE, '9999-12-31')
```

### Data Tests (25+)

| Test | Count | Tables |
|---|---|---|
| `unique` | 7 | Primary/surrogate keys across staging + mart models |
| `not_null` | 12 | Key business fields |
| `accepted_values` | 8 | Plans (free/basic/premium/enterprise), statuses, priorities, types |
| `relationships` | 3 | Foreign key integrity (customer_id → dim_customer) |

---

## Dashboard Pages

The dashboard is a FastAPI application with **6 routes**. All data is queried live from Snowflake MARTS tables via Plotly charts.

### Page 1: Pipeline Overview (`/`)

**8 metric cards** showing record counts across all pipeline stages:
- Raw Customers, Staging Customers, SCD2 Versions, Purchases
- Subscriptions, Invoices, Usage Events, Support Tickets
- Plan distribution bar chart

### Page 2: Customer History (`/customers`)

- Dropdown selector across all 1,000 customers
- SCD2 timeline chart (colored bars per plan version)
- Historical version table with valid_from, valid_to, days_on_plan, is_current

### Page 3: Purchase Analysis (`/purchases`)

The **temporal join proof** page:
- Table with purchase details + **plan_at_purchase** vs **current_plan**
- **🔴 DIFFERENT** / **🟢 SAME** badges
- Revenue by plan, purchase count by plan charts

### Page 4: Subscriptions (`/subscriptions`)

- Active vs cancelled pie chart
- Plan breakdown bar chart
- Full subscription table with plan, price, status, dates

### Page 5: Billing & Revenue (`/billing`)

- Monthly collected revenue bar chart
- Invoice status pie chart (paid/pending/overdue/refunded)
- Invoice table with payment status and days_to_pay

### Page 6: Usage Analytics (`/usage`)

- Usage distribution pie chart (api_call, storage, bandwidth, users)
- Per-customer usage grouped bar chart
- Usage event type breakdown table

### Running the Dashboard

```bash
python streamlit/app.py
# Visit http://127.0.0.1:8000
```

---

## Key Concepts Explained

### Change Data Capture (CDC)

CDC identifies what changed since you last checked. Instead of full-table copies, you only move what's new.

**Our approach: Watermark**
1. Store "last processed timestamp" in `watermark.json`
2. Query `WHERE cursor_field > watermark` for all 7 tables
3. Save new watermark after successful processing

**Safety guarantee**: At-least-once semantics. If the script crashes mid-way, the next run reprocesses the same batch. No data loss.

### SCD Type 2 (Slowly Changing Dimension Type 2)

SCD2 preserves every version of a record. When Alice upgrades from Basic to Premium, the old version closes and a new version opens.

**Without SCD2**: You only know the current state.

**With SCD2**: You can answer "What was true at any point in time?"

| Version | Customer | Plan | Valid From | Valid To | Status |
|---|---|---|---|---|---|
| 1 | Alice | Basic | 2024-01-01 | 2026-06-05 | Closed |
| 2 | Alice | Premium | 2026-06-05 | NULL | Current |

### Temporal Join

Links facts to the historically correct dimension version using date ranges:

```sql
SELECT purchase.*, customer.plan
FROM purchase
JOIN customer
  ON purchase.customer_id = customer.customer_id
 AND purchase.date BETWEEN customer.valid_from AND customer.valid_to
```

This is the core analytical pattern for historical accuracy.

### Why Manual Tasks?

All Snowflake tasks have **NO SCHEDULE**. The pipeline runs in 3 manual steps:
1. `PUT file://... @RAW_STAGE` — upload CSV
2. `ALTER PIPE xxx REFRESH` — trigger Snowpipe (required because internal stage can't auto-ingest)
3. `EXECUTE TASK xxx` — merge stream into staging

This eliminates idle polling costs and gives full control over when data is processed.

### Data Determinism

Seed data uses `random.seed(42)` — every run produces identical data. Useful for testing, debugging, and demo consistency.

---

## Verification Queries

Run these in Snowflake to validate the pipeline:

### 1. Alice's Plan History (2 versions if she changed plans)

```sql
SELECT customer_id, full_name, plan, dbt_valid_from, dbt_valid_to, is_current
FROM SUBSTRACK_DB.MARTS.DIM_CUSTOMER
WHERE customer_id = 'CUST_0001'
ORDER BY dbt_valid_from;
```

### 2. Pipeline Counts Across All Layers

```sql
SELECT 'RAW.CUSTOMERS' AS layer, COUNT(*) FROM SUBSTRACK_DB.RAW.CUSTOMERS
UNION ALL SELECT 'STAGING.CUSTOMERS', COUNT(*) FROM SUBSTRACK_DB.STAGING.CUSTOMERS
UNION ALL SELECT 'SNAPSHOTS.DIM_CUSTOMER_SNAPSHOT', COUNT(*) FROM SUBSTRACK_DB.SNAPSHOTS.DIM_CUSTOMER_SNAPSHOT
UNION ALL SELECT 'MARTS.DIM_CUSTOMER', COUNT(*) FROM SUBSTRACK_DB.MARTS.DIM_CUSTOMER
UNION ALL SELECT 'MARTS.FCT_PURCHASES', COUNT(*) FROM SUBSTRACK_DB.MARTS.FCT_PURCHASES
UNION ALL SELECT 'MARTS.FCT_BILLING_INVOICES', COUNT(*) FROM SUBSTRACK_DB.MARTS.FCT_BILLING_INVOICES
UNION ALL SELECT 'MARTS.FCT_USAGE_EVENTS', COUNT(*) FROM SUBSTRACK_DB.MARTS.FCT_USAGE_EVENTS
ORDER BY layer;
```

### 3. Temporal Join Proof

```sql
SELECT f.purchase_id, f.customer_name, f.purchase_date, f.amount,
       f.plan_at_purchase, c.plan AS current_plan,
       CASE WHEN f.plan_at_purchase != c.plan THEN 'DIFFERENT' ELSE 'SAME' END AS match_status
FROM SUBSTRACK_DB.MARTS.FCT_PURCHASES f
JOIN SUBSTRACK_DB.MARTS.DIM_CUSTOMER c
    ON f.customer_id = c.customer_id AND c.is_current = TRUE
WHERE f.plan_at_purchase != c.plan
ORDER BY f.purchase_date;
```

### 4. No Overlapping SCD2 Date Ranges

```sql
SELECT a.customer_id, a.dbt_valid_from, a.dbt_valid_to
FROM SUBSTRACK_DB.MARTS.DIM_CUSTOMER a
JOIN SUBSTRACK_DB.MARTS.DIM_CUSTOMER b
    ON a.customer_id = b.customer_id
    AND a.customer_sk != b.customer_sk
    AND a.dbt_valid_from < COALESCE(b.dbt_valid_to, '9999-12-31')
    AND b.dbt_valid_from < COALESCE(a.dbt_valid_to, '9999-12-31');
-- Expected: 0 rows
```

### 5. Subscription Status Breakdown

```sql
SELECT status, COUNT(*) as n
FROM SUBSTRACK_DB.MARTS.DIM_SUBSCRIPTION
WHERE is_current = TRUE
GROUP BY status;
```

### 6. Monthly Revenue

```sql
SELECT DATE_TRUNC('month', due_date) as month, SUM(collected_revenue) as revenue
FROM SUBSTRACK_DB.MARTS.FCT_BILLING_INVOICES
WHERE payment_status = 'paid'
GROUP BY month
ORDER BY month;
```

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit using conventional commits (`feat:`, `fix:`, `docs:`, etc.)
4. Push (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

*Built for learning. Designed for production. Scaled to 1,000+ customers.*
