from pathlib import Path
import pandas as pd
import streamlit as st

# Project Paths
BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data" / "processed"

# Transaction Dataset
@st.cache_data(show_spinner=False)
def load_transactions():
    df = pd.read_csv(DATA_DIR / "customer_analytics_featured.csv")

    # Convert datetime columns
    datetime_columns = [
        "order_purchase_timestamp",
        "order_approved_at",
        "order_delivered_carrier_date",
        "order_delivered_customer_date",
        "order_estimated_delivery_date",
        "shipping_limit_date"
    ]
    for column in datetime_columns:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    return df

# Customer Features
@st.cache_data(show_spinner=False)
def load_customer_features():
    return pd.read_csv(DATA_DIR / "customer_features.csv")

# Cluster Profile
@st.cache_data(show_spinner=False)
def load_cluster_profile():
    return pd.read_csv(DATA_DIR / "cluster_profile.csv")

@st.cache_data
def load_customer_features():
    path = (DATA_DIR/ "customer_features.csv")
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_customer_segments():
    path = ( DATA_DIR / "customer_segments.csv")
    df = pd.read_csv(path)
    return df