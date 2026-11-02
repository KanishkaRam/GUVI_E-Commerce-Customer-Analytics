import streamlit as st
from pathlib import Path
from dashboard.utils.config import (
    APP_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE
)
from dashboard.components.sidebar import render_sidebar
from dashboard.components.footer import render_footer
from dashboard.pages import (
    home,
    executive_dashboard,
    customer_analytics,
    recommendation,
    business_insights,
    explainable_ai
)


# --------------------------------------------------
# Streamlit Page Configuration
# --------------------------------------------------
st.set_page_config(
    page_title=APP_TITLE,
    
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)


st.markdown("""
<style>
/* Sidebar selectbox background */
section[data-testid="stSidebar"]
[data-testid="stSelectbox"]
div[data-baseweb="select"] > div {
    background-color: #FFFFFF !important;
    border-radius: 8px !important;
}

/* Selected text in sidebar selectboxes */
section[data-testid="stSidebar"]
[data-testid="stSelectbox"]
div[data-baseweb="select"] * {
    color: #1E293B !important;
    -webkit-text-fill-color: #1E293B !important;
}

/* Dropdown options */
div[data-baseweb="popover"]
[role="option"] {
    color: #1E293B !important;
}

/* Dropdown option hover */
div[data-baseweb="popover"]
[role="option"]:hover {
    background-color: #DBEAFE !important;
    color: #0F172A !important;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# Load Global CSS
# --------------------------------------------------
css_path = Path("dashboard/assets/styles.css")
if css_path.exists():
    with open(css_path) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# --------------------------------------------------
# Sidebar Navigation
# --------------------------------------------------
selected_page = render_sidebar()

# --------------------------------------------------
# Page Routing
# --------------------------------------------------
if selected_page == "🏠 Home":
    home.show()
elif selected_page == "📊 Executive Dashboard":
    executive_dashboard.show()
elif selected_page == "👤 Customer Analytics":
    customer_analytics.show()
elif selected_page == "🎯 Recommendation Engine":
    recommendation.show()
elif selected_page == "📈 Business Insights":
    business_insights.show()
elif selected_page == "🤖 Explainable AI":
    explainable_ai.show()

# --------------------------------------------------
# Footer
# --------------------------------------------------
render_footer()