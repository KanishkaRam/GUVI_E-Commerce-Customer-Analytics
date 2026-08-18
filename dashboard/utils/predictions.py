import pandas as pd

def predict_repeat_purchase(customer_transactions: pd.DataFrame, model, preprocessor):
    # Apply the fitted Phase-6 preprocessor
    X_processed = preprocessor.transform(customer_transactions)

    # Get probability of class 1
    transaction_probabilities = (model.predict_proba(X_processed)[:, 1])

    # Aggregate transaction probabilities
    customer_probability = (transaction_probabilities.mean())

    # Explicitly return a Python float
    return float(customer_probability)

def predict_customer_clv( customer,clv_model):
    # Predict Customer Lifetime Value using the trained CatBoost pipeline.

    clv_features = pd.DataFrame(
        [{
            "Total_Orders":
                customer["Total_Orders"],

            "Average_Basket_Size":
                customer["Average_Basket_Size"],

            "Recency":
                customer["Recency"],

            "Frequency":
                customer["Frequency"],

            "Customer_Tenure":
                customer["Customer_Tenure"],

            "Days_Since_Last_Purchase":
                customer["Days_Since_Last_Purchase"],

            "Average_Review_Rating":
                customer["Average_Review_Rating"],

            "Preferred_Payment_Method":
                customer["Preferred_Payment_Method"]
        }]
    )

    predicted_clv = clv_model.predict(
        clv_features
    )[0]

    return float(predicted_clv)