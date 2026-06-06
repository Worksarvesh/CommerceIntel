import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
import pickle
from src.database_manager import DatabaseManager
from src.rfm_analysis import perform_rfm

# ── MUST be the very first Streamlit call ──────────────────────────────────────
st.set_page_config(layout="wide", page_title="CommerceIntel Analytics")

# ── Data loaders ───────────────────────────────────────────────────────────────

@st.cache_data
def load_data():
    db_manager = DatabaseManager()
    # Use explicit column aliases to avoid duplicate-column issues from the JOIN
    query = """
        SELECT
            t.invoice_no,
            t.stock_code,
            t.quantity,
            t.unit_price,
            (t.quantity * t.unit_price) AS total_amount,
            o.invoice_date,
            o.customer_id,
            p.description,
            c.country
        FROM transactions t
        JOIN orders   o ON t.invoice_no  = o.invoice_no
        JOIN products p ON t.stock_code  = p.stock_code
        JOIN customers c ON o.customer_id = c.customer_id
    """
    df = db_manager.run_query(query)
    # Parse the date column; errors='coerce' turns unparseable values into NaT
    df["InvoiceDate"] = pd.to_datetime(df["invoice_date"], errors="coerce")
    return df


@st.cache_data
def load_rfm_data():
    return pd.read_csv("data/rfm_data.csv")


@st.cache_data
def load_segmented_data():
    return pd.read_csv("data/segmented_customers.csv")


@st.cache_resource
def load_ml_models():
    with open("models/kmeans_model.pkl", "rb") as f:
        kmeans_data = pickle.load(f)
    kmeans_model = kmeans_data["model"]
    scaler      = kmeans_data["scaler"]
    with open("models/churn_model.pkl", "rb") as f:
        churn_model = pickle.load(f)
    return kmeans_model, scaler, churn_model


# ── Load everything once ───────────────────────────────────────────────────────
df            = load_data()
rfm_df        = load_rfm_data()
segmented_df  = load_segmented_data()
kmeans_model, scaler, churn_model = load_ml_models()

# ── Sidebar navigation ─────────────────────────────────────────────────────────
st.title("CommerceIntel Analytics Platform")
st.sidebar.title("Navigation")
page = st.sidebar.radio(
    "Go to",
    ["Overview", "Sales Analytics", "Customer Segments", "Recommendations", "Churn Prediction"],
)

# ── Pages ──────────────────────────────────────────────────────────────────────

if page == "Overview":
    st.header("Overview")

    col1, col2, col3 = st.columns(3)

    # Guard against missing / all-NaN column
    total_revenue   = df["total_amount"].sum()   if "total_amount" in df.columns else 0
    total_orders    = df["invoice_no"].nunique()  if "invoice_no"   in df.columns else 0
    total_customers = df["customer_id"].nunique() if "customer_id"  in df.columns else 0

    col1.metric("Total Revenue",    f"${total_revenue:,.2f}")
    col2.metric("Total Orders",     f"{total_orders:,}")
    col3.metric("Total Customers",  f"{total_customers:,}")

    st.subheader("Monthly Revenue Trend")

    # Drop rows where the date couldn't be parsed before resampling
    revenue_ts = (
        df.dropna(subset=["InvoiceDate"])
          .set_index("InvoiceDate")["total_amount"]
          .resample("ME")          # "ME" = Month-End (replaces deprecated "M")
          .sum()
          .reset_index()
    )

    fig = px.line(revenue_ts, x="InvoiceDate", y="total_amount", title="Monthly Revenue")
    st.plotly_chart(fig, use_container_width=True)


elif page == "Sales Analytics":
    st.header("Sales Analytics")

    st.subheader("Top 10 Products by Revenue")
    top_products = (
        df.groupby("description")["total_amount"]
          .sum()
          .sort_values(ascending=False)
          .head(10)
          .reset_index()
    )
    fig = px.bar(top_products, x="description", y="total_amount", title="Top 10 Products")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Sales by Country")
    sales_by_country = (
        df.groupby("country")["total_amount"]
          .sum()
          .sort_values(ascending=False)
          .head(10)
          .reset_index()
    )
    fig = px.bar(sales_by_country, x="country", y="total_amount", title="Sales by Country")
    st.plotly_chart(fig, use_container_width=True)


elif page == "Customer Segments":
    st.header("Customer Segments")

    st.subheader("RFM Segments Distribution")
    fig = px.pie(segmented_df, names="Segment", title="RFM Segments")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("K-Means Clusters")
    fig = px.scatter(
        segmented_df,
        x="Recency", y="Monetary",
        color="Cluster",
        hover_data=["Frequency"],
        title="Customer Clusters (Recency vs Monetary)",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Segment Details")
    st.dataframe(
        segmented_df.groupby("Segment")[["Recency", "Frequency", "Monetary"]]
                    .mean()
                    .reset_index()
    )


elif page == "Recommendations":
    st.header("Product Recommendations")

    from src.recommender import Recommender

    # Build the model once (outside the widget callback)
    @st.cache_resource
    def get_recommender():
        rec = Recommender("data/cleaned_online_retail.csv")
        rec.build_collaborative_filtering()
        return rec

    recommender = get_recommender()

    product_list     = sorted(df["description"].dropna().unique().tolist())
    selected_product = st.selectbox("Select a product to get recommendations:", product_list)

    if selected_product:
        stock_code_series = df[df["description"] == selected_product]["stock_code"]
        if stock_code_series.empty:
            st.error("Stock code not found for the selected product.")
        else:
            stock_code      = stock_code_series.iloc[0]
            recommendations = recommender.get_recommendations(stock_code)

            st.subheader(f"Recommendations for: {selected_product}")
            if recommendations:
                recommended_df = (
                    df[df["stock_code"].isin(recommendations)][["description", "stock_code"]]
                      .drop_duplicates()
                )
                st.dataframe(recommended_df)
            else:
                st.info("No recommendations found for this product.")


elif page == "Churn Prediction":
    st.header("Customer Churn Prediction")

    st.subheader("Predict Churn for a Customer")
    customer_id_input = st.number_input("Enter Customer ID", min_value=1, value=12347, step=1)

    if st.button("Predict Churn"):
        customer_data = rfm_df[rfm_df["CustomerID"] == int(customer_id_input)]

        if customer_data.empty:
            st.error("Customer ID not found in RFM data.")
        else:
            recency   = customer_data["Recency"].iloc[0]
            frequency = customer_data["Frequency"].iloc[0]
            monetary  = customer_data["Monetary"].iloc[0]

            input_features = pd.DataFrame(
                [[recency, frequency, monetary]],
                columns=["Recency", "Frequency", "Monetary"],
            )

            churn_prediction = churn_model.predict(input_features)[0]

            # predict_proba may not exist on all estimators — fall back gracefully
            if hasattr(churn_model, "predict_proba"):
                churn_proba = churn_model.predict_proba(input_features)[0][1]
                proba_text  = f" (Probability: {churn_proba:.2f})"
            else:
                proba_text  = ""

            if churn_prediction == 1:
                st.warning(f"Customer {customer_id_input} is likely to churn{proba_text}.")
            else:
                st.success(f"Customer {customer_id_input} is unlikely to churn{proba_text}.")

            st.write(f"**Recency:** {recency} | **Frequency:** {frequency} | **Monetary:** ${monetary:,.2f}")