from flask import Flask, render_template, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import os

app = Flask(__name__)

# ── MongoDB Connection ──────────────────────────────────────────
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URI)
db = client["storebase"]
products_col = db["products"]

# ── Helper ──────────────────────────────────────────────────────
def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

# ── Pages ───────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ── UC-03 / UC-04  Stats Dashboard ──────────────────────────────
@app.route("/api/stats")
def stats():
    total = products_col.count_documents({})
    low_stock = products_col.count_documents({"stock": {"$lt": 5}})
    pipeline = [
        {"$group": {
            "_id": None,
            "total_value": {"$sum": {"$multiply": ["$price", "$stock"]}}
        }}
    ]
    agg = list(products_col.aggregate(pipeline))
    total_value = round(agg[0]["total_value"], 2) if agg else 0
    return jsonify({
        "total_products": total,
        "low_stock": low_stock,
        "total_value": total_value
    })

# ── UC-02  Low Stock Alerts ──────────────────────────────────────
@app.route("/api/products/low-stock")
def low_stock():
    items = list(products_col.find({"stock": {"$lt": 5}}).sort("stock", 1))
    return jsonify([serialize(p) for p in items])

# ── UC-04  Search & Filter Products ─────────────────────────────
@app.route("/api/products")
def get_products():
    query = {}
    search   = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    if search:
        query["$or"] = [
            {"name":        {"$regex": search, "$options": "i"}},
            {"description": {"$regex": search, "$options": "i"}}
        ]
    if category:
        query["category"] = {"$regex": f"^{category}$", "$options": "i"}

    items = list(products_col.find(query).sort("name", 1))
    return jsonify([serialize(p) for p in items])

# ── UC-01  Get Single Product ────────────────────────────────────
@app.route("/api/products/<id>")
def get_product(id):
    p = products_col.find_one({"_id": ObjectId(id)})
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(serialize(p))

# ── UC-01  Create Product ────────────────────────────────────────
@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.json or {}
    name  = data.get("name", "").strip()
    price = data.get("price")

    if not name or price is None:
        return jsonify({"error": "Name and price are required"}), 400

    product = {
        "name":        name,
        "category":    data.get("category", "Uncategorized").strip() or "Uncategorized",
        "price":       float(price),
        "stock":       int(data.get("stock", 0)),
        "description": data.get("description", "").strip(),
        "created_at":  datetime.utcnow().isoformat()
    }
    result = products_col.insert_one(product)
    product["_id"] = str(result.inserted_id)
    return jsonify(product), 201

# ── UC-01  Update Product ────────────────────────────────────────
@app.route("/api/products/<id>", methods=["PUT"])
def update_product(id):
    data = request.json or {}
    updates = {}

    for field in ["name", "category", "description"]:
        if field in data:
            updates[field] = data[field].strip()
    if "price" in data:
        updates["price"] = float(data["price"])
    if "stock" in data:
        updates["stock"] = int(data["stock"])

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    result = products_col.update_one({"_id": ObjectId(id)}, {"$set": updates})
    if result.matched_count == 0:
        return jsonify({"error": "Product not found"}), 404
 
    updated = products_col.find_one({"_id": ObjectId(id)})
    return jsonify(serialize(updated))

# ── UC-01  Delete Product ────────────────────────────────────────
@app.route("/api/products/<id>", methods=["DELETE"])
def delete_product(id):
    result = products_col.delete_one({"_id": ObjectId(id)})
    if result.deleted_count == 0:
        return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product deleted successfully"})

# ── UC-02  Mark as Restocked ─────────────────────────────────────
@app.route("/api/products/<id>/restock", methods=["PUT"])
def restock_product(id):
    qty = int(request.json.get("quantity", 10))
    result = products_col.update_one(
        {"_id": ObjectId(id)},
        {"$inc": {"stock": qty}}
    )
    if result.matched_count == 0:
        return jsonify({"error": "Product not found"}), 404
    updated = products_col.find_one({"_id": ObjectId(id)})
    return jsonify(serialize(updated))

# ── UC-05  Category Listing with counts ──────────────────────────
@app.route("/api/categories")
def get_categories():
    pipeline = [
        {"$group": {"_id": "$category", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    cats = list(products_col.aggregate(pipeline))
    return jsonify([{"name": c["_id"], "count": c["count"]} for c in cats])

if __name__ == "__main__":
    app.run(debug=True, port=5000)


