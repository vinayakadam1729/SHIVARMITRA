import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean, DateTime, ForeignKey, Enum
)
from sqlalchemy.orm import relationship
from app.database import Base

class AdminUser(Base):
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(150), default="Store Owner")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name_en = Column(String(100), nullable=False)
    name_mr = Column(String(100), nullable=False)
    name_hi = Column(String(100), nullable=False)
    icon = Column(String(50), default="sprout")
    image_url = Column(String(500), nullable=True)
    display_order = Column(Integer, default=0)
    
    products = relationship("Product", back_populates="category")

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(150), unique=True, index=True, nullable=False)
    
    # Trilingual Names
    name_en = Column(String(200), nullable=False)
    name_mr = Column(String(200), nullable=False)
    name_hi = Column(String(200), nullable=False)
    
    # Trilingual Descriptions
    description_en = Column(Text, nullable=False)
    description_mr = Column(Text, nullable=False)
    description_hi = Column(Text, nullable=False)
    
    # Category
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Pricing & Units
    price = Column(Float, nullable=False)
    original_price = Column(Float, nullable=True)
    discount_percent = Column(Integer, default=0)
    
    # Trilingual Units (e.g. 10 kg bag / 10 किलो बॅग / 10 किग्रा थैला)
    unit_en = Column(String(50), default="1 unit")
    unit_mr = Column(String(50), default="१ नग")
    unit_hi = Column(String(50), default="१ नग")
    
    # Inventory
    stock_quantity = Column(Integer, default=50)
    in_stock = Column(Boolean, default=True)
    
    # Media & Display
    image_url = Column(String(500), nullable=False)
    badge = Column(String(50), nullable=True)  # "Best Seller", "Top Rated", "New"
    rating = Column(Float, default=4.8)
    reviews_count = Column(Integer, default=15)
    is_featured = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    category = relationship("Category", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String(50), unique=True, index=True, nullable=False)
    
    # Customer Details
    customer_name = Column(String(150), nullable=False)
    customer_phone = Column(String(20), nullable=False)
    customer_email = Column(String(100), nullable=True)
    
    # Delivery Address
    address_line = Column(String(255), nullable=False)
    village = Column(String(100), nullable=False)
    taluka = Column(String(100), nullable=False)
    district = Column(String(100), nullable=False)
    state = Column(String(100), default="Maharashtra")
    pincode = Column(String(10), nullable=False)
    delivery_notes = Column(Text, nullable=True)
    
    # Totals
    total_amount = Column(Float, nullable=False)
    discount_amount = Column(Float, default=0.0)
    delivery_fee = Column(Float, default=0.0)
    grand_total = Column(Float, nullable=False)
    
    # Status & Payment
    payment_method = Column(String(50), default="COD")  # "COD", "UPI_QR", "RAZORPAY"
    payment_status = Column(String(50), default="PENDING")  # "PENDING", "PAID", "FAILED"
    order_status = Column(String(50), default="Pending")  # "Pending", "Confirmed", "Shipped", "Delivered", "Cancelled"
    
    # WhatsApp Integration
    whatsapp_sent = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")

class OrderItem(Base):
    __tablename__ = "order_items"
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    
    product_name = Column(String(200), nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Integer, default=1)
    unit = Column(String(50), default="unit")
    subtotal = Column(Float, nullable=False)
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")
