import sqlite3
import os

DB_PATH = "source/substrack.db"

def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id TEXT PRIMARY KEY,
            email TEXT NOT NULL,
            full_name TEXT NOT NULL,
            plan TEXT NOT NULL,
            plan_price REAL NOT NULL,
            status TEXT NOT NULL DEFAULT 'active',
            signup_date TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            purchase_id TEXT PRIMARY KEY,
            customer_id TEXT NOT NULL,
            product_name TEXT NOT NULL,
            amount REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()
    print("Database created successfully")

if __name__ == "__main__":
    create_database()
