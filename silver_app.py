import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
import requests

# Page setup
st.set_page_config(page_title="Silver Price Calculator & Sales Analysis", layout="wide")

# Title
st.title("Silver Price Calculator & Silver Sales Analysis Dashboard")

# Load datasets
@st.cache_data
def load_data():
    hist_df = pd.read_csv("historical_silver_price.csv")
    hist_df['Date'] = pd.to_datetime(hist_df['Year'].astype(str) + '-' + hist_df['Month'], format='%Y-%b')
    state_df = pd.read_csv("state_wise_silver_purchased_kg.csv")
    india_gdf = gpd.read_file("india_states.geojson")
    return hist_df, state_df, india_gdf

hist_df, state_df, india_gdf = load_data()

# State name mapping
state_mapping = {
    'Orissa': 'Odisha',
    'Uttaranchal': 'Uttarakhand',
    'Jammu and Kashmir': 'Jammu & Kashmir'
}
india_gdf['NAME_1'] = india_gdf['NAME_1'].replace(state_mapping)

# Merge state data with geo data
merged_gdf = india_gdf.merge(state_df, left_on='NAME_1', right_on='State', how='left')
merged_gdf['Silver_Purchased_kg'] = merged_gdf['Silver_Purchased_kg'].fillna(0)

# Tabs for sections
tab1, tab2 = st.tabs(["Silver Price Calculator", "Silver Sales Dashboard"])

# Tab 1: Calculator
with tab1:
    st.header("Silver Price Calculator")

    col1, col2 = st.columns(2)

    with col1:
        weight_unit = st.selectbox("Weight Unit", ["grams", "kilograms"])
        weight = st.number_input(f"Weight ({weight_unit})", min_value=0.0, value=100.0)

        price_per_gram = st.number_input("Current Price per Gram (INR)", min_value=0.0, value=50.0)

        if weight_unit == "kilograms":
            total_cost = weight * 1000 * price_per_gram
        else:
            total_cost = weight * price_per_gram

        st.subheader(f"Total Cost: ₹{total_cost:,.2f}")

        # Currency conversion
        currency = st.selectbox("Convert to", ["USD", "EUR", "GBP"])
        exchange_rates = {
            "USD": 0.012,  # Approximate INR to USD
            "EUR": 0.011,
            "GBP": 0.0095
        }
        converted = total_cost * exchange_rates[currency]
        st.write(f"Equivalent in {currency}: {converted:,.2f}")

    with col2:
        st.subheader("Historical Silver Price Chart")

        # Filters
        price_filter = st.selectbox("Price Range Filter", [
            "All",
            "≤ 20,000 INR per kg",
            "20,000 - 30,000 INR per kg",
            "≥ 30,000 INR per kg"
        ])

        filtered_hist = hist_df.copy()
        if price_filter == "≤ 20,000 INR per kg":
            filtered_hist = filtered_hist[filtered_hist['Silver_Price_INR_per_kg'] <= 20000]
        elif price_filter == "20,000 - 30,000 INR per kg":
            filtered_hist = filtered_hist[(filtered_hist['Silver_Price_INR_per_kg'] > 20000) & (filtered_hist['Silver_Price_INR_per_kg'] <= 30000)]
        elif price_filter == "≥ 30,000 INR per kg":
            filtered_hist = filtered_hist[filtered_hist['Silver_Price_INR_per_kg'] >= 30000]

        fig = px.line(filtered_hist, x='Date', y='Silver_Price_INR_per_kg', title='Historical Silver Price (INR per kg)')
        st.plotly_chart(fig)

# Tab 2: Dashboard
with tab2:
    st.header("Silver Sales Dashboard")

    # Map
    st.subheader("State-wise Silver Purchases Map")
    fig_map = px.choropleth(
        merged_gdf,
        geojson=merged_gdf.__geo_interface__,
        locations='NAME_1',
        color='Silver_Purchased_kg',
        featureidkey="properties.NAME_1",
        hover_name='NAME_1',
        hover_data=['Silver_Purchased_kg'],
        color_continuous_scale="Blues",
        title="Silver Purchases by State (kg)"
    )
    fig_map.update_geos(fitbounds="locations", visible=False)
    st.plotly_chart(fig_map)

    col1, col2 = st.columns(2)

    with col1:
        # Top 5 states bar chart
        st.subheader("Top 5 States by Silver Purchases")
        top5 = state_df.nlargest(5, 'Silver_Purchased_kg')
        fig_bar = px.bar(top5, x='State', y='Silver_Purchased_kg', title='Top 5 States')
        st.plotly_chart(fig_bar)

    with col2:
        # Monthly sales - assuming January prices as "jan monthly sales"
        st.subheader("January Silver Prices Over Years")
        jan_data = hist_df[hist_df['Month'] == 'Jan']
        fig_line = px.line(jan_data, x='Year', y='Silver_Price_INR_per_kg', title='January Silver Prices (INR per kg)')
        st.plotly_chart(fig_line)

# Footer
st.markdown("---")
st.write("Dashboard created for Silver Price Analysis")