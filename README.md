# 🌾 Shivar (शिवार) - Agricultural E-Commerce Marketplace

> **Production-Ready Multi-Language Agri-Commerce Platform for Farmers and Agribusiness Owners**  
> Empowering farmers with certified seeds, fertilizers, pesticides, irrigation equipment, and instant WhatsApp ordering directly with store owners.

---

## 🚜 Key Features

### 1. 👥 User Roles & Access Control
- **Owner / Store Admin**:
  - Secure authentication portal (`/admin/login`).
  - Full CRUD operations to add, edit, or delete agricultural products with trilingual details.
  - Live inventory tracking with automatic **Low Stock Alerts**.
  - Customer order management with workflow status updating (*Pending* ⏳ ➔ *Confirmed* ✔️ ➔ *Shipped* 🚚 ➔ *Delivered* 🌾 ➔ *Cancelled* ❌).
  - One-click **Excel / CSV Order Export**.
  - Direct WhatsApp button for each customer in order rows.
- **Customer / Farmer**:
  - Fast, mobile-first browsing without mandatory signup.
  - Instant search across Marathi, Hindi, and English product names and descriptions.
  - Category filters (Seeds, Fertilizers, Crop Protection, Equipment, Irrigation, Organic).
  - Flexible cart and instant 1-click **"Order Now" (आता खरेदी करा / अभी खरीदें)**.

---

### 2. ⚡ Product Browsing & Automated WhatsApp Ordering Flow
1. **Catalog & Search**: Farmer browses products, views prices, units (उदा. ४ किलो बॅग, ५०० मिली बाटली, १ नग), and stock availability.
2. **Order Now Button**: Clicking **"Order Now"** takes the customer to a dedicated checkout page.
3. **Delivery Details**: Farmer provides Name, WhatsApp Phone, Address, Village (गाव), Taluka (तालुका), District (जिल्हा), and Pincode.
4. **Order Placement**: Order number is generated (e.g. `#SHV-2608-4821`).
5. **Automated WhatsApp Redirection**: The system immediately calculates all items, prepares a localized summary in Marathi/Hindi/English, and **automatically opens WhatsApp to the owner at `9021273002`** (`https://wa.me/919021273002?text=...`) alongside direct call links (`tel:9021273002`).

---

### 3. 🌐 Multi-Language Support (Marathi, Hindi, English)
- Seamless trilingual switcher (`मराठी` | `हिंदी` | `English`) located on top bar and mobile menu.
- Complete UI translation dictionary for all labels, placeholders, badges, buttons, and alert messages.
- Full trilingual support in database models (`name_mr`, `name_hi`, `name_en`, `description_mr`, `description_hi`, `description_en`, `unit_mr`, `unit_hi`, `unit_en`).
- Persistent storage of language preference in `localStorage`.

---

### 4. 💳 Payment Integration & Options
- **Cash on Delivery (COD)**: Farmers can inspect goods at the farm/doorstep and pay cash upon delivery.
- **Dynamic UPI QR Code**: Instant 0% fee payment via PhonePe, Google Pay, BHIM, or Paytm with auto-generated transaction notes.

---

### 5. 📍 Real-Time Order Tracking
- Dedicated `/track` portal where farmers can track their delivery status using their **Order ID** or **Mobile Number** with a visual step-by-step progress timeline.

---

## 🛠️ Tech Stack & Architecture

- **Backend**: Python 3.10+ with **FastAPI** (high performance, asynchronous REST API)
- **Database**: **SQLite** (out-of-the-box zero setup) with **SQLAlchemy ORM**; seamlessly switchable to **PostgreSQL** or **MySQL**.
- **Frontend**: Responsive HTML5, **Tailwind CSS**, **FontAwesome Icons**, **Vanilla / Alpine.js** reactivity.
- **Security**: HMAC-PBKDF2-SHA256 salted password hashing, JWT bearer tokens, CORS protection.

---

## 📁 Directory Structure

```
Shivar/
├── app/
│   ├── config.py             # Environment configuration & Owner settings
│   ├── database.py           # SQLAlchemy database engine & session maker
│   ├── models.py             # Database models (AdminUser, Category, Product, Order, OrderItem)
│   ├── schemas.py            # Pydantic validation schemas
│   ├── auth.py               # Password hashing & JWT token validation
│   ├── seed_data.py          # Auto-seeding 14+ realistic agricultural products
│   └── routes/
│       ├── products.py       # Public & Admin product endpoints
│       ├── orders.py         # Order creation & WhatsApp message builder
│       ├── admin.py          # Owner dashboard statistics & order status updates
│       └── payments.py       # UPI QR code and payment methods
├── static/
│   ├── css/
│   │   └── styles.css        # Custom styles, animations, WhatsApp floating button
│   └── js/
│       ├── translations.js   # Marathi, Hindi, English dictionary
│       ├── app.js            # Customer cart, reactivity, search, order trigger
│       └── admin.js          # Owner admin dashboard logic
├── templates/
│   ├── base.html             # Base layout with navbar, language switcher, cart drawer
│   ├── index.html            # Customer storefront (hero, categories, product grid)
│   ├── product_detail.html   # Dedicated product details page
│   ├── order.html            # Dedicated order & checkout page
│   ├── order_success.html    # Confirmation & 3-second WhatsApp auto-redirect
│   ├── track_order.html      # Visual order status tracker
│   ├── admin_login.html      # Owner login page
│   └── admin_dashboard.html  # Full owner management dashboard
├── .env.example              # Environment variables template
├── .env                      # Active environment configuration
├── requirements.txt          # Python dependencies
├── Dockerfile                # Production container specification
├── docker-compose.yml        # Multi-container orchestration
├── run.py                    # Python launch script
├── start.bat                 # Windows 1-click batch launcher
├── start.ps1                 # PowerShell 1-click launcher
└── README.md                 # Documentation
```

---

## 🚀 Quick Start (Local Setup)

### 1. Run with Python
Ensure Python 3.10+ is installed:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the application
python run.py
```
Or on Windows, simply double-click **`start.bat`**.

The server will start at:
- 🛒 **Customer Storefront**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- 📦 **Order Tracking**: [http://127.0.0.1:8000/track](http://127.0.0.1:8000/track)
- 👑 **Owner Admin Dashboard**: [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin)
- 🔑 **Default Admin Login**:
  - **Username**: `admin@shivar.com`
  - **Password**: `shivar@2026`
- 📚 **Interactive API Docs (Swagger)**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

## 🐳 Docker Deployment

To launch with Docker:
```bash
docker-compose up --build -d
```
The application will be accessible on port `8000`.

---

## ⚙️ Environment Configuration (`.env`)

| Variable | Default Value | Description |
|---|---|---|
| `OWNER_PHONE` | `9021273002` | Primary phone for direct farmer calls |
| `OWNER_WHATSAPP` | `9021273002` | WhatsApp number for automated order routing |
| `OWNER_NAME` | `Shivar Krushi Seva Kendra` | Store display title |
| `ADMIN_USERNAME` | `admin@shivar.com` | Owner login username |
| `ADMIN_PASSWORD` | `shivar@2026` | Owner login password |
| `DATABASE_URL` | `sqlite:///./shivar.db` | Database connection URI (SQLite / PostgreSQL) |
| `SECRET_KEY` | *(Secure String)* | JWT and session signing secret |

---

## 📱 WhatsApp Integration Details

When an order is submitted:
1. An order record is saved with unique ID `#SHV-YYMMDD-XXXX`.
2. A localized message string is generated containing the farmer's name, phone, village address, items ordered with units and subtotals, grand total, and payment method.
3. The customer's browser automatically navigates to:
   ```
   https://wa.me/919021273002?text=<ENCODED_ORDER_DETAILS>
   ```
4. If WhatsApp doesn't open automatically, a prominent button and a direct phone call button are provided.

---

## 📄 License & Credits

Created for **Shivar Agricultural Marketplace (शिवार कृषी बाजारपेठ)**.  
Empowering Indian agriculture through modern digital technology.
#   S H I V A R M A R T  
 