from pathlib import Path
import pandas as pd
import streamlit as st
from dashboard.utils.data_loader import load_transactions
from dashboard.components.kpi_cards import metric_card
from dashboard.utils.charts import line_chart, bar_chart, pie_chart

BASE_DIR = Path(__file__).resolve().parents[2]
RAW_DIR = BASE_DIR / 'data' / 'raw'

@st.cache_data(show_spinner=False)
def load_financial_sources():
    payments = pd.read_csv(RAW_DIR / 'olist_order_payments_dataset.csv')
    items = pd.read_csv(RAW_DIR / 'olist_order_items_dataset.csv')
    # The source keys should identify individual payments and line items.
    if payments.duplicated(['order_id', 'payment_sequential']).any():
        raise ValueError('Duplicate payment keys in raw payment dataset')
    if items.duplicated(['order_id', 'order_item_id']).any():
        raise ValueError('Duplicate item keys in raw order item dataset')
    return payments, items


def show():
    st.title('📊 Executive Dashboard')
    st.markdown('Monitor revenue, customers, orders, categories, sellers, payments and reviews.')
    st.divider()

    df = load_transactions()
    payments, items = load_financial_sources()
    df = df.copy()
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'], errors='coerce')

    st.sidebar.header('🎛️ Dashboard Filters')
    years = sorted(df['order_purchase_timestamp'].dt.year.dropna().astype(int).unique().tolist())
    states = sorted(df['customer_state'].dropna().unique().tolist())
    methods = sorted(payments['payment_type'].dropna().unique().tolist())
    year = st.sidebar.selectbox('Select Year', ['All'] + years)
    state = st.sidebar.selectbox('Select State', ['All'] + states)
    method = st.sidebar.selectbox('Payment Method', ['All'] + methods)

    # Use only unique order identifiers for filter membership.
    orders = df[['order_id', 'customer_unique_id', 'customer_state', 'order_purchase_timestamp']].drop_duplicates('order_id')
    if year != 'All':
        orders = orders[orders['order_purchase_timestamp'].dt.year == year]
    if state != 'All':
        orders = orders[orders['customer_state'] == state]
    if method != 'All':
        method_orders = payments.loc[payments['payment_type'] == method, 'order_id']
        orders = orders[orders['order_id'].isin(method_orders)]
    if orders.empty:
        st.warning('No data available for the selected filters.')
        return

    order_ids = set(orders['order_id'])
    selected_payments = payments[payments['order_id'].isin(order_ids)].copy()
    if method != 'All':
        selected_payments = selected_payments[selected_payments['payment_type'] == method]
    selected_items = items[items['order_id'].isin(order_ids)].copy()

    revenue = selected_payments['payment_value'].sum()
    total_orders = orders['order_id'].nunique()
    customers = orders['customer_unique_id'].nunique()
    aov = revenue / total_orders if total_orders else 0

    cols = st.columns(4)
    for col, label, value in zip(cols,
        ['💰 Total Revenue', '🛒 Total Orders', '👥 Total Customers', '📦 Average Order Value'],
        [f'R$ {revenue:,.2f}', f'{total_orders:,}', f'{customers:,}', f'R$ {aov:,.2f}']):
        with col:
            metric_card(label, value)
    st.divider()

    # Aggregate payments once per original payment row, then attach order month.
    monthly_payments = selected_payments.merge(orders[['order_id', 'order_purchase_timestamp']], on='order_id', how='left', validate='many_to_one')
    monthly_payments['month'] = monthly_payments['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_revenue = monthly_payments.groupby('month', as_index=False)['payment_value'].sum()
    monthly_orders = orders.assign(month=orders['order_purchase_timestamp'].dt.to_period('M').astype(str)).groupby('month', as_index=False)['order_id'].nunique()
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(line_chart(monthly_revenue, 'month', 'payment_value', 'Monthly Revenue Trend'), use_container_width=True)
    with c2:
        st.plotly_chart(line_chart(monthly_orders, 'month', 'order_id', 'Monthly Orders Trend'), use_container_width=True)
    st.divider()

    # Product metadata comes from the joined dataset; actual sales come from raw items.
    product_categories = df[['product_id', 'product_category_name_english']].dropna(subset=['product_id']).drop_duplicates('product_id')
    category_items = selected_items.merge(product_categories, on='product_id', how='left', validate='many_to_one')
    category = (category_items.dropna(subset=['product_category_name_english'])
        .groupby('product_category_name_english', as_index=False)['price'].sum()
        .sort_values('price', ascending=False).head(10))
    seller = (selected_items.groupby('seller_id', as_index=False)['price'].sum()
        .sort_values('price', ascending=False).head(10))
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(bar_chart(category, 'product_category_name_english', 'price', 'Top 10 Product Categories by Item Sales'), use_container_width=True)
    with c2:
        st.plotly_chart(bar_chart(seller, 'seller_id', 'price', 'Top 10 Sellers by Item Sales'), use_container_width=True)
    st.divider()

    payment_summary = selected_payments.groupby('payment_type', as_index=False)['payment_value'].sum()
    # Deduplicate review IDs, not order IDs: an order may legitimately have more than one review.
    reviews = (df.loc[df['order_id'].isin(order_ids), ['review_id', 'review_score']]
        .dropna(subset=['review_id']).drop_duplicates('review_id'))
    review_summary = reviews['review_score'].dropna().value_counts().sort_index().rename_axis('review_score').reset_index(name='count')
    c1, c2 = st.columns(2)
    with c1:
        st.plotly_chart(pie_chart(payment_summary, 'payment_type', 'payment_value', 'Payment Method Distribution'), use_container_width=True)
    with c2:
        st.plotly_chart(bar_chart(review_summary, 'review_score', 'count', 'Customer Review Score Distribution'), use_container_width=True)
    st.caption('Revenue is based on recorded payments, including freight. Category and seller sales use item prices excluding freight. A payment-method filter shows only payments made by that method.')
