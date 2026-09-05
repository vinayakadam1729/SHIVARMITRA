from pathlib import Path
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Depends, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import engine, Base, SessionLocal, get_db
from app.seed_data import seed_database
from app.routes import products, orders, admin, payments

# Application Base Path
BASE_DIR = Path(__file__).resolve().parent.parent

def init_db():
    """Ensure database schema is created and initial seed data is loaded."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()

# Auto-initialize on start
init_db()

# Create tables and seed data at startup
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database
    init_db()
    yield
    # Shutdown: Clean up resources if any

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version=settings.VERSION,
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files
static_dir = BASE_DIR / "static"
static_dir.mkdir(parents=True, exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Jinja2 Templates Configuration
templates_dir = BASE_DIR / "templates"
templates_dir.mkdir(parents=True, exist_ok=True)
templates = Jinja2Templates(directory=str(templates_dir))

# Include API Routers
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(payments.router)

# Context processor for templates
def get_template_context(request: Request, **extra):
    ctx = {
        "request": request,
        "owner_name": settings.OWNER_NAME,
        "owner_phone": settings.OWNER_PHONE,
        "owner_whatsapp": settings.OWNER_WHATSAPP,
        "store_location": settings.STORE_LOCATION,
        "currency_symbol": settings.CURRENCY_SYMBOL,
        "default_lang": settings.DEFAULT_LANGUAGE
    }
    ctx.update(extra)
    return ctx

# ----------------- HTML PAGE ROUTES ----------------- #

@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Storefront homepage."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=get_template_context(request, active_page="home")
    )

@app.get("/product/{slug}", response_class=HTMLResponse)
async def product_detail_page(request: Request, slug: str):
    """Dedicated product detail page."""
    return templates.TemplateResponse(
        request=request,
        name="product_detail.html",
        context=get_template_context(request, slug=slug, active_page="products")
    )

@app.get("/order", response_class=HTMLResponse)
async def order_page(request: Request):
    """Dedicated order / checkout page."""
    return templates.TemplateResponse(
        request=request,
        name="order.html",
        context=get_template_context(request, active_page="order")
    )

@app.get("/order/success", response_class=HTMLResponse)
async def order_success_page(request: Request):
    """Order confirmation and WhatsApp redirection page."""
    return templates.TemplateResponse(
        request=request,
        name="order_success.html",
        context=get_template_context(request, active_page="order")
    )

@app.get("/track", response_class=HTMLResponse)
async def track_order_page(request: Request):
    """Order tracking page."""
    return templates.TemplateResponse(
        request=request,
        name="track_order.html",
        context=get_template_context(request, active_page="track")
    )

@app.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Owner admin login page."""
    return templates.TemplateResponse(
        request=request,
        name="admin_login.html",
        context=get_template_context(request, active_page="admin_login")
    )

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_page(request: Request):
    """Owner admin management dashboard."""
    return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context=get_template_context(request, active_page="admin_dashboard")
    )

@app.get("/invoice/{order_number}", response_class=HTMLResponse)
async def invoice_page(request: Request, order_number: str, db: Session = Depends(get_db)):
    """Customer & Owner printable Tax Invoice / Bill page."""
    from app.models import Order
    order = db.query(Order).filter(Order.order_number == order_number).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
        
    return templates.TemplateResponse(
        request=request,
        name="invoice.html",
        context=get_template_context(request, order=order)
    )

