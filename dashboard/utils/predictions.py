"""Customer-level, cutoff-safe 90-day repeat purchase scoring (v3)."""
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ARTIFACTS = Path(__file__).resolve().parents[2] / 'artifacts'
MODEL_NAME = 'repeat_purchase_90d_customer_v3.pkl'
METADATA_NAME = 'repeat_purchase_90d_customer_v3_metadata.json'


def load_repeat_purchase_v3():
    """Load trusted locally generated artifacts; joblib/pickle must not be untrusted."""
    model_path = ARTIFACTS / MODEL_NAME
    metadata_path = ARTIFACTS / METADATA_NAME
    if not model_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError(f'Place {MODEL_NAME} and {METADATA_NAME} in {ARTIFACTS}')
    with metadata_path.open(encoding='utf-8') as f:
        metadata = json.load(f)
    model = joblib.load(model_path)
    return model, metadata


def customer_snapshot(transactions: pd.DataFrame, customer_id: str, cutoff, features=None):
    """Match notebook v3: unique order IDs, strictly earlier than cutoff."""
    required = {'customer_unique_id', 'order_id', 'order_purchase_timestamp'}
    missing = required - set(transactions.columns)
    if missing:
        raise ValueError(f'Missing transaction columns: {sorted(missing)}')
    cutoff = pd.Timestamp(cutoff)
    if pd.isna(cutoff):
        raise ValueError('Invalid prediction cutoff')
    rows = transactions.loc[transactions['customer_unique_id'].eq(customer_id),
                            ['order_id', 'order_purchase_timestamp']].copy()
    rows['order_purchase_timestamp'] = pd.to_datetime(rows['order_purchase_timestamp'], errors='coerce')
    rows = rows.dropna(subset=['order_id', 'order_purchase_timestamp'])
    rows = rows.loc[rows['order_purchase_timestamp'] < cutoff]
    # An order may appear repeatedly in joined item/payment rows.
    rows = rows.sort_values('order_purchase_timestamp').drop_duplicates('order_id', keep='first')
    if rows.empty:
        return None
    dates = rows['order_purchase_timestamp']
    tenure = (cutoff - dates.min()).total_seconds() / 86400
    values = {
        'total_orders': int(rows['order_id'].nunique()),
        'recency_days': (cutoff - dates.max()).total_seconds() / 86400,
        'tenure_days': tenure,
    }
    for days in (30, 90, 180):
        values[f'orders_last_{days}d'] = int(rows.loc[dates >= cutoff - pd.Timedelta(days=days), 'order_id'].nunique())
    values['orders_per_month'] = values['total_orders'] / max(tenure / 30.44, 1)
    columns = features or list(values)
    if set(columns) != set(values):
        raise ValueError(f'Unexpected model feature schema: {columns}')
    return pd.DataFrame([values], columns=columns)


def predict_repeat_purchase_v3(transactions, customer_id, model, metadata, cutoff=None):
    cutoff = pd.Timestamp(cutoff if cutoff is not None else metadata['test_cutoff'])
    X = customer_snapshot(transactions, customer_id, cutoff, metadata['features'])
    if X is None:
        return None, None
    score = float(model.predict_proba(X)[:, 1][0])
    if not np.isfinite(score):
        raise ValueError('Model returned a nonfinite score')
    return score, X


def predict_customer_clv(customer, clv_model):
    columns = ['Total_Orders', 'Average_Basket_Size', 'Recency', 'Frequency',
               'Customer_Tenure', 'Days_Since_Last_Purchase', 'Average_Review_Rating',
               'Preferred_Payment_Method']
    X = pd.DataFrame([{key: customer[key] for key in columns}])
    return float(clv_model.predict(X)[0])
