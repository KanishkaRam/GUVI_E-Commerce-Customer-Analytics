import streamlit as st
from dashboard.utils.data_loader import load_transactions
from dashboard.components.kpi_cards import metric_card
from dashboard.utils.charts import (
    line_chart,
    bar_chart,
    pie_chart
)


def show():
    # PAGE HEADER
    st.title("📊 Executive Dashboard")
    st.markdown(
        """
        Monitor overall e-commerce performance through
        revenue, customers, orders, product categories,
        sellers, payments and customer reviews.
        """
    )
    st.divider()

    # LOAD DATA
    df = load_transactions()

    # SIDEBAR FILTERS
    st.sidebar.header("🎛️ Dashboard Filters")

    # Year Filter
    years = sorted(
        df["order_purchase_timestamp"]
        .dt.year
        .dropna()
        .unique()
    )

    selected_year = st.sidebar.selectbox(
        "Select Year",
        ["All"] + list(years)
    )

    # State Filter
    states = sorted(
        df["customer_state"]
        .dropna()
        .unique()
    )

    selected_state = st.sidebar.selectbox(
        "Select State",
        ["All"] + list(states)
    )

    # Payment Filter
    payments = sorted(
        df["payment_type"]
        .dropna()
        .unique()
    )

    selected_payment = st.sidebar.selectbox(
        "Payment Method",
        ["All"] + list(payments)
    )

    # APPLY FILTERS
    filtered_df = df.copy()
    if selected_year != "All":
        filtered_df = filtered_df[
            filtered_df[
                "order_purchase_timestamp"
            ].dt.year == selected_year
        ]
    if selected_state != "All":
        filtered_df = filtered_df[
            filtered_df["customer_state"]
            == selected_state
        ]
    if selected_payment != "All":
        filtered_df = filtered_df[
            filtered_df["payment_type"]
            == selected_payment
        ]

    # Empty Dataset Protection
    if filtered_df.empty:
        st.warning("No data available for the selected filters.")
        return

    # ORDER-LEVEL DATA
    order_level = (
        filtered_df[
            [
                "order_id",
                "customer_unique_id",
                "order_purchase_timestamp",
                "payment_value"
            ]
        ]
        .drop_duplicates(
            subset=["order_id"]
        )
        .copy()
    )

    # KPI CALCULATIONS
    total_revenue = (
        order_level["payment_value"]
        .sum()
    )

    total_orders = (
        order_level["order_id"]
        .nunique()
    )

    total_customers = (
        order_level["customer_unique_id"]
        .nunique()
    )

    average_order_value = (
        total_revenue / total_orders
        if total_orders > 0
        else 0
    )

    # KPI CARDS
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        metric_card(
            "💰 Total Revenue",
            f"R$ {total_revenue:,.2f}"
        )

    with col2:
        metric_card(
            "🛒 Total Orders",
            f"{total_orders:,}"
        )

    with col3:
        metric_card(
            "👥 Total Customers",
            f"{total_customers:,}"
        )

    with col4:
        metric_card(
            "📦 Average Order Value",
            f"R$ {average_order_value:,.2f}"
        )
    st.divider()

    # MONTHLY REVENUE
    revenue = (
        order_level
        .groupby(
            order_level[
                "order_purchase_timestamp"
            ].dt.to_period("M")
        )["payment_value"]
        .sum()
        .reset_index()
    )

    revenue[
        "order_purchase_timestamp"
    ] = revenue[
        "order_purchase_timestamp"
    ].astype(str)

    revenue_fig = line_chart(
        revenue,
        "order_purchase_timestamp",
        "payment_value",
        "Monthly Revenue Trend"
    )

    # MONTHLY ORDERS
    orders = (
        order_level
        .groupby(
            order_level[
                "order_purchase_timestamp"
            ].dt.to_period("M")
        )["order_id"]
        .nunique()
        .reset_index()
    )

    orders[
        "order_purchase_timestamp"
    ] = orders[
        "order_purchase_timestamp"
    ].astype(str)

    orders_fig = line_chart(
        orders,
        "order_purchase_timestamp",
        "order_id",
        "Monthly Orders Trend"
    )

    # DISPLAY TREND CHARTS
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            revenue_fig,
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            orders_fig,
            use_container_width=True
        )

    st.divider()

    # TOP PRODUCT CATEGORIES
    category = (
        filtered_df
        .dropna(
            subset=[
                "product_category_name_english"
            ]
        )
        .groupby(
            "product_category_name_english"
        )["price"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    category_fig = bar_chart(
        category,
        "product_category_name_english",
        "price",
        "Top 10 Product Categories"
    )

    # TOP SELLERS
    seller = (
        filtered_df
        .groupby(
            "seller_id"
        )["price"]
        .sum()
        .sort_values(
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    seller_fig = bar_chart(
        seller,
        "seller_id",
        "price",
        "Top 10 Sellers by Sales"
    )

    # DISPLAY CATEGORY & SELLER
    col1, col2 = st.columns(2)

    with col1:

        st.plotly_chart(
            category_fig,
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            seller_fig,
            use_container_width=True
        )
    st.divider()

    # PAYMENT DISTRIBUTION
    payment = (
        filtered_df
        .dropna(
            subset=["payment_type"]
        )
        .groupby(
            "payment_type"
        )["payment_value"]
        .sum()
        .reset_index()
    )

    payment_fig = pie_chart(
        payment,
        "payment_type",
        "payment_value",
        "Payment Method Distribution"
    )

    # REVIEW DISTRIBUTION
    review = (
        filtered_df[
            "review_score"
        ]
        .dropna()
        .value_counts()
        .sort_index()
        .reset_index()
    )

    review.columns = [
        "review_score",
        "count"
    ]

    review_fig = bar_chart(
        review,
        "review_score",
        "count",
        "Customer Review Score Distribution"
    )

    # DISPLAY PAYMENT & REVIEW
    col1, col2 = st.columns(2)
    with col1:
        st.plotly_chart(
            payment_fig,
            use_container_width=True
        )

    with col2:
        st.plotly_chart(
            review_fig,
            use_container_width=True
        )

    # FOOTNOTE
    st.caption(
        "Use the filters in the sidebar to dynamically "
        "explore business performance."
    )