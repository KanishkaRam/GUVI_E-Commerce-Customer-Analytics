import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import joblib

from dashboard.utils.model_loader import (
    load_repeat_purchase_model
)


def show():

    st.title("🧠 Explainable AI")

    st.markdown(
        """
        Understand why the machine learning model predicts
        repeat purchase behavior using feature importance
        and SHAP-based explanations.
        """
    )

    st.divider()

    # --------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------

    model = load_repeat_purchase_model()

    if model is None:
        st.error(
            "Repeat purchase model could not be loaded."
        )
        return

    st.success(
        "LightGBM Repeat Purchase Model loaded successfully."
    )

    # --------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------

    st.subheader("📊 Feature Importance")

    st.markdown(
        """
        Feature importance shows which features contribute most
        to the LightGBM repeat-purchase prediction model.
        """
    )

    feature_path = (
        Path(__file__).resolve()
        .parents[2]
        / "artifacts"
        / "feature_importance.csv"
    )

    if not feature_path.exists():

        st.warning(
            "Feature importance file was not found."
        )
        return

    feature_importance = pd.read_csv(
        feature_path
    )

    st.write(
        "Feature Importance Shape:",
        feature_importance.shape
    )

    # --------------------------------------------------
    # FEATURE IMPORTANCE
    # --------------------------------------------------

    st.subheader("📊 Feature Importance")

    st.markdown(
        """
        Feature importance shows which input features have the
        greatest influence on the LightGBM repeat-purchase model.
        Higher importance indicates greater contribution to the model.
        """
    )

    feature_path = (
        Path(__file__).resolve().parents[2]
        / "artifacts"
        / "feature_importance.csv"
    )

    if not feature_path.exists():

        st.warning(
            "Feature importance file was not found."
        )

    else:

        feature_importance = pd.read_csv(
            feature_path
        )

        # --------------------------------------------------
        # VALIDATE FILE
        # --------------------------------------------------

        required_columns = [
            "Feature",
            "Importance"
        ]

        if not all(
            column in feature_importance.columns
            for column in required_columns
        ):

            st.error(
                "feature_importance.csv does not contain "
                "the expected columns: Feature and Importance."
            )

            return

        # --------------------------------------------------
        # TOP FEATURES
        # --------------------------------------------------

        top_features = (
            feature_importance
            .sort_values(
                "Importance",
                ascending=False
            )
            .head(20)
            .sort_values(
                "Importance",
                ascending=True
            )
        )

        # --------------------------------------------------
        # FEATURE IMPORTANCE CHART
        # --------------------------------------------------

        fig = px.bar(
            top_features,
            x="Importance",
            y="Feature",
            orientation="h",
            title="Top 20 Features Influencing Repeat Purchase",
            text="Importance"
        )

        fig.update_traces(
            textposition="outside"
        )

        fig.update_layout(
            xaxis_title="Importance",
            yaxis_title="Feature",
            height=700,
            showlegend=False
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # --------------------------------------------------
        # RAW FEATURE IMPORTANCE TABLE
        # --------------------------------------------------

        with st.expander(
            "View Complete Feature Importance Table"
        ):

            st.dataframe(
                feature_importance,
                use_container_width=True,
                hide_index=True
            )

    # ==================================================
    # SHAP SUMMARY ANALYSIS
    # ==================================================

    st.divider()

    st.subheader("🔍 SHAP Summary Analysis")

    st.markdown(
        """
        SHAP (SHapley Additive exPlanations) shows how each feature
        influences the model's repeat-purchase prediction.

        Features at the top have the greatest overall impact on
        the model's predictions.
        """
    )

    # --------------------------------------------------
    # SHAP ARTIFACT PATHS
    # --------------------------------------------------

    artifacts_path = (
        Path(__file__).resolve().parents[2]
        / "artifacts"
    )

    shap_values_path = (
        artifacts_path /
        "shap_values_sample.pkl"
    )

    shap_features_path = (
        artifacts_path /
        "shap_feature_names.pkl"
    )

    # --------------------------------------------------
    # CHECK SHAP ARTIFACTS
    # --------------------------------------------------

    if not shap_values_path.exists():

        st.warning(
            "SHAP values artifact was not found."
        )

    elif not shap_features_path.exists():

        st.warning(
            "SHAP feature names artifact was not found."
        )

    else:

        # --------------------------------------------------
        # LOAD SHAP ARTIFACTS
        # --------------------------------------------------

        shap_values = joblib.load(
            shap_values_path
        )

        shap_feature_names = joblib.load(
            shap_features_path
        )

        st.write(
            "SHAP Sample Size:",
            shap_values.values.shape[0]
        )

        st.write(
            "SHAP Feature Count:",
            shap_values.values.shape[1]
        )

        # --------------------------------------------------
        # SHAP SUMMARY PLOT
        # --------------------------------------------------

        import shap
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(
            figsize=(12, 8)
        )

        shap.summary_plot(
            shap_values.values,
            features=shap_values.data,
            feature_names=shap_feature_names,
            max_display=20,
            show=False
        )

        plt.tight_layout()

        st.pyplot(
            fig,
            clear_figure=True
        )

        plt.close(fig)