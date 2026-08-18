import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.utils.data_loader import load_transactions


def show():
    st.title("📊 Business Insights")
    st.markdown(
        """
        Explore key business trends across sales, customers,
        product categories, payments, delivery performance,
        and customer reviews.
        """
    )

    # --------------------------------------------------
    # LOAD TRANSACTION DATA
    # --------------------------------------------------

    df = load_transactions()
    if df.empty:
        st.warning("Transaction data is not available.")
        return
    st.success(f"Loaded {len(df):,} transaction records.")

    # --------------------------------------------------
    # BASIC DATA INFORMATION
    # --------------------------------------------------
    st.subheader("📋 Business Data Overview")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(
            "Total Transactions",
            f"{len(df):,}"
        )
    with col2:
        st.metric(
            "Total Customers",
            f"{df['customer_unique_id'].nunique():,}"
        )
    with col3:
        st.metric(
            "Total Orders",
            f"{df['order_id'].nunique():,}"
        )
    with col4:
        st.metric(
            "Total Revenue",
            f"R$ {df['payment_value'].sum():,.2f}"
        )
    st.divider()

    # --------------------------------------------------
    # SALES TRENDS
    # --------------------------------------------------

    st.subheader("📈 Sales Trends")

    sales_df = df.copy()

    sales_df["order_purchase_timestamp"] = pd.to_datetime(
        sales_df["order_purchase_timestamp"],
        errors="coerce"
    )

    sales_df = sales_df.dropna(
        subset=["order_purchase_timestamp"]
    )

    # --------------------------------------------------
    # MONTHLY REVENUE
    # --------------------------------------------------

    monthly_revenue = (
        sales_df
        .groupby(
            sales_df["order_purchase_timestamp"].dt.to_period("M")
        )["payment_value"]
        .sum()
        .reset_index()
    )

    monthly_revenue["Month"] = (
        monthly_revenue["order_purchase_timestamp"]
        .astype(str)
    )

    monthly_revenue = monthly_revenue.rename(
        columns={
            "payment_value": "Revenue"
        }
    )

    revenue_fig = px.line(
        monthly_revenue,
        x="Month",
        y="Revenue",
        markers=True,
        title="Monthly Revenue"
    )

    revenue_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (R$)",
        hovermode="x unified"
    )

    st.plotly_chart(
        revenue_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # MONTHLY ORDERS
    # --------------------------------------------------

    monthly_orders = (
        sales_df
        .groupby(
            sales_df["order_purchase_timestamp"].dt.to_period("M")
        )["order_id"]
        .nunique()
        .reset_index()
    )

    monthly_orders["Month"] = (
        monthly_orders["order_purchase_timestamp"]
        .astype(str)
    )

    monthly_orders = monthly_orders.rename(
        columns={
            "order_id": "Orders"
        }
    )

    orders_fig = px.bar(
        monthly_orders,
        x="Month",
        y="Orders",
        title="Monthly Orders"
    )

    orders_fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Number of Orders",
        hovermode="x unified"
    )

    st.plotly_chart(
        orders_fig,
        use_container_width=True
    )

    st.divider()

    # --------------------------------------------------
    # CATEGORY PERFORMANCE
    # --------------------------------------------------

    st.subheader("🏷️ Category Performance")

    category_df = df.copy()

    # Remove rows without category information
    category_df = category_df.dropna(
        subset=["product_category_name_english"]
    )

    # Aggregate revenue by category
    category_revenue = (
        category_df
        .groupby("product_category_name_english")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    category_revenue = category_revenue.rename(
        columns={
            "product_category_name_english": "Category",
            "payment_value": "Revenue"
        }
    )

    # Create horizontal bar chart
    category_fig = px.bar(
        category_revenue.sort_values("Revenue"),
        x="Revenue",
        y="Category",
        orientation="h",
        title="Top 10 Product Categories by Revenue",
        text="Revenue"
    )

    category_fig.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    category_fig.update_layout(
        xaxis_title="Revenue (R$)",
        yaxis_title="Product Category",
        showlegend=False
    )

    st.plotly_chart(
        category_fig,
        use_container_width=True
    )

    st.markdown("### 📋 Category Revenue Summary")
    category_display = category_revenue.copy()
    category_display["Revenue"] = (
        category_display["Revenue"]
        .map(lambda x: f"R$ {x:,.2f}")
    )
    st.dataframe(
        category_display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    # --------------------------------------------------
    # SELLER PERFORMANCE
    # --------------------------------------------------

    st.subheader("🏪 Seller Performance")

    seller_df = df.copy()

    # Remove rows without seller information
    seller_df = seller_df.dropna(
        subset=["seller_id"]
    )

    # Aggregate seller revenue
    seller_revenue = (
        seller_df
        .groupby("seller_id")["payment_value"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    seller_revenue = seller_revenue.rename(
        columns={
            "seller_id": "Seller ID",
            "payment_value": "Revenue"
        }
    )

    # --------------------------------------------------
    # SELLER REVENUE CHART
    # --------------------------------------------------

    seller_fig = px.bar(
        seller_revenue.sort_values("Revenue"),
        x="Revenue",
        y="Seller ID",
        orientation="h",
        title="Top 10 Sellers by Revenue",
        text="Revenue"
    )

    seller_fig.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    seller_fig.update_layout(
        xaxis_title="Revenue (R$)",
        yaxis_title="Seller ID",
        showlegend=False
    )

    st.plotly_chart(
        seller_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # SELLER SUMMARY TABLE
    # --------------------------------------------------

    st.markdown("### 📋 Seller Revenue Summary")

    seller_display = seller_revenue.copy()

    seller_display["Revenue"] = (
        seller_display["Revenue"]
        .map(lambda x: f"R$ {x:,.2f}")
    )

    st.dataframe(
        seller_display,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------
    # SELLER PERFORMANCE
    # --------------------------------------------------

    st.subheader("🏪 Seller Performance")

    seller_df = df.copy()

    seller_df = seller_df.dropna(
        subset=["seller_id"]
    )

    seller_performance = (
        seller_df
        .groupby("seller_id")
        .agg(
            Revenue=("payment_value", "sum"),
            Orders=("order_id", "nunique"),
            Products_Sold=("product_id", "nunique")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    seller_performance = seller_performance.rename(
        columns={
            "seller_id": "Seller ID"
        }
    )

    seller_fig = px.bar(
    seller_performance.sort_values("Revenue"),
    x="Revenue",
    y="Seller ID",
    orientation="h",
    title="Top 10 Sellers by Revenue",
    text="Revenue",
    hover_data=[
        "Orders",
        "Products_Sold"
    ]
)

    seller_fig.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    seller_fig.update_layout(
        xaxis_title="Revenue (R$)",
        yaxis_title="Seller ID",
        showlegend=False
    )

    st.plotly_chart(
        seller_fig,
        use_container_width=True
    )

    seller_display = seller_performance.copy()

    seller_display["Revenue"] = (
        seller_display["Revenue"]
        .map(lambda x: f"R$ {x:,.2f}")
    )

    st.markdown("### 📋 Seller Performance Summary")

    st.dataframe(
        seller_display,
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    # --------------------------------------------------
    # GEOGRAPHIC SALES DISTRIBUTION
    # --------------------------------------------------

    st.subheader("🌎 Geographic Sales Distribution")

    geo_df = df.copy()

    geo_df = geo_df.dropna(
        subset=["customer_state"]
    )

    state_sales = (
        geo_df
        .groupby("customer_state")
        .agg(
            Revenue=("payment_value", "sum"),
            Orders=("order_id", "nunique"),
            Customers=("customer_unique_id", "nunique")
        )
        .sort_values(
            "Revenue",
            ascending=False
        )
        .reset_index()
    )

    state_sales = state_sales.rename(
        columns={
            "customer_state": "State"
        }
    )

    # --------------------------------------------------
    # STATE REVENUE CHART
    # --------------------------------------------------

    geo_fig = px.bar(
        state_sales.sort_values("Revenue"),
        x="Revenue",
        y="State",
        orientation="h",
        title="Revenue by Customer State",
        text="Revenue",
        hover_data=[
            "Orders",
            "Customers"
        ]
    )

    geo_fig.update_traces(
        texttemplate="R$ %{text:,.0f}",
        textposition="outside"
    )

    geo_fig.update_layout(
        xaxis_title="Revenue (R$)",
        yaxis_title="Customer State",
        showlegend=False,
        height=700
    )

    st.plotly_chart(
        geo_fig,
        use_container_width=True
    )

    st.markdown("### 📋 Geographic Sales Summary")

    geo_display = state_sales.copy()

    geo_display["Revenue"] = (
        geo_display["Revenue"]
        .map(lambda x: f"R$ {x:,.2f}")
    )

    st.dataframe(
        geo_display,
        use_container_width=True,
        hide_index=True
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "States with Sales",
            f"{state_sales['State'].nunique():,}"
        )

    with col2:
        st.metric(
            "Top State",
            state_sales.iloc[0]["State"]
        )

    with col3:
        st.metric(
            "Top State Revenue",
            f"R$ {state_sales.iloc[0]['Revenue']:,.2f}"
        )

    st.divider()
    # --------------------------------------------------
    # REVIEW SCORE ANALYSIS
    # --------------------------------------------------

    st.subheader("⭐ Review Score Analysis")

    review_df = df.copy()

    review_df = review_df.dropna(
        subset=["review_score"]
    )

    # --------------------------------------------------
    # REVIEW KPIs
    # --------------------------------------------------

    average_review = review_df["review_score"].mean()

    positive_reviews = (
        review_df["review_score"] >= 4
    ).mean() * 100

    negative_reviews = (
        review_df["review_score"] <= 2
    ).mean() * 100

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Average Review Score",
            f"{average_review:.2f} / 5"
        )

    with col2:
        st.metric(
            "Positive Reviews",
            f"{positive_reviews:.1f}%"
        )

    with col3:
        st.metric(
            "Negative Reviews",
            f"{negative_reviews:.1f}%"
        )

    # --------------------------------------------------
    # REVIEW DISTRIBUTION
    # --------------------------------------------------

    review_distribution = (
        review_df["review_score"]
        .value_counts()
        .sort_index()
        .reset_index()
    )

    review_distribution.columns = [
        "Review Score",
        "Reviews"
    ]

    review_fig = px.bar(
        review_distribution,
        x="Review Score",
        y="Reviews",
        title="Review Score Distribution",
        text="Reviews"
    )

    review_fig.update_traces(
        textposition="outside"
    )

    review_fig.update_layout(
        xaxis_title="Review Score",
        yaxis_title="Number of Reviews",
        height=500
    )

    st.plotly_chart(
        review_fig,
        use_container_width=True
    )

    # --------------------------------------------------
    # REVIEW INTERPRETATION
    # --------------------------------------------------

    if average_review >= 4:
        st.success(
            "Overall customer satisfaction is strong, "
            "with an average review score of 4 or above."
        )

    elif average_review >= 3:
        st.warning(
            "Customer satisfaction is moderate. "
            "There may be opportunities to improve the customer experience."
        )

    else:
        st.error(
            "Customer satisfaction is relatively low. "
            "Further investigation into product and delivery issues is recommended."
        )