from pathlib import Path
import joblib
import streamlit as st

# PROJECT PATH
BASE_DIR = Path(__file__).resolve().parents[2]
ARTIFACT_DIR = BASE_DIR / "artifacts"

# LIGHTGBM REPEAT PURCHASE MODEL
@st.cache_resource(show_spinner=False)
def load_repeat_purchase_model():
    model_path = (ARTIFACT_DIR/ "lightgbm_repeat_purchase_model.pkl")
    return joblib.load(model_path)

# LIGHTGBM PREPROCESSOR
@st.cache_resource(show_spinner=False)
def load_repeat_purchase_preprocessor():
    preprocessor_path = (ARTIFACT_DIR/ "preprocessor.pkl")
    return joblib.load(preprocessor_path)

# CATBOOST CLV MODEL
@st.cache_resource(show_spinner=False)
def load_clv_model():
    model_path = (ARTIFACT_DIR/ "catboost_clv_model.pkl")
    return joblib.load(model_path)

@st.cache_resource
def load_customer_similarity():
    return joblib.load(ARTIFACT_DIR / "customer_similarity.pkl")

@st.cache_resource
def load_customer_product_matrix():
    return joblib.load(ARTIFACT_DIR / "customer_product_matrix.pkl")
