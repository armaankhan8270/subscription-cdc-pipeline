🚀 Scaled my CDC + SCD2 pipeline to 1,000 customers — here's what changed.

Last week I built a simple SQLite → Snowflake → dbt → FastAPI pipeline. This week I scaled it to a full SaaS dataset:

📊 **Scale:**
• 1,000 customers (was 6)
• 7 source tables (was 2)
• 2,000 purchases, 6,000 invoices, 4,000 usage events, 2,000 support tickets
• 4 SCD2 snapshots tracking plan changes, payment methods, ticket status
• 6 dashboard pages (was 4)
• ~16,000 total records flowing through the pipeline

🏗️ **Architecture:**
SQLite (7 tables) → CDC (watermark-based) → Snowflake Stage → 7 Snowpipes → 7 Streams → 7 Tasks (manual MERGE) → dbt (4 SCD2 snapshots + 6 mart models) → FastAPI dashboard (6 pages live from Snowflake)

🎯 **The core problem it solves:**
When Alice upgrades from Basic → Premium, her Feb purchase shouldn't retroactively show Premium pricing. SCD2 + temporal joins ensure revenue reports are historically correct — every time.

🧪 **25+ dbt data tests enforcing:**
• unique keys, not-null fields, accepted values, referential integrity
• No overlapping SCD2 date ranges
• Temporal join accuracy (DIFFERENT vs SAME badges on dashboard)

🔗 **Code:** github.com/armaankhan8270/subscription-cdc-pipeline

#DataEngineering #Snowflake #dbt #CDC #SCD2 #FastAPI #DataPipeline
