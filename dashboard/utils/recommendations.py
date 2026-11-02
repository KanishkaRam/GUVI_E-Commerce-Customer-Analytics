"""Customer-based collaborative filtering with optional popularity fallback."""
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity


def recommend_products(customer_id, customer_product_matrix, top_n=5,
                       similar_customer_count=20, return_scores=False,
                       fallback=False):
    """Recommend unseen items. Scores are relative affinity, not probabilities.

    By default preserves the original list-of-product-IDs return contract.
    Set return_scores=True to obtain a DataFrame with ranking details.
    """
    matrix = customer_product_matrix
    columns = ['Product ID', 'Recommendation Score', 'Recommendation Method']
    empty = pd.DataFrame(columns=columns)
    if matrix is None or matrix.empty or top_n <= 0:
        return empty if return_scores else []
    if not matrix.index.is_unique or not matrix.columns.is_unique:
        raise ValueError('Customer and product IDs must be unique in the interaction matrix.')
    if customer_id not in matrix.index and not fallback:
        return empty if return_scores else []

    values = matrix.to_numpy(dtype=np.float64, copy=False)
    if not np.isfinite(values).all() or (values < 0).any():
        raise ValueError('Interaction matrix must contain finite nonnegative values.')
    purchased = np.zeros(values.shape[1], dtype=bool)
    scores = np.zeros(values.shape[1], dtype=float)
    method = 'Collaborative filtering'

    if customer_id in matrix.index:
        pos = matrix.index.get_loc(customer_id)
        purchased = values[pos] > 0
        sims = cosine_similarity(values[pos:pos + 1], values).ravel()
        sims[pos] = 0.0
        neighbors = np.flatnonzero(sims > 0)
        neighbors = sorted(neighbors, key=lambda i: (-sims[i], i))[:max(0, similar_customer_count)]
        if neighbors:
            scores = sims[neighbors] @ values[neighbors]
            scores[purchased] = 0.0

    if not np.any(scores > 0) and fallback:
        scores = (values > 0).sum(axis=0).astype(float)
        scores[purchased] = 0.0
        method = 'Popular products (fallback)'

    candidates = np.flatnonzero(scores > 0)
    ranked = sorted(candidates, key=lambda i: (-scores[i], str(matrix.columns[i])))[:top_n]
    result = pd.DataFrame({
        'Product ID': matrix.columns[ranked].tolist(),
        'Recommendation Score': scores[ranked].tolist(),
        'Recommendation Method': [method] * len(ranked),
    })
    return result if return_scores else result['Product ID'].tolist()
