# Intelligent E-Commerce Customer Analytics Platform

**GUVI AI/ML Capstone Project | Brazilian Olist E-Commerce Dataset**

An end-to-end customer analytics project combining data integration, exploratory analysis, customer segmentation, repeat-purchase prediction, historical customer spending estimation, product recommendations, and explainable machine learning. A multi-page **Streamlit** application presents business insights and model outputs in an interactive dashboard.

## Project objectives

- Understand sales trends, customer behavior, and purchasing patterns.
- Group customers with similar characteristics using unsupervised learning.
- Estimate repeat-purchase propensity from historical customer activity.
- Estimate historical customer spending using regression models.
- Recommend relevant products using customer–product interactions.
- Interpret selected model predictions and feature importance with SHAP.
- Present actionable findings through a user-friendly dashboard.

## Dashboard modules

| Page | Description |
| --- | --- |
| Home | Project introduction and navigation |
| Executive Dashboard | High-level business KPIs, trends, and filters |
| Customer Analytics | Customer profiles, segments, and predictive insights |
| Recommendation Engine | Personalized product recommendations |
| Business Insights | Business-oriented sales and customer analysis |
| Explainable AI | Feature importance and SHAP explanations |

## Machine learning methods

| Task | Approach |
| --- | --- |
| Customer segmentation | K-Means clustering, scaling, and PCA visualization |
| Repeat-purchase prediction | Classification, including a 90-day repeat-purchase model |
| Customer spending estimate | Regression, including CatBoost experimentation |
| Product recommendation | Customer–product collaborative filtering with fallback recommendations |
| Model interpretation | Feature importance and SHAP |

**Interpretation notes:** The spending model estimates **historical spending**, not verified future customer lifetime value. Repeat-purchase model scores should not be described as calibrated probabilities without calibration testing. The Explainable AI page may display explanations for a legacy LightGBM model rather than the current repeat-purchase classifier; its labels should make that distinction clear.

## Technology stack

- **Language:** Python
- **Application:** Streamlit
- **Data analysis:** Pandas, NumPy
- **Visualization:** Plotly, Matplotlib, Seaborn
- **Machine learning:** scikit-learn, LightGBM, XGBoost, CatBoost
- **Explainability:** SHAP
- **Development:** Jupyter Notebook, VS Code, Git/GitHub

## Project structure

```text
E-Commerce-Customer-Analytics/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── artifacts/
│   ├── catboost_clv_model.pkl
│   ├── lightgbm_repeat_purchase_model.pkl
│   ├── preprocessor.pkl
│   ├── customer_product_matrix.pkl
│   ├── customer_similarity.pkl
│   ├── feature_importance.csv
│   ├── shap_feature_names.pkl
│   ├── shap_sample.npy
│   ├── shap_values_sample.pkl
│   └── repeat_purchase_90d_*  # versioned model artifacts
├── dashboard/
│   ├── assets/
│   │   └── styles.css
│   ├── components/
│   │   ├── footer.py
│   │   ├── kpi_cards.py
│   │   └── sidebar.py
│   ├── pages/
│   │   ├── home.py
│   │   ├── executive_dashboard.py
│   │   ├── customer_analytics.py
│   │   ├── recommendation.py
│   │   ├── business_insights.py
│   │   └── explainable_ai.py
│   └── utils/
│       ├── charts.py
│       ├── config.py
│       ├── data_loader.py
│       ├── model_loader.py
│       ├── predictions.py
│       └── recommendations.py
├── data/
│   ├── raw/
│   └── processed/
│       ├── customer_analytics_dataset.csv
│       ├── customer_analytics_cleaned.csv
│       ├── customer_analytics_featured.csv
│       ├── customer_features.csv
│       ├── customer_segments.csv
│       ├── product_features.csv
│       ├── seller_features.csv
│       └── cluster_profile.csv
├── models/
├── notebooks/
│   ├── 01_Data_Integration.ipynb
│   ├── 02_Data_Cleaning.ipynb
│   ├── 03_Exploratory Data Analysis.ipynb
│   ├── 04_Feature_Engineering.ipynb
│   ├── 05_Customer_Segmentation.ipynb
│   ├── 06_Purchase_Prediction.ipynb
│   ├── 07_Customer Lifetime Value Prediction.ipynb
│   ├── 08_Product Recommendation System.ipynb
│   └── 09_Explainable_AI.ipynb
├── reports/
└── src/
```

`__pycache__` folders are generated automatically and should not be committed. Some model and data artifacts may be too large for ordinary GitHub uploads.

## Installation and local execution

**Prerequisites:** Python 3.10 or 3.11 is a reasonable starting point for the ML dependency stack; use a Python version compatible with the versions of your saved models.

1. Clone the repository and open the project folder.
2. Create a virtual environment:

   ```bash
   python -m venv .venv
   ```

3. Activate it:

   **Windows PowerShell**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   source .venv/bin/activate
   ```

4. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

5. Ensure the required CSV files under `data/processed/` and model files under `artifacts/` are available locally.
6. Start the dashboard:

   ```bash
   python -m streamlit run app.py
   ```

7. Open the local URL shown in the terminal (usually `http://localhost:8501`).

> **Note:** The package ranges in `requirements.txt` are a starting point inferred from the notebooks and project layout, not an exact export of the environment used to train the saved `.pkl` models. If model deserialization fails, install the same package versions used when those artifacts were created.

## Notebook workflow

The numbered notebooks cover the project pipeline from data integration and cleaning through EDA, feature engineering, segmentation, predictive modeling, recommendation, and explainability. They can be explored in order, but the Streamlit application uses precomputed datasets and saved artifacts rather than retraining every model on startup.

## Dataset

The project uses the **Brazilian E-Commerce Public Dataset by Olist**, comprising order, customer, product, seller, payment, review, and related records. Follow the dataset's source terms when sharing or redistributing raw data.

## Results and limitations

The dashboard combines descriptive business analytics with experimental machine learning outputs. Classification and recommendation performance should be interpreted in the context of class imbalance and sparse purchase interactions. Historical spending estimates should not be represented as forecasts of future revenue.

For a portfolio or academic demonstration, this application illustrates the full workflow from data preparation to interactive delivery. It is not a production decisioning system.

## GitHub and deployment notes

- Do not commit virtual environments, Python caches, secrets, or API credentials.
- Review large CSV and `.pkl` files before pushing. GitHub rejects ordinary Git files above its size limit; use a separate artifact storage strategy if necessary.
- A deployed Streamlit app must have access to every processed CSV and model artifact it loads. If those files are excluded from GitHub, provide a supported way to retrieve them before deploying.
- Verify the deployed environment can load the saved model files; package-version compatibility matters for pickle-based artifacts.

## Author / submission

Developed as a **GUVI AI/ML capstone project**. Add your preferred name, GitHub repository URL, live Streamlit URL, and dashboard screenshots before final submission.
