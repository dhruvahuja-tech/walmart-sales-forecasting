# ============================================================
# app.py
# Purpose: Streamlit web app for Walmart Sales Forecasting
# Model  : XGBoost (primary) + Random Forest (comparison)
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import os

# ============================================================
# PAGE CONFIGURATION
# ============================================================
st.set_page_config(
    page_title = "Walmart Sales Forecaster",
    page_icon  = "🛒",
    layout     = "wide"
)

# ============================================================
# LOAD MODELS
# ============================================================
# @st.cache_resource → loads model once and caches it
# Without this → model reloads every time user clicks anything
@st.cache_resource
def load_models():
    xgb = joblib.load(r"D:\Data Science\Sales Forecasting Project\models\xgboost.pkl")
    rf  = joblib.load(r"D:\Data Science\Sales Forecasting Project\models\random_forest.pkl")
    return xgb, rf

xgb, rf = load_models()

# ============================================================
# LOAD DATA — for reference ranges
# ============================================================
@st.cache_data
def load_data():
    return pd.read_csv(r"D:\Data Science\Sales Forecasting Project\Clean Dataset for modelling\walmart_features.csv")

df = load_data()

# ============================================================
# HEADER
# ============================================================
st.title("🛒 Walmart Store Sales Forecaster")
st.markdown("""
Predict weekly sales for any Walmart store and department
using Machine Learning models trained on 421,570 records
across 45 stores.
""")

# Horizontal divider
st.markdown("---")

# ============================================================
# SIDEBAR — Model Selection
# ============================================================
st.sidebar.title("⚙️ Settings")
st.sidebar.markdown("### Select Model")

model_choice = st.sidebar.radio(
    "Choose prediction model:",
    ["XGBoost (Recommended)", "Random Forest"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Model Performance")

# Show model metrics in sidebar
if model_choice == "XGBoost (Recommended)":
    st.sidebar.metric("R² Score",  "0.9741")
    st.sidebar.metric("MAE",       "$1,919")
    st.sidebar.metric("RMSE",      "$3,673")
else:
    st.sidebar.metric("R² Score",  "0.9729")
    st.sidebar.metric("MAE",       "$1,504")
    st.sidebar.metric("RMSE",      "$3,758")

# ============================================================
# INPUT SECTION
# ============================================================
st.subheader("📋 Enter Store & Week Details")

# Two column layout for inputs
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**Store Information**")

    store = st.selectbox(
        "Store Number",
        options = sorted(df["store"].unique()),
        help    = "Select Walmart store (1-45)"
    )

    dept = st.selectbox(
        "Department",
        options = sorted(df["dept"].unique()),
        help    = "Select department number"
    )

    # Get store type and size automatically from data
    store_info  = df[df["store"] == store].iloc[0]
    store_type  = int(store_info["store_type"])
    store_size  = int(store_info["store_size"])

    st.info(f"""
    **Store {store} Details:**
    Type : {'A' if store_type==0 else 'B' if store_type==1 else 'C'}
    Size : {store_size:,} sq ft
    """)

with col2:
    st.markdown("**Date & Holiday**")

    # Date picker
    selected_date = st.date_input(
        "Select Week Date",
        help = "Select the Friday of the week to forecast"
    )

    # Extract date features automatically
    month        = selected_date.month
    year         = selected_date.year
    week_of_year = selected_date.isocalendar()[1]
    quarter      = (month - 1) // 3 + 1
    is_quarter_end = 1 if month in [3, 6, 9, 12] else 0

    st.markdown(f"""
    **Extracted Date Features:**
    - Month        : {month}
    - Week of Year : {week_of_year}
    - Quarter      : Q{quarter}
    """)

    is_holiday = st.selectbox(
        "Holiday Week?",
        options = [0, 1],
        format_func = lambda x: "Yes — Holiday Week" if x == 1 else "No — Regular Week",
        help = "Super Bowl, Labour Day, Thanksgiving, Christmas"
    )

with col3:
    st.markdown("**Economic & Store Conditions**")

    temperature = st.slider(
        "Temperature (°F)",
        min_value = float(df["temperature"].min()),
        max_value = float(df["temperature"].max()),
        value     = float(df["temperature"].mean()),
        step      = 0.1
    )

    fuel_price = st.slider(
        "Fuel Price ($)",
        min_value = float(df["fuel_price"].min()),
        max_value = float(df["fuel_price"].max()),
        value     = float(df["fuel_price"].mean()),
        step      = 0.01
    )

    cpi = st.slider(
        "CPI",
        min_value = float(df["cpi"].min()),
        max_value = float(df["cpi"].max()),
        value     = float(df["cpi"].mean()),
        step      = 0.1
    )

    unemployment = st.slider(
        "Unemployment Rate (%)",
        min_value = float(df["unemployment"].min()),
        max_value = float(df["unemployment"].max()),
        value     = float(df["unemployment"].mean()),
        step      = 0.1
    )

# ── Markdown inputs ──────────────────────────────────────────
st.markdown("---")
st.subheader("🏷️ Promotional Markdowns (Leave 0 if no promotion)")

m1, m2, m3, m4, m5 = st.columns(5)

with m1:
    markdown1 = st.number_input("Markdown 1 ($)", min_value=0.0, value=0.0, step=100.0)
with m2:
    markdown2 = st.number_input("Markdown 2 ($)", min_value=0.0, value=0.0, step=100.0)
with m3:
    markdown3 = st.number_input("Markdown 3 ($)", min_value=0.0, value=0.0, step=100.0)
with m4:
    markdown4 = st.number_input("Markdown 4 ($)", min_value=0.0, value=0.0, step=100.0)
with m5:
    markdown5 = st.number_input("Markdown 5 ($)", min_value=0.0, value=0.0, step=100.0)

# ============================================================
# PREDICTION
# ============================================================
st.markdown("---")

# Derive markdown features
has_markdown   = 1 if any([markdown1, markdown2, markdown3,
                            markdown4, markdown5]) else 0
total_markdown = markdown1 + markdown2 + markdown3 + markdown4 + markdown5

# Build input DataFrame — must match exact training feature order
input_data = pd.DataFrame([{
    "store"          : store,
    "dept"           : dept,
    "is_holiday"     : is_holiday,
    "store_type"     : store_type,
    "store_size"     : store_size,
    "temperature"    : temperature,
    "fuel_price"     : fuel_price,
    "markdown1"      : markdown1,
    "markdown2"      : markdown2,
    "markdown3"      : markdown3,
    "markdown4"      : markdown4,
    "markdown5"      : markdown5,
    "cpi"            : cpi,
    "unemployment"   : unemployment,
    "has_markdown"   : has_markdown,
    "total_markdown" : total_markdown,
    "month"          : month,
    "year"           : year,
    "week_of_year"   : week_of_year,
    "quarter"        : quarter,
    "is_quarter_end" : is_quarter_end
}])

# Predict button
if st.button("🔮 Predict Weekly Sales", use_container_width=True):

    # Select model based on user choice
    model = xgb if model_choice == "XGBoost (Recommended)" else rf

    # Make prediction
    prediction = model.predict(input_data)[0]

    # Show result
    st.markdown("---")
    st.subheader("📊 Prediction Result")

    # Large metric display
    col_result1, col_result2, col_result3 = st.columns(3)

    with col_result1:
        st.metric(
            label = "Predicted Weekly Sales",
            value = f"${prediction:,.2f}"
        )

    with col_result2:
        st.metric(
            label = "Model Used",
            value = model_choice.split(" ")[0]
        )

    with col_result3:
        st.metric(
            label = "Store Type",
            value = f"Type {'A' if store_type==0 else 'B' if store_type==1 else 'C'} — {store_size:,} sq ft"
        )

    # Context message
    avg_sales = df[
        (df["store"] == store) &
        (df["dept"]  == dept)
    ]["weekly_sales"].mean()

    if not np.isnan(avg_sales):
        diff = prediction - avg_sales
        if diff > 0:
            st.success(f"📈 This is ${diff:,.2f} ABOVE the historical average of ${avg_sales:,.2f} for Store {store} Dept {dept}")
        else:
            st.warning(f"📉 This is ${abs(diff):,.2f} BELOW the historical average of ${avg_sales:,.2f} for Store {store} Dept {dept}")

    # Show input summary
    with st.expander("📋 View Input Summary"):
        st.dataframe(input_data.T.rename(columns={0: "Value"}))

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray;'>
    Built by Dhruv Ahuja | Walmart Sales Forecasting Project |
    Models: XGBoost (R²=0.974) & Random Forest (R²=0.973)
</div>
""", unsafe_allow_html=True)