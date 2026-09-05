import uvicorn
import os
import sys
from dotenv import load_dotenv

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

load_dotenv()

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "8000"))
    
    print("\n" + "="*60)
    print("SHIVAR - AGRICULTURAL MARKETPLACE (शिवार कृषी बाजार)")
    print("="*60)
    print(f"Server running on: http://{host}:{port}")
    print(f"Customer Store:    http://{host}:{port}/")
    print(f"Track Orders:      http://{host}:{port}/track")
    print(f"Owner Dashboard:   http://{host}:{port}/admin")
    print(f"Owner Login:       http://{host}:{port}/admin/login")
    print(f"Credentials:       admin@shivar.com / shivar@2026")
    print(f"Owner Helpline:    +91 9021273002")
    print("="*60 + "\n")
    
    uvicorn.run("app.main:app", host=host, port=port, reload=True)
