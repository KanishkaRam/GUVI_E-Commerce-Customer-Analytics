import pandas as pd
import streamlit as st

from dashboard.utils.data_loader import (
    load_customer_features,
    load_transactions
)

from dashboard.utils.model_loader import (
    load_customer_similarity,
    load_customer_product_matrix
)

from dashboard.utils.recommendations import (
    recommend_products
)


def show():

    st.title("🛍️ Recommendation Engine")

    st.markdown(
        """
        Discover personalized product recommendations based on
        customer similarity and collaborative filtering.
        """
    )

    # --------------------------------------------------
    # LOAD DATA
    # --------------------------------------------------

    customer_df = load_customer_features()
    transaction_df = load_transactions()

    customer_similarity_df = load_customer_similarity()
    customer_product_matrix = load_customer_product_matrix()

    # --------------------------------------------------
    # CUSTOMER VALIDATION
    # --------------------------------------------------

    if customer_df.empty:

        st.warning(
            "Customer data is not available."
        )

        return

    # --------------------------------------------------
    # CUSTOMER SELECTOR
    # --------------------------------------------------

    st.subheader("🔎 Select Customer")
    # --------------------------------------------------
    # CUSTOMERS AVAILABLE FOR RECOMMENDATIONS
    # --------------------------------------------------

    recommendation_customer_ids = (
        customer_product_matrix.index
        .dropna()
        .tolist()
    )

    recommendation_customer_ids = sorted(
        recommendation_customer_ids
    )

    if not recommendation_customer_ids:

        st.warning(
            "No customers are available in the "
            "recommendation dataset."
        )

        return

    st.caption(
        f"{len(recommendation_customer_ids):,} customers "
        "are available for personalized recommendations."
    )

    selected_customer = st.selectbox(
        "Customer ID",
        recommendation_customer_ids
    )
    st.divider()

    # --------------------------------------------------
    # GENERATE RECOMMENDATIONS
    # --------------------------------------------------

    recommendations = recommend_products(
        customer_id=selected_customer,
        customer_similarity_df=customer_similarity_df,
        customer_product_matrix=customer_product_matrix,
        top_n=5
    )

    # --------------------------------------------------
    # RECOMMENDED PRODUCTS
    # --------------------------------------------------

    st.subheader("🎯 Top 5 Recommended Products")

    if not recommendations:

        st.info(
            """
            No personalized recommendations are available
            for this customer.
            """
        )

    else:

        recommendation_df = pd.DataFrame(
            {
                "Rank": range(
                    1,
                    len(recommendations) + 1
                ),
                "Product ID": recommendations
            }
        )

        st.dataframe(
            recommendation_df,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------
    # PREVIOUSLY PURCHASED PRODUCTS
    # --------------------------------------------------

    st.divider()

    st.subheader(
        "🛒 Previously Purchased Products"
    )

    purchased_products = (
        customer_product_matrix
        .loc[selected_customer]
    )

    purchased_products = purchased_products[
        purchased_products > 0
    ].index.tolist()

    if not purchased_products:

        st.info(
            "No previously purchased products found."
        )

    else:

        purchased_df = pd.DataFrame(
            {
                "Product ID": purchased_products
            }
        )

        st.dataframe(
            purchased_df,
            use_container_width=True,
            hide_index=True
        )