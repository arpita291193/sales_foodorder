# Diner Sales Command Center

A Flask dashboard built on the 30-row `sales_data.csv` (cartoon-character
food orders across four regions). Designed to deploy straight to Render.

## Deploy to Render

1. Push this folder to a GitHub repo (or connect it directly if Render
   supports your source).
2. In Render: **New → Web Service**, point at the repo.
3. Render will pick up `render.yaml` automatically. If configuring by hand:
   - **Build command:** `pip install -r requirements.txt`
   - **Start command:** `gunicorn app:app`
   - **Environment:** Python 3.12
4. No environment variables or database needed — `sales_data.csv` ships
   with the app and loads at request time.

## Run locally

```bash
pip install -r requirements.txt
python app.py
```
Visit `http://localhost:5000`.

## What's inside

- **Introduction (hero)** — headline KPIs (total revenue, orders, AOV,
  completion rate) framed around the dataset's actual story.
- **Business Questions** — six framing questions a shift manager would
  actually ask: revenue source, at-risk revenue, rep performance, regional
  concentration, payment mix, seasonality.
- **Demographics** — top-customer and sales-rep leaderboards, plus
  payment-method and order-status donuts.
- **Geography** — since the data only records compass directions (not
  coordinates), this is a stylized regional "compass" with bubbles sized
  by revenue, plus a ranked bar chart.
- **Bar · Pie · Donut** — product revenue and rep revenue bars, region and
  product-mix pies, payment-method and status donuts — kept genuinely
  distinct chart types as requested.
- **KPIs & Trends** — a receipt-styled summary card (the page's signature
  visual element) plus a combo bar/line chart of monthly revenue vs.
  order volume.
- **Technical Analysis** — brief statistical read: quantity/revenue and
  price/quantity correlations, order-value spread (std dev, coefficient
  of variation), revenue concentration among top customers, regional
  spread, and payment-method mix — explicitly flagged as directional
  given the small sample (n = 30).

## Design notes

- Fully self-hosted Chart.js (`static/js/chart.umd.js`) — no CDN
  dependency, so it won't break if a third-party CDN is unreachable.
- Animated multi-color gradient background plus a mouse-tracking
  "flashlight" spotlight overlay (plain JS `mousemove`, no framework).
- Google Fonts (Fredoka display / Inter body / IBM Plex Mono data) are
  loaded from Google's CDN — this needs the end user's browser to have
  normal internet access, same as any font CDN.
- Tabs are handled client-side (no page reloads); all chart data is
  computed server-side with pandas and passed to the template as JSON.
