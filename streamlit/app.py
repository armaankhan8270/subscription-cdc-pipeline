from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from jinja2 import Environment, FileSystemLoader
import snowflake.connector
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="SubsTrack Dashboard")
env = Environment(loader=FileSystemLoader("streamlit/templates"), auto_reload=False)

SNOWFLAKE_CONFIG = {
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "role": os.getenv("SNOWFLAKE_ROLE"),
    "login_timeout": 10
}

def q(sql):
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cur = conn.cursor()
    cur.execute("USE DATABASE SUBSTRACK_DB")
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=cols)

def render(name, **ctx):
    tpl = env.get_template(name)
    return HTMLResponse(tpl.render(ctx))

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    rc = q("SELECT COUNT(*) as n FROM RAW.CUSTOMERS")["N"][0]
    sc = q("SELECT COUNT(*) as n FROM STAGING.CUSTOMERS")["N"][0]
    sv = q("SELECT COUNT(*) as n FROM SNAPSHOTS.DIM_CUSTOMER_SNAPSHOT")["N"][0]
    tp = q("SELECT COUNT(*) as n FROM MARTS.FCT_PURCHASES")["N"][0]

    df = q("SELECT plan, COUNT(*) as n FROM MARTS.DIM_CUSTOMER WHERE is_current = TRUE GROUP BY plan")
    fig = px.bar(df, x="PLAN", y="N", color="PLAN",
                 color_discrete_map={"free":"#9ca3af","basic":"#60a5fa","premium":"#fbbf24","enterprise":"#a78bfa"})
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
    chart = fig.to_html(full_html=False, include_plotlyjs="cdn")

    return render("overview.html", active="overview",
                  counts={"raw_customers":rc,"staging_customers":sc,"snapshot_versions":sv,"total_purchases":tp},
                  chart=chart, tasks=[])

@app.get("/customers", response_class=HTMLResponse)
def customers(request: Request, customer_id: str = ""):
    df = q("SELECT DISTINCT customer_id, full_name FROM MARTS.DIM_CUSTOMER ORDER BY full_name")
    custs = [list(r) for r in df.itertuples(index=False, name=None)]
    history = None
    timeline = None

    if customer_id:
        conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
        cur = conn.cursor()
        cur.execute("USE DATABASE SUBSTRACK_DB")
        cur.execute(f"""
            SELECT customer_id, full_name, plan, plan_price, status,
                   valid_from, valid_to, days_on_plan
            FROM MARTS.DIM_CUSTOMER WHERE customer_id = '{customer_id}'
            ORDER BY valid_from
        """)
        rows = cur.fetchall()
        names = [d[0] for d in cur.description]
        history = [list(r) for r in rows]
        cur.close()
        conn.close()

        df_h = pd.DataFrame(rows, columns=names)
        if not df_h.empty:
            df_h["VALID_TO"] = df_h["VALID_TO"].fillna(pd.Timestamp.now())
            fig = px.timeline(df_h, x_start="VALID_FROM", x_end="VALID_TO", y="PLAN",
                              color="PLAN", title=f"Plan Timeline — {df_h['FULL_NAME'].iloc[0]}",
                              color_discrete_map={"free":"#9ca3af","basic":"#60a5fa",
                                                  "premium":"#fbbf24","enterprise":"#a78bfa"})
            fig.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
            timeline = fig.to_html(full_html=False, include_plotlyjs="cdn")

    return render("customers.html", active="customers",
                  customers=custs, selected=customer_id,
                  history=history, timeline=timeline)

@app.get("/purchases", response_class=HTMLResponse)
def purchases(request: Request):
    df = q("""
        SELECT f.purchase_id, f.customer_name, f.product_name, f.purchase_date,
               f.amount, f.plan_at_purchase, c.plan AS current_plan
        FROM MARTS.FCT_PURCHASES f
        JOIN MARTS.DIM_CUSTOMER c ON f.customer_id = c.customer_id AND c.is_current = TRUE
        ORDER BY f.purchase_date
    """)
    rows = [list(r) for r in df.itertuples(index=False, name=None)]

    rev = q("""
        SELECT plan_at_purchase, COUNT(*) as n, SUM(amount) as rev
        FROM MARTS.FCT_PURCHASES GROUP BY plan_at_purchase
    """)
    if not rev.empty:
        bar = px.bar(rev, x="PLAN_AT_PURCHASE", y="REV", color="PLAN_AT_PURCHASE", text="REV",
                     title="Revenue by Plan When Purchased")
        bar.update_traces(texttemplate="$%{text}", textposition="outside")
        bar.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", showlegend=False)
        pie = px.pie(rev, values="N", names="PLAN_AT_PURCHASE", title="Purchase Count by Plan")
        pie.update_layout(plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)")
    else:
        bar = go.Figure()
        pie = go.Figure()

    return render("purchases.html", active="purchases", purchases=rows,
                  bar_chart=bar.to_html(full_html=False, include_plotlyjs="cdn"),
                  pie_chart=pie.to_html(full_html=False, include_plotlyjs="cdn"))

@app.get("/distribution", response_class=HTMLResponse)
def distribution(request: Request):
    df = q("""
        SELECT plan, COUNT(DISTINCT customer_id) as n, SUM(plan_price) as rev
        FROM MARTS.DIM_CUSTOMER WHERE is_current = TRUE GROUP BY plan
    """)
    if not df.empty:
        pie = px.pie(df, values="N", names="PLAN", title="Customers by Plan",
                     color="PLAN", color_discrete_map={"free":"#9ca3af","basic":"#60a5fa",
                                                       "premium":"#fbbf24","enterprise":"#a78bfa"})
        bar = px.bar(df, x="PLAN", y="REV", color="PLAN", text="REV", title="Monthly Revenue by Plan")
        bar.update_traces(texttemplate="$%{text}", textposition="outside")
        bar.update_layout(showlegend=False)
    else:
        pie = go.Figure()
        bar = go.Figure()

    df_v = q("""
        SELECT customer_id, full_name, COUNT(*) as n,
               MIN(valid_from) as f, MAX(valid_from) as l
        FROM MARTS.DIM_CUSTOMER GROUP BY customer_id, full_name ORDER BY n DESC
    """)
    versions = [list(r) for r in df_v.itertuples(index=False, name=None)]

    return render("distribution.html", active="distribution",
                  pie=pie.to_html(full_html=False, include_plotlyjs="cdn"),
                  bar=bar.to_html(full_html=False, include_plotlyjs="cdn"),
                  versions=versions)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
