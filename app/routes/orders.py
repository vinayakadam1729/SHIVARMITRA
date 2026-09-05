import urllib.parse
import random
import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import desc

from app.database import get_db
from app.models import Order, OrderItem, Product, AdminUser
from app.schemas import OrderCreate, OrderOut, OrderStatusUpdate
from app.auth import get_current_admin
from app.config import settings

router = APIRouter(prefix="/api/orders", tags=["orders"])

def generate_order_number() -> str:
    """Generate a clean, unique order reference e.g., SHV-2608-7891"""
    now = datetime.datetime.now()
    date_str = now.strftime("%y%m%d")
    rand_digits = random.randint(1000, 9999)
    return f"SHV-{date_str}-{rand_digits}"

def build_whatsapp_message(order: Order, lang: str = "mr") -> str:
    """Build prefilled WhatsApp message to the owner (9021273002) in Marathi/Hindi/English."""
    owner_phone = settings.OWNER_WHATSAPP
    
    items_text = ""
    for item in order.items:
        items_text += f"• {item.product_name} x {item.quantity} {item.unit} = ₹{int(item.subtotal)}\n"
        
    full_address = f"{order.address_line}, {order.village}, ता. {order.taluka}, जि. {order.district}, पिन: {order.pincode}"

    if lang == "mr":
        msg = (
            f"🌾 *नवीन शिवार कृषी ऑर्डर* 🌾\n\n"
            f"📋 *ऑर्डर क्र:* #{order.order_number}\n"
            f"👤 *शेतकरी नाव:* {order.customer_name}\n"
            f"📱 *मोबाईल क्र:* {order.customer_phone}\n"
            f"📍 *पत्ता:* {full_address}\n\n"
            f"📦 *ऑर्डर साहित्य:*\n{items_text}\n"
            f"💰 *एकूण रक्कम:* ₹{int(order.grand_total)}\n"
            f"💳 *पेमेंट पद्धत:* {order.payment_method}\n"
            f"📝 *नोंद:* {order.delivery_notes or 'लागू नाही'}\n\n"
            f"कृपया माझी ऑर्डर कन्फर्म करून डिलिव्हरीची माहिती द्यावी. धन्यवाद!"
        )
    elif lang == "hi":
        msg = (
            f"🌾 *नई शिवार कृषि ऑर्डर* 🌾\n\n"
            f"📋 *ऑर्डर नं:* #{order.order_number}\n"
            f"👤 *किसान का नाम:* {order.customer_name}\n"
            f"📱 *मोबाइल नं:* {order.customer_phone}\n"
            f"📍 *पता:* {full_address}\n\n"
            f"📦 *ऑर्डर सामग्री:*\n{items_text}\n"
            f"💰 *कुल राशि:* ₹{int(order.grand_total)}\n"
            f"💳 *भुगतान विधि:* {order.payment_method}\n"
            f"📝 *टिप्पणी:* {order.delivery_notes or 'लागू नहीं'}\n\n"
            f"कृपया मेरी ऑर्डर की पुष्टि करें और डिलीवरी का विवरण साझा करें। धन्यवाद!"
        )
    else:  # English
        msg = (
            f"🌾 *New Shivar Agricultural Order* 🌾\n\n"
            f"📋 *Order ID:* #{order.order_number}\n"
            f"👤 *Customer:* {order.customer_name}\n"
            f"📱 *Phone:* {order.customer_phone}\n"
            f"📍 *Address:* {full_address}\n\n"
            f"📦 *Order Items:*\n{items_text}\n"
            f"💰 *Grand Total:* ₹{int(order.grand_total)}\n"
            f"💳 *Payment Method:* {order.payment_method}\n"
            f"📝 *Notes:* {order.delivery_notes or 'N/A'}\n\n"
            f"Please confirm my order and share delivery schedule. Thank you!"
        )
        
    encoded_text = urllib.parse.quote(msg)
    return f"https://wa.me/91{owner_phone}?text={encoded_text}"

@router.post("", status_code=status.HTTP_201_CREATED)
def place_order(order_data: OrderCreate, db: Session = Depends(get_db)):
    """Customer: Place a new order with auto-generated order tracking & WhatsApp redirection URL."""
    if not order_data.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")
        
    # Calculate totals and process inventory
    total_amount = 0.0
    order_items_objs = []
    
    for item in order_data.items:
        subtotal = item.price * item.quantity
        total_amount += subtotal
        
        # Check and update product inventory if product_id is provided
        if item.product_id:
            product = db.query(Product).filter(Product.id == item.product_id).first()
            if product:
                if product.stock_quantity >= item.quantity:
                    product.stock_quantity -= item.quantity
                    if product.stock_quantity == 0:
                        product.in_stock = False
                        
        order_item = OrderItem(
            product_id=item.product_id,
            product_name=item.product_name,
            price=item.price,
            quantity=item.quantity,
            unit=item.unit,
            subtotal=subtotal
        )
        order_items_objs.append(order_item)
        
    # Delivery fee calculation (Free delivery above ₹1000)
    delivery_fee = 0.0 if total_amount >= 1000 else 50.0
    discount_amount = 0.0
    grand_total = total_amount + delivery_fee - discount_amount
    
    order_number = generate_order_number()
    
    order = Order(
        order_number=order_number,
        customer_name=order_data.customer_name.strip(),
        customer_phone=order_data.customer_phone.strip(),
        customer_email=order_data.customer_email.strip() if order_data.customer_email else None,
        address_line=order_data.address_line.strip(),
        village=order_data.village.strip(),
        taluka=order_data.taluka.strip(),
        district=order_data.district.strip(),
        state=order_data.state.strip(),
        pincode=order_data.pincode.strip(),
        delivery_notes=order_data.delivery_notes.strip() if order_data.delivery_notes else None,
        total_amount=total_amount,
        discount_amount=discount_amount,
        delivery_fee=delivery_fee,
        grand_total=grand_total,
        payment_method=order_data.payment_method,
        payment_status="PAID" if order_data.payment_method == "UPI_QR" else "PENDING",
        order_status="Confirmed" if order_data.payment_method == "UPI_QR" else "Pending",
        items=order_items_objs
    )
    
    db.add(order)
    db.commit()
    db.refresh(order)
    
    # Generate WhatsApp URL
    whatsapp_url = build_whatsapp_message(order, lang=order_data.preferred_language or "mr")
    
    return {
        "success": True,
        "message": "Order placed successfully!",
        "order_number": order.order_number,
        "order_id": order.id,
        "grand_total": order.grand_total,
        "customer_phone": order.customer_phone,
        "whatsapp_url": whatsapp_url,
        "owner_phone": settings.OWNER_PHONE,
        "direct_call_url": f"tel:{settings.OWNER_PHONE}"
    }

@router.get("/track/{identifier}")
def track_order(identifier: str, db: Session = Depends(get_db)):
    """Customer: Track order by Order Number or Phone Number."""
    identifier = identifier.strip()
    order = db.query(Order).filter(
        (Order.order_number == identifier) | (Order.customer_phone == identifier)
    ).order_by(desc(Order.created_at)).first()
    
    if not order:
        raise HTTPException(status_code=404, detail="No order found with provided details.")
        
    return {
        "id": order.id,
        "order_number": order.order_number,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "address": f"{order.address_line}, {order.village}, {order.taluka}, {order.district} - {order.pincode}",
        "total_amount": order.total_amount,
        "delivery_fee": order.delivery_fee,
        "grand_total": order.grand_total,
        "payment_method": order.payment_method,
        "payment_status": order.payment_status,
        "order_status": order.order_status,
        "created_at": order.created_at.strftime("%d %b %Y, %I:%M %p"),
        "items": [
            {
                "product_name": item.product_name,
                "price": item.price,
                "quantity": item.quantity,
                "unit": item.unit,
                "subtotal": item.subtotal
            } for item in order.items
        ]
    }
