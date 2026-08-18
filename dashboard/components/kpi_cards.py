import streamlit as st

def metric_card(title, value, delta=None):
    if delta is None:
        st.metric(
            label=title,
            value=value
        )
    else:
        st.metric(
            label=title,
            value=value,
            delta=delta
        )