# server.py
from typing import Any
import pandas as pd
import joblib
from datetime import datetime, timedelta
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("merch")

# load model & product mapping on startup
MODEL = None
PRODUCT_MAP = None
SALES_DF = None

def load_artifacts():
    global MODEL, PRODUCT_MAP, SALES_DF
    MODEL = joblib.load("demand_model.pkl")
    PRODUCT_MAP = joblib.load("product_map.pkl")  # dict: code -> product_id
    SALES_DF = pd.read_csv("sales_history.csv")
    SALES_DF['date'] = pd.to_datetime(SALES_DF['date'])

@mcp.tool(name="predict_demand", description="Predict demand for product_id starting from start_date for 'periods' days.")
async def predict_demand(product_id: str, start_date: str, periods: int = 14) -> Any:
    """
    input: {"product_id":"P1", "start_date":"2025-05-01", "periods":14}
    returns: {"dates":[...],"pred":[...]}
    """
    if MODEL is None:
        load_artifacts()
    start = pd.to_datetime(start_date)
    # find product_code
    # invert product_map
    inv = {v:k for k,v in PRODUCT_MAP.items()}
    if product_id not in inv:
        return {"error": f"Unknown product_id {product_id}"}
    product_code = inv[product_id]
    preds = []
    last_df = SALES_DF[SALES_DF['product_id']==product_id].sort_values('date')
    last_sales = last_df['sales'].values[-30:] if len(last_df)>=1 else [10]*30
    # naive iterative prediction using last known features
    lag_1 = int(last_sales[-1]) if len(last_sales)>0 else 0
    lag_7 = int(last_sales[-7]) if len(last_sales)>7 else int(lag_1)
    rolling_30 = float(sum(last_sales)/len(last_sales))
    out_dates=[]
    for i in range(periods):
        cur_date = start + pd.Timedelta(days=i)
        Xrow = [[product_code, cur_date.month, cur_date.day, lag_1, lag_7, rolling_30, 1.0]] # assume promo=1.0 default
        pred = float(max(0, MODEL.predict(Xrow)[0]))
        preds.append(round(pred))
        out_dates.append(cur_date.strftime("%Y-%m-%d"))
        # update lags for next iteration (simple)
        lag_7 = lag_1 if lag_7==0 else lag_7
        lag_1 = pred
        # update rolling_30 (naive)
        rolling_30 = (rolling_30*29 + pred)/30
    return {"product_id":product_id, "dates":out_dates, "pred":preds}

@mcp.tool(name="recommend_purchase", description="Recommend purchase qty for upcoming season")
async def recommend_purchase(product_id: str, season: str, safety_stock_ratio: float = 0.2) -> Any:
    # mapping season to months (simple)
    season_months = {
        "summer": [5,6,7,8],
        "winter": [11,12,1,2],
        "monsoon": [6,7,8,9],
        "all": list(range(1,13))
    }
    months = season_months.get(season.lower(), season_months['all'])
    # aggregate historical average daily demand for those months, then scale for 30 days
    if MODEL is None:
        load_artifacts()
    dfp = SALES_DF[(SALES_DF['product_id']==product_id) & (SALES_DF['date'].dt.month.isin(months))]
    if dfp.empty:
        return {"error": "No history for this product & season"}
    avg_daily = float(dfp['sales'].mean())
    planned_period_days = 30
    required = avg_daily * planned_period_days
    safety = required * float(safety_stock_ratio)
    purchase_qty = int(round(max(0, required + safety)))
    return {"product_id":product_id, "season":season, "avg_daily":avg_daily, "recommended_purchase_qty":purchase_qty}

if __name__ == "__main__":
    load_artifacts()
    print("MCP merch server ready")
    # Use the current FastMCP API: run() (replaces old serve())
    # Default transport is stdio; you can pass transport="sse" or "streamable-http"
    mcp.run()
