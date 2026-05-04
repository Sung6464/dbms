from flask import Flask, render_template, request, jsonify
import pymysql.cursors
from datetime import datetime
import os

app = Flask(__name__)

# ── MySQL Connection ──────────────────────────────────────────
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")

def get_db():
    return pymysql.connect(
        host=MYSQL_HOST,
        user=MYSQL_USER,
        password=MYSQL_PASSWORD,
        database="storebase",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

# ── Pages ───────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

# ── UC-03 / UC-04  Stats Dashboard ──────────────────────────────
@app.route("/api/stats")
def stats():
    try:
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total_products, SUM(IF(stock < 5, 1, 0)) as low_stock, SUM(price * stock) as total_value FROM products")
            result = cursor.fetchone()
            
        return jsonify({
            "total_products": result["total_products"] or 0,
            "low_stock": int(result["low_stock"] or 0),
            "total_value": float(result["total_value"] or 0)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── UC-02  Low Stock Alerts ──────────────────────────────────────
@app.route("/api/products/low-stock")
def low_stock():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM products WHERE stock < 5 ORDER BY stock ASC")
        items = cursor.fetchall()
    return jsonify(items)

# ── UC-04  Search & Filter Products ─────────────────────────────
@app.route("/api/products")
def get_products():
    db = get_db()
    search   = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if search:
        query += " AND (name LIKE %s OR description LIKE %s)"
        search_term = f"%{search}%"
        params.extend([search_term, search_term])
    if category:
        query += " AND category = %s"
        params.append(category)
        
    query += " ORDER BY name ASC"

    with db.cursor() as cursor:
        cursor.execute(query, params)
        items = cursor.fetchall()
    return jsonify(items)

# ── UC-01  Get Single Product ────────────────────────────────────
@app.route("/api/products/<int:id>")
def get_product(id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        p = cursor.fetchone()
    if not p:
        return jsonify({"error": "Product not found"}), 404
    return jsonify(p)

# ── UC-01  Create Product ────────────────────────────────────────
@app.route("/api/products", methods=["POST"])
def create_product():
    data = request.json or {}
    name  = data.get("name", "").strip()
    price = data.get("price")

    if not name or price is None:
        return jsonify({"error": "Name and price are required"}), 400

    category = data.get("category", "Uncategorized").strip() or "Uncategorized"
    stock = int(data.get("stock", 0))
    description = data.get("description", "").strip()

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(
            "INSERT INTO products (name, category, price, stock, description) VALUES (%s, %s, %s, %s, %s)",
            (name, category, price, stock, description)
        )
        new_id = cursor.lastrowid
        cursor.execute("SELECT * FROM products WHERE id = %s", (new_id,))
        product = cursor.fetchone()

    return jsonify(product), 201

# ── UC-01  Update Product ────────────────────────────────────────
@app.route("/api/products/<int:id>", methods=["PUT"])
def update_product(id):
    data = request.json or {}
    updates = []
    params = []

    for field in ["name", "category", "description"]:
        if field in data:
            updates.append(f"{field} = %s")
            params.append(data[field].strip())
            
    if "price" in data:
        updates.append("price = %s")
        params.append(float(data["price"]))
    if "stock" in data:
        updates.append("stock = %s")
        params.append(int(data["stock"]))

    if not updates:
        return jsonify({"error": "Nothing to update"}), 400

    query = f"UPDATE products SET {', '.join(updates)} WHERE id = %s"
    params.append(id)

    db = get_db()
    with db.cursor() as cursor:
        cursor.execute(query, params)
        if cursor.rowcount == 0:
            cursor.execute("SELECT id FROM products WHERE id = %s", (id,))
            if not cursor.fetchone():
                return jsonify({"error": "Product not found"}), 404

        cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        updated = cursor.fetchone()
        
    return jsonify(updated)

# ── UC-01  Delete Product ────────────────────────────────────────
@app.route("/api/products/<int:id>", methods=["DELETE"])
def delete_product(id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("DELETE FROM products WHERE id = %s", (id,))
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
    return jsonify({"message": "Product deleted successfully"})

# ── UC-02  Mark as Restocked ─────────────────────────────────────
@app.route("/api/products/<int:id>/restock", methods=["PUT"])
def restock_product(id):
    qty = int(request.json.get("quantity", 10))
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("UPDATE products SET stock = stock + %s WHERE id = %s", (qty, id))
        if cursor.rowcount == 0:
            return jsonify({"error": "Product not found"}), 404
            
        cursor.execute("SELECT * FROM products WHERE id = %s", (id,))
        updated = cursor.fetchone()
        
    return jsonify(updated)

# ── UC-05  Category Listing with counts ──────────────────────────
@app.route("/api/categories")
def get_categories():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT category as name, COUNT(*) as count FROM products GROUP BY category ORDER BY category ASC")
        cats = cursor.fetchall()
    return jsonify(cats)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
