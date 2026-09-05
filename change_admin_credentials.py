"""
Script to change or reset Admin email / password from terminal.
Usage:
    python change_admin_credentials.py <new_email> <new_password>
Or run interactively:
    python change_admin_credentials.py
"""
import sys
from app.database import SessionLocal
from app.models import AdminUser
from app.auth import hash_password

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def update_admin(email, password, full_name=None):
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).first()
        if not admin:
            admin = AdminUser(
                username=email,
                hashed_password=hash_password(password),
                full_name=full_name or "Shivar Krushi Seva Kendra",
                is_active=True
            )
            db.add(admin)
        else:
            admin.username = email
            admin.hashed_password = hash_password(password)
            if full_name:
                admin.full_name = full_name
                
        db.commit()
        print("\n" + "="*50)
        print("✅ ADMIN CREDENTIALS UPDATED SUCCESSFULLY!")
        print("="*50)
        print(f"📧 New Email / Username: {admin.username}")
        print(f"🔑 New Password:         {password}")
        print(f"👤 Full Name:            {admin.full_name}")
        print("="*50 + "\n")
    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) >= 3:
        email = sys.argv[1].strip()
        pwd = sys.argv[2].strip()
        name = sys.argv[3].strip() if len(sys.argv) > 3 else None
        update_admin(email, pwd, name)
    else:
        print("\n--- Shivar Admin Credentials Setup ---")
        email = input("Enter new Admin Email / Username [admin@shivar.com]: ").strip() or "admin@shivar.com"
        pwd = input("Enter new Admin Password [shivar@2026]: ").strip() or "shivar@2026"
        name = input("Enter Store / Owner Name [Shivar Krushi Seva Kendra]: ").strip() or "Shivar Krushi Seva Kendra"
        update_admin(email, pwd, name)
