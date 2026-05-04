let currentTab = 'all';
let allProducts = [];

document.addEventListener('DOMContentLoaded', () => {
    fetchStats();
    fetchCategories();
    loadTab(currentTab);

    // Setup Tabs
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            currentTab = e.target.dataset.tab;
            loadTab(currentTab);
        });
    });

    // Search and Filter
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');

    let debounceTimer;
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => fetchProducts(e.target.value, categoryFilter.value), 300);
    });

    categoryFilter.addEventListener('change', (e) => {
        fetchProducts(searchInput.value, e.target.value);
    });
});

async function loadTab(tab) {
    const title = document.getElementById('sectionTitle');
    document.getElementById('searchInput').value = '';
    document.getElementById('categoryFilter').value = '';

    if (tab === 'low-stock') {
        title.textContent = 'Low Stock Alerts';
        fetchLowStock();
    } else {
        title.textContent = 'Current Inventory';
        fetchProducts();
    }
}

// ================= FETCH DATA =================

async function fetchStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        document.getElementById('statTotal').textContent = data.total_products;
        document.getElementById('statLowStock').textContent = data.low_stock;
        document.getElementById('statValue').textContent = '₹' + data.total_value.toLocaleString('en-IN');
    } catch (error) { console.error(error); }
}

async function fetchCategories() {
    try {
        const res = await fetch('/api/categories');
        const categories = await res.json();
        const filter = document.getElementById('categoryFilter');
        const list = document.getElementById('categoryList');
        
        filter.innerHTML = '<option value="">All Categories</option>';
        list.innerHTML = '';
        
        categories.forEach(c => {
            filter.insertAdjacentHTML('beforeend', `<option value="${c.name}">${c.name}</option>`);
            list.insertAdjacentHTML('beforeend', `<option value="${c.name}">`);
        });
    } catch (error) { console.error(error); }
}

async function fetchProducts(search = '', category = '') {
    if (currentTab === 'low-stock') return; // Handled separately
    try {
        const params = new URLSearchParams();
        if (search) params.append('search', search);
        if (category) params.append('category', category);
        
        const res = await fetch(`/api/products?${params.toString()}`);
        allProducts = await res.json();
        renderProducts(allProducts);
    } catch (error) { console.error(error); }
}

async function fetchLowStock() {
    try {
        const res = await fetch('/api/products/low-stock');
        allProducts = await res.json();
        renderProducts(allProducts);
    } catch (error) { console.error(error); }
}

// ================= RENDER =================

function renderProducts(products) {
    const grid = document.getElementById('productsGrid');
    grid.innerHTML = '';
    
    if (products.length === 0) {
        grid.innerHTML = '<div class="empty-state">No products found.</div>';
        return;
    }

    products.forEach(p => {
        const isOut = p.stock === 0;
        const isLow = p.stock > 0 && p.stock < 5;
        const stockClass = isOut ? 'stock-out' : (isLow ? 'stock-low' : 'stock-good');
        
        grid.insertAdjacentHTML('beforeend', `
            <div class="product-card">
                <div class="product-actions">
                    <button class="btn-icon" title="Edit" onclick="editProduct('${p._id}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path></svg>
                    </button>
                    <button class="btn-icon" title="Restock" onclick="openRestockModal('${p._id}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
                    </button>
                    <button class="btn-icon" style="color:var(--danger-color)" title="Delete" onclick="deleteProduct('${p._id}')">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                </div>
                <div class="product-category">${p.category}</div>
                <h3 class="product-name">${p.name}</h3>
                <p class="product-desc">${p.description}</p>
                <div class="product-footer">
                    <div class="product-price">₹${p.price.toLocaleString('en-IN')}</div>
                    <div class="product-stock ${stockClass}">${p.stock} in stock</div>
                </div>
            </div>
        `);
    });
}

// ================= MODALS & ACTIONS =================

function openModal(id) { document.getElementById(id).classList.add('active'); }
function closeModal(id) { document.getElementById(id).classList.remove('active'); }

function openProductModal() {
    document.getElementById('modalTitle').textContent = 'Add Product';
    document.getElementById('productForm').reset();
    document.getElementById('productId').value = '';
    openModal('productModal');
}

function editProduct(id) {
    const p = allProducts.find(x => x._id === id);
    if (!p) return;
    
    document.getElementById('modalTitle').textContent = 'Edit Product';
    document.getElementById('productId').value = p._id;
    document.getElementById('productName').value = p.name;
    document.getElementById('productCategory').value = p.category;
    document.getElementById('productPrice').value = p.price;
    document.getElementById('productStock').value = p.stock;
    document.getElementById('productDesc').value = p.description;
    
    openModal('productModal');
}

async function handleProductSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('productId').value;
    
    const payload = {
        name: document.getElementById('productName').value,
        category: document.getElementById('productCategory').value,
        price: parseFloat(document.getElementById('productPrice').value),
        stock: parseInt(document.getElementById('productStock').value),
        description: document.getElementById('productDesc').value
    };

    const method = id ? 'PUT' : 'POST';
    const url = id ? `/api/products/${id}` : '/api/products';

    try {
        await fetch(url, {
            method: method,
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        closeModal('productModal');
        refreshData();
    } catch (error) { console.error('Error saving:', error); }
}

function openRestockModal(id) {
    document.getElementById('restockForm').reset();
    document.getElementById('restockProductId').value = id;
    openModal('restockModal');
}

async function handleRestockSubmit(e) {
    e.preventDefault();
    const id = document.getElementById('restockProductId').value;
    const qty = document.getElementById('restockQty').value;

    try {
        await fetch(`/api/products/${id}/restock`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ quantity: parseInt(qty) })
        });
        closeModal('restockModal');
        refreshData();
    } catch (error) { console.error('Error restocking:', error); }
}

async function deleteProduct(id) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    try {
        await fetch(`/api/products/${id}`, { method: 'DELETE' });
        refreshData();
    } catch (error) { console.error('Error deleting:', error); }
}

function refreshData() {
    fetchStats();
    fetchCategories();
    loadTab(currentTab);
}
