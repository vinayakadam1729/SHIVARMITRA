/**
 * Shivar Frontend Application Logic
 */

// Cart State Manager
const Cart = {
  items: [],
  
  init() {
    try {
      const saved = localStorage.getItem("shivar_cart");
      this.items = saved ? JSON.parse(saved) : [];
    } catch (e) {
      this.items = [];
    }
    this.updateUI();
  },

  save() {
    localStorage.setItem("shivar_cart", JSON.stringify(this.items));
    this.updateUI();
  },

  addItem(product, quantity = 1) {
    const existing = this.items.find(i => i.id === product.id);
    if (existing) {
      existing.quantity += quantity;
    } else {
      this.items.push({
        id: product.id,
        name: product.name,
        name_mr: product.name_mr,
        name_hi: product.name_hi,
        name_en: product.name_en,
        price: product.price,
        unit: product.unit,
        image_url: product.image_url,
        quantity: quantity
      });
    }
    this.save();
    showToast(`${product.name} ${t('add_to_cart')}`, 'success');
  },

  removeItem(id) {
    this.items = this.items.filter(i => i.id !== id);
    this.save();
  },

  updateQuantity(id, delta) {
    const item = this.items.find(i => i.id === id);
    if (item) {
      item.quantity += delta;
      if (item.quantity <= 0) {
        this.removeItem(id);
      } else {
        this.save();
      }
    }
  },

  clear() {
    this.items = [];
    this.save();
  },

  getTotal() {
    return this.items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  },

  getCount() {
    return this.items.reduce((sum, item) => sum + item.quantity, 0);
  },

  updateUI() {
    const count = this.getCount();
    const badges = document.querySelectorAll(".cart-count-badge");
    badges.forEach(b => {
      b.innerText = count;
      b.style.display = count > 0 ? "inline-flex" : "none";
    });

    const cartDrawerItems = document.getElementById("cart-drawer-items");
    const cartDrawerTotal = document.getElementById("cart-drawer-total");
    const cartEmptyMsg = document.getElementById("cart-empty-msg");
    const cartCheckoutBtn = document.getElementById("cart-checkout-btn");

    if (cartDrawerItems) {
      if (this.items.length === 0) {
        cartDrawerItems.innerHTML = "";
        if (cartEmptyMsg) cartEmptyMsg.classList.remove("hidden");
        if (cartCheckoutBtn) cartCheckoutBtn.classList.add("hidden");
        if (cartDrawerTotal) cartDrawerTotal.innerText = "₹0";
      } else {
        if (cartEmptyMsg) cartEmptyMsg.classList.add("hidden");
        if (cartCheckoutBtn) cartCheckoutBtn.classList.remove("hidden");
        
        const lang = getLang();
        cartDrawerItems.innerHTML = this.items.map(item => {
          const name = item[`name_${lang}`] || item.name || item.name_en;
          return `
            <div class="flex items-center justify-between p-3 bg-gray-50 rounded-xl border border-gray-100 mb-2">
              <img src="${item.image_url}" class="w-14 h-14 rounded-lg object-cover border" alt="${name}">
              <div class="flex-1 ml-3">
                <h4 class="font-semibold text-gray-800 text-sm line-clamp-1">${name}</h4>
                <div class="text-xs text-gray-500">₹${item.price} / ${item.unit}</div>
                <div class="flex items-center mt-2 space-x-2">
                  <button onclick="Cart.updateQuantity(${item.id}, -1)" class="w-6 h-6 rounded bg-gray-200 text-gray-700 flex items-center justify-center font-bold text-sm hover:bg-gray-300">-</button>
                  <span class="font-bold text-sm text-gray-800">${item.quantity}</span>
                  <button onclick="Cart.updateQuantity(${item.id}, 1)" class="w-6 h-6 rounded bg-gray-200 text-gray-700 flex items-center justify-center font-bold text-sm hover:bg-gray-300">+</button>
                </div>
              </div>
              <div class="text-right">
                <div class="font-bold text-emerald-800 text-sm">₹${item.price * item.quantity}</div>
                <button onclick="Cart.removeItem(${item.id})" class="text-red-500 hover:text-red-700 text-xs mt-2">
                  <i class="fas fa-trash-alt"></i>
                </button>
              </div>
            </div>
          `;
        }).join('');
        
        if (cartDrawerTotal) {
          cartDrawerTotal.innerText = `₹${this.getTotal()}`;
        }
      }
    }
  }
};

// Toast Notifications
function showToast(message, type = 'info') {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  const bgClass = type === 'success' ? 'bg-emerald-800 text-white' : type === 'error' ? 'bg-red-700 text-white' : 'bg-gray-800 text-white';
  
  toast.className = `toast px-4 py-3 rounded-xl shadow-lg flex items-center space-x-3 text-sm font-medium ${bgClass}`;
  toast.innerHTML = `
    <span>${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = '0';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

// Global Quick Buy / Order Now Flow
function orderNowSingle(productId) {
  window.location.href = `/order?product_id=${productId}`;
}

// Open / Close Cart Drawer
function toggleCartDrawer(open = null) {
  const drawer = document.getElementById("cart-drawer");
  const backdrop = document.getElementById("cart-backdrop");
  if (!drawer) return;

  const isOpen = !drawer.classList.contains("translate-x-full");
  const shouldOpen = open !== null ? open : !isOpen;

  if (shouldOpen) {
    drawer.classList.remove("translate-x-full");
    if (backdrop) backdrop.classList.remove("hidden");
  } else {
    drawer.classList.add("translate-x-full");
    if (backdrop) backdrop.classList.add("hidden");
  }
}

// Initial setup on document ready
document.addEventListener("DOMContentLoaded", () => {
  const savedLang = getLang();
  applyLanguage(savedLang);
  Cart.init();

  // Language switch buttons
  document.querySelectorAll(".lang-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const lang = btn.getAttribute("data-lang");
      setLang(lang);
    });
  });

  // Mobile menu toggle
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");
  if (mobileMenuBtn && mobileMenu) {
    mobileMenuBtn.addEventListener("click", () => {
      mobileMenu.classList.toggle("hidden");
    });
  }
});
