from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime

# Category Schemas
class CategoryBase(BaseModel):
    slug: str
    name_en: str
    name_mr: str
    name_hi: str
    icon: Optional[str] = "sprout"
    image_url: Optional[str] = None
    display_order: Optional[int] = 0

class CategoryOut(CategoryBase):
    id: int
    class Config:
        from_attributes = True

# Product Schemas
class ProductBase(BaseModel):
    name_en: str
    name_mr: str
    name_hi: str
    description_en: str
    description_mr: str
    description_hi: str
    category_id: int
    price: float
    original_price: Optional[float] = None
    discount_percent: Optional[int] = 0
    unit_en: str = "1 unit"
    unit_mr: str = "१ नग"
    unit_hi: str = "१ नग"
    stock_quantity: int = 50
    in_stock: bool = True
    image_url: str
    badge: Optional[str] = None
    is_featured: bool = False

class ProductCreate(ProductBase):
    slug: Optional[str] = None

class ProductUpdate(BaseModel):
    name_en: Optional[str] = None
    name_mr: Optional[str] = None
    name_hi: Optional[str] = None
    description_en: Optional[str] = None
    description_mr: Optional[str] = None
    description_hi: Optional[str] = None
    category_id: Optional[int] = None
    price: Optional[float] = None
    original_price: Optional[float] = None
    discount_percent: Optional[int] = None
    unit_en: Optional[str] = None
    unit_mr: Optional[str] = None
    unit_hi: Optional[str] = None
    stock_quantity: Optional[int] = None
    in_stock: Optional[bool] = None
    image_url: Optional[str] = None
    badge: Optional[str] = None
    is_featured: Optional[bool] = None

class ProductOut(ProductBase):
    id: int
    slug: str
    rating: float
    reviews_count: int
    created_at: datetime
    category: Optional[CategoryOut] = None

    class Config:
        from_attributes = True

# Order Schemas
class OrderItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    price: float
    quantity: int = 1
    unit: str = "unit"

class OrderCreate(BaseModel):
    customer_name: str
    customer_phone: str
    customer_email: Optional[str] = None
    address_line: str
    village: str
    taluka: str
    district: str
    state: str = "Maharashtra"
    pincode: str
    delivery_notes: Optional[str] = None
    payment_method: str = "COD"  # "COD", "UPI_QR", "RAZORPAY"
    items: List[OrderItemCreate]
    preferred_language: Optional[str] = "mr"

class OfflineSaleCreate(BaseModel):
    customer_name: Optional[str] = "Offline Sale"
    amount: float

class OrderItemOut(BaseModel):
    id: int
    product_id: Optional[int]
    product_name: str
    price: float
    quantity: int
    unit: str
    subtotal: float

    class Config:
        from_attributes = True

class OrderOut(BaseModel):
    id: int
    order_number: str
    customer_name: str
    customer_phone: str
    customer_email: Optional[str]
    address_line: str
    village: str
    taluka: str
    district: str
    state: str
    pincode: str
    delivery_notes: Optional[str]
    total_amount: float
    discount_amount: float
    delivery_fee: float
    grand_total: float
    payment_method: str
    payment_status: str
    order_status: str
    whatsapp_sent: bool
    created_at: datetime
    items: List[OrderItemOut]

    class Config:
        from_attributes = True

class OrderStatusUpdate(BaseModel):
    order_status: str  # Pending, Confirmed, Shipped, Delivered, Cancelled
    payment_status: Optional[str] = None

# Admin Schemas
class AdminLogin(BaseModel):
    username: str
    password: str

class AdminToken(BaseModel):
    access_token: str
    token_type: str = "bearer"
    admin_name: str

class AdminProfileUpdate(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None

class AdminPasswordChange(BaseModel):
    current_password: str
    new_password: str

