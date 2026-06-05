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
    "login_timeout": 10,
}

COLORS = {"free": "#9ca3af", "basic": "#60a5fa", "premium": "#fbbf24", "enterprise": "#a78bfa"}

def q(sql, db="SUBSTRACK_DB"):
    conn = snowflake.connector.connect(**SNOWFLAKE_CONFIG)
    cur = conn.cursor()
    cur.execute(f"USE DATABASE {db}")
    cur.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=cols)

def render(name, **ctx):
    tpl = env.get_template(name)
    return HTMLResponse(tpl.render(ctx))

def plotly_style(fig):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#374151"),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    return fig.to_html(full_html=False, include_plotlyjs="cdn")


@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    counts = {
        "Raw Customers": q("SELECT COUNT(*) as n FROM RAW.CUSTOMERS")["N"][0],
        "Staging Customers": q("SELECT COUNT(*) as n FROM STAGING.CUSTOMERS")["N"][0],
        "SCD2 Versions": q("SELECT COUNT(*) as n FROM SNAPSHOTS.DIM_CUSTOMER_SNAPSHOT")["N"][0],
        "Purchases": q("SELECT COUNT(*) as n FROM MARTS.FCT_PURCHASES")["N"][0],
        "Subscriptions": q("SELECT COUNT(*) as n FROM STAGING.SUBSCRIPTIONS")["N"][0],
        "Invoices": q("SELECT COUNT(*) as n FROM STAGING.BILLING_INVOICES")["N"][0],
        "Usage Events": q("SELECT COUNT(*) as n FROM STAGING.USAGE_EVENTS")["N"][0],
        "Support Tickets": q("SELECT COUNT(*) as n FROM STAGING.SUPPORT_TICKETS")["N"][0],
    }
    df = q("SELECT plan, COUNT(*) as n FROM MARTS.DIM_CUSTOMER WHERE is_current = TRUE GROUP BY plan")
    bar = px.bar(df, x="PLAN", y="N", color="PLAN", color_discrete_map=COLORS)
    return render("overview.html", active="overview", counts=counts, chart=plotly_style(bar))


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
                   dbt_valid_from as valid_from, dbt_valid_to as valid_to, days_on_plan,
                   is_current
            FROM MARTS.DIM_CUSTOMER WHERE customer_id = '{customer_id}'
            ORDER BY dbt_valid_from
        """)
        rows = cur.fetchall()
        names = [d[0] for d in cur.description]
        history = [list(r) for r in rows]
        cur.close()
        conn.close()
        df_h = pd.DataFrame(rows, columns=names)
        if not df_h.empty:
            df_h["VALID_TO"] = df_h["VALID_TO"].fillna(pd.Timestamp.now())
            fig = px.timeline(
                df_h, x_start="VALID_FROM", x_end="VALID_TO", y="PLAN",
                color="PLAN", title=f"Plan Timeline — {df_h['FULL_NAME'].iloc[0]}",
                color_discrete_map=COLORS,
            )
            fig.update_layout(showlegend=False)
            timeline = fig.to_html(full_html=False, include_plotlyjs="cdn")
    return render("customers.html", active="customers", customers=custs, selected=customer_id, history=history, timeline=timeline)


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
        bar = px.bar(rev, x="PLAN_AT_PURCHASE", y="REV", color="PLAN_AT_PURCHASE", text="REV", title="Revenue by Plan When Purchased", color_discrete_map=COLORS)
        bar.update_traces(texttemplate="$%{text}", textposition="outside")
        bar.update_layout(showlegend=False)
        pie = px.pie(rev, values="N", names="PLAN_AT_PURCHASE", title="Purchase Count by Plan", color_discrete_map=COLORS, color="PLAN_AT_PURCHASE")
    else:
        bar, pie = go.Figure(), go.Figure()
    return render("purchases.html", active="purchases", purchases=rows, bar_chart=plotly_style(bar), pie_chart=plotly_style(pie))


@app.get("/subscriptions", response_class=HTMLResponse)
def subscriptions(request: Request):
    df = q("""
        SELECT s.subscription_id, s.customer_id, c.full_name, s.plan_type,
               s.plan_price, s.status, s.start_date, s.end_date, s.is_active
        FROM MARTS.DIM_SUBSCRIPTION s
        JOIN MARTS.DIM_CUSTOMER c ON s.customer_id = c.customer_id AND c.is_current = TRUE
        WHERE s.is_current = TRUE
        ORDER BY s.start_date DESC
    """)
    rows = [list(r) for r in df.itertuples(index=False, name=None)]
    status_df = q("""
        SELECT status, COUNT(*) as n FROM MARTS.DIM_SUBSCRIPTION
        WHERE is_current = TRUE GROUP BY status
    """)
    pie = px.pie(status_df, values="N", names="STATUS", title="Subscription Status", color_discrete_map={"active": "#10b981", "cancelled": "#e94560", "expired": "#9ca3af"}, color="STATUS") if not status_df.empty else go.Figure()
    plan_df = q("""
        SELECT plan_type, COUNT(*) as n FROM MARTS.DIM_SUBSCRIPTION
        WHERE is_current = TRUE AND status = 'active' GROUP BY plan_type
    """)
    bar = px.bar(plan_df, x="PLAN_TYPE", y="N", color="PLAN_TYPE", title="Active Subscriptions by Plan", color_discrete_map=COLORS) if not plan_df.empty else go.Figure()
    bar.update_layout(showlegend=False)
    return render("subscriptions.html", active="subscriptions", subs=rows, pie=plotly_style(pie), bar=plotly_style(bar))


@app.get("/billing", response_class=HTMLResponse)
def billing(request: Request):
    df = q("""
        SELECT invoice_id, customer_name, amount, currency, payment_status,
               due_date, paid_at, is_paid, days_to_pay
        FROM MARTS.FCT_BILLING_INVOICES
        ORDER BY due_date DESC
    """)
    rows = [list(r) for r in df.itertuples(index=False, name=None)]
    rev_df = q("""
        SELECT DATE_TRUNC('month', due_date) as month, SUM(collected_revenue) as rev
        FROM MARTS.FCT_BILLING_INVOICES
        WHERE payment_status = 'paid'
        GROUP BY month ORDER BY month
    """)
    bar = px.bar(rev_df, x="MONTH", y="REV", title="Monthly Collected Revenue", text="REV") if not rev_df.empty else go.Figure()
    bar.update_traces(texttemplate="$%{text}", textposition="outside")
    bar.update_layout(showlegend=False)
    status_df = q("""
        SELECT payment_status, COUNT(*) as n, SUM(amount) as total
        FROM MARTS.FCT_BILLING_INVOICES GROUP BY payment_status
    """)
    pie = px.pie(status_df, values="N", names="PAYMENT_STATUS", title="Invoices by Status") if not status_df.empty else go.Figure()
    return render("billing.html", active="billing", invoices=rows, bar=plotly_style(bar), pie=plotly_style(pie))


@app.get("/usage", response_class=HTMLResponse)
def usage(request: Request):
    df = q("""
        SELECT event_type, event_category, SUM(quantity) as total, COUNT(*) as n
        FROM MARTS.FCT_USAGE_EVENTS
        GROUP BY event_type, event_category ORDER BY total DESC
    """)
    rows = [list(r) for r in df.itertuples(index=False, name=None)]
    by_cat = q("""
        SELECT event_category, SUM(quantity) as total, COUNT(*) as n
        FROM MARTS.FCT_USAGE_EVENTS
        GROUP BY event_category
    """)
    pie = px.pie(by_cat, values="TOTAL", names="EVENT_CATEGORY", title="Usage by Category") if not by_cat.empty else go.Figure()
    by_cust = q("""
        SELECT u.customer_name, u.event_category, SUM(u.quantity) as total
        FROM MARTS.FCT_USAGE_EVENTS u
        GROUP BY u.customer_name, u.event_category
    """)
    heat = px.bar(by_cust, x="CUSTOMER_NAME", y="TOTAL", color="EVENT_CATEGORY", title="Usage per Customer", barmode="group") if not by_cust.empty else go.Figure()
    return render("usage.html", active="usage", events=rows, pie=plotly_style(pie), heat=plotly_style(heat))


@app.get("/distribution", response_class=HTMLResponse)
def distribution(request: Request):
    df = q("""
        SELECT plan, COUNT(DISTINCT customer_id) as n, SUM(plan_price) as rev
        FROM MARTS.DIM_CUSTOMER WHERE is_current = TRUE GROUP BY plan
    """)
    if not df.empty:
        pie = px.pie(df, values="N", names="PLAN", title="Customers by Plan", color="PLAN", color_discrete_map=COLORS)
        bar = px.bar(df, x="PLAN", y="REV", color="PLAN", text="REV", title="Monthly Revenue by Plan", color_discrete_map=COLORS)
        bar.update_traces(texttemplate="$%{text}", textposition="outside")
        bar.update_layout(showlegend=False)
    else:
        pie, bar = go.Figure(), go.Figure()
    df_v = q("""
        SELECT customer_id, full_name, COUNT(*) as n,
               MIN(dbt_valid_from) as f, MAX(dbt_valid_from) as l
        FROM MARTS.DIM_CUSTOMER GROUP BY customer_id, full_name ORDER BY n DESC
    """)
    versions = [list(r) for r in df_v.itertuples(index=False, name=None)]
    return render("distribution.html", active="distribution", pie=plotly_style(pie), bar=plotly_style(bar), versions=versions)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
