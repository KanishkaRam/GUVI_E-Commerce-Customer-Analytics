"""Business Insights dashboard using original payment and order-item grains.

Place this file at dashboard/pages/business_insights.py.
Requires the corrected dashboard/pages/executive_dashboard.py from Step 2.
"""
import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.utils.data_loader import load_transactions
from dashboard.pages.executive_dashboard import load_financial_sources


def _bar(data, x, y, title, horizontal=False):
    if data.empty:
        st.info(f'No data available for {title}.')
        return
    fig = px.bar(data, x=x, y=y, orientation='h' if horizontal else 'v', title=title)
    fig.update_layout(margin=dict(l=20, r=25, t=55, b=30))
    st.plotly_chart(fig, use_container_width=True)


def show():
    st.title('📊 Business Insights')
    st.markdown('Explore sales, customers, categories, sellers, payments, delivery performance and reviews.')

    try:
        transactions = load_transactions().copy()
        payments, items = load_financial_sources()
    except (FileNotFoundError, ValueError) as exc:
        st.error(f'Unable to load the business data: {exc}')
        return

    if transactions.empty:
        st.warning('Transaction data is not available.')
        return

    transactions['order_purchase_timestamp'] = pd.to_datetime(
        transactions['order_purchase_timestamp'], errors='coerce'
    )
    # The transaction table is joined at item/payment grain. Build one row per order.
    orders = transactions[[
        'order_id', 'customer_unique_id', 'customer_state', 'order_purchase_timestamp'
    ]].drop_duplicates('order_id').copy()
    orders = orders.dropna(subset=['order_id'])
    order_ids = set(orders['order_id'])
    payments = payments[payments['order_id'].isin(order_ids)].copy()
    items = items[items['order_id'].isin(order_ids)].copy()

    total_revenue = payments['payment_value'].sum()
    st.subheader('📋 Business Data Overview')
    c1, c2, c3, c4 = st.columns(4)
    c1.metric('Integrated Rows', f'{len(transactions):,}')
    c2.metric('Total Customers', f"{orders['customer_unique_id'].nunique():,}")
    c3.metric('Total Orders', f"{orders['order_id'].nunique():,}")
    c4.metric('Total Revenue', f'R$ {total_revenue:,.2f}')
    st.caption('Revenue uses original payment records (including freight). Integrated rows are not unique transactions.')
    st.divider()

    st.subheader('📈 Sales Trends')
    dated_orders = orders.dropna(subset=['order_purchase_timestamp']).copy()
    dated_orders['Month'] = dated_orders['order_purchase_timestamp'].dt.to_period('M').astype(str)
    monthly_orders = dated_orders.groupby('Month', as_index=False)['order_id'].nunique()
    monthly_orders = monthly_orders.rename(columns={'order_id': 'Orders'})
    monthly_payments = payments.merge(
        dated_orders[['order_id', 'Month']], on='order_id', how='inner', validate='many_to_one'
    )
    monthly_revenue = monthly_payments.groupby('Month', as_index=False)['payment_value'].sum()
    monthly_revenue = monthly_revenue.rename(columns={'payment_value': 'Revenue'})
    if not monthly_revenue.empty:
        fig = px.line(monthly_revenue, x='Month', y='Revenue', markers=True, title='Monthly Revenue (R$)')
        st.plotly_chart(fig, use_container_width=True)
    _bar(monthly_orders, 'Month', 'Orders', 'Monthly Orders')
    st.divider()

    # Item-level prices are not payment revenue; do not allocate full payment amounts to each item.
    st.subheader('🏷️ Category Performance')
    product_categories = transactions[[
        'product_id', 'product_category_name_english'
    ]].dropna(subset=['product_id']).drop_duplicates('product_id')
    category_items = items.merge(product_categories, on='product_id', how='left', validate='many_to_one')
    category_sales = (category_items.dropna(subset=['product_category_name_english'])
        .groupby('product_category_name_english', as_index=False)['price'].sum()
        .sort_values('price', ascending=False).head(10)
        .rename(columns={'product_category_name_english': 'Category', 'price': 'Item Sales'}))
    _bar(category_sales.sort_values('Item Sales'), 'Item Sales', 'Category',
         'Top 10 Product Categories by Item Sales (R$)', horizontal=True)
    st.dataframe(category_sales, hide_index=True, use_container_width=True)
    st.divider()

    st.subheader('🏪 Seller Performance')
    seller_sales = (items.groupby('seller_id', as_index=False)
        .agg(Item_Sales=('price', 'sum'), Orders=('order_id', 'nunique'),
             Products_Sold=('product_id', 'nunique'))
        .sort_values('Item_Sales', ascending=False).head(10)
        .rename(columns={'seller_id': 'Seller ID'}))
    _bar(seller_sales.sort_values('Item_Sales'), 'Item_Sales', 'Seller ID',
         'Top 10 Sellers by Item Sales (R$)', horizontal=True)
    st.dataframe(seller_sales, hide_index=True, use_container_width=True)
    st.divider()

    st.subheader('🌎 Geographic Sales Distribution')
    state_orders = orders.dropna(subset=['customer_state'])
    state_payments = payments.merge(
        state_orders[['order_id', 'customer_state']], on='order_id', how='inner', validate='many_to_one'
    )
    state_revenue = state_payments.groupby('customer_state')['payment_value'].sum().rename('Revenue')
    state_counts = state_orders.groupby('customer_state').agg(
        Orders=('order_id', 'nunique'), Customers=('customer_unique_id', 'nunique'))
    state_sales = (state_counts.join(state_revenue, how='left').fillna({'Revenue': 0})
        .reset_index().rename(columns={'customer_state': 'State'})
        .sort_values('Revenue', ascending=False))
    _bar(state_sales.sort_values('Revenue'), 'Revenue', 'State',
         'Recorded Payment Revenue by Customer State (R$)', horizontal=True)
    st.dataframe(state_sales, hide_index=True, use_container_width=True)
    if not state_sales.empty:
        c1, c2, c3 = st.columns(3)
        c1.metric('States with Orders', f'{len(state_sales):,}')
        c2.metric('Top State', state_sales.iloc[0]['State'])
        c3.metric('Top State Revenue', f"R$ {state_sales.iloc[0]['Revenue']:,.2f}")
    st.divider()

    st.subheader('💳 Payment Method Distribution')
    payment_summary = payments.groupby('payment_type', as_index=False)['payment_value'].sum()
    if not payment_summary.empty:
        fig = px.pie(payment_summary, names='payment_type', values='payment_value',
                     hole=0.45, title='Recorded Payment Value by Method')
        st.plotly_chart(fig, use_container_width=True)
    st.divider()

    st.subheader('⭐ Review Score Analysis')
    # Original review IDs allow reviews to be counted once despite item/payment joins.
    if 'review_id' in transactions.columns:
        reviews = transactions[['review_id', 'review_score']].dropna(subset=['review_id'])
        reviews = reviews.drop_duplicates('review_id')
    else:
        st.warning('review_id not available; using one score per order as an approximation.')
        reviews = transactions[['order_id', 'review_score']].drop_duplicates('order_id')
    reviews = reviews.dropna(subset=['review_score'])
    if reviews.empty:
        st.info('No review scores are available.')
        return
    average = reviews['review_score'].mean()
    positive = reviews['review_score'].ge(4).mean() * 100
    negative = reviews['review_score'].le(2).mean() * 100
    c1, c2, c3 = st.columns(3)
    c1.metric('Average Review Score', f'{average:.2f} / 5')
    c2.metric('Positive Reviews', f'{positive:.1f}%')
    c3.metric('Negative Reviews', f'{negative:.1f}%')
    distribution = reviews['review_score'].value_counts().sort_index().rename_axis('Review Score').reset_index(name='Reviews')
    _bar(distribution, 'Review Score', 'Reviews', 'Review Score Distribution')
    if average >= 4:
        st.success('Average review score is 4 or above.')
    elif average >= 3:
        st.warning('Average review score is between 3 and 4.')
    else:
        st.error('Average review score is below 3.')
