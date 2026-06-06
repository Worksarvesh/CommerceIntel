import pandas as pd
import numpy as np
import os

def clean_data(input_path, output_path):
    print(f"Loading data from {input_path}...")
    # Load dataset
    df = pd.read_csv(input_path)
    
    print("Initial Data Info:")
    print(df.info())
    
    # 1. Missing Value Handling
    print("Handling missing values...")
    # Drop rows where CustomerID is missing as it's crucial for RFM and Segmentation
    df = df.dropna(subset=['CustomerID'])
    # Fill missing Description with 'Unknown'
    df['Description'] = df['Description'].fillna('Unknown')
    
    # 2. Duplicate Removal
    print("Removing duplicates...")
    df = df.drop_duplicates()
    
    # 3. Data Type Correction
    print("Correcting data types...")
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    df['CustomerID'] = df['CustomerID'].astype(int)
    
    # 4. Outlier Detection & Treatment
    print("Treating outliers...")
    # Remove negative or zero quantities and unit prices (returns or errors)
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # Cap outliers for Quantity and UnitPrice at 99th percentile to keep data realistic
    q_cap = df['Quantity'].quantile(0.99)
    p_cap = df['UnitPrice'].quantile(0.99)
    df['Quantity'] = df['Quantity'].clip(upper=q_cap)
    df['UnitPrice'] = df['UnitPrice'].clip(upper=p_cap)
    
    # 5. Feature Engineering
    print("Engineering features...")
    df['TotalAmount'] = df['Quantity'] * df['UnitPrice']
    df['InvoiceMonth'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    df['DayOfWeek'] = df['InvoiceDate'].dt.day_name()
    
    # Save cleaned data
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")
    print(f"Final shape: {df.shape}")
    return df

if __name__ == "__main__":
    input_file = "data/online_retail.csv"
    output_file = "data/cleaned_online_retail.csv"
    if os.path.exists(input_file):
        clean_data(input_file, output_file)
    else:
        print(f"Error: {input_file} not found.")
