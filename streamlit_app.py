import streamlit as st
import subprocess
import os
import pandas as pd
from datetime import datetime, timedelta
import json

st.set_page_config(layout="wide", page_title="Merchant Agent Dashboard")

st.title("🏪 Merchant Agent Dashboard")
st.markdown("*Demand forecasting & purchase recommendations powered by AI*")

SERVER_PATH = os.path.join(os.path.dirname(__file__), "server.py")
PYTHON_EXE = "python"

@st.cache_resource
def get_server_subprocess():
    """Start the MCP server as a subprocess."""
    proc = subprocess.Popen(
        [PYTHON_EXE, SERVER_PATH],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return proc

# Start server in background
server_proc = get_server_subprocess()

def call_mcp_tool(tool_name: str, params: dict):
    """Call an MCP tool via the client subprocess."""
    try:
        # Use client.py to call the tool
        result = subprocess.run(
            [PYTHON_EXE, "-c", f"""
import asyncio
import sys
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import json

async def main():
    async with AsyncExitStack() as stack:
        server_params = StdioServerParameters(command='{PYTHON_EXE}', args=['{SERVER_PATH}'])
        stdio_transport = await stack.enter_async_context(stdio_client(server_params))
        stdio, write = stdio_transport
        session = await stack.enter_async_context(ClientSession(stdio, write))
        await session.initialize()
        result = await session.call_tool('{tool_name}', {json.dumps(params)})
        def safe(obj):
            # Convert common objects to JSON-serializable structures
            if obj is None or isinstance(obj, (str, int, float, bool)):
                return obj
            if isinstance(obj, dict):
                return {{k: safe(v) for k, v in obj.items()}}
            if isinstance(obj, list):
                return [safe(v) for v in obj]
            # Fallback: try to extract .content or .text attributes, then str()
            if hasattr(obj, 'content'):
                return safe(getattr(obj, 'content'))
            if hasattr(obj, 'text'):
                return safe(getattr(obj, 'text'))
            try:
                return str(obj)
            except Exception:
                return None

        if hasattr(result, 'content'):
            print(json.dumps(safe(result.content)))
        else:
            print(json.dumps({{"error": "No content in result"}}))

asyncio.run(main())
"""],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout:
            return json.loads(result.stdout)
        else:
            return {"error": f"Tool call failed: {result.stderr}"}
    except Exception as e:
        return {"error": str(e)}

# --- Demand Prediction Section ---
st.header("📈 Demand Prediction")

col1, col2, col3 = st.columns(3)
with col1:
    product_id_predict = st.selectbox("Select Product ID", ["P1", "P2", "P3"], key="predict_product")
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
    product_id_recommend = st.selectbox("Select Product ID", ["P1", "P2", "P3"], key="recommend_product")
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
