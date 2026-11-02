"""Streamlit recommendation dashboard."""
import pandas as pd
import streamlit as st

from dashboard.utils.data_loader import load_customer_features, load_transactions
from dashboard.utils.model_loader import load_customer_product_matrix
from dashboard.utils.recommendations import recommend_products


def show():
    st.title('🛍️ Recommendation Engine')
    st.markdown('Discover personalized product recommendations based on customer similarity and collaborative filtering.')
    customer_df = load_customer_features()
    transaction_df = load_transactions()
    matrix = load_customer_product_matrix()
    if customer_df is None or customer_df.empty:
        st.warning('Customer data is not available.')
        return
    if matrix is None or matrix.empty:
        st.warning('Customer-product interaction matrix is not available.')
        return
    ids = sorted(matrix.index.dropna().tolist())
    if not ids:
        st.warning('No customers are available in the recommendation dataset.')
        return

    st.subheader('🔎 Select Customer')
    st.caption(f'{len(ids):,} customers are available for recommendations.')
    selected = st.selectbox('Customer ID', ids)
    use_fallback = st.checkbox('Show popular products if personalized recommendations are unavailable', value=True)
    result = recommend_products(selected, matrix, top_n=5, return_scores=True, fallback=use_fallback)

    st.divider()
    st.subheader('🎯 Top Recommended Products')
    if result.empty:
        st.info('No recommendations are available for this customer.')
    else:
        # Category metadata is descriptive, not used to compute the collaborative scores.
        if transaction_df is not None and not transaction_df.empty and {'product_id', 'product_category_name_english'}.issubset(transaction_df.columns):
            lookup = (transaction_df[['product_id', 'product_category_name_english']]
                      .dropna(subset=['product_id']).drop_duplicates(subset=['product_id']))
            lookup = lookup.rename(columns={'product_id': 'Product ID', 'product_category_name_english': 'Category'})
            result = result.merge(lookup, on='Product ID', how='left', validate='many_to_one')
            result['Category'] = result['Category'].fillna('Unknown')
        result.insert(0, 'Rank', range(1, len(result) + 1))
        st.dataframe(result, width='stretch', hide_index=True)
        st.caption('Scores are relative similarity-weighted affinities, not purchase probabilities. Popular-product fallback is not personalized.')

    st.divider()
    st.subheader('🛒 Previously Purchased Products')
    purchased = matrix.loc[selected]
    purchased_ids = purchased[purchased > 0].index.tolist()
    if not purchased_ids:
        st.info('No previously purchased products found.')
    else:
        st.dataframe(pd.DataFrame({'Product ID': purchased_ids}), width='stretch', hide_index=True)
