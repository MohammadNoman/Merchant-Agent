import streamlit as st
import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import json
import asyncio

st.set_page_config(layout="wide", page_title="Merchant Agent Dashboard")

st.title("🏪 Merchant Agent Dashboard")
st.markdown("*Demand forecasting & purchase recommendations powered by AI*")

# Import server functions directly (avoids subprocess issues on Windows/Streamlit Cloud)
try:
    import server as local_server
    # Ensure artifacts are loaded
    if getattr(local_server, 'MODEL', None) is None:
        local_server.load_artifacts()
    SERVER_AVAILABLE = True
except Exception as e:
    st.error(f"Failed to load server: {e}")
    SERVER_AVAILABLE = False

def call_mcp_tool(tool_name: str, params: dict):
    """Call an MCP tool by invoking local server functions."""
    if not SERVER_AVAILABLE:
        return {"error": "Server not available"}
    
    try:
        if tool_name == 'predict_demand':
            result = asyncio.run(local_server.predict_demand(**params))
        elif tool_name == 'recommend_purchase':
            result = asyncio.run(local_server.recommend_purchase(**params))
        else:
            return {"error": f"Unknown tool: {tool_name}"}
        
        # Normalize result (handle MCP TextContent wrapper)
        if hasattr(result, 'content'):
            return result.content
        return result
    except Exception as e:
        return {"error": str(e)}

# --- Demand Prediction Section ---
st.header("📈 Demand Prediction")

col1, col2, col3 = st.columns(3)
with col1:
    product_id_predict = st.selectbox("Select Product ID", ["T-Shirt", "Jeans", "Trousers"], key="predict_product")
with col2:
    start_date_predict = st.date_input("Start Date", datetime.now().date() + timedelta(days=1), key="predict_start_date")
with col3:
    periods_predict = st.number_input("Number of Days", min_value=1, max_value=90, value=14, key="predict_periods")

if st.button("🔮 Predict Demand", key="btn_predict"):
    with st.spinner("Generating forecast..."):
        result = call_mcp_tool(
            "predict_demand",
            {
                "product_id": product_id_predict,
                "start_date": start_date_predict.strftime("%Y-%m-%d"),
                "periods": periods_predict,
            }
        )
        if "error" not in result:
            st.success("✅ Forecast generated!")
            st.subheader("Prediction Results:")
            df_pred = pd.DataFrame({
                "Date": result["dates"],
                "Predicted Sales": result["pred"]
            })
            st.dataframe(df_pred, use_container_width=True)
            st.line_chart(df_pred.set_index("Date")["Predicted Sales"])
        else:
            st.error(f"❌ Error: {result['error']}")

# --- Purchase Recommendation Section ---
st.header("🛒 Purchase Recommendation")

col1, col2, col3 = st.columns(3)
with col1:
    product_id_recommend = st.selectbox("Select Product ID", ["T-Shirt", "Jeans", "Trousers"], key="recommend_product")
with col2:
    season_recommend = st.selectbox("Select Season", ["Summer", "Winter", "Monsoon", "All"], key="recommend_season")
with col3:
    safety_stock_ratio_recommend = st.slider("Safety Stock Ratio", min_value=0.0, max_value=1.0, value=0.2, step=0.05, key="recommend_safety_ratio")

if st.button("📊 Recommend Purchase", key="btn_recommend"):
    with st.spinner("Calculating recommendation..."):
        result = call_mcp_tool(
            "recommend_purchase",
            {
                "product_id": product_id_recommend,
                "season": season_recommend.lower(),
                "safety_stock_ratio": safety_stock_ratio_recommend,
            }
        )
        if "error" not in result:
            st.success("✅ Recommendation generated!")
            st.subheader("Recommendation Results:")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Product ID", result["product_id"])
            with col2:
                st.metric("Avg Daily Demand", f"{result['avg_daily']:.1f}")
            with col3:
                st.metric("Recommended Qty", result["recommended_purchase_qty"])
            st.info(f"**Season:** {result['season']} | **Safety Stock Ratio:** {safety_stock_ratio_recommend}")
        else:
            st.error(f"❌ Error: {result['error']}")

st.divider()
st.markdown("""
### 📖 How to Use:
1. **Demand Prediction**: Select a product, start date, and forecast period to generate sales predictions.
2. **Purchase Recommendation**: Select a product and season to get recommended purchase quantities based on historical demand patterns.

**Server Status:** ✅ Running
""")
