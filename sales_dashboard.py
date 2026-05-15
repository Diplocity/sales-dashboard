import streamlit as st
import pandas as pd
from io import BytesIO
import matplotlib.pyplot as plt

# -------------------------
# LOGIN CREDENTIALS (demo only)
# -------------------------
USERNAME = "admin"
PASSWORD = "1234"

# -------------------------
# SESSION STATE
# -------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# -------------------------
# LOAD DATA
# -------------------------
def load_data():
    df = pd.read_csv("data/eCommercePK.csv")
    df = df.drop_duplicates()
    df = df.dropna()
    df["Revenue"] = df["quantity"] * df["sales"]
    return df

# -------------------------
# SAFE BUSINESS SUMMARY
# -------------------------
def generate_summary(df):

    # 🚨 Handle empty data safely
    if df.empty:
        return "⚠️ No data available for selected filters. Please adjust filters."

    total_revenue = df["Revenue"].sum()
    total_orders = df["order_id"].nunique()
    avg_order = df["Revenue"].mean()

    top_product_series = df.groupby("sku")["Revenue"].sum()
    top_city_series = df.groupby("city")["Revenue"].sum()

    top_product = top_product_series.idxmax() if not top_product_series.empty else "N/A"
    top_city = top_city_series.idxmax() if not top_city_series.empty else "N/A"

    return f"""
📊 BUSINESS REPORT

Total Revenue: {total_revenue:,.0f}
Total Orders: {total_orders}
Average Order Value: {avg_order:,.2f}

Top Product: {top_product}
Top City: {top_city}

Insight:
Sales are mainly driven by {top_product}.
Top performing region is {top_city}.
Focus marketing on high-performing segments for better ROI.
"""

# -------------------------
# EXPORT EXCEL
# -------------------------
def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Report")
    return output.getvalue()

# -------------------------
# BAR CHART
# -------------------------
def create_bar_chart(data, title, xlabel, ylabel):
    fig, ax = plt.subplots()
    data.plot(kind="bar", ax=ax)
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    plt.xticks(rotation=45)
    return fig

# -------------------------
# LOGIN PAGE
# -------------------------
def login():
    st.title("🔐 Login Required")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username == USERNAME and password == PASSWORD:
            st.session_state.logged_in = True
            st.success("Login successful!")
            st.rerun()
        else:
            st.error("Invalid credentials")

# -------------------------
# DASHBOARD
# -------------------------
def dashboard():

    # Logout
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

    df = load_data()

    st.title("📊 Sales Intelligence Dashboard")
    st.markdown("Automated SaaS-style analytics system")

    # -------------------------
    # FILTERS
    # -------------------------
    st.sidebar.header("Filters")

    category_filter = st.sidebar.multiselect(
        "Category",
        df["category"].unique(),
        default=df["category"].unique()
    )

    city_filter = st.sidebar.multiselect(
        "City",
        df["city"].unique(),
        default=df["city"].unique()
    )

    filtered_df = df[
        (df["category"].isin(category_filter)) &
        (df["city"].isin(city_filter))
    ]

    # -------------------------
    # EMPTY DATA GUARD (IMPORTANT FIX)
    # -------------------------
    if filtered_df.empty:
        st.warning("⚠️ No data found for selected filters. Try different options.")
        st.stop()

    # -------------------------
    # KPI METRICS
    # -------------------------
    total_revenue = filtered_df["Revenue"].sum()
    total_orders = filtered_df["order_id"].nunique()
    avg_order = filtered_df["Revenue"].mean()

    col1, col2, col3 = st.columns(3)

    col1.metric("💰 Revenue", f"{total_revenue:,.0f}")
    col2.metric("📦 Orders", total_orders)
    col3.metric("📊 Avg Order", f"{avg_order:,.2f}")

    # -------------------------
    # WRITTEN REPORT
    # -------------------------
    st.subheader("🧾 Business Report")
    st.text(generate_summary(filtered_df))

    # -------------------------
    # CHARTS
    # -------------------------
    st.subheader("📊 Top Products")
    top_products = filtered_df.groupby("sku")["Revenue"].sum()
    st.pyplot(create_bar_chart(top_products, "Top Products", "SKU", "Revenue"))

    st.subheader("🌍 City Sales")
    st.bar_chart(filtered_df.groupby("city")["Revenue"].sum())

    st.subheader("📂 Category Sales")
    st.bar_chart(filtered_df.groupby("category")["Revenue"].sum())

    # -------------------------
    # RAW DATA
    # -------------------------
    st.subheader("Raw Data")
    st.dataframe(filtered_df)

    # -------------------------
    # DOWNLOAD REPORT
    # -------------------------
    excel_data = to_excel(filtered_df)

    st.download_button(
        label="📥 Download Report (Excel)",
        data=excel_data,
        file_name="sales_report.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

# -------------------------
# APP ROUTER
# -------------------------
if not st.session_state.logged_in:
    login()
else:
    dashboard()