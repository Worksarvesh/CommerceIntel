-- CommerceIntel Analytics Platform - SQLite Schema

PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS customers;

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    country TEXT NOT NULL,
    first_purchase_date TEXT,
    last_purchase_date TEXT,
    total_orders INTEGER DEFAULT 0,
    total_revenue REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    stock_code TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    category TEXT,
    avg_unit_price REAL,
    total_quantity_sold INTEGER DEFAULT 0,
    total_revenue REAL DEFAULT 0
);

CREATE TABLE orders (
    order_id TEXT PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    order_total REAL NOT NULL,
    country TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id TEXT NOT NULL,
    customer_id INTEGER NOT NULL,
    stock_code TEXT NOT NULL,
    description TEXT,
    category TEXT,
    quantity INTEGER NOT NULL,
    unit_price REAL NOT NULL,
    revenue REAL NOT NULL,
    transaction_date TEXT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(order_id),
    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
    FOREIGN KEY (stock_code) REFERENCES products(stock_code)
);

CREATE INDEX idx_transactions_customer ON transactions(customer_id);
CREATE INDEX idx_transactions_product ON transactions(stock_code);
CREATE INDEX idx_transactions_date ON transactions(transaction_date);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE INDEX idx_orders_date ON orders(order_date);
