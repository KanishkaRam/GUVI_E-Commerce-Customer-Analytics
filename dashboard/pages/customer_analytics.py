import pandas as pd
import streamlit as st
from dashboard.utils.data_loader import (
    load_customer_features,
    load_customer_segments,
    load_transactions
)
from dashboard.utils.predictions import (
    predict_repeat_purchase,
    predict_customer_clv
)
from dashboard.utils.model_loader import (
    load_repeat_purchase_model,
    load_repeat_purchase_preprocessor,
    load_clv_model
)

def show():

    st.title("👤 Customer Analytics")
    st.markdown(
        """
        Analyze individual customer behavior, purchasing patterns,
        repeat-purchase probability, and predicted customer lifetime value.
        """
    )
    # Load customer features
    customer_df = load_customer_features()

    # Load customer segmentation
    segments_df = load_customer_segments()

    transaction_df = load_transactions()

    if customer_df.empty:
        st.warning("Customer data is not available.")
        return
    
    # Merge segmentation
    customer_df = customer_df.merge(
        segments_df[
            [
                "customer_unique_id",
                "Cluster",
                "Customer_Segment"
            ]
        ],
        on="customer_unique_id",
        how="left"
    )

    repeat_model = load_repeat_purchase_model()
    repeat_preprocessor = load_repeat_purchase_preprocessor()
    clv_model = load_clv_model()

    # --------------------------------------------------
    # CUSTOMER SELECTOR
    # --------------------------------------------------

    st.subheader("🔎 Select Customer")
    customer_ids = (
        customer_df["customer_unique_id"]
        .dropna()
        .sort_values()
        .tolist()
    )
    selected_customer = st.selectbox(
        "Customer ID",
        customer_ids
    )

    # --------------------------------------------------
    # GET SELECTED CUSTOMER
    # --------------------------------------------------

    customer = customer_df[
        customer_df["customer_unique_id"]
        == selected_customer
    ].iloc[0]

    customer_transactions = transaction_df[
    transaction_df["customer_unique_id"]
    == selected_customer
    ].copy()

    # --------------------------------------------------
    # CUSTOMER PROFILE
    # --------------------------------------------------
    st.divider()
    st.subheader("👤 Customer Profile")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Orders",f"{customer['Total_Orders']:,.0f}")
    with col2:
        st.metric("Total Spending",f"R$ {customer['Total_Spending']:,.2f}" )
    with col3:
        st.metric("Average Order Value",f"R$ {customer['Average_Order_Value']:,.2f}")
    with col4:
        st.metric("Average Basket Size",f"{customer['Average_Basket_Size']:,.2f}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Recency", f"{customer['Recency']:,.0f} days")
    with col2:
        st.metric("Frequency",f"{customer['Frequency']:,.0f}" )
    with col3:
        st.metric("Monetary",f"R$ {customer['Monetary']:,.2f}")
    with col4:
        st.metric("Customer Tenure",f"{customer['Customer_Tenure']:,.0f} days")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Average Review Rating",f"{customer['Average_Review_Rating']:.2f} / 5")
    with col2:
        st.metric("Preferred Payment Method",str(customer["Preferred_Payment_Method"]).replace("_", " ").title())

    drop_columns = [
    "customer_id",
    "customer_unique_id",
    "order_id",
    "review_id",
    "product_id",
    "seller_id",

    "review_comment_title",
    "review_comment_message",

    "order_purchase_timestamp",
    "order_approved_at",
    "order_delivered_customer_date",
    "order_delivered_carrier_date",
    "order_estimated_delivery_date",
    "shipping_limit_date",
    "review_creation_date",
    "review_answer_timestamp",

    "Next_Purchase_Date",
    "Days_To_Next_Purchase",
    "Repeat_Purchase"
    ]
    X_customer = customer_transactions.drop(columns=drop_columns,errors="ignore")
    if len(X_customer) > 0:
        repeat_probability = predict_repeat_purchase(
            X_customer,
            repeat_model,
            repeat_preprocessor
        )
    else:
        repeat_probability = None

    st.subheader("🎯 Customer Segment")

    segment = customer["Customer_Segment"]
    if pd.isna(segment):
         st.warning("Customer segment unavailable.")
    else:
        st.info(f"Segment: **{segment}**" )
        
    st.divider()

    # --------------------------------------------------
    # Repeat Purchase 
    # --------------------------------------------------

    st.subheader("🔮 Repeat Purchase Prediction")
    if repeat_probability is not None:
        col1, col2 = st.columns(2)
        with col1: st.metric("Repeat Purchase Probability",f"{repeat_probability:.2%}")
        with col2:
            if repeat_probability >= 0.70:
                status = "High likelihood"
            elif repeat_probability >= 0.40:
                status = "Medium likelihood"
            else:
                status = "Low likelihood"
            st.metric("Purchase Likelihood",status)
    else:
        st.warning("No transaction data available for this customer." )

    # --------------------------------------------------
    # CUSTOMER LIFETIME VALUE
    # --------------------------------------------------
    predicted_clv = predict_customer_clv(customer, clv_model)
    st.divider()
    st.subheader("💰 Customer Lifetime Value")
    st.metric("Predicted Customer Lifetime Value",f"R$ {predicted_clv:,.2f}")


    # --------------------------------------------------
    # CUSTOMER PURCHASE HISTORY
    # --------------------------------------------------
    st.divider()
    st.subheader("🛒 Customer Purchase History")
    purchase_history = transaction_df[transaction_df["customer_unique_id"] == selected_customer].copy()
    if purchase_history.empty:
        st.info("No purchase history available for this customer.")
    else:
        # --------------------------------------------------
        # PURCHASE HISTORY SUMMARY
        # --------------------------------------------------

        history_col1, history_col2, history_col3 = st.columns(3)
        with history_col1:
            st.metric("Orders",f"{purchase_history['order_id'].nunique():,}" )

        with history_col2:
            st.metric("Products Purchased", f"{purchase_history['product_id'].nunique():,}" )

        with history_col3:
            st.metric("Purchase Records",f"{len(purchase_history):,}" )

    st.markdown("### Order Details")

    # --------------------------------------------------
    # SELECT DISPLAY COLUMNS
    # --------------------------------------------------
    history_columns = [
        "order_id",
        "order_purchase_timestamp",
        "product_category_name_english",
        "price",
        "freight_value",
        "payment_type",
        "review_score",
        "delivery_days",
        "On_Time"
    ]

    available_columns = [
        column
        for column in history_columns
        if column in purchase_history.columns
    ]

    history_display = purchase_history[
        available_columns
    ].copy()

    # --------------------------------------------------
    # FORMAT PURCHASE DATE
    # --------------------------------------------------

    if "order_purchase_timestamp" in history_display.columns:

        history_display[
            "order_purchase_timestamp"
        ] = pd.to_datetime(
            history_display[
                "order_purchase_timestamp"
            ],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # --------------------------------------------------
    # FORMAT CURRENCY
    # --------------------------------------------------

    if "price" in history_display.columns:

        history_display["price"] = (
            history_display["price"]
            .map(
                lambda x:
                f"R$ {x:,.2f}"
                if pd.notna(x)
                else "-"
            )
        )

    if "freight_value" in history_display.columns:

        history_display["freight_value"] = (
            history_display["freight_value"]
            .map(
                lambda x:
                f"R$ {x:,.2f}"
                if pd.notna(x)
                else "-"
            )
        )

    # --------------------------------------------------
    # RENAME COLUMNS
    # --------------------------------------------------

    history_display = history_display.rename(
        columns={
            "order_id": "Order ID",
            "order_purchase_timestamp": "Purchase Date",
            "product_category_name_english": "Product Category",
            "price": "Price",
            "freight_value": "Freight",
            "payment_type": "Payment Method",
            "review_score": "Review Score",
            "delivery_days": "Delivery Days",
            "On_Time": "On Time"
        }
    )

    # --------------------------------------------------
    # DISPLAY TABLE
    # --------------------------------------------------

    st.dataframe(
        history_display,
        use_container_width=True,
        hide_index=True
    )