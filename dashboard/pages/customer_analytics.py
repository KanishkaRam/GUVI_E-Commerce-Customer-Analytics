import pandas as pd
import streamlit as st
from dashboard.utils.data_loader import (
    load_customer_features,
    load_customer_segments,
    load_transactions
)
from dashboard.utils.predictions import (
    load_repeat_purchase_v3,
    predict_repeat_purchase_v3,
    predict_customer_clv
)
from dashboard.utils.model_loader import (
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
    
    # Ensure each customer has one feature row and one segment row.
    if customer_df["customer_unique_id"].duplicated().any():
        st.error("Duplicate customer IDs found in customer_features.csv. Check feature aggregation.")
        return
    if segments_df["customer_unique_id"].duplicated().any():
        st.error("Duplicate customer IDs found in customer_segments.csv. Check segmentation output.")
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
        how="left",
        validate="one_to_one"
    )

    # Load the v3 customer-level model independently of the old transaction model.
    try:
        repeat_model, repeat_metadata = load_repeat_purchase_v3()
        repeat_load_error = None
    except (FileNotFoundError, ValueError, OSError, ImportError) as exc:
        repeat_model, repeat_metadata = None, None
        repeat_load_error = str(exc)
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

    # Score from historical orders only, not joined transaction-level model inputs.
    repeat_probability = None
    prediction_error = repeat_load_error
    snapshot = None
    if repeat_model is not None:
        try:
            repeat_probability, snapshot = predict_repeat_purchase_v3(
                transaction_df, selected_customer, repeat_model, repeat_metadata
            )
        except (ValueError, KeyError, TypeError) as exc:
            prediction_error = str(exc)

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

    st.subheader("🔮 Historical 90-Day Repeat-Purchase Model (v3)")
    st.caption("Experimental customer-level score at the historical test cutoff. "
               "The class-weighted model is not probability-calibrated; this is NOT "
               "a current-day prediction or a validated purchase probability.")
    if repeat_metadata is not None:
        st.write(f"**Prediction cutoff:** {repeat_metadata['test_cutoff']} "
                 f"| **Horizon:** {repeat_metadata['horizon_days']} days")
    if prediction_error:
        st.error(f"v3 model unavailable or input mismatch: {prediction_error}")
    elif repeat_probability is None:
        st.info("This customer has no orders before the historical cutoff; no v3 score is available.")
    else:
        threshold = float(repeat_metadata['selected_threshold'])
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Experimental Model Score", f"{repeat_probability:.2%}")
        with col2:
            st.metric("Validation Threshold Flag", "Flagged" if repeat_probability >= threshold else "Not flagged")
        st.caption(f"Validation-selected threshold: {threshold:.4f}. "
                   "Flagging is a model decision, not a high/low probability claim.")
        with st.expander("View historical model inputs"):
            st.dataframe(snapshot, hide_index=True, width='stretch')
    st.divider()

    # --------------------------------------------------
    # CUSTOMER LIFETIME VALUE
    # --------------------------------------------------
    st.divider()
    st.subheader("💰 Historical Spending Model Estimate")
    st.caption("The current CatBoost model was trained against historical Total_Spending, not future customer lifetime value.")
    try:
        predicted_clv = predict_customer_clv(customer, clv_model)
        st.metric("Estimated Historical Spending", f"R$ {predicted_clv:,.2f}")
    except (ValueError, KeyError, TypeError) as exc:
        st.error(f"Spending estimate failed due to an input schema mismatch: {exc}")


    # --------------------------------------------------
    # CUSTOMER PURCHASE HISTORY
    # --------------------------------------------------
    st.divider()
    st.subheader("🛒 Customer Purchase History")
    purchase_history = customer_transactions.copy()
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
    # Do not claim one row per item without a stable item-level identifier.
    # Drop exact duplicates only; payment joins may still produce repeated items.
    purchase_history = purchase_history.drop_duplicates()

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
    st.caption("Transaction detail is derived from a joined dataset and may contain repeated order items from payment joins.")

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
        width="stretch",
        hide_index=True
    )