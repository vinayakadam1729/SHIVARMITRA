import io
import csv
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.database import get_db
from app.models import AdminUser, Order, OrderItem, Product, Category
from app.schemas import (
    ProductCreate, ProductUpdate, ProductOut,
    OrderOut, OrderStatusUpdate, AdminProfileUpdate, AdminPasswordChange, OfflineSaleCreate,
    AdminLogin, AdminToken
)
from app.auth import verify_password, hash_password, create_access_token, get_current_admin
from app.config import settings

router = APIRouter(prefix="/api/admin", tags=["admin"])

@router.post("/login", response_model=AdminToken)
def admin_login(creds: AdminLogin, response: Response, db: Session = Depends(get_db)):
    """Owner / Admin login."""
    user = db.query(AdminUser).filter(AdminUser.username == creds.username.strip()).first()
    if not user or not verify_password(creds.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
        
    token = create_access_token(data={"sub": user.username, "name": user.full_name})
    
    response.set_cookie(
        key="admin_token",
        value=token,
        httponly=True,
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        samesite="lax"
    )
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "admin_name": user.full_name
    }

@router.post("/logout")
def admin_logout(response: Response):
    """Owner logout, clear cookie."""
    response.delete_cookie("admin_token")
    return {"message": "Logged out successfully"}

@router.get("/me")
def get_admin_profile(admin: AdminUser = Depends(get_current_admin)):
    """Get current logged in admin user."""
    return {
        "id": admin.id,
        "username": admin.username,
        "full_name": admin.full_name
    }

@router.put("/profile")
def update_admin_profile(
    data: AdminProfileUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update admin full name or email/username."""
    if data.username:
        new_username = data.username.strip()
        existing = db.query(AdminUser).filter(AdminUser.username == new_username, AdminUser.id != admin.id).first()
        if existing:
            raise HTTPException(status_code=400, detail="हा ईमेल / युझरनेम आधीपासून वापरात आहे (Username already in use)")
        admin.username = new_username
        
    if data.full_name:
        admin.full_name = data.full_name.strip()
        
    db.commit()
    db.refresh(admin)
    
    new_token = create_access_token(data={"sub": admin.username, "name": admin.full_name})
    return {
        "message": "प्रोफाइल माहिती अपडेट केली गेली आहे (Profile updated)",
        "username": admin.username,
        "full_name": admin.full_name,
        "access_token": new_token
    }

@router.put("/change-password")
def change_admin_password(
    data: AdminPasswordChange,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Change admin password securely."""
    if not verify_password(data.current_password, admin.hashed_password):
        raise HTTPException(status_code=400, detail="सध्याचा पासवर्ड चुकीचा आहे (Current password incorrect)")
        
    if len(data.new_password) < 4:
        raise HTTPException(status_code=400, detail="नवीन पासवर्ड किमान ४ अक्षरांचा असावा (New password too short)")
        
    admin.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "पासवर्ड यशस्वीरित्या बदलला गेला आहे (Password updated successfully)"}


@router.get("/dashboard-stats")
def get_dashboard_stats(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get summary metrics for owner dashboard."""
    from datetime import date
    today = date.today()
    
    total_orders = db.query(Order).count()
    today_orders = db.query(Order).filter(func.date(Order.created_at) == today).count()
    
    pending_orders = db.query(Order).filter(Order.order_status == "Pending").count()
    completed_orders = db.query(Order).filter(Order.order_status == "Delivered").count()
    
    total_revenue = db.query(func.sum(Order.grand_total)).scalar() or 0.0
    today_revenue = db.query(func.sum(Order.grand_total)).filter(func.date(Order.created_at) == today).scalar() or 0.0
    
    total_products = db.query(Product).count()
    low_stock_products = db.query(Product).filter(Product.stock_quantity <= 10).count()
    out_of_stock_products = db.query(Product).filter(Product.stock_quantity == 0).count()
    
    recent_orders = db.query(Order).order_by(desc(Order.created_at)).limit(10).all()
    
    formatted_recent_orders = []
    for o in recent_orders:
        formatted_recent_orders.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "village": o.village,
            "district": o.district,
            "grand_total": o.grand_total,
            "payment_method": o.payment_method,
            "payment_status": o.payment_status,
            "order_status": o.order_status,
            "items_count": len(o.items),
            "created_at": o.created_at.strftime("%d %b %Y, %I:%M %p")
        })
        
    return {
        "total_revenue": round(total_revenue, 2),
        "today_revenue": round(today_revenue, 2),
        "total_orders": total_orders,
        "today_orders": today_orders,
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_products": total_products,
        "low_stock_products": low_stock_products,
        "out_of_stock_products": out_of_stock_products,
        "recent_orders": formatted_recent_orders
    }

@router.get("/orders")
def get_all_orders(
    status_filter: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: View and filter all customer orders."""
    query = db.query(Order)
    
    if status_filter and status_filter != "all":
        query = query.filter(Order.order_status == status_filter)
        
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            (Order.order_number.ilike(search_term)) |
            (Order.customer_name.ilike(search_term)) |
            (Order.customer_phone.ilike(search_term)) |
            (Order.village.ilike(search_term)) |
            (Order.district.ilike(search_term))
        )
        
    orders = query.order_by(desc(Order.created_at)).all()
    
    results = []
    for o in orders:
        results.append({
            "id": o.id,
            "order_number": o.order_number,
            "customer_name": o.customer_name,
            "customer_phone": o.customer_phone,
            "customer_email": o.customer_email,
            "address": f"{o.address_line}, {o.village}, {o.taluka}, {o.district} - {o.pincode}",
            "notes": o.delivery_notes,
            "total_amount": o.total_amount,
            "delivery_fee": o.delivery_fee,
            "grand_total": o.grand_total,
            "payment_method": o.payment_method,
            "payment_status": o.payment_status,
            "order_status": o.order_status,
            "created_at": o.created_at.strftime("%d %b %Y, %I:%M %p"),
            "items": [
                {
                    "product_name": item.product_name,
                    "price": item.price,
                    "quantity": item.quantity,
                    "unit": item.unit,
                    "subtotal": item.subtotal
                } for item in o.items
            ]
        })
        
    return results

@router.post("/offline-sale")
def add_offline_sale(
    data: OfflineSaleCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Add an offline manual sale to today's revenue."""
    import uuid
    # Create a dummy order to represent the offline sale
    order_num = f"OFFLINE-{uuid.uuid4().hex[:6].upper()}"
    new_order = Order(
        order_number=order_num,
        customer_name=data.customer_name or "Offline Customer",
        customer_phone="0000000000",
        address_line="Offline Store",
        village="N/A",
        taluka="N/A",
        district="N/A",
        pincode="000000",
        total_amount=data.amount,
        delivery_fee=0.0,
        grand_total=data.amount,
        payment_method="CASH",
        payment_status="PAID",
        order_status="Delivered"
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    
    # Add a dummy item
    dummy_item = OrderItem(
        order_id=new_order.id,
        product_name="Offline Sale / Manual Entry",
        price=data.amount,
        quantity=1,
        unit="unit",
        subtotal=data.amount
    )
    db.add(dummy_item)
    db.commit()
    
    return {"message": "Offline sale added successfully", "order_number": order_num, "amount": data.amount}

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update order delivery or payment status."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    order.order_status = data.order_status
    if data.payment_status:
        order.payment_status = data.payment_status
        
    db.commit()
    return {"message": "Order status updated", "order_status": order.order_status, "payment_status": order.payment_status}

@router.delete("/orders/{order_id}")
def delete_order(
    order_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Delete an order and its items."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # Delete order items first
    for item in order.items:
        db.delete(item)
    
    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully", "order_id": order_id}

@router.put("/orders/{order_id}/edit-amount")
def edit_order_amount(
    order_id: int,
    data: dict,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Manually edit an order's grand total (revenue adjustment)."""
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    new_amount = data.get("grand_total")
    if new_amount is None or float(new_amount) < 0:
        raise HTTPException(status_code=400, detail="Invalid amount")
    
    order.grand_total = float(new_amount)
    db.commit()
    return {"message": "Order amount updated", "grand_total": order.grand_total}


@router.get("/orders/export-csv")
def export_orders_csv(
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Download orders as CSV."""
    orders = db.query(Order).order_by(desc(Order.created_at)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write CSV Header
    writer.writerow([
        "Order ID", "Date", "Customer Name", "Phone", "Village", "Taluka", 
        "District", "Pincode", "Items", "Grand Total (INR)", "Payment Method", "Payment Status", "Order Status"
    ])
    
    for o in orders:
        items_summary = "; ".join([f"{i.product_name} ({i.quantity} {i.unit})" for i in o.items])
        writer.writerow([
            o.order_number,
            o.created_at.strftime("%Y-%m-%d %H:%M"),
            o.customer_name,
            o.customer_phone,
            o.village,
            o.taluka,
            o.district,
            o.pincode,
            items_summary,
            o.grand_total,
            o.payment_method,
            o.payment_status,
            o.order_status
        ])
        
    output.seek(0)
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=shivar_orders.csv"}
    )
