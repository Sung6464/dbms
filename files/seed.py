import pymysql
import os

MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")

print(f"Connecting to MySQL at {MYSQL_HOST} as {MYSQL_USER}...")
# Connect without database first to create it
try:
    connection = pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        autocommit=True
    )
except Exception as e:
    print(f"❌ Failed to connect to MySQL: {e}")
    print("Please make sure MySQL is running and accessible.")
    exit(1)

with connection.cursor() as cursor:
    print("Creating database 'storebase'...")
    cursor.execute("CREATE DATABASE IF NOT EXISTS storebase")
    cursor.execute("USE storebase")
    
    print("Creating 'products' table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            category VARCHAR(100) DEFAULT 'Uncategorized',
            price DECIMAL(10,2) NOT NULL,
            stock INT DEFAULT 0,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    print("Clearing existing data...")
    cursor.execute("TRUNCATE TABLE products")
    
    sample = [
        # Electronics (3)
        ("Wireless Headphones", "Electronics", 2499.00, 12, "Noise-cancelling Bluetooth headphones, 30h battery."),
        ("USB-C Hub 7-in-1", "Electronics", 1299.00, 8, "HDMI, USB-A x3, SD card, PD charging."),
        ("Mechanical Keyboard", "Electronics", 3999.00, 3, "TKL layout, blue switches, RGB backlit."),
        # Clothing (1)
        ("Cotton T-Shirt", "Clothing", 499.00, 0, "100% cotton, available in multiple colours."),
        # Food & Beverage (1)
        ("Green Tea Pack", "Food & Beverage", 349.00, 2, "25 pyramid tea bags, antioxidant rich."),
        # Furniture (1)
        ("Ergonomic Chair", "Furniture", 12999.00, 4, "Lumbar support, adjustable armrests, mesh back."),
        # Stationery (2)
        ("Notebook Set", "Stationery", 299.00, 0, "Pack of 3 A5 dotted notebooks, 160 pages each."),
        ("Ballpoint Pens", "Stationery", 99.00, 0, "12-pack, 0.7mm smooth blue ink."),
        # Sports (2)
        ("Yoga Mat", "Sports", 849.00, 1, "6mm non-slip eco TPE mat with carry strap."),
        ("Resistance Bands Set", "Sports", 599.00, 2, "5 resistance levels, includes carry bag.")
    ]
    
    cursor.executemany(
        "INSERT INTO products (name, category, price, stock, description) VALUES (%s, %s, %s, %s, %s)",
        sample
    )
    
    inserted_count = cursor.rowcount
    print(f"✅  Inserted {inserted_count} products into storebase.products")

    cursor.execute("SELECT COUNT(*) FROM products")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM products WHERE stock < 5")
    low = cursor.fetchone()[0]
    
    cursor.execute("SELECT SUM(price * stock) FROM products")
    val = cursor.fetchone()[0] or 0
    
    print(f"📦  Total: {total}  |  Low stock: {low}  |  Value: ₹{val:,.0f}")

connection.close()
