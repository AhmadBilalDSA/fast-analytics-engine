import streamlit as st
import duckdb
import polars as pl
import plotly.express as px
import time

st.set_page_config(page_title="Fast Analytics Engine", page_icon="⚡", layout="wide")

st.title("⚡ Fast Analytics Engine (DuckDB + Polars)")
st.markdown("Execute high-performance vectorized SQL queries on structured data in memory.")

# Generate synthetic dataset for immediate demonstration
@st.cache_data
def generate_sample_data(n_rows=50000):
    import numpy as np
    import pandas as pd
    np.random.seed(42)
    categories = ["Finance", "Technology", "Healthcare", "Retail", "Logistics"]
    regions = ["EMEA", "APAC", "North America", "LATAM"]
    
    df = pd.DataFrame({
        "transaction_id": [f"TXN-{100000 + i}" for i in range(n_rows)],
        "category": np.random.choice(categories, n_rows),
        "region": np.random.choice(regions, n_rows),
        "revenue": np.round(np.random.uniform(10.0, 500.0, n_rows), 2),
        "profit_margin": np.round(np.random.uniform(0.05, 0.40, n_rows), 4),
        "rating": np.random.randint(1, 6, n_rows)
    })
    return df

df = generate_sample_data()

# Register DataFrame into DuckDB in-memory session
con = duckdb.connect(database=":memory:")
con.register("transactions", df)

st.sidebar.header("📊 Engine Controls")
st.sidebar.metric("Loaded In-Memory Rows", f"{len(df):,}")

# KPI Row
total_rev = df["revenue"].sum()
avg_margin = df["profit_margin"].mean() * 100
total_records = len(df)

col1, col2, col3 = st.columns(3)
col1.metric("Total Ingested Revenue", f"${total_rev:,.2f}")
col2.metric("Average Profit Margin", f"{avg_margin:.2f}%")
col3.metric("Total Transactions", f"{total_records:,}")

st.markdown("---")

# SQL Query Editor
st.subheader("🛠️ Ad-Hoc Vectorized SQL Query")
default_query = """SELECT 
    category,
    region,
    COUNT(*) as total_orders,
    ROUND(SUM(revenue), 2) as total_revenue,
    ROUND(AVG(profit_margin) * 100, 2) as avg_margin_pct
FROM transactions
GROUP BY category, region
ORDER BY total_revenue DESC;"""

query = st.text_area("DuckDB SQL Query Input", value=default_query, height=130)

if st.button("Run Query ⚡", type="primary"):
    start_time = time.perf_counter()
    result_df = con.execute(query).df()
    duration_ms = (time.perf_counter() - start_time) * 1000

    st.success(f"Query executed in **{duration_ms:.2f} ms** ({len(result_df)} rows returned)")
    
    tab1, tab2 = st.tabs(["📋 Data Output", "📈 Visual Breakdown"])
    
    with tab1:
        st.dataframe(result_df, use_container_width=True)
    
    with tab2:
        if "category" in result_df.columns and "total_revenue" in result_df.columns:
            fig = px.bar(
                result_df, 
                x="category", 
                y="total_revenue", 
                color="region" if "region" in result_df.columns else None,
                barmode="group",
                title="Revenue by Category & Region",
                template="plotly_dark"
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Ensure output columns include 'category' and 'total_revenue' to generate the chart.")