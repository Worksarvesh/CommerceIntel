import sqlite3
import pandas as pd
import os

class DatabaseManager:
    def __init__(self, db_path="database/commerce_intel.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def create_tables(self):
        print("Creating database tables...")
        # Customers Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                customer_id INTEGER PRIMARY KEY,
                country TEXT
            )
        ''')
        
        # Products Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                stock_code TEXT PRIMARY KEY,
                description TEXT
            )
        ''')
        
        # Orders Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                invoice_no TEXT PRIMARY KEY,
                customer_id INTEGER,
                invoice_date TIMESTAMP,
                total_amount REAL,
                FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
            )
        ''')
        
        # Transactions Table
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT,
                stock_code TEXT,
                quantity INTEGER,
                unit_price REAL,
                total_amount REAL,
                FOREIGN KEY (invoice_no) REFERENCES orders(invoice_no),
                FOREIGN KEY (stock_code) REFERENCES products(stock_code)
            )
        ''')
        self.conn.commit()

    def ingest_data(self, csv_path):
        print(f"Ingesting data from {csv_path}...")
        df = pd.read_csv(csv_path)
        
        # Ingest Customers
        customers = df[['CustomerID', 'Country']].drop_duplicates(subset=['CustomerID'])
        customers.columns = ['customer_id', 'country']
        customers.to_sql('customers', self.conn, if_exists='replace', index=False)
        
        # Ingest Products
        products = df[['StockCode', 'Description']].drop_duplicates(subset=['StockCode'])
        products.columns = ['stock_code', 'description']
        products.to_sql('products', self.conn, if_exists='replace', index=False)
        
        # Ingest Orders (Simplified as one order per InvoiceNo)
        orders = df.groupby('InvoiceNo').agg({
            'CustomerID': 'first',
            'InvoiceDate': 'first',
            'TotalAmount': 'sum'
        }).reset_index()
        orders.columns = ['invoice_no', 'customer_id', 'invoice_date', 'total_amount']
        orders.to_sql('orders', self.conn, if_exists='replace', index=False)
        
        # Ingest Transactions
        transactions = df[['InvoiceNo', 'StockCode', 'Quantity', 'UnitPrice', 'TotalAmount']]
        transactions.columns = ['invoice_no', 'stock_code', 'quantity', 'unit_price', 'total_amount']
        transactions.to_sql('transactions', self.conn, if_exists='replace', index=False)
        
        self.conn.commit()
        print("Data ingestion complete.")

    def run_query(self, query):
        return pd.read_sql_query(query, self.conn)

    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = DatabaseManager()
    db.create_tables()
    db.ingest_data("data/cleaned_online_retail.csv")
    
    # Test Query
    res = db.run_query("SELECT COUNT(*) as total_orders FROM orders")
    print(f"Total Orders in DB: {res.iloc[0]['total_orders']}")
    db.close()
