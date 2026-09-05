/**
 * Shivar Admin Dashboard Logic
 */

const AdminApp = {
  token: localStorage.getItem("shivar_admin_token") || null,
  activeTab: "orders",

  init() {
    this.checkAuth();
    this.bindEvents();
  },

  checkAuth() {
    if (!this.token) {
      if (window.location.pathname.includes("/admin") && !window.location.pathname.includes("/login")) {
        window.location.href = "/admin/login";
      }
      return;
    }

    // Verify token with backend
    fetch("/api/admin/me", {
      headers: { "Authorization": `Bearer ${this.token}` }
    })
    .then(res => {
      if (!res.ok) throw new Error("Invalid session");
      return res.json();
    })
    .then(user => {
      const nameEl = document.getElementById("admin-user-name");
      if (nameEl) nameEl.innerText = user.full_name || "Store Owner";
      this.loadDashboardStats();
      this.loadOrders();
      this.loadProducts();
    })
    .catch(() => {
      this.logout();
    });
  },

  logout() {
    localStorage.removeItem("shivar_admin_token");
    fetch("/api/admin/logout", { method: "POST" }).finally(() => {
      window.location.href = "/admin/login";
    });
  },

  bindEvents() {
    const logoutBtn = document.getElementById("admin-logout-btn");
    if (logoutBtn) logoutBtn.addEventListener("click", () => this.logout());

    // Tab switching
    document.querySelectorAll(".admin-tab-btn").forEach(btn => {
      btn.addEventListener("click", () => {
        const tab = btn.getAttribute("data-tab");
        this.switchTab(tab);
      });
    });
  },

  switchTab(tab) {
    this.activeTab = tab;
    document.querySelectorAll(".admin-tab-btn").forEach(btn => {
      if (btn.getAttribute("data-tab") === tab) {
        btn.classList.add("bg-emerald-700", "text-white");
        btn.classList.remove("text-gray-600", "hover:bg-gray-100");
      } else {
        btn.classList.remove("bg-emerald-700", "text-white");
        btn.classList.add("text-gray-600", "hover:bg-gray-100");
      }
    });

    document.querySelectorAll(".admin-tab-pane").forEach(pane => {
      pane.classList.add("hidden");
    });
    const activePane = document.getElementById(`tab-${tab}`);
    if (activePane) activePane.classList.remove("hidden");
  },

  async loadDashboardStats() {
    try {
      const res = await fetch("/api/admin/dashboard-stats", {
        headers: { "Authorization": `Bearer ${this.token}` }
      });
      const data = await res.json();

      document.getElementById("stat-revenue").innerText = `₹${data.today_revenue.toLocaleString()}`;
      document.getElementById("stat-orders").innerText = data.today_orders;
      document.getElementById("stat-pending").innerText = data.pending_orders;
      document.getElementById("stat-products").innerText = data.total_products;
      
      const lowStockAlert = document.getElementById("low-stock-alert-box");
      if (lowStockAlert) {
        if (data.low_stock_products > 0) {
          lowStockAlert.classList.remove("hidden");
          document.getElementById("low-stock-count").innerText = data.low_stock_products;
        } else {
          lowStockAlert.classList.add("hidden");
        }
      }
    } catch (e) {
      console.error("Failed to load dashboard stats", e);
    }
  },

  async loadOrders(status = "all", search = "") {
    try {
      let url = `/api/admin/orders?status_filter=${status}`;
      if (search) url += `&search=${encodeURIComponent(search)}`;

      const res = await fetch(url, {
        headers: { "Authorization": `Bearer ${this.token}` }
      });
      const orders = await res.json();
      this.renderOrdersTable(orders);
    } catch (e) {
      console.error("Failed to load orders", e);
    }
  },

  renderOrdersTable(orders) {
    const tbody = document.getElementById("orders-table-body");
    if (!tbody) return;

    if (orders.length === 0) {
      tbody.innerHTML = `<tr><td colspan="7" class="text-center py-8 text-gray-500 font-medium">कोणतीही ऑर्डर आढळली नाही (No orders found)</td></tr>`;
      return;
    }

    tbody.innerHTML = orders.map(o => {
      const statusColors = {
        'Pending': 'bg-amber-100 text-amber-800 border-amber-300',
        'Confirmed': 'bg-blue-100 text-blue-800 border-blue-300',
        'Shipped': 'bg-purple-100 text-purple-800 border-purple-300',
        'Delivered': 'bg-emerald-100 text-emerald-800 border-emerald-300',
        'Cancelled': 'bg-red-100 text-red-800 border-red-300'
      };
      const badgeClass = statusColors[o.order_status] || 'bg-gray-100 text-gray-800';

      const itemsList = o.items.map(i => `<span class="inline-block bg-gray-100 px-2 py-0.5 rounded text-xs mr-1 mb-1 font-medium">${i.product_name} (${i.quantity} ${i.unit})</span>`).join('');

      return `
        <tr class="border-b hover:bg-gray-50 transition">
          <td class="px-4 py-3 font-mono font-bold text-emerald-800 text-sm">#${o.order_number}</td>
          <td class="px-4 py-3 text-xs text-gray-500">${o.created_at}</td>
          <td class="px-4 py-3">
            <div class="font-bold text-gray-800 text-sm">${o.customer_name}</div>
            <div class="text-xs text-gray-600 font-mono"><i class="fas fa-phone mr-1 text-emerald-600"></i>${o.customer_phone}</div>
            <div class="text-xs text-gray-500 line-clamp-1">${o.address}</div>
          </td>
          <td class="px-4 py-3">${itemsList}</td>
          <td class="px-4 py-3 font-bold text-gray-900 text-sm">₹${o.grand_total}</td>
          <td class="px-4 py-3">
            <select onchange="AdminApp.updateOrderStatus(${o.id}, this.value)" class="text-xs font-semibold rounded-lg px-2.5 py-1.5 border shadow-sm ${badgeClass} cursor-pointer focus:outline-none">
              <option value="Pending" ${o.order_status === 'Pending' ? 'selected' : ''}>⏳ Pending (प्रलंबित)</option>
              <option value="Confirmed" ${o.order_status === 'Confirmed' ? 'selected' : ''}>✔️ Confirmed (स्वीकृत)</option>
              <option value="Shipped" ${o.order_status === 'Shipped' ? 'selected' : ''}>🚚 Shipped (मार्गावर)</option>
              <option value="Delivered" ${o.order_status === 'Delivered' ? 'selected' : ''}>🌾 Delivered (पोहोचले)</option>
              <option value="Cancelled" ${o.order_status === 'Cancelled' ? 'selected' : ''}>❌ Cancelled (रद्द)</option>
            </select>
          </td>
          <td class="px-4 py-3 text-right">
            <div class="flex items-center justify-end flex-wrap gap-1.5">
              <!-- View / Print Bill Button -->
              <a href="/invoice/${o.order_number}" target="_blank" class="inline-flex items-center text-xs px-2.5 py-1.5 bg-blue-50 text-blue-700 border border-blue-200 font-bold rounded-lg hover:bg-blue-100 transition shadow-sm" title="बिल प्रिंट करा">
                <i class="fas fa-file-invoice text-blue-600 mr-1"></i> बिल
              </a>

              <!-- Send Bill via WhatsApp -->
              <a href="https://wa.me/91${o.customer_phone}?text=${encodeURIComponent('🌾 *शिवार कृषी सेवा केंद्र - खरेदी बिल* 🌾\n\nनमस्कार ' + o.customer_name + ' जी,\nआपली ऑर्डर #' + o.order_number + ' यशस्वीरित्या डिलिव्हर झाली आहे.\n💰 एकूण रक्कम: ₹' + o.grand_total + '\n\n📄 ऑनलाईन बिल:\n' + window.location.origin + '/invoice/' + o.order_number + '\n\nधन्यवाद!')}" target="_blank" class="inline-flex items-center text-xs px-2.5 py-1.5 bg-emerald-600 text-white font-bold rounded-lg hover:bg-emerald-700 transition shadow-sm" title="WhatsApp वर बिल पाठवा">
                <i class="fab fa-whatsapp mr-1"></i> पाठवा
              </a>

              <!-- Edit Revenue / Amount -->
              <button onclick="AdminApp.editOrderAmount(${o.id}, ${o.grand_total})" class="inline-flex items-center text-xs px-2.5 py-1.5 bg-yellow-50 text-yellow-700 border border-yellow-200 font-bold rounded-lg hover:bg-yellow-100 transition shadow-sm" title="रक्कम बदला (Edit Revenue)">
                <i class="fas fa-edit mr-1"></i> रक्कम
              </button>

              <!-- Delete Order -->
              <button onclick="AdminApp.deleteOrder(${o.id}, '${o.order_number}')" class="inline-flex items-center text-xs px-2.5 py-1.5 bg-red-50 text-red-600 border border-red-200 font-bold rounded-lg hover:bg-red-100 transition shadow-sm" title="ऑर्डर डिलीट करा">
                <i class="fas fa-trash mr-1"></i> डिलीट
              </button>
            </div>
          </td>
        </tr>
      `;
    }).join('');
  },

  async updateOrderStatus(orderId, newStatus) {
    try {
      const res = await fetch(`/api/admin/orders/${orderId}/status`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.token}`
        },
        body: JSON.stringify({ order_status: newStatus })
      });
      if (!res.ok) throw new Error("Failed to update");
      showToast(`Order #${orderId} status updated to ${newStatus}`, "success");
      this.loadDashboardStats();
    } catch (e) {
      showToast("Error updating order status", "error");
    }
  },

  async deleteOrder(orderId, orderNumber) {
    const confirmed = confirm(`⚠️ ऑर्डर #${orderNumber} कायमची डिलीट करायची आहे का?\n\nहे action परत होणार नाही!`);
    if (!confirmed) return;
    try {
      const res = await fetch(`/api/admin/orders/${orderId}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${this.token}` }
      });
      if (!res.ok) throw new Error("Failed to delete");
      showToast(`ऑर्डर #${orderNumber} डिलीट झाली!`, "success");
      this.fetchOrders();
      this.fetchDashboardStats();
    } catch (e) {
      showToast("Error deleting order", "error");
    }
  },

  async editOrderAmount(orderId, currentAmount) {
    const newAmount = prompt(`ऑर्डर #${orderId} ची नवीन रक्कम टाका:\n(सध्याची रक्कम: ₹${currentAmount})`, currentAmount);
    if (newAmount === null) return; // Cancelled
    const parsed = parseFloat(newAmount);
    if (isNaN(parsed) || parsed < 0) {
      alert("कृपया योग्य रक्कम टाका!");
      return;
    }
    try {
      const res = await fetch(`/api/admin/orders/${orderId}/edit-amount`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.token}`
        },
        body: JSON.stringify({ grand_total: parsed })
      });
      if (!res.ok) throw new Error("Failed to update amount");
      showToast(`रक्कम ₹${parsed} वर अपडेट झाली!`, "success");
      this.fetchOrders();
      this.fetchDashboardStats();
    } catch (e) {
      showToast("Error updating amount", "error");
    }
  },

  async loadProducts() {
    try {
      const res = await fetch("/api/products?lang=mr");
      const products = await res.json();
      this.renderProductsTable(products);
    } catch (e) {
      console.error("Failed to load products", e);
    }
  },

  renderProductsTable(products) {
    const tbody = document.getElementById("products-table-body");
    if (!tbody) return;

    tbody.innerHTML = products.map(p => {
      const stockBadge = p.stock_quantity <= 5 
        ? `<span class="px-2 py-0.5 rounded text-xs bg-red-100 text-red-800 font-bold">कमी साठा (${p.stock_quantity})</span>`
        : `<span class="px-2 py-0.5 rounded text-xs bg-emerald-100 text-emerald-800 font-semibold">${p.stock_quantity} नग</span>`;

      return `
        <tr class="border-b hover:bg-gray-50 transition">
          <td class="px-4 py-3">
            <div class="flex items-center space-x-3">
              <img src="${p.image_url}" class="w-12 h-12 object-cover rounded-lg border" alt="${p.name_mr}">
              <div>
                <div class="font-bold text-gray-900 text-sm">${p.name_mr}</div>
                <div class="text-xs text-gray-500">${p.name_en}</div>
              </div>
            </div>
          </td>
          <td class="px-4 py-3 text-xs font-semibold text-emerald-800">${p.category_name}</td>
          <td class="px-4 py-3 font-bold text-gray-900 text-sm">₹${p.price} <span class="text-xs font-normal text-gray-500">/${p.unit_mr}</span></td>
          <td class="px-4 py-3">${stockBadge}</td>
          <td class="px-4 py-3">
            <span class="px-2.5 py-1 rounded-full text-xs font-bold ${p.in_stock ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
              ${p.in_stock ? 'सक्रिय' : 'बंद'}
            </span>
          </td>
          <td class="px-4 py-3 text-right space-x-2">
            <button onclick="AdminApp.openEditProductModal(${p.id})" class="px-3 py-1 bg-amber-50 text-amber-700 border border-amber-200 rounded-lg text-xs font-semibold hover:bg-amber-100">
              <i class="fas fa-edit mr-1"></i> संपादन
            </button>
            <button onclick="AdminApp.deleteProduct(${p.id}, '${p.name_mr}')" class="px-3 py-1 bg-red-50 text-red-700 border border-red-200 rounded-lg text-xs font-semibold hover:bg-red-100">
              <i class="fas fa-trash-alt mr-1"></i> हटवा
            </button>
          </td>
        </tr>
      `;
    }).join('');
  },

  openOfflineSaleModal() {
    document.getElementById("offline-sale-form").reset();
    document.getElementById("offline-sale-modal").classList.remove("hidden");
  },
  
  closeOfflineSaleModal() {
    document.getElementById("offline-sale-modal").classList.add("hidden");
  },
  
  async submitOfflineSale(event) {
    event.preventDefault();
    const customer_name = document.getElementById("offline-customer-name").value.trim();
    const amount = parseFloat(document.getElementById("offline-amount").value);
    
    try {
      const res = await fetch("/api/admin/offline-sale", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.token}`
        },
        body: JSON.stringify({
          customer_name: customer_name,
          amount: amount
        })
      });
      
      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "विक्री जोडता आली नाही.");
      }
      
      this.closeOfflineSaleModal();
      alert("विक्री यशस्वीरित्या जोडली गेली! (Sale added successfully)");
      this.fetchDashboardStats(); // Refresh dashboard to show new revenue/orders
      this.fetchOrders();         // Refresh orders table
    } catch (e) {
      alert("Error: " + e.message);
    }
  },

  openAddProductModal() {
    document.getElementById("product-modal-title").innerText = "नवीन कृषी उत्पादन जोडा (Add Product)";
    document.getElementById("product-form").reset();
    document.getElementById("product-form-id").value = "";
    document.getElementById("product-modal").classList.remove("hidden");
  },

  async openEditProductModal(productId) {
    try {
      const res = await fetch(`/api/products/${productId}?lang=en`);
      const p = await res.json();

      document.getElementById("product-modal-title").innerText = `उत्पादन संपादन: ${p.name_mr}`;
      document.getElementById("product-form-id").value = p.id;
      
      document.getElementById("p-name-en").value = p.name_en || "";
      document.getElementById("p-name-mr").value = p.name_mr || "";
      document.getElementById("p-name-hi").value = p.name_hi || "";
      
      document.getElementById("p-desc-en").value = p.description_en || "";
      document.getElementById("p-desc-mr").value = p.description_mr || "";
      document.getElementById("p-desc-hi").value = p.description_hi || "";

      document.getElementById("p-category").value = p.category_id;
      document.getElementById("p-price").value = p.price;
      document.getElementById("p-original-price").value = p.original_price || p.price;
      document.getElementById("p-unit-en").value = p.unit_en || "1 unit";
      document.getElementById("p-unit-mr").value = p.unit_mr || "१ नग";
      document.getElementById("p-unit-hi").value = p.unit_hi || "१ नग";
      document.getElementById("p-stock").value = p.stock_quantity;
      document.getElementById("p-image").value = p.image_url;
      document.getElementById("p-badge").value = p.badge || "";
      document.getElementById("p-in-stock").checked = p.in_stock;

      document.getElementById("product-modal").classList.remove("hidden");
    } catch (e) {
      showToast("Failed to fetch product data", "error");
    }
  },

  closeProductModal() {
    document.getElementById("product-modal").classList.add("hidden");
  },

  async saveProduct(event) {
    event.preventDefault();
    const id = document.getElementById("product-form-id").value;

    const payload = {
      name_en: document.getElementById("p-name-en").value.trim(),
      name_mr: document.getElementById("p-name-mr").value.trim(),
      name_hi: document.getElementById("p-name-hi").value.trim(),
      description_en: document.getElementById("p-desc-en").value.trim(),
      description_mr: document.getElementById("p-desc-mr").value.trim(),
      description_hi: document.getElementById("p-desc-hi").value.trim(),
      category_id: parseInt(document.getElementById("p-category").value),
      price: parseFloat(document.getElementById("p-price").value),
      original_price: parseFloat(document.getElementById("p-original-price").value) || parseFloat(document.getElementById("p-price").value),
      unit_en: document.getElementById("p-unit-en").value.trim(),
      unit_mr: document.getElementById("p-unit-mr").value.trim(),
      unit_hi: document.getElementById("p-unit-hi").value.trim(),
      stock_quantity: parseInt(document.getElementById("p-stock").value),
      in_stock: document.getElementById("p-in-stock").checked,
      image_url: document.getElementById("p-image").value.trim(),
      badge: document.getElementById("p-badge").value.trim() || null,
      is_featured: true
    };

    try {
      const url = id ? `/api/admin/products/${id}` : `/api/admin/products`;
      const method = id ? "PUT" : "POST";

      const res = await fetch(url, {
        method: method,
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.token}`
        },
        body: JSON.stringify(payload)
      });

      if (!res.ok) throw new Error("Failed to save product");
      
      showToast(id ? "उत्पादन यशस्वीरित्या अपडेट केले!" : "नवीन उत्पादन जोडले गेले!", "success");
      this.closeProductModal();
      this.loadProducts();
      this.loadDashboardStats();
    } catch (e) {
      showToast("त्रुटी: उत्पादन सेव्ह करता आले नाही", "error");
    }
  },

  async deleteProduct(id, name) {
    if (!confirm(`तुम्हाला नक्की "${name}" हे उत्पादन हटवायचे आहे का?`)) return;

    try {
      const res = await fetch(`/api/admin/products/${id}`, {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${this.token}` }
      });
      if (!res.ok) throw new Error("Failed to delete");
      showToast("उत्पादन हटवले गेले!", "success");
      this.loadProducts();
      this.loadDashboardStats();
    } catch (e) {
      showToast("उत्पादन हटवताना त्रुटी आली", "error");
    }
  },

  exportCSV() {
    window.location.href = `/api/admin/orders/export-csv`;
  },

  async updateProfile(event) {
    event.preventDefault();
    const btn = document.getElementById("admin-profile-save-btn");
    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1"></i> सेव्ह करत आहे...`;

    const payload = {
      full_name: document.getElementById("setting-fullname").value.trim(),
      username: document.getElementById("setting-email").value.trim()
    };

    try {
      const res = await fetch("/api/admin/profile", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.token}`
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to update profile");

      if (data.access_token) {
        this.token = data.access_token;
        localStorage.setItem("shivar_admin_token", data.access_token);
      }

      document.getElementById("admin-user-name").innerText = data.full_name;
      showToast(data.message, "success");
    } catch (e) {
      showToast(`त्रुटी: ${e.message}`, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<i class="fas fa-save mr-1"></i> माहिती सेव्ह करा`;
    }
  },

  async changePassword(event) {
    event.preventDefault();
    const btn = document.getElementById("admin-pwd-save-btn");
    const newPwd = document.getElementById("setting-new-pwd").value;
    const confirmPwd = document.getElementById("setting-confirm-pwd").value;

    if (newPwd !== confirmPwd) {
      showToast("नवीन पासवर्ड आणि पुष्टीकरण पासवर्ड जुळत नाहीत", "error");
      return;
    }

    btn.disabled = true;
    btn.innerHTML = `<i class="fas fa-spinner fa-spin mr-1"></i> पासवर्ड बदलत आहे...`;

    const payload = {
      current_password: document.getElementById("setting-curr-pwd").value,
      new_password: newPwd
    };

    try {
      const res = await fetch("/api/admin/change-password", {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${this.token}`
        },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to change password");

      showToast(data.message, "success");
      document.getElementById("admin-pwd-form").reset();
    } catch (e) {
      showToast(`त्रुटी: ${e.message}`, "error");
    } finally {
      btn.disabled = false;
      btn.innerHTML = `<i class="fas fa-key mr-1"></i> नवीन पासवर्ड सेट करा`;
    }
  }
};

document.addEventListener("DOMContentLoaded", () => {
  AdminApp.init();
});
