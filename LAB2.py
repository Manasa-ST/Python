import streamlit as st
import pandas as pd


# Page setup
st.set_page_config(page_title="Shopping Behaviour Analysis", layout="wide")


# Title and description
st.title("Shopping Behaviour Analysis Dashboard")
st.write(
   "This dashboard helps understand customer shopping behaviour "
   "using interactive filters and visual graphs."
)


# Load dataset
df = pd.read_csv("shopping_behavior_updated.csv")


# Convert USD to INR
df["Purchase Amount INR"] = df["Purchase Amount (USD)"] * 83
purchase_col = "Purchase Amount INR"


# ---------------- Sidebar Filters ----------------
with st.sidebar:
   st.header("Filter Options")


   gender = st.radio("Gender", df["Gender"].unique())


   category = st.selectbox("Category", df["Category"].unique())


   payment = st.selectbox("Payment Method", df["Payment Method"].unique())


   age_range = st.slider(
       "Age Range",
       int(df["Age"].min()),
       int(df["Age"].max()),
       (20, 60)
   )


# Apply filters
filtered_df = df[
   (df["Gender"] == gender) &
   (df["Category"] == category) &
   (df["Payment Method"] == payment) &
   (df["Age"].between(age_range[0], age_range[1]))
]


# ---------------- KPIs ----------------
st.subheader("Key Performance Indicators")


k1, k2, k3, k4, k5 = st.columns(5)


k1.metric(
   "Total Purchase (INR)",
   round(filtered_df[purchase_col].sum(), 2)
)


k2.metric(
   "Average Purchase (INR)",
   round(filtered_df[purchase_col].mean(), 2)
)


k3.metric(
   "Total Purchases",
   len(filtered_df)
)


gender_counts = filtered_df["Gender"].value_counts().to_dict()


k4.metric("Male Purchases", gender_counts.get("Male", 0))
k5.metric("Female Purchases", gender_counts.get("Female", 0))


# ---------------- Data Preview ----------------
st.subheader("Filtered Data Preview")
st.dataframe(
   filtered_df[["Age", "Gender", "Category", "Payment Method", purchase_col]].head(10)
)


# ---------------- Graph Tabs ----------------
tab1, tab2, tab3 = st.tabs(
   ["Category Graph", "Age Trend", "Age vs Purchase"]
)


# Bar chart
with tab1:
   st.subheader("Purchase Count by Category")
   category_data = df["Category"].value_counts()
   st.bar_chart(category_data)


# Line chart
with tab2:
   st.subheader("Average Purchase by Age")
   age_data = filtered_df.groupby("Age")[purchase_col].mean()
   st.line_chart(age_data)


# Scatter chart
with tab3:
   st.subheader("Age vs Purchase Amount")
   scatter_data = filtered_df[["Age", purchase_col]].dropna().head(300)
   st.scatter_chart(scatter_data, x="Age", y=purchase_col)


# ---------------- Explanation ----------------
with st.expander("What I implemented"):
   st.write("""
   - Designed an interactive Streamlit dashboard.
   - Added sidebar filters for gender, category, age range, and payment method.
   - Converted purchase values from USD to INR.
   - Displayed KPIs including total, average, and gender-based purchase counts.
   - Used tabs for navigating between bar, line, and scatter charts.
   - Used columns, sidebar, and expander for clean layout and readability.
   - Enabled visual exploration of customer shopping behaviour.
   """)