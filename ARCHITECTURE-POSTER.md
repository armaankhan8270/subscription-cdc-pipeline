# Architecture Poster Prompt (1000+ Customer Scale)

Use with Midjourney / DALL-E / Gemini / Leonardo to generate a professional enterprise-grade architecture poster.

---

## Short Prompt

```
Enterprise architecture diagram "SubsTrack — CDC + SCD2 SaaS Pipeline" in 4 horizontal medallion layers. Dark navy background (#0a0e27). 1000+ customer scale.

LAYER 1 (blue): SOURCE & INGESTION — SQLite database with 7 tables: customers (1000 rows), purchases (2000), subscriptions (1100), billing_invoices (6000), payment_methods (1060), usage_events (4000), support_tickets (2000). CDC engine with watermark.json extracting changes into timestamped CSVs. Upload arrow labeled "PUT file://... @RAW_STAGE" into Snowflake internal stage.

LAYER 2 (purple): SNOWFLAKE PROCESSING — 7 Snowpipe pipes loading CSV into RAW tables. 7 Streams (delta icons) on each RAW table. 7 Tasks (gear icons) merging data into STAGING tables. Yellow highlight: "NO SCHEDULE — EXECUTE TASK manual only". STAGING holds current state (1 row per customer, 1 per purchase, etc.).

LAYER 3 (orange, AMBER GLOW focus): dbt TRANSFORMATIONS — Large dbt logo. Three sections:
- Left: 7 staging models cleaning and enriching data
- Center (GLOWING): 4 SCD2 snapshots — customers (2+ versions for 8%), subscriptions (plan changes tracked), payment_methods (card updates), support_tickets (status history). Show Alice example with 2 rows: Basic (2024→2026) → Premium (2026→present). dbt_scd_id, dbt_valid_from, dbt_valid_to columns highlighted.
- Right: Mart models — dim_customer, dim_subscription, fct_purchases with temporal join "purchase_date BETWEEN valid_from AND valid_to". DIFFERENT/SAME badges proving historical accuracy.

LAYER 4 (green): DASHBOARD — FastAPI with 6 pages:
- Overview (8 metric cards + plan bar chart)
- Customers (dropdown + SCD2 timeline)
- Purchases (DIFFERENT red / SAME green badges)
- Subscriptions (active vs cancelled, plan breakdown)
- Billing (monthly revenue chart, invoice status)
- Usage (usage category pie, per-customer grouped bars)

Left sidebar: Pipeline health (Data Freshness, Total Records: 16000+, Tests: 25+ passing). Right sidebar: Tech stack badges (Python, SQLite, Snowflake, dbt 1.8.5, FastAPI, Plotly). Bottom strip: Git commit history with 8 nodes. 4K, 16:9, professional keynote quality. Glowing cyan arrows connecting layers.
```

---

## Detailed Prompt

```
Create a 4K (3840×2160) enterprise architecture poster titled "SubsTrack — CDC + SCD2 SaaS Pipeline" in 4 horizontal medallion layers. Dark navy background (#0a0e27) with subtle grid. Each layer is a large card with semi-transparent background and colored border.

=== LAYER 1 — SOURCE & INGESTION (Blue #1565c0) ===

SECTION: SQLite Source (left)
- Large database cylinder icon
- 7 table icons inside, each with row count:
  - customers: 1,000 rows
  - purchases: ~2,000 rows
  - subscriptions: ~1,100 rows
  - billing_invoices: ~6,000 rows
  - payment_methods: ~1,060 rows
  - usage_events: ~4,000 rows
  - support_tickets: ~2,000 rows
- "updated_at" column highlighted yellow on customers table (CDC cursor)

SECTION: CDC Engine (center)
- Python icon + watermark.json file
- Flow: watermark → SQL query → CSV output
- Multiple timestamped CSV files coming out
- Note: "At-least-once semantics"

SECTION: Snowflake Stage (right)
- Cloud folder icon @RAW_STAGE
- 7 folder paths: /customers/, /purchases/, /subscriptions/, etc.
- Arrow to Layer 2: "ALTER PIPE REFRESH (manual trigger)"

=== LAYER 2 — SNOWFLAKE PROCESSING (Purple #6a1b9a) ===

SECTION: Snowpipes (left)
- 7 pipe icons stacked, each with table name
- Arrow: CSV → RAW table (append-only)

SECTION: Streams (center)
- 7 delta icons (Δ)
- Each on a RAW table: APPEND_ONLY = TRUE
- Arrow: "Stream has data →"

SECTION: Tasks (right)
- 7 gear icons
- SQL: "MERGE INTO STAGING.xxx USING STREAM"
- YELLOW BOX: "NO SCHEDULE — manual EXECUTE TASK"
- Result: STAGING tables with current state

=== LAYER 3 — dbt TRANSFORMATIONS (Orange #ef6c00, LARGEST) ===
This layer is 1.5x the height of others. AMBER GLOW (#ffb300) on center section.

HEADER: dbt logo + "16 staging models + 4 SCD2 snapshots + 6 mart models • 25+ tests passing"

LEFT — Staging Models (7 files):
- stg_customers.sql: plan_rank, days_since_signup
- stg_purchases.sql: purchase_month, purchase_year
- stg_subscriptions.sql: plan_rank, is_active
- stg_billing_invoices.sql: is_paid, days_to_pay
- stg_payment_methods.sql: is_valid, expiration_date
- stg_usage_events.sql: event_category, event_date
- stg_support_tickets.sql: priority_rank, ticket_age_days

CENTER — SCD2 Snapshots (AMBER GLOW, visual focus):
- 4 snapshot configs: customers, subscriptions, payment_methods, support_tickets
- Strategy: timestamp on updated_at
- CENTERPIECE: Alice's customer data as 2 rows:
  Row 1: Basic | dbt_valid_from: 2024-01-01 | dbt_valid_to: 2026-06-05
  Row 2: Premium | dbt_valid_from: 2026-06-05 | dbt_valid_to: NULL (CURRENT)
- Highlighted columns: dbt_scd_id (surrogate key), dbt_valid_from, dbt_valid_to
- Note: "SCD2 preserves every version — 8% of customers have plan changes"

RIGHT — Mart Models:
- dim_customer: plan_tier, is_current, days_on_plan, estimated_revenue
- dim_subscription: plan_tier, total_subscription_days
- fct_purchases (HIGHLIGHTED): temporal join — "purchase_date BETWEEN valid_from AND valid_to"
- Example result: Alice Feb purchase → Basic (NOT Premium!) — DIFFERENT badge
- fct_billing_invoices: collected_revenue, outstanding_revenue
- fct_usage_events: joined with customer dimension
- dim_support_ticket: SCD2 tracked status changes

=== LAYER 4 — DASHBOARD (Green #2e7d32) ===

FastAPI logo + "6 Pages • Live Snowflake Queries"

6 panels in a 3x2 grid:
1. Overview: 8 metric cards (all 7 tables + SCD2 versions) + plan bar chart
2. Customers: dropdown selector + SCD2 timeline chart per customer
3. Purchases: Table with 🔴 DIFFERENT / 🟢 SAME badges + revenue charts
4. Subscriptions: Active vs cancelled pie chart + plan breakdown bar chart
5. Billing: Monthly revenue bar chart + invoice status pie chart
6. Usage: Usage category pie + per-customer grouped bar chart

SIDEBARS:
Left: Pipeline health — "Total Records: ~16,000+ • Tests: 25+ Passing • Freshness: Live"
Right: Tech badges — Python 3.12, SQLite, Snowflake, dbt 1.8.5, FastAPI, Plotly, Jinja2, Git

BOTTOM: Git history — 8 commit nodes connected by line
"scaffold → source → cdc → snowflake → dbt → dashboard → scale → docs"
GitHub URL: github.com/armaankhan8270/subscription-cdc-pipeline

STYLE: Professional keynote/enterprise presentation. Inter font. Smooth cyan bezier arrows. Geometric outlined icons. Generous whitespace. 4K, 16:9, 300 DPI. No watermarks.
```

---

## Midjourney Version

```
/imagine prompt: Enterprise architecture poster "SubsTrack CDC SCD2 SaaS Pipeline" in 4 horizontal medallion layers, full width, dark navy background #0a0e27, 4K quality. Layer 1 blue: SQLite database with 7 tables labeled with row counts (1000 customers, 2000 purchases, etc), CDC Python engine with watermark.json, CSV upload to Snowflake stage @RAW_STAGE. Layer 2 purple: 7 Snowpipe icons, 7 stream delta icons, 7 task gear icons, yellow highlight "NO SCHEDULE manual only". Layer 3 orange LARGEST with AMBER GLOW center: dbt logo, 4 SCD2 snapshots showing Alice 2-row example (Basic→Premium with dbt_valid_from/to dates), temporal join SQL highlighted, DIFFERENT/SAME badges visible. Layer 4 green: FastAPI dashboard with 6 panels (Overview, Customers, Purchases, Subscriptions, Billing, Usage), metric cards showing ~16K total records. Left sidebar pipeline health, right sidebar tech stack badges. Bottom strip git history 8 commits. Glowing cyan arrows. Professional keynote quality, generous spacing, geometric icons, monospace code fonts --ar 16:9 --style raw --v 6
```
