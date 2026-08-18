import pandas as pd


def recommend_products(
    customer_id,
    customer_similarity_df,
    customer_product_matrix,
    top_n=5,
    similar_customer_count=20
):
    """
    Generate product recommendations using
    customer-based collaborative filtering.
    """

    # --------------------------------------------------
    # Validate customer
    # --------------------------------------------------

    if customer_id not in customer_similarity_df.index:
        return []

    if customer_id not in customer_product_matrix.index:
        return []

    # --------------------------------------------------
    # Get customer similarity scores
    # --------------------------------------------------

    similarity_scores = (
        customer_similarity_df
        .loc[customer_id]
        .drop(customer_id, errors="ignore")
        .sort_values(ascending=False)
    )

    # Keep only customers with non-zero similarity
    similarity_scores = similarity_scores[
        similarity_scores > 0
    ]

    # Select top similar customers
    similar_customers = similarity_scores.head(
        similar_customer_count
    )

    # --------------------------------------------------
    # Get products already purchased
    # --------------------------------------------------

    customer_products = (
        customer_product_matrix.loc[customer_id]
    )

    purchased_products = set(
        customer_products[
            customer_products > 0
        ].index
    )

    # --------------------------------------------------
    # No similar customers
    # --------------------------------------------------

    if similar_customers.empty:
        return []

    # --------------------------------------------------
    # Calculate recommendation scores
    # --------------------------------------------------

    recommendation_scores = {}

    for similar_customer_id, similarity_score in (
        similar_customers.items()
    ):

        similar_customer_products = (
            customer_product_matrix
            .loc[similar_customer_id]
        )

        similar_products = (
            similar_customer_products[
                similar_customer_products > 0
            ]
        )

        for product_id, interaction in (
            similar_products.items()
        ):

            # Don't recommend products already purchased
            if product_id in purchased_products:
                continue

            recommendation_scores[product_id] = (
                recommendation_scores.get(
                    product_id,
                    0
                )
                + similarity_score * interaction
            )

    # --------------------------------------------------
    # Rank products
    # --------------------------------------------------

    recommendations = sorted(
        recommendation_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    # --------------------------------------------------
    # Return product IDs
    # --------------------------------------------------

    return [
        product_id
        for product_id, score
        in recommendations[:top_n]
    ]