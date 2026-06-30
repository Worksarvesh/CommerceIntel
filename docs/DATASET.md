# Dataset Documentation

## Selected Dataset

**Primary:** [Online Retail Dataset](https://www.kaggle.com/datasets/carrie1/ecommerce-data) (`carrie1/ecommerce-data`)

**Fallback reference:** E-commerce Customer Behaviour Dataset (`paulsamuelwe/e-commerce-customer-behaviour-dataset`)

## Why This Dataset Was Chosen

The requested Kaggle slug `alaaazazi/e-commerce-customer-behavior-dataset` was unavailable (404/403). Among the preferred alternatives:

| Dataset | Strength | Limitation |
|---------|----------|------------|
| Online Retail (UCI) | 541K real transactions, industry benchmark | No explicit product categories |
| Customer Behaviour (Gretel) | Demographics + reviews | Only ~13 rows, unsuitable for ML |
| Olist Brazilian E-commerce | Rich relational schema | Different domain, heavier preprocessing |

**Online Retail** was selected because it best supports the full project scope:

- Transaction-level data for SQLite modeling
- Sufficient volume for RFM, clustering, recommendations, and churn modeling
- Real business patterns (returns handling, missing IDs, international customers)
- Widely recognized by recruiters and interviewers

## Dataset Columns

| Column | Type | Description |
|--------|------|-------------|
| `InvoiceNo` | string | Unique invoice/order identifier (starts with `C` for cancellations) |
| `StockCode` | string | Product identifier |
| `Description` | string | Product name |
| `Quantity` | integer | Units purchased |
| `InvoiceDate` | datetime | Transaction timestamp |
| `UnitPrice` | float | Unit price in GBP |
| `CustomerID` | float | Unique customer identifier |
| `Country` | string | Customer country |

## Engineered Columns

| Column | Description |
|--------|-------------|
| `revenue` | `quantity * unit_price` |
| `category` | Derived product category from description keywords |

## Business Objective

Build an end-to-end **CommerceIntel Analytics Platform** that:

1. Cleans and models e-commerce transactions in SQLite
2. Identifies high-value customer segments via RFM and K-Means
3. Delivers hybrid product recommendations (collaborative + content-based)
4. Predicts customer churn to enable proactive retention campaigns
5. Presents actionable KPIs through an interactive Streamlit dashboard

## Data Volume (Post-Cleaning)

Approximately **397K+ transactions**, **4.3K+ customers**, and **3.6K+ products** after removing cancellations, negative quantities, and missing customer IDs.

## Download Instructions

```bash
pip install kaggle
# Place kaggle.json in ~/.kaggle/ (Windows: C:\Users\<user>\.kaggle\)
python run_pipeline.py --download
```

The pipeline uses `carrie1/ecommerce-data` by default.
