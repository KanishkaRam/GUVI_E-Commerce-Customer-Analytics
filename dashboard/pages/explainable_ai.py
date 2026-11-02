"""Global explainability for the saved repeat-purchase classifier."""
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from dashboard.utils.model_loader import load_repeat_purchase_model

ARTIFACTS = Path(__file__).resolve().parents[2] / 'artifacts'

@st.cache_data
def read_importance(path: str):
    return pd.read_csv(path)

@st.cache_resource
def read_shap(path: str, names_path: str):
    return joblib.load(path), joblib.load(names_path)

def show():
    st.title('🧠 Explainable AI')
    st.write('Explore global feature importance and SHAP explanations for the legacy LightGBM repeat-purchase model (not the 90-day v3 Logistic Regression model).')
    try:
        model = load_repeat_purchase_model()
        if model is None:
            st.error('Repeat-purchase model could not be loaded.')
            return
    except Exception as exc:
        st.error(f'Could not load repeat-purchase model: {exc}')
        return
    st.success('Legacy LightGBM repeat-purchase model loaded successfully.')
    st.info('These explanations apply to the legacy LightGBM model only. They do not explain the historical 90-day customer-level v3 Logistic Regression predictions.')

    st.divider()
    st.subheader('📊 Global Feature Importance')
    st.caption('Importance ranks model features; it does not indicate whether a feature raises or lowers a prediction. The interpretation depends on the importance metric used when the CSV was created.')
    importance_path = ARTIFACTS / 'feature_importance.csv'
    if not importance_path.is_file():
        st.warning('feature_importance.csv was not found.')
    else:
        try:
            importance = read_importance(str(importance_path))
            if not {'Feature', 'Importance'}.issubset(importance.columns):
                st.error('Feature importance CSV must contain Feature and Importance columns.')
            else:
                importance = importance.copy()
                importance['Importance'] = pd.to_numeric(importance['Importance'], errors='coerce')
                importance = importance.dropna(subset=['Feature', 'Importance'])
                if importance.empty:
                    st.warning('Feature importance CSV has no valid feature scores.')
                else:
                    top = importance.nlargest(20, 'Importance').sort_values('Importance')
                    fig = px.bar(top, x='Importance', y='Feature', orientation='h', title='Top 20 Model Features')
                    fig.update_layout(height=max(450, len(top) * 28), showlegend=False)
                    st.plotly_chart(fig, width="stretch")
                    with st.expander('View complete feature importance table'):
                        st.dataframe(importance.sort_values('Importance', ascending=False), width="stretch", hide_index=True)
        except Exception as exc:
            st.error(f'Could not display feature importance: {exc}')

    st.divider()
    st.subheader('🔍 SHAP Summary Analysis')
    st.caption('SHAP summarizes how features affect model output across the saved sample. It is not a customer-specific explanation, and the output scale depends on how SHAP values were generated.')
    shap_path = ARTIFACTS / 'shap_values_sample.pkl'
    names_path = ARTIFACTS / 'shap_feature_names.pkl'
    missing = [p.name for p in (shap_path, names_path) if not p.is_file()]
    if missing:
        st.warning('Missing SHAP artifact(s): ' + ', '.join(missing))
        return
    try:
        shap_obj, names_obj = read_shap(str(shap_path), str(names_path))
        import shap
        import matplotlib.pyplot as plt
        # The notebook may save a SHAP Explanation or a plain array.
        values = np.asarray(getattr(shap_obj, 'values', shap_obj))
        data = getattr(shap_obj, 'data', None)
        names = list(names_obj)
        if values.ndim == 3:
            # For two-output classification explanations, use positive-class output.
            if values.shape[2] != 2:
                st.warning('Multi-output SHAP array detected; cannot identify the positive class safely.')
                return
            values = values[:, :, 1]
        if values.ndim != 2:
            st.error(f'Expected 2D SHAP values, received shape {values.shape}.')
            return
        if len(names) != values.shape[1]:
            st.error(f'SHAP feature count ({values.shape[1]}) does not match feature names ({len(names)}).')
            return
        if data is not None:
            data = np.asarray(data)
            if data.shape != values.shape:
                st.warning('Saved SHAP feature data has a different shape; showing mean absolute SHAP importance instead.')
                data = None
        st.write('SHAP sample size:', values.shape[0])
        st.write('SHAP feature count:', values.shape[1])
        if data is None:
            summary = pd.DataFrame({'Feature': names, 'Mean absolute SHAP': np.abs(values).mean(axis=0)})
            top = summary.nlargest(20, 'Mean absolute SHAP').sort_values('Mean absolute SHAP')
            st.plotly_chart(px.bar(top, x='Mean absolute SHAP', y='Feature', orientation='h', title='Global SHAP Magnitude'), width="stretch")
        else:
            plt.figure(figsize=(11, 7))
            shap.summary_plot(values, features=data, feature_names=names, max_display=20, show=False)
            fig = plt.gcf()
            st.pyplot(fig, clear_figure=True)
            plt.close(fig)
    except Exception as exc:
        st.error(f'Could not display SHAP explanations: {exc}')
