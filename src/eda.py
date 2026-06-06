import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

def run_eda(csv_path, output_dir="docs/plots"):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_path)
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # Set Style
    sns.set_theme(style="whitegrid")
    
    # 1. Revenue Trends (Monthly)
    print("Generating Revenue Trends...")
    df['MonthYear'] = df['InvoiceDate'].dt.to_period('M').astype(str)
    monthly_revenue = df.groupby('MonthYear')['TotalAmount'].sum().reset_index()
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=monthly_revenue, x='MonthYear', y='TotalAmount', marker='o')
    plt.title('Monthly Revenue Trends')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{output_dir}/revenue_trends.png")
    plt.close()

    # 2. Top Products by Revenue
    print("Generating Top Products...")
    top_products = df.groupby('Description')['TotalAmount'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    top_products.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Products by Revenue')
    plt.ylabel('Revenue')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/top_products.png")
    plt.close()

    # 3. Top Customers by Revenue
    print("Generating Top Customers...")
    top_customers = df.groupby('CustomerID')['TotalAmount'].sum().sort_values(ascending=False).head(10)
    plt.figure(figsize=(12, 6))
    top_customers.plot(kind='bar', color='salmon')
    plt.title('Top 10 Customers by Revenue')
    plt.ylabel('Revenue')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/top_customers.png")
    plt.close()

    # 4. Customer Purchase Frequency
    print("Generating Purchase Frequency...")
    plt.figure(figsize=(10, 6))
    cust_freq = df.groupby('CustomerID')['InvoiceNo'].nunique()
    sns.histplot(cust_freq, bins=50, kde=True, color='green')
    plt.title('Customer Purchase Frequency Distribution')
    plt.xlabel('Number of Invoices')
    plt.tight_layout()
    plt.savefig(f"{output_dir}/purchase_frequency.png")
    plt.close()

    print(f"EDA plots saved to {output_dir}")

if __name__ == "__main__":
    run_eda("data/cleaned_online_retail.csv")
