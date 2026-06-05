# Architecture Poster Prompt

Generate a clean horizontal infographic/poster (wide 16:9, 1920×1080) showing the **SubsTrack** pipeline as a step-by-step flow from left to right. Each step is a connected box with arrows. Style: dark mode, minimal, glowing connections, modern data engineering aesthetic.

---

## The Layout — 7 Connected Boxes in Sequence

```
[1. SQLite] → [2. CDC Extract] → [3. Snowflake Stage] → [4. Snowpipe] → [5. Stream + Task] → [6. dbt] → [7. Dashboard]
                                                                                                ↓
                                                                                          SCD2 Snapshots
```

Each box should show what happens INSIDE it. Below is the detail for each.

---

## Box 1 — SQLite (Source Database)
- **Position**: Far left
- **Label**: "SQLite — Source Database"
- **Color**: Blue (#1565c0)
- **Inside the box show two tables**:
  - `customers` table icon with 3 highlighted rows:
    - Alice | premium | updated_at: 2026-06-05  (highlight this column in yellow — this is the CDC cursor)
    - Bob | basic | updated_at: 2026-06-05
    - Carol | cancelled | updated_at: 2026-06-01
  - `purchases` table icon with 3 rows:
    - PUR_001 | Alice | Feb | $29
    - PUR_002 | Bob | Feb | $79
    - PUR_003 | Alice | May | $29
- **At bottom of box**: small "python seed_data.py + simulate_changes.py" text
- **Right side arrow**: labeled "CDC Extraction (watermark)"

---

## Box 2 — CDC Extract (Python Script)
- **Position**: Second from left, connected by arrow from Box 1
- **Label**: "CDC Extraction — watermark.json"
- **Color**: Teal (#00897b)
- **Inside show**:
  - A file icon "watermark.json" with content: `{ "customers": "2026-06-05 14:00:00" }`
  - Arrow from watermark → SQL table: "SELECT * WHERE updated_at > watermark"
  - Result: CSV files "customers_20260605_140000.csv", "purchases_20260605_140000.csv"
  - Small checkmark: "at-least-once semantics"
- **Right side arrow**: labeled "Upload to Snowflake Stage"

---

## Box 3 — Snowflake Internal Stage
- **Position**: Middle, connected by arrow from Box 2
- **Label**: "@RAW_STAGE — Landing Zone"
- **Color**: Snowflake blue (#00aae1)
- **Inside show**:
  - A cloud folder icon
  - Two file paths: `@RAW_STAGE/customers/customers_20260605.csv`
  - Small note: "Staging area — files not yet loaded"
- **Right side arrow**: labeled "ALTER PIPE REFRESH (manual trigger)"

---

## Box 4 — Snowpipe (Serverless Load)
- **Position**: Middle-right, connected by arrow from Box 3
- **Label**: "Snowpipe — COPY INTO RAW"
- **Color**: Snowflake blue (#00aae1)
- **Inside show**:
  - A pipe icon with gear symbol
  - Arrow showing: CSV on stage → RAW.CUSTOMERS table (append-only)
  - Table icon "RAW.CUSTOMERS" showing 6 rows stacked (all historical records)
  - Note: "AUTO_INGEST = FALSE (manual trigger)"
- **Right side arrow**: labeled "Stream captures changes"

---

## Box 5 — Stream + Task (Processing)
- **Position**: Center-right, connected by arrow from Box 4
- **Label**: "Stream + Task — MERGE to Staging"
- **Color**: Purple (#6a1b9a)
- **Inside show TWO sub-boxes**:

  **Sub-box A — Stream**:
  - Icon: delta symbol (Δ)
  - Name: "CUSTOMERS_STREAM"
  - Shows 3 change rows: CUST_001 (UPSERT), CUST_002 (UPSERT), CUST_003 (UPSERT)
  
  **Sub-box B — Task**:
  - Icon: clock/schedule gear
  - Name: "PROCESS_CUSTOMERS_TASK"
  - SQL inside: `MERGE INTO STAGING.CUSTOMERS USING STREAM`
  - Highlight: **"NO SCHEDULE — run via EXECUTE TASK"** in yellow
  - Result table: "STAGING.CUSTOMERS" with current state (6 rows, each customer only once)
  
  Arrow connecting: Stream → Task → Staging table
- **Right side arrow**: labeled "dbt reads from Staging"

---

## Box 6 — dbt (Transformation)
- **Position**: Second from right, connected by arrow from Box 5
- **Label**: "dbt — Clean → Snapshot → Mart"
- **Color**: Orange (#ef6c00)
- **Inside show THREE sub-boxes stacked vertically**:

  **Sub-box A — Staging Models** (top):
  - stg_customers.sql: adds plan_rank, days_since_signup
  - stg_purchases.sql: adds purchase_month/year
  - Checkmark: "16 data tests passing"

  **Sub-box B — SCD2 Snapshot** (middle, highlighted with glow):
  - dim_customer_snapshot.sql
  - Strategy: timestamp on updated_at
  - Show Alice's data as two version rows:
    - Version 1: Basic | 2024-01-01 → 2026-06-05
    - Version 2: Premium | 2026-06-05 → NULL (current)
  - Note: "dbt adds: dbt_scd_id, dbt_valid_from, dbt_valid_to"

  **Sub-box C — Mart Models** (bottom):
  - dim_customer.sql: plan_tier, is_current, days_on_plan, estimated_revenue
  - fct_purchases.sql: **THE KEY LINE** — "purchase_date BETWEEN valid_from AND valid_to"
  - Show the temporal join result for Alice:
    - Feb purchase → plan_at_purchase = Basic (NOT Premium!)
    - Highlight: "DIFFERENT — Historical truth vs current state"

- **Right side arrow**: labeled "Snowflake queries"

---

## Box 7 — FastAPI Dashboard
- **Position**: Far right, connected by arrow from Box 6
- **Label**: "FastAPI Dashboard — 4 Pages"
- **Color**: Green (#2e7d32)
- **Inside show 4 small rectangles in a 2×2 grid**:

  **Overview**:
  - 4 count boxes: RAW=8, STAGING=6, SCD2=10, PURCHASES=5
  - Small bar chart: plan distribution

  **Customers**:
  - Dropdown showing "Alice"
  - Timeline bar: Basic (blue bar) → Premium (green bar)
  - Label: "2 versions"

  **Purchases** (highlight with glow):
  - Table with rows showing DIFFERENT/SAME badges
  - Alice: Feb $29 → Basic (DIFFERENT) in red
  - Alice: May $29 → Basic (DIFFERENT) in red
  - Carol: Mar $79 → Enterprise (SAME) in green
  - Small chart: revenue by plan

  **Distribution**:
  - Pie chart: plan % breakdown
  - Small table: versions per customer

- **Right edge**: URL "http://127.0.0.1:8000" with "Live Snowflake queries"

---

## Bottom Strip — Git & Deployment
- Full width strip below the 7 boxes
- Shows the 6 git commits as small nodes connected by a line:
  `feat: scaffold → feat: source → feat: cdc → feat: snowflake → feat: dbt → feat: dashboard → docs: readme`
- Small badge: "Conventional Commits"
- GitHub URL: "github.com/armaankhan8270/subscription-cdc-pipeline"

---

## Connection Arrows Between Boxes

Each arrow should have:
1. The arrow line (glowing cyan, #00d4ff, with slight glow effect)
2. A small label on top describing the action
3. Optional: an icon in the middle of the arrow

| From | To | Arrow Label | Icon |
|---|---|---|---|
| Box 1 → Box 2 | "python cdc_extract.py" | Python (🐍) |
| Box 2 → Box 3 | "PUT file to stage" | Upload (↑) |
| Box 3 → Box 4 | "ALTER PIPE REFRESH" | Play (▶) |
| Box 4 → Box 5 | "Stream captures delta" | Delta (Δ) |
| Box 5 → Box 6 | "dbt snapshot + run" | dbt logo |
| Box 6 → Box 7 | "FastAPI queries" | Database (🗄) |

---

## Color Palette

| Element | Hex | Usage |
|---|---|---|
| Background | #0a0e27 | Main dark background |
| Grid lines | #1a1f3a | Subtle grid |
| Box 1 (SQLite) | #1565c0 | Dark blue |
| Box 2 (CDC) | #00897b | Teal |
| Box 3 (Stage) | #0277bd | Medium blue |
| Box 4 (Snowpipe) | #0288d1 | Light blue |
| Box 5 (Stream+Task) | #6a1b9a | Purple |
| Box 6 (dbt) | #ef6c00 | Orange |
| Box 7 (Dashboard) | #2e7d32 | Green |
| Arrows | #00d4ff | Glowing cyan |
| Highlight | #ffb300 | Amber/gold |
| Error/DIFFERENT | #ff1744 | Red |
| Success/SAME | #00e676 | Green |
| Text primary | #ffffff | White |
| Text secondary | #b0bec5 | Light gray |

---

## Styling Notes
- Each box: rounded corners (8px), semi-transparent background, subtle border glow matching its color
- Arrow lines: 2px thick, #00d4ff with 1px glow
- Font: monospace for code/table names, sans-serif for labels (Inter or SF Pro)
- Icons: outline style, matching the box color
- No cartoon/flat icons — use geometric outlined icon style
- Keep 30% empty space — don't overcrowd
- The SCD2 snapshot in Box 6 should have a special Amber glow (#ffb300) — this is the most important part of the whole pipeline
- The DIFFERENT/SAME badges in Box 7 should also draw attention — this is the visible proof that the pipeline works
- Final touch at very bottom right corner: small text "Built for learning. Designed for production."

---

## Output
Generate this as a clean exportable poster in PNG 1920×1080 (or SVG). Ready to share on LinkedIn, Twitter, or print as an A3 reference sheet.
