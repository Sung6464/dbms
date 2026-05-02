"""
seed.py  —  Populates MongoDB with sample data matching the StoreBase UI.
Run once:  python seed.py
"""
from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017/")
db = client["storebase"]
col = db["products"]

col.delete_many({})   # clear existing

now = datetime.utcnow().isoformat()

sample = [
    # Electronics (3)
    {"name": "Wireless Headphones",  "category": "Electronics",   "price": 2499,  "stock": 12, "description": "Noise-cancelling Bluetooth headphones, 30h battery."},
    {"name": "USB-C Hub 7-in-1",     "category": "Electronics",   "price": 1299,  "stock": 8,  "description": "HDMI, USB-A x3, SD card, PD charging."},
    {"name": "Mechanical Keyboard",  "category": "Electronics",   "price": 3999,  "stock": 3,  "description": "TKL layout, blue switches, RGB backlit."},
    # Clothing (1)
    {"name": "Cotton T-Shirt",       "category": "Clothing",      "price": 499,   "stock": 0,  "description": "100% cotton, available in multiple colours."},
    # Food & Beverage (1)
    {"name": "Green Tea Pack",       "category": "Food & Beverage","price": 349,  "stock": 2,  "description": "25 pyramid tea bags, antioxidant rich."},
    # Furniture (1)
    {"name": "Ergonomic Chair",      "category": "Furniture",     "price": 12999, "stock": 4,  "description": "Lumbar support, adjustable armrests, mesh back."},
    # Stationery (2)
    {"name": "Notebook Set",         "category": "Stationery",    "price": 299,   "stock": 0,  "description": "Pack of 3 A5 dotted notebooks, 160 pages each."},
    {"name": "Ballpoint Pens",       "category": "Stationery",    "price": 99,    "stock": 0,  "description": "12-pack, 0.7mm smooth blue ink."},
    # Sports (2)
    {"name": "Yoga Mat",             "category": "Sports",        "price": 849,   "stock": 1,  "description": "6mm non-slip eco TPE mat with carry strap."},
    {"name": "Resistance Bands Set", "category": "Sports",        "price": 599,   "stock": 2,  "description": "5 resistance levels, includes carry bag."},
]

for p in sample:
    p["created_at"] = now

result = col.insert_many(sample)
print(f"✅  Inserted {len(result.inserted_ids)} products into storebase.products")

# Quick verification
total = col.count_documents({})
low   = col.count_documents({"stock": {"$lt": 5}})
pipeline = [{"$group": {"_id": None, "v": {"$sum": {"$multiply": ["$price", "$stock"]}}}}]
val = list(col.aggregate(pipeline))
print(f"📦  Total: {total}  |  Low stock: {low}  |  Value: ₹{val[0]['v']:,.0f}")
