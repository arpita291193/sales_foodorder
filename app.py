"""
Diner Sales Command Center
===========================
A Flask app (Render-deployable) that turns the 30-row sales_data.csv into
an interactive single-page dashboard: introduction, guiding business
questions, customer/rep demographics, a regional "geography" view, bar/
pie/donut charts, a flashlight cursor, a colorful animated background,
and a brief technical/statistical read with KPI numbers and trend lines.
"""

import json
import os

import pandas as pd
from flask import Flask, render_template

app = Flask(__name__)

DATA_PATH = os.path.join(os.path.dirname(__file__), "sales_data.csv")


def load_data():
    df = pd.read_csv(DATA_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    df["total_sales"] = df["total_sales"].astype(float)
    return df


def build_context():
    df = load_data()
    n = len(df)

    total_revenue = float(df["total_sales"].sum())
    avg_order_value = float(df["total_sales"].mean())
    total_orders = int(n)
    completed = df[df["status"] == "Completed"]
    pending = df[df["status"] == "Pending"]
    cancelled = df[df["status"] == "Cancelled"]
    completion_rate = len(completed) / n * 100
    pending_rate = len(pending) / n * 100
    cancellation_rate = len(cancelled) / n * 100
    completed_revenue = float(completed["total_sales"].sum())
    at_risk_revenue = float(pending["total_sales"].sum() + cancelled["total_sales"].sum())

    top_product_row = df.groupby("product")["total_sales"].sum().idxmax()
    top_region_row = df.groupby("region")["total_sales"].sum().idxmax()
    top_rep_row = df.groupby("sales_rep")["total_sales"].sum().idxmax()
    top_customer_row = df.groupby("customer_name")["total_sales"].sum().idxmax()

    avg_items_per_order = float(df["quantity"].mean())
    avg_unit_price = float(df["unit_price"].mean())

    # ---- chart-ready aggregates ----
    by_region = df.groupby("region")["total_sales"].sum().sort_values(ascending=False)
    by_product = df.groupby("product")["total_sales"].sum().sort_values(ascending=False)
    by_status = df["status"].value_counts()
    by_payment = df["payment_method"].value_counts()
    by_rep = df.groupby("sales_rep")["total_sales"].sum().sort_values(ascending=False)
    by_customer = df.groupby("customer_name")["total_sales"].sum().sort_values(ascending=False)
    by_month = df.groupby(df["order_date"].dt.strftime("%b")).agg(
        revenue=("total_sales", "sum"), orders=("order_id", "count")
    )
    month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    by_month = by_month.reindex([m for m in month_order if m in by_month.index])

    region_status = df.groupby(["region", "status"])["order_id"].count().unstack(fill_value=0)

    # ---- brief technical analysis numbers ----
    qty_sales_corr = float(df["quantity"].corr(df["total_sales"]))
    price_qty_corr = float(df["unit_price"].corr(df["quantity"]))
    revenue_std = float(df["total_sales"].std())
    revenue_cv = float(revenue_std / df["total_sales"].mean() * 100)
    top_customer_share = float(by_customer.iloc[0] / total_revenue * 100)
    top3_customer_share = float(by_customer.iloc[:3].sum() / total_revenue * 100)
    region_revenue_range = float(by_region.max() - by_region.min())
    north_share = float(by_region.get("North", 0) / total_revenue * 100)
    cash_share = float(by_payment.get("Cash", 0) / n * 100)

    kpis = {
        "total_revenue": round(total_revenue, 2),
        "total_orders": total_orders,
        "avg_order_value": round(avg_order_value, 2),
        "completion_rate": round(completion_rate, 1),
        "pending_rate": round(pending_rate, 1),
        "cancellation_rate": round(cancellation_rate, 1),
        "completed_revenue": round(completed_revenue, 2),
        "at_risk_revenue": round(at_risk_revenue, 2),
        "top_product": top_product_row,
        "top_region": top_region_row,
        "top_rep": top_rep_row,
        "top_customer": top_customer_row,
        "avg_items_per_order": round(avg_items_per_order, 1),
        "avg_unit_price": round(avg_unit_price, 2),
    }

    tech = {
        "qty_sales_corr": round(qty_sales_corr, 3),
        "price_qty_corr": round(price_qty_corr, 3),
        "revenue_std": round(revenue_std, 2),
        "revenue_cv": round(revenue_cv, 1),
        "top_customer_share": round(top_customer_share, 1),
        "top3_customer_share": round(top3_customer_share, 1),
        "region_revenue_range": round(region_revenue_range, 2),
        "north_share": round(north_share, 1),
        "cash_share": round(cash_share, 1),
        "n": n,
    }

    charts = {
        "region_labels": by_region.index.tolist(),
        "region_values": [round(v, 2) for v in by_region.values.tolist()],
        "product_labels": by_product.index.tolist(),
        "product_values": [round(v, 2) for v in by_product.values.tolist()],
        "status_labels": by_status.index.tolist(),
        "status_values": by_status.values.tolist(),
        "payment_labels": by_payment.index.tolist(),
        "payment_values": by_payment.values.tolist(),
        "rep_labels": by_rep.index.tolist(),
        "rep_values": [round(v, 2) for v in by_rep.values.tolist()],
        "customer_labels": by_customer.index.tolist(),
        "customer_values": [round(v, 2) for v in by_customer.values.tolist()],
        "month_labels": by_month.index.tolist(),
        "month_revenue": [round(v, 2) for v in by_month["revenue"].values.tolist()],
        "month_orders": by_month["orders"].values.tolist(),
        "region_status": {
            region: [int(region_status.loc[region].get(s, 0)) for s in ["Completed", "Pending", "Cancelled"]]
            for region in region_status.index
        },
    }

    records = df.assign(order_date=df["order_date"].dt.strftime("%Y-%m-%d")).to_dict(orient="records")

    return {
        "kpis": kpis,
        "tech": tech,
        "charts_json": json.dumps(charts),
        "records_json": json.dumps(records),
    }


@app.route("/")
def index():
    ctx = build_context()
    return render_template("index.html", **ctx)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
