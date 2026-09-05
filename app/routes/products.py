import re
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.database import get_db
from app.models import Product, Category, AdminUser
from app.schemas import ProductOut, ProductCreate, ProductUpdate, CategoryOut
from app.auth import get_current_admin

router = APIRouter(prefix="/api", tags=["products"])

def generate_slug(name: str) -> str:
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name).strip().lower()
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug or "product"

@router.get("/categories", response_model=List[CategoryOut])
def get_categories(db: Session = Depends(get_db)):
    """Fetch all product categories sorted by display order."""
    return db.query(Category).order_by(Category.display_order.asc()).all()

@router.get("/products")
def get_products(
    category: Optional[str] = Query(None, description="Category slug or 'all'"),
    search: Optional[str] = Query(None, description="Search term in EN/MR/HI"),
    featured: Optional[bool] = Query(None, description="Filter featured only"),
    sort: Optional[str] = Query("popular", description="popular, price_low, price_high, rating, new"),
    lang: Optional[str] = Query("mr", description="mr, hi, en"),
    db: Session = Depends(get_db)
):
    """Retrieve catalog products with multi-language filtering and search."""
    query = db.query(Product)
    
    # Category filter
    if category and category != "all":
        cat = db.query(Category).filter(Category.slug == category).first()
        if cat:
            query = query.filter(Product.category_id == cat.id)
            
    # Featured filter
    if featured is not None:
        query = query.filter(Product.is_featured == featured)
        
    # Search query filter across English, Marathi, Hindi fields
    if search:
        search_term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Product.name_en.ilike(search_term),
                Product.name_mr.ilike(search_term),
                Product.name_hi.ilike(search_term),
                Product.description_en.ilike(search_term),
                Product.description_mr.ilike(search_term),
                Product.description_hi.ilike(search_term),
                Product.badge.ilike(search_term)
            )
        )
        
    # Sorting
    if sort == "price_low":
        query = query.order_by(Product.price.asc())
    elif sort == "price_high":
        query = query.order_by(Product.price.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())
    elif sort == "new":
        query = query.order_by(Product.created_at.desc())
    else:  # "popular"
        query = query.order_by(Product.reviews_count.desc(), Product.rating.desc())
        
    products = query.all()
    
    # Format localized response list
    results = []
    for p in products:
        results.append({
            "id": p.id,
            "slug": p.slug,
            "name": getattr(p, f"name_{lang}", p.name_en),
            "name_en": p.name_en,
            "name_mr": p.name_mr,
            "name_hi": p.name_hi,
            "description": getattr(p, f"description_{lang}", p.description_en),
            "description_en": p.description_en,
            "description_mr": p.description_mr,
            "description_hi": p.description_hi,
            "price": p.price,
            "original_price": p.original_price,
            "discount_percent": p.discount_percent,
            "unit": getattr(p, f"unit_{lang}", p.unit_en),
            "unit_en": p.unit_en,
            "unit_mr": p.unit_mr,
            "unit_hi": p.unit_hi,
            "stock_quantity": p.stock_quantity,
            "in_stock": p.in_stock and p.stock_quantity > 0,
            "image_url": p.image_url,
            "badge": p.badge,
            "rating": p.rating,
            "reviews_count": p.reviews_count,
            "is_featured": p.is_featured,
            "category_id": p.category_id,
            "category_name": getattr(p.category, f"name_{lang}", p.category.name_en) if p.category else "",
            "category_slug": p.category.slug if p.category else ""
        })
        
    return results

@router.get("/products/{slug_or_id}")
def get_product(slug_or_id: str, lang: str = "mr", db: Session = Depends(get_db)):
    """Fetch single product details."""
    if slug_or_id.isdigit():
        prod = db.query(Product).filter(Product.id == int(slug_or_id)).first()
    else:
        prod = db.query(Product).filter(Product.slug == slug_or_id).first()
        
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    return {
        "id": prod.id,
        "slug": prod.slug,
        "name": getattr(prod, f"name_{lang}", prod.name_en),
        "name_en": prod.name_en,
        "name_mr": prod.name_mr,
        "name_hi": prod.name_hi,
        "description": getattr(prod, f"description_{lang}", prod.description_en),
        "description_en": prod.description_en,
        "description_mr": prod.description_mr,
        "description_hi": prod.description_hi,
        "price": prod.price,
        "original_price": prod.original_price,
        "discount_percent": prod.discount_percent,
        "unit": getattr(prod, f"unit_{lang}", prod.unit_en),
        "unit_en": prod.unit_en,
        "unit_mr": prod.unit_mr,
        "unit_hi": prod.unit_hi,
        "stock_quantity": prod.stock_quantity,
        "in_stock": prod.in_stock and prod.stock_quantity > 0,
        "image_url": prod.image_url,
        "badge": prod.badge,
        "rating": prod.rating,
        "reviews_count": prod.reviews_count,
        "is_featured": prod.is_featured,
        "category_id": prod.category_id,
        "category_name": getattr(prod.category, f"name_{lang}", prod.category.name_en) if prod.category else "",
        "category_slug": prod.category.slug if prod.category else ""
    }

# Admin endpoints for Product Management
@router.post("/admin/products", status_code=status.HTTP_201_CREATED)
def create_product(
    data: ProductCreate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Add a new agricultural product."""
    slug = data.slug or generate_slug(data.name_en)
    # Ensure unique slug
    base_slug = slug
    counter = 1
    while db.query(Product).filter(Product.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1
        
    prod = Product(
        slug=slug,
        name_en=data.name_en,
        name_mr=data.name_mr,
        name_hi=data.name_hi,
        description_en=data.description_en,
        description_mr=data.description_mr,
        description_hi=data.description_hi,
        category_id=data.category_id,
        price=data.price,
        original_price=data.original_price or data.price,
        discount_percent=data.discount_percent or 0,
        unit_en=data.unit_en,
        unit_mr=data.unit_mr,
        unit_hi=data.unit_hi,
        stock_quantity=data.stock_quantity,
        in_stock=data.in_stock,
        image_url=data.image_url,
        badge=data.badge,
        is_featured=data.is_featured
    )
    db.add(prod)
    db.commit()
    db.refresh(prod)
    return {"message": "Product created successfully", "id": prod.id, "slug": prod.slug}

@router.put("/admin/products/{product_id}")
def update_product(
    product_id: int,
    data: ProductUpdate,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Update existing product details & inventory."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    update_data = data.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(prod, field, val)
        
    db.commit()
    db.refresh(prod)
    return {"message": "Product updated successfully", "id": prod.id}

@router.delete("/admin/products/{product_id}")
def delete_product(
    product_id: int,
    admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin: Delete a product."""
    prod = db.query(Product).filter(Product.id == product_id).first()
    if not prod:
        raise HTTPException(status_code=404, detail="Product not found")
        
    db.delete(prod)
    db.commit()
    return {"message": "Product deleted successfully"}
