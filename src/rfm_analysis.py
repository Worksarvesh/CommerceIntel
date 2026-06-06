import pandas as pd
import numpy as np
import datetime as dt
import os

def perform_rfm(csv_path, output_path="data/rfm_data.csv"):
    df = pd.read_csv(csv_path)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Snapshot date for Recency (day after last transaction)
    snapshot_date = df['InvoiceDate'].max() + dt.timedelta(days=1)
    
    # Aggregate RFM metrics
    rfm = df.groupby('CustomerID').agg({
        'InvoiceDate': lambda x: (snapshot_date - x.max()).days,
        'InvoiceNo': 'nunique',
        'TotalAmount': 'sum'
    })
    
    rfm.rename(columns={
        'InvoiceDate': 'Recency',
        'InvoiceNo': 'Frequency',
        'TotalAmount': 'Monetary'
    }, inplace=True)
    
    # Assign scores (1-5) using quantiles
    # Recency: lower is better (5)
    rfm["R_Score"] = pd.qcut(rfm["Recency"], 5, labels=[5, 4, 3, 2, 1], duplicates="drop")
    # Frequency & Monetary: higher is better (5)
    rfm["F_Score"] = pd.qcut(rfm["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    rfm["M_Score"] = pd.qcut(rfm["Monetary"], 5, labels=[1, 2, 3, 4, 5], duplicates="drop")
    
    # Combined RFM Score
    rfm['RFM_Group'] = rfm.R_Score.astype(str) + rfm.F_Score.astype(str) + rfm.M_Score.astype(str)
    rfm['RFM_Score'] = rfm[['R_Score', 'F_Score', 'M_Score']].sum(axis=1)
    
    # Define Segments
    def segment_customer(df):
        score = df['RFM_Score']
        if score >= 13:
            return 'Champions'
        elif score >= 10:
            return 'Loyal Customers'
        elif score >= 7:
            return 'Potential Loyalists'
        elif score >= 5:
            return 'At Risk'
        else:
            return 'Lost Customers'

    rfm['Segment'] = rfm.apply(segment_customer, axis=1)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    rfm.to_csv(output_path)
    print(f"RFM analysis saved to {output_path}")
    print(rfm['Segment'].value_counts())
    return rfm

if __name__ == "__main__":
    perform_rfm("data/cleaned_online_retail.csv")
