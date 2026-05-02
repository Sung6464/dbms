# StoreBase — Backend Setup Guide

## Project Structure
```
storebase/
├── app.py              ← Flask backend (all API routes)
├── seed.py             ← Populates MongoDB with sample data
├── requirements.txt    ← Python dependencies
└── templates/
    └── index.html      ← Frontend UI
```

## Step-by-Step Setup

### 1. Install Python packages
```bash
pip install flask pymongo
```

### 2. Start MongoDB
```bash
# Windows — open Services and start "MongoDB" OR run:
net start MongoDB

# macOS
brew services start mongodb-community

# Linux
sudo systemctl start mongod
```

### 3. Load sample data
```bash
python seed.py
```
Expected output:
```
✅  Inserted 10 products into storebase.products
📦  Total: 10  |  Low stock: 7  |  Value: ₹...
```

### 4. Run the app
```bash
python app.py
```
Open → **http://localhost:5000**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/stats` | Dashboard stats (total, low stock, value) |
| GET | `/api/products` | All products (supports `?search=` & `?category=`) |
| GET | `/api/products/<id>` | Single product |
| POST | `/api/products` | Add new product |
| PUT | `/api/products/<id>` | Update product |
| DELETE | `/api/products/<id>` | Delete product |
| PUT | `/api/products/<id>/restock` | Mark as restocked (+qty) |
| GET | `/api/products/low-stock` | Products with stock < 5 |
| GET | `/api/categories` | All categories with counts |

---

## DBMS Concepts Demonstrated
| Concept | Where Used |
|---------|-----------|
| CRUD Operations | POST / GET / PUT / DELETE routes |
| Filtering / Search | `$regex` queries on name & description |
| Aggregation | `$group + $multiply + $sum` for inventory value |
| `$inc` operator | Restock endpoint increments stock count |
| `distinct()` → pipeline | Category listing with product counts |
| Low stock query | `$lt` comparison operator |
