import streamlit as st

def show():
    # Header
    st.title("🛒 Intelligent E-Commerce Customer Analytics Platform")
    st.markdown(
        """
        ### End-to-End Machine Learning & Business Intelligence Platform
        
        Transforming customer transaction data into actionable business insights using
        Machine Learning, Customer Segmentation, Predictive Analytics,
        Recommendation Systems and Explainable AI.
        """
    )
    st.divider()

    # Project Overview
    st.header("📌 Project Overview")
    st.write(
        """
        This project uses the Brazilian Olist E-Commerce Dataset to analyze customer
        purchasing behavior and provide intelligent business insights.

        The platform integrates:

        - Customer Segmentation
        - Repeat Purchase Prediction
        - Customer Lifetime Value Prediction
        - Product Recommendation System
        - Explainable AI
        - Interactive Business Dashboard
        """
    )
    st.divider()

    # Dataset Summary
    st.header("📂 Dataset Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.info(
            """
            **Dataset**
            Brazilian Olist E-Commerce Dataset
            """
        )
        st.success(
            """
            Multiple interconnected tables
            ✔ Customers
            ✔ Orders
            ✔ Order Items
            ✔ Products
            ✔ Sellers
            ✔ Payments
            ✔ Reviews
            ✔ Geolocation
            """
        )
    with col2:
        st.warning(
            """
            **Business Objective**
            Understand customer behavior,
            predict future purchases,
            estimate customer lifetime value,
            recommend products,
            and provide actionable business insights.
            """
        )
    st.divider()

    # Workflow
    st.header("⚙ Machine Learning Workflow")
    workflow = [
        "Phase 1 → Data Integration",
        "Phase 2 → Data Cleaning",
        "Phase 3 → Exploratory Data Analysis",
        "Phase 4 → Feature Engineering",
        "Phase 5 → Customer Segmentation",
        "Phase 6 → Repeat Purchase Prediction",
        "Phase 7 → Customer Lifetime Value Prediction",
        "Phase 8 → Recommendation System",
        "Phase 9 → Explainable AI",
        "Phase 10 → Streamlit Dashboard"
    ]
    for phase in workflow:
        st.markdown(f"✅ {phase}")
    st.divider()

    # Technology Stack
    st.header("🛠 Technology Stack")
    tech1, tech2, tech3 = st.columns(3)
    with tech1:
        st.subheader("Programming")
        st.write("""
        - Python
        - Pandas
        - NumPy
        """)
    with tech2:
        st.subheader("Machine Learning")
        st.write("""
        - Scikit-learn
        - LightGBM
        - CatBoost
        - XGBoost
        """)
    with tech3:
        st.subheader("Visualization")
        st.write("""
        - Plotly
        - Matplotlib
        - SHAP
        - Streamlit
        """)
    st.divider()

    # Project Highlights
    st.header("⭐ Project Highlights")
    highlight1, highlight2 = st.columns(2)

    with highlight1:
        st.success("✔ Customer Segmentation")
        st.success("✔ Purchase Prediction")
        st.success("✔ CLV Prediction")
    with highlight2:
        st.success("✔ Recommendation Engine")
        st.success("✔ Explainable AI")
        st.success("✔ Interactive Dashboard")
    st.divider()

    # Navigation
    st.header("🚀 Explore Dashboard")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info("📊 Executive Dashboard")
    with col2:
        st.info("👤 Customer Analytics")
    with col3:
        st.info("📈 Business Insights")
    col4, col5 = st.columns(2)
    with col4:
        st.info("🎯 Recommendation Engine")
    with col5:
        st.info("🤖 Explainable AI")