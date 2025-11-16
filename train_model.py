# train_model.py
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import joblib

def make_features(df):
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    # rolling lag features per product
    df = df.sort_values(['product_id','date'])
    df['lag_1'] = df.groupby('product_id')['sales'].shift(1).fillna(0)
    df['lag_7'] = df.groupby('product_id')['sales'].shift(7).fillna(0)
    df['rolling_30'] = df.groupby('product_id')['sales'].transform(lambda x: x.rolling(30, min_periods=1).mean()).fillna(0)
    # encode product_id as cat codes
    df['product_code'] = df['product_id'].astype('category').cat.codes
    return df

def train():
    df = pd.read_csv("sales_history.csv")
    df = make_features(df)
    X = df[['product_code','month','day','lag_1','lag_7','rolling_30','promo']]
    y = df['sales']
    # simple time-split: use last 90 days as test
    df['date'] = pd.to_datetime(df['date'])
    cutoff = df['date'].max() - pd.Timedelta(days=90)
    train_mask = df['date'] <= cutoff
    X_train = X[train_mask]
    y_train = y[train_mask]
    # train one global model
    model = RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    joblib.dump(model, "demand_model.pkl")
    # save product mapping
    prod_map = dict(enumerate(df['product_id'].astype('category').cat.categories))
    joblib.dump(prod_map, "product_map.pkl")
    print("Model trained and saved (demand_model.pkl).")

if __name__ == "__main__":
    train()
