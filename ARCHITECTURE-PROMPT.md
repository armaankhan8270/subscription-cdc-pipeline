# Enterprise Architecture Poster Prompt

Use with Midjourney / DALL-E / Gemini / Leonardo / Recraft to generate a production-scale architecture poster.

---

## Short Prompt

```
A professional enterprise architecture diagram titled "SubsTrack — CDC + SCD2 Data Pipeline" in a wide 16:9 format. Dark mode. Multi-layered architecture with 4 horizontal layers (like the medallion architecture pattern) running left to right across the full width.

LAYER 1 — SOURCE & INGESTION (top, full width):
Left: SQLite database icon with 3 tables inside (customers, purchases, audit_log). Center: CDC Python engine icon processing data through watermark.json with multiple parallel CSV outputs streaming rightward. Right: Snowflake internal stage "@RAW_STAGE" with separate folder paths for each table.

LAYER 2 — SNOWFLAKE RAW & PROCESSING (second from top):
Multiple Snowpipe pipes feeding data into RAW.CUSTOMERS and RAW.PURCHASES tables. Stream objects (delta icons) sitting on each RAW table detecting changes. Task objects actively merging data into STAGING.CUSTOMERS. Also show a STAGING.PURCHASES table. All connected with arrows showing data flow direction.

LAYER 3 — dbt TRANSFORMATIONS (third layer, full width):
A large dbt logo in center. Three processing stages within:
  - Left: Staging models (stg_customers.sql, stg_purchases.sql) with transformation rules visible.
  - Center (HIGHLIGHTED with amber glow): SCD2 Snapshot showing historical versioning — display a customer "Alice" with two rows: "Version 1: Basic (2024-01-01 to 2026-06-05)" and "Version 2: Premium (2026-06-05 to Present)". Show the SCD2 columns being added: dbt_scd_id, dbt_valid_from, dbt_valid_to.
  - Right: Mart models (dim_customer.sql, fct_purchases.sql) with temporal join logic highlighted: "purchase_date BETWEEN valid_from AND valid_to".

LAYER 4 — DASHBOARD & CONSUMPTION (bottom, full width):
FastAPI lightning bolt icon. Four distinct panel windows showing:
  - Pipeline Overview with metric cards and bar charts
  - Customer Detail with timeline view of plan changes
  - Purchase Analysis with DIFFERENT (red) and SAME (green) badges highlighting the temporal join accuracy
  - Distribution Analytics with pie charts and version count tables

SIDE PANELS (vertical strips on both edges):
Left side: Key metrics column showing pipeline stats (Total Versions, Data Freshness, Records Processed)
Right side: Color legend and technology badges (Python, Snowflake, dbt, FastAPI, Git, GitHub)

BOTTOM STRIP: Full width git commit history line showing evolution: Project Setup → Source Database → CDC Pipeline → Snowflake Infra → dbt Models → Dashboard → Documentation

COLOR SCHEME:
- Background: Deep dark navy (#0a0e27)
- Layer backgrounds: Semi-transparent dark panels (#131a3a with 85% opacity)
- Layer 1 (Ingestion): Blue tones (#1565c0)
- Layer 2 (Processing): Purple tones (#6a1b9a)
- Layer 3 (Transformation): Orange tones (#ef6c00) with amber SCD2 glow (#ffb300)
- Layer 4 (Presentation): Green tones (#2e7d32)
- Connectors and arrows: Glowing cyan (#00d4ff) with arrowheads
- Highlight badges: Red (#ff1744) for DIFFERENT, Green (#00e676) for SAME
- Text: White primary (#ffffff), Gray secondary (#90a4ae)

STYLE: Enterprise data architecture diagram style comparable to Snowflake Summit keynotes or dbt Coalesce conference presentations. Large clear components, generous spacing, professional layout. Icons should be clean outlined professional style (not cartoon). Table icons should show actual row data with readable column names. Connections should be clean lines with directional arrows. Include a subtle grid background pattern. 4K quality, 16:9 aspect ratio, 300 DPI. No watermarks or branding overlays.
```

---

## Detailed Enterprise Prompt

```
Create a large-scale enterprise architecture diagram for "SubsTrack — CDC + SCD2 Pipeline" in a professional 4-layer medallion architecture layout. Size: 16:9, 3840×2160 (4K), dark theme.

=== OVERALL STRUCTURE ===

The image is divided into 4 horizontal layers stacked vertically, each spanning the full width. Left and right edges have vertical sidebar panels. Bottom has a git history strip. The background is deep navy (#0a0e27) with a faint grid overlay.

=== LAYER 1 — SOURCE & INGESTION (top layer, y=0 to y=480) ===
Background panel: semi-transparent dark blue box (#131a3a, 85% opacity) with blue border (#1565c0, 1px)

SECTION 1.1 — SQLite Source (left, x=60, width=400):
- Large database cylinder icon (blue #1565c0), 80px tall
- Label: "SOURCE DATABASE" in uppercase, 11px tracking
- Title: "SQLite — Production DB" in bold 20px
- Inside database: three table icons showing:
  - "customers": customer_id, full_name, plan, plan_price, status, signup_date, updated_at (yellow highlight on updated_at column)
  - "purchases": purchase_id, customer_id, product_name, amount, purchase_date, created_at
  - "audit_log": log_id, table_name, record_id, old_value, new_value, changed_at
- Bottom: "python seed_data.py + simulate_changes.py" in gray 10px
- Arrow exiting right: thick arrow labeled "CDC Extraction Trigger"

SECTION 1.2 — CDC Engine (center, x=520, width=500):
- Python logo icon (60px) with gear icon next to it
- Label: "CHANGE DATA CAPTURE" uppercase
- Title: "CDC Extraction Engine" bold 20px
- Center element: "watermark.json" file card showing:
  {
    "customers": "2026-06-05 14:00:00",
    "purchases": "2026-06-05 14:00:00"
  }
- Flow diagram inside: Watermark → SQLite Query ("SELECT * WHERE updated_at > watermark") → CSV Writer
- Three CSV file icons with timestamps:
  - customers_20260605_140000.csv (size 2.4KB)
  - purchases_20260605_140000.csv (size 1.1KB)
  - audit_log_20260605_140000.csv (size 0.8KB)
- Small green check: "At-least-once semantics — watermark saved AFTER success"
- Arrow exiting right: thick arrow labeled "PUT files to Snowflake Stage"

SECTION 1.3 — Snowflake Staging (right, x=1080, width=500):
- Snowflake logo (60px) with folder icon
- Label: "LANDING ZONE" uppercase
- Title: "@RAW_STAGE — Internal Stage" bold 20px
- Three folder paths in monospace:
  - @RAW_STAGE/customers/
  - @RAW_STAGE/purchases/
  - @RAW_STAGE/audit_log/
- Each folder has a CSV file icon inside
- Note card: "Internal stage — no auto-ingest available. Uses manual ALTER PIPE REFRESH"
- Arrow exiting down (to Layer 2): "ALTER PIPE REFRESH (manual trigger)"

=== LAYER 2 — SNOWFLAKE RAW & PROCESSING (y=520 to y=1000) ===
Background panel: semi-transparent dark purple box (#1a1040, 85% opacity) with purple border (#6a1b9a, 1px)

SECTION 2.1 — Snowpipe Loading (left, x=60, width=500):
- Three Snowpipe icons (pipe shape with gear) stacked vertically:
  - "CUSTOMERS_PIPE" — copies CSV → RAW.CUSTOMERS
  - "PURCHASES_PIPE" — copies CSV → RAW.PURCHASES
  - "AUDIT_LOG_PIPE" — copies CSV → RAW.AUDIT_LOG
- Each pipe shows arrow: Stage File → Snowpipe (auto COPY) → RAW Table
- Note on each: "APPEND-ONLY — preserves full history"
- Data flows rightward to Streams

SECTION 2.2 — Streams (center, x=620, width=400):
- Three delta icons (Δ) stacked vertically:
  - "CUSTOMERS_STREAM" — on RAW.CUSTOMERS, APPEND_ONLY = TRUE
  - "PURCHASES_STREAM" — on RAW.PURCHASES, APPEND_ONLY = TRUE  
  - "AUDIT_LOG_STREAM" — on RAW.AUDIT_LOG, APPEND_ONLY = TRUE
- Each stream shows mini table rows of captured changes:
  - Stream shows: CUST_001 (UPSERT), CUST_002 (UPSERT) — with METADATA$ACTION, METADATA$ISUPDATE columns
- Arrow from streams → Tasks: "Stream has data → triggers WHEN condition"

SECTION 2.3 — Tasks & Staging (right, x=1080, width=500):
- Two large gear/task icons:
  - "PROCESS_CUSTOMERS_TASK" — MERGE INTO STAGING.CUSTOMERS
  - "PROCESS_PURCHASES_TASK" — MERGE INTO STAGING.PURCHASES
- SQL snippet shown on customers task:
  MERGE INTO STAGING.CUSTOMERS
  USING CUSTOMERS_STREAM
  ON customer_id = customer_id
  WHEN MATCHED THEN UPDATE SET plan = source.plan, ...
  WHEN NOT MATCHED THEN INSERT ...
- YELLOW HIGHLIGHT BOX: "NO SCHEDULE — EXECUTE TASK runs manually after Snowpipe"
- Result tables shown:
  - "STAGING.CUSTOMERS: 6 rows (1 per customer — current state only)"
  - "STAGING.PURCHASES: 5 rows (1 per purchase)"
- Arrow exiting down (to Layer 3): "dbt transforms staging data"

=== LAYER 3 — dbt TRANSFORMATIONS (y=1040 to y=1600) ===
Background panel: semi-transparent dark orange box (#1a0e00, 85% opacity) with orange border (#ef6c00, 1px) — LARGEST LAYER, most emphasis

SECTION 3.0 — dbt Header (full width top of layer):
- Large dbt logo (orange cube, 100px) centered
- Title: "dbt — Data Build Tool" bold 28px white
- Subtitle: "Transformations | SCD2 Snapshots | Business Marts"
- Label: "16 data tests: unique, not_null, accepted_values, relationships — ALL PASSING ✓"

SECTION 3.1 — Staging Models (left, x=60, width=450):
- Card titled "STAGING MODELS (Silver Layer)"
- Two SQL file icons:
  - "stg_customers.sql" with transformations visible:
    - LOWER(email), TRIM(full_name)
    - plan_rank: CASE plan WHEN 'free' THEN 0 WHEN 'basic' THEN 1 WHEN 'premium' THEN 2 WHEN 'enterprise' THEN 3
    - days_since_signup: DATEDIFF(day, signup_date, CURRENT_DATE)
    - WHERE _is_deleted = FALSE
  - "stg_purchases.sql" with transformations visible:
    - TRIM(product_name)
    - purchase_month: DATE_TRUNC(month, purchase_date)
    - purchase_year: YEAR(purchase_date)
- Small badge: "Source: STAGING schema → Output: View"
- Arrow right: "Clean data flows to snapshot"

SECTION 3.2 — SCD2 Snapshot (center, x=570, width=700) — AMBER GLOW HIGHLIGHT
- **MOST PROMINENT SECTION** — golden/amber glow border (#ffb300), slightly larger
- Card titled "★ SCD2 SNAPSHOT — Slowly Changing Dimension Type 2"
- File icon: "dim_customer_snapshot.sql"
- Configuration visible:
  strategy: timestamp
  unique_key: customer_id  
  updated_at: updated_at
  invalidate_hard_deletes: True
- CENTERPIECE — Alice's data shown as TWO DISTINCT PHYSICAL ROWS in a table:

  ┌─────────────┬──────────┬────────┬──────────────────────┬──────────────────────┬──────────┐
  │ dbt_scd_id  │ full_name│ plan   │ dbt_valid_from       │ dbt_valid_to         │ is_current │
  ├─────────────┼──────────┼────────┼──────────────────────┼──────────────────────┼──────────┤
  │ abc123def   │ Alice    │ Basic  │ 2024-01-01 00:00:00  │ 2026-06-05 14:00:00  │ FALSE    │
  │ ghi456jkl   │ Alice    │ Premium│ 2026-06-05 14:00:00  │ NULL                 │ TRUE     │
  └─────────────┴──────────┴────────┴──────────────────────┴──────────────────────┴──────────┘

- Visual callout boxes pointing to the columns:
  - "dbt_scd_id: Surrogate key (hash of customer_id + valid_from)"
  - "dbt_valid_from: When this version became active"
  - "dbt_valid_to: NULL = current version"
- Additional row examples below for Bob (Premium→Basic, 2 versions), Dave (Free→Basic, 2 versions), Carol (Enterprise, 1 version cancelled)
- Total count: "10 SCD2 versions across 6 customers"
- Arrow right: "SCD2 versions feed mart models"

SECTION 3.3 — Mart Models (right, x=1330, width=450):
- Card titled "MART MODELS (Gold Layer)"
- Two table icons:

  "dim_customer.sql" — Materialized as TABLE
  - Columns: customer_sk, customer_id, full_name, plan, plan_tier (Growth/Starter/Enterprise), is_current, days_on_plan, estimated_revenue_this_period
  - "Enriched, business-ready dimension"

  "fct_purchases.sql" — Materialized as TABLE (HIGHLIGHTED)
  - **THE TEMPORAL JOIN** — shown with yellow highlight:
    SELECT p.purchase_id, p.amount, p.purchase_date,
           c.plan AS plan_at_purchase,
           c2.plan AS current_plan
    FROM stg_purchases p
    LEFT JOIN dim_customer c
      ON p.customer_id = c.customer_id
      AND p.purchase_date >= c.valid_from::DATE
      AND p.purchase_date < COALESCE(c.valid_to::DATE, '9999-12-31')
    LEFT JOIN dim_customer c2
      ON p.customer_id = c2.customer_id AND c2.is_current = TRUE

  - Result preview table (CRITICAL — shows the proof):
    PUR_001 | Alice | 2024-02-15 | $29 | Basic | Premium | ← DIFFERENT
    PUR_002 | Bob   | 2024-02-20 | $79 | Premium | Basic  | ← DIFFERENT
    PUR_005 | Carol | 2024-03-10 | $79 | Enterprise | Enterprise | ← SAME

- Arrow exiting down (to Layer 4): "FastAPI queries Gold layer"

=== LAYER 4 — DASHBOARD & CONSUMPTION (y=1640 to y=1950) ===
Background panel: semi-transparent dark green box (#0a1a0a, 85% opacity) with green border (#2e7d32, 1px)

SECTION 4.0 — Dashboard Header (full width):
- FastAPI lightning bolt logo (60px) + "DASHBOARD — Real-Time Visualization" title 22px

SECTION 4.1 — Four Dashboard Panels (evenly spaced across width):

Panel A — "Pipeline Overview" (x=60, width=400):
- URL bar: "GET /" with status 200 OK
- Four metric cards in 2x2 grid:
  - [RAW Records: 8] [Staging Customers: 6]
  - [SCD2 Versions: 10] [Total Purchases: 5]
- Small bar chart: "Plan Distribution" (3 bars: Free 1, Basic 2, Premium 2, Enterprise 1)

Panel B — "Customer History" (x=520, width=400):
- Dropdown: "Alice ▼"
- Horizontal timeline bar showing:
  [████████ Basic ████████] → [████████ Premium ████████]
  2024-01-01                   2026-06-05               Present
- Label: "2 versions • 5 months on Basic • 0 months on Premium"
- Below: small table of all 6 customers with version count

Panel C — "Purchase Analysis" (x=980, width=400) — HIGHLIGHTED:
- Table with columns: Purchase ID, Customer, Date, Amount, Plan When Bought, Current Plan, Match?
- Rows shown:
  PUR_001 | Alice | Feb 15 | $29 | Basic | Premium | 🔴 DIFFERENT
  PUR_002 | Bob | Feb 20 | $79 | Premium | Basic | 🔴 DIFFERENT
  PUR_003 | Alice | May 01 | $29 | Basic | Premium | 🔴 DIFFERENT
  PUR_004 | Dave | Apr 05 | $0 | Free | Basic | 🔴 DIFFERENT
  PUR_005 | Carol | Mar 10 | $79 | Enterprise | Enterprise | 🟢 SAME
- Small dual chart below: Revenue by Plan (bar), Purchase Count by Plan (pie)

Panel D — "Distribution" (x=1440, width=400):
- Large pie chart: current plan distribution with percentages
- Small table: "SCD2 Versions Per Customer"
  Alice: 2 | Bob: 2 | Carol: 1 | Dave: 2 | Eve: 1 | Frank: 2
- Note: "6 customers • 10 total versions • avg 1.67 per customer"

=== LEFT SIDEBAR (vertical strip, x=0 to x=40, full height) ===
Narrow strip with:
- Top: "PIPELINE HEALTH" — 3 green dots (healthy)
- Middle: Key metrics rotating:
  - "Data Freshness: 2 min ago"
  - "Total Records: 29"
  - "SCD2 Accuracy: 100%"
  - "Tests Passing: 16/16"
- Bottom: "Last Pipeline Run: 2026-06-05 14:02"

=== RIGHT SIDEBAR (vertical strip, x=1880 to x=1920, full height) ===
Narrow strip with:
- Technology stack badges stacked vertically:
  - Python 3.12 (blue badge)
  - SQLite 3 (light blue badge)
  - Snowflake (blue-white badge)
  - dbt 1.8.5 (orange badge)
  - FastAPI (green badge)
  - Jinja2 (gray badge)
  - Plotly (cyan badge)
  - Git (red badge)

=== BOTTOM STRIP (y=1960 to y=2040, full width) ===
Dark strip (#050814) with:
- Left: GitHub logo + "github.com/armaankhan8270/subscription-cdc-pipeline"
- Center: Git commit history line — 7 nodes connected by horizontal line:
  [Project Setup] → [Source DB] → [CDC Extract] → [Snowflake Infra] → [dbt Models] → [Dashboard] → [Documentation]
- Right: "Conventional Commits • 7 commits • main branch"
- Small text far right: "Built for learning. Designed for production."

=== COLOR PALETTE REFERENCE ===
Background main:    #0a0e27
Panel backgrounds:  #131a3a (85% opacity with colored borders)
Grid lines:         #1a1f3a (5% opacity)
Layer 1 border:     #1565c0 (blue)
Layer 2 border:     #6a1b9a (purple)
Layer 3 border:     #ef6c00 (orange)
Layer 4 border:     #2e7d32 (green)
SCD2 glow:          #ffb300 (amber) with golden border glow
Arrows:             #00d4ff (cyan, 3px, with drop shadow glow)
DIFFERENT badge:    #ff1744 (red, bold)
SAME badge:         #00e676 (green, bold)
Text primary:       #ffffff (white)
Text secondary:     #90a4ae (gray)
Code font color:    #80cbc4 (teal monospace)
Highlight box bg:   rgba(255, 179, 0, 0.12) (amber transparent)

=== STYLE INSTRUCTIONS ===
1. PROFESSIONAL ENTERPRISE GRADE — This must look like it belongs in a Snowflake Summit keynote or dbt Coalesce presentation. Clean, modern, premium.
2. GENEROUS SPACING — Do not crowd elements. Each layer has breathing room. Components should be large and readable.
3. ICON STYLE — Outlined geometric icons (like Carbon Design System or Material Design outlined icons). NOT flat, NOT cartoon, NOT filled. Clean 2px stroke.
4. FONTS — Use Inter for all labels/titles (sans-serif). Use JetBrains Mono or Fira Code for code/table content (monospace). Font sizes should be clearly readable.
5. CONNECTORS AND ARROWS — All arrows should be smooth bezier curves (not rigid 90-degree angles) with visible arrowheads. Cyan (#00d4ff) with a subtle outer glow.
6. THE SCD2 SECTION (Layer 3, Center) MUST BE THE VISUAL FOCUS — It should have a golden glow effect that draws the eye first. This is the most important part of the entire architecture.
7. THE TEMPORAL JOIN RESULT (Layer 3, Right) IS THE SECOND FOCUS — The DIFFERENT/SAME comparison proves the pipeline works. It should be clearly visible and readable.
8. THE DIFFERENT BADGES IN THE DASHBOARD should be highly visible — Red badges on dark green panel = high contrast.
9. DEPTH — Add subtle shadowing to panels and cards. Each layer should feel like it floats slightly above the background.
10. NO CLUTTER — Every element must serve a purpose. If it doesn't add understanding, remove it.
11. OUTPUT: 4K resolution (3840×2160), 300 DPI, PNG format without watermarks or branding overlays.
```

---

## Midjourney Version

```
/imagine prompt: Enterprise architecture diagram "SubsTrack CDC SCD2 Pipeline" in 4 horizontal layers full width, dark navy background #0a0e27, professional data engineering style, large and scalable layout. Layer 1 (blue): SQLite database feeding CDC Python engine with watermark.json, output CSV files uploading to Snowflake internal stage @RAW_STAGE. Layer 2 (purple): Snowpipe pipes loading RAW tables, delta stream icons capturing changes, task gear icons merging into staging tables, yellow highlight "NO SCHEDULE manual trigger". Layer 3 (orange, LARGEST with AMBER GLOW): dbt logo center with three sections — left staging models with transformations, center SCD2 snapshot showing Alice two rows "Basic 2024-01 to 2026-06" and "Premium 2026-06 to NULL" with amber golden glow effect as visual focus, right mart models with temporal join SQL "purchase_date BETWEEN valid_from AND valid_to" showing DIFFERENT and SAME results. Layer 4 (green): FastAPI dashboard with 4 panels — overview metric cards, customer timeline, purchase analysis table with red DIFFERENT badges and green SAME badges, distribution pie chart. Left sidebar pipeline health metrics, right sidebar technology stack badges. Bottom strip git commit history. Glowing cyan arrows connecting all components. Enterprise keynote presentation quality, 4K, 16:9, generous spacing, outlined geometric icons, monospace code font, sans-serif labels, no clutter --ar 16:9 --style raw --v 6
```

---

## TL;DR — Key changes from the old version

| Before (small) | Now (scalable) |
|---|---|
| 7 small boxes in a row | 4 massive horizontal layers |
| Tiny columns, cramped | Large components, generous spacing |
| Just SQLite → Snowflake → dbt → Dashboard | Full medallion architecture with audit support |
| No sidebars | Pipeline health + tech stack badges |
| 1920×1080 | 3840×2160 (4K) |
| Simple arrows | Smooth bezier curves with glow |
| SCD2 section normal | SCD2 section gets AMBER GLOW focus |
| Dashboard small | 4 full panels with mock data visible |
