# data_sim.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def simulate_sales(start="2021-01-01", end="2024-12-31", products=None, seed=42):
    np.random.seed(seed)
    if products is None:
        products = [
            {"id": "P1", "name": "T-Shirt", "seasonality": [0,0,0,0,0.2,0.6,0.9,0.8,0.3,0,0,0]}, # summer peak
            {"id": "P2", "name": "Jacket", "seasonality": [0.8,0.9,0.7,0.4,0.1,0,0,0,0,0.3,0.7,0.9]}, # winter peak
            {"id": "P3", "name": "Umbrella", "seasonality": [0.4,0.6,0.6,0.6,0.5,0.3,0.2,0.3,0.6,0.7,0.6,0.5]} # rainy months
        ]

    dates = pd.date_range(start, end, freq="D")
    rows = []
    for p in products:
        base = 20 + np.random.randint(-5, 6)
        for d in dates:
            month = d.month - 1
            season_factor = p["seasonality"][month]
            trend = 1 + 0.01 * ((d.year - pd.Timestamp(start).year))
            promo = 1.0
            # occasional promotions
            if np.random.rand() < 0.02:
                promo = 1.6
            noise = np.random.normal(scale=3.0)
            sales = max(0, round(base * (1 + season_factor) * trend * promo + noise))
            rows.append({
                "date": d.strftime("%Y-%m-%d"),
                "product_id": p["id"],
                "product_name": p["name"],
                "sales": int(sales),
                "promo": float(promo)
            })
    df = pd.DataFrame(rows)
    return df

if __name__ == "__main__":
    df = simulate_sales()
    df.to_csv("sales_history.csv", index=False)
    print("sales_history.csv written, rows:", len(df))
