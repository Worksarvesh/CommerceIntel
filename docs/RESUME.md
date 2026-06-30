# Resume & Interview Content

## Project Title

**CommerceIntel Analytics Platform – E-commerce Recommendation & Customer Segmentation**

## Resume Project Description (3-4 lines)

Built an end-to-end e-commerce analytics platform processing 540K+ retail transactions using Python, Pandas, scikit-learn, SQLite, and Streamlit. Engineered RFM segmentation and K-Means clustering to identify high-value customer cohorts, implemented hybrid collaborative/content-based recommendation engine, and deployed a Random Forest churn model achieving strong classification performance. Delivered interactive executive dashboards with revenue KPIs, segment insights, and retention analytics.

## ATS Keywords

Python, Pandas, NumPy, SQL, SQLite, scikit-learn, Random Forest, K-Means Clustering, RFM Analysis, Customer Segmentation, Recommendation Systems, Collaborative Filtering, Content-Based Filtering, Feature Engineering, Data Cleaning, EDA, Matplotlib, Plotly, Streamlit, Machine Learning, Churn Prediction, E-commerce Analytics, Data Pipeline, Unit Testing, pytest, Kaggle, Business Intelligence

## Interview Explanation (60 seconds)

"I built CommerceIntel, a production-style analytics platform on the Online Retail dataset. I started with data cleaning—handling cancellations, missing customer IDs, and outlier capping—then loaded normalized tables into SQLite. For customer intelligence, I implemented RFM scoring and K-Means segmentation to classify champions, at-risk, and loyal segments. For growth, I built a hybrid recommender combining collaborative filtering with TF-IDF content similarity. For retention, I trained a Random Forest churn model using recency, frequency, monetary, and diversity features. Everything is orchestrated through a modular pipeline and exposed in a Streamlit dashboard with sales, segmentation, recommendations, and churn pages."

## STAR Format

**Situation:** An e-commerce business needed unified analytics to improve retention, personalization, and revenue forecasting from fragmented transaction data.

**Task:** Design and implement an end-to-end data science platform covering ingestion, warehousing, segmentation, recommendations, churn prediction, and visualization.

**Action:**
- Selected and cleaned the Online Retail dataset (541K rows)
- Built SQLite star schema and analytical SQL queries
- Implemented RFM + K-Means customer segmentation with business labels
- Developed hybrid recommendation engine (collaborative + content-based)
- Trained Random Forest churn classifier with feature importance analysis
- Created Streamlit dashboard and pytest unit test suite

**Result:** Delivered a GitHub-ready platform enabling segment-level targeting, personalized product recommendations, churn risk identification, and executive KPI monitoring—demonstrating full-stack data science capability from raw data to business-facing product.

## Talking Points for Deep Dives

1. **Why RFM + K-Means?** RFM is interpretable for marketing teams; K-Means adds multivariate behavioral patterns.
2. **Churn label definition:** Customers inactive >90 days from last purchase relative to dataset max date.
3. **Recommendation cold start:** Popularity fallback for new users; content-based anchor from recent purchases.
4. **Data quality decisions:** Removed invoice cancellations (`InvoiceNo` starting with `C`) to avoid biased revenue.
