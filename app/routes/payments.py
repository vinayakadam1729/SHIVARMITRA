from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.config import settings

router = APIRouter(prefix="/api/payments", tags=["payments"])

class UPIQRRequest(BaseModel):
    order_number: str
    amount: float
    customer_name: str

@router.post("/upi-qr")
def generate_upi_payload(payload: UPIQRRequest):
    """
    Generate dynamic UPI QR payload string for fast Indian payments (PhonePe, GPay, Paytm, BHIM).
    UPI URI format: upi://pay?pa=PHONE@upi&pn=NAME&am=AMOUNT&cu=INR&tn=ORDER_ID
    """
    # Owner UPI VPA based on owner phone 9021273002
    vpa = f"{settings.OWNER_PHONE}@ybl"  # or paytm/okicici
    store_name = settings.OWNER_NAME
    note = f"Shivar Order {payload.order_number}"
    
    upi_uri = f"upi://pay?pa={vpa}&pn={store_name}&am={payload.amount:.2f}&cu=INR&tn={note}"
    
    # Generate Google Chart QR URL for instant scanning
    qr_image_url = f"https://api.qrserver.com/v1/create-qr-code/?size=240x240&data={upi_uri}"
    
    return {
        "vpa": vpa,
        "amount": payload.amount,
        "upi_uri": upi_uri,
        "qr_image_url": qr_image_url,
        "owner_phone": settings.OWNER_PHONE
    }

@router.get("/methods")
def get_supported_payment_methods():
    """List enabled payment options."""
    return {
        "methods": [
            {
                "id": "COD",
                "name_en": "Cash on Delivery (COD)",
                "name_mr": "डिलिव्हरीच्या वेळी रोख रक्कम (COD)",
                "name_hi": "डिलीवरी पर नकद (COD)",
                "description_en": "Pay in cash when products are delivered to your farm",
                "description_mr": "माल शेतावर पोहोचल्यावर पैसे द्या",
                "description_hi": "सामान मिलने पर नकद भुगतान करें",
                "icon": "banknote"
            },
            {
                "id": "UPI_QR",
                "name_en": "UPI / Google Pay / PhonePe / Paytm",
                "name_mr": "फोनपे / गुगल पे / UPI QR स्कॅन",
                "name_hi": "फ़ोनपे / गूगल पे / यूपीआई क्यूआर",
                "description_en": "Instant 0% fee payment via any UPI app",
                "description_mr": "कोणत्याही UPI अ‍ॅपवरून झटपट क्यूआर स्कॅन करा",
                "description_hi": "किसी भी UPI ऐप से तुरंत स्कैन करके भुगतान करें",
                "icon": "qr-code"
            }
        ]
    }
