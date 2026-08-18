import streamlit as st

def render_sidebar():
    st.sidebar.image("https://img.icons8.com/color/96/shopping-cart.png",   width=90   )
    st.sidebar.title("🛒 Customer Analytics")
    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "📊 Executive Dashboard",
            "👤 Customer Analytics",
            "🎯 Recommendation Engine",
            "📈 Business Insights",
            "🤖 Explainable AI"
        ]
    )
    st.sidebar.markdown("---")
    st.sidebar.info(
        """
        Intelligent E-Commerce
        Customer Analytics Platform
        """
    )
    return page

