import json
import os
import hashlib
import uuid
import secrets
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "sb_hydrographics_data.json")

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

DEFAULT_DATABASE = {
    "settings": {
        "shop_name": "SB HYDRO-GRAPHICS",
        "tagline": "Professional Water Transfer Printing & Specialized Coating Studio",
        "phone": "+91 98765 43210",
        "whatsapp": "919876543210",
        "gstin": "27AABCS1234F1Z5",
        "address": "Plot 12, Automobile Craft Zone, Main Highway Road, Pune, Maharashtra - 411019",
        "owner": "Sajib Biswas",
        "upi_id": "sbhydro@okhdfcbank",
        "terms": "1. 1-Year coating warranty against peel-off under regular automotive use. 2. Clean surface with soft microfiber cloth. Do not use industrial acids or wire brushes.",
        "updated_at": datetime.now().isoformat()
    },
    "users": [
        {
            "id": "USR-1",
            "username": "admin",
            "password_hash": hash_password("sbadmin123"),
            "pin": "1234",
            "name": "Sajib Biswas (Owner / Admin)",
            "role": "admin",
            "phone": "9876543210",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": "USR-2",
            "username": "sbwork",
            "password_hash": hash_password("sbwork123"),
            "pin": "2222",
            "name": "Workshop Manager",
            "role": "manager",
            "phone": "9822000000",
            "created_at": datetime.now().isoformat()
        }
    ],
    "sessions": {},
    "jobs": [],
    "stock": [
        {"id": "STK-1", "name": "3D Twill Carbon Fiber Film (100cm)", "cat": "FILM", "sku": "FLM-CF-01", "qty": 38.5, "unit": "Meters", "price": 350},
        {"id": "STK-2", "name": "Forged Carbon Hydrographic Film (50cm)", "cat": "FILM", "sku": "FLM-FC-02", "qty": 22.0, "unit": "Meters", "price": 420},
        {"id": "STK-3", "name": "Military Digital Camo Pattern (50cm)", "cat": "FILM", "sku": "FLM-CM-03", "qty": 14.0, "unit": "Meters", "price": 320},
        {"id": "STK-4", "name": "Reaper Flame Skulls Film (50cm)", "cat": "FILM", "sku": "FLM-SK-04", "qty": 4.5, "unit": "Meters", "price": 380},
        {"id": "STK-5", "name": "Dark Walnut Burl Wood Film (100cm)", "cat": "FILM", "sku": "FLM-WD-05", "qty": 18.0, "unit": "Meters", "price": 400},
        {"id": "STK-6", "name": "Pro Hydro Activator Chemical", "cat": "CHEMICAL", "sku": "CHM-ACT-A", "qty": 8.5, "unit": "Liters", "price": 850},
        {"id": "STK-7", "name": "Activator Aerosol Spray Cans (400ml)", "cat": "CHEMICAL", "sku": "CHM-ACT-CAN", "qty": 12.0, "unit": "Cans", "price": 450},
        {"id": "STK-8", "name": "2K High Solids Gloss Clear Coat + Hardener", "cat": "PAINT", "sku": "PNT-2K-GLOSS", "qty": 6.0, "unit": "Liters", "price": 1200},
        {"id": "STK-9", "name": "Jet Black Base Coat Primer", "cat": "PAINT", "sku": "PNT-PRIMER-BLK", "qty": 10.0, "unit": "Liters", "price": 750},
        {"id": "STK-10", "name": "Pre-Dipped Carbon Keychains", "cat": "RETAIL", "sku": "RTL-KEY-CF", "qty": 35.0, "unit": "Pcs", "price": 199}
    ],
    "bills": [],
    "payments": []
}

def load_db():
    if not os.path.exists(DATA_FILE):
        save_db(DEFAULT_DATABASE)
        return DEFAULT_DATABASE
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            users = data.get("users", [])
            has_sbwork = any(u.get("username") == "sbwork" for u in users)
            if not has_sbwork:
                users = [u for u in users if u.get("username") != "karigar"]
                users.append({
                    "id": "USR-2",
                    "username": "sbwork",
                    "password_hash": hash_password("sbwork123"),
                    "pin": "2222",
                    "name": "Workshop Manager",
                    "role": "manager",
                    "phone": "9822000000",
                    "created_at": datetime.now().isoformat()
                })
                data["users"] = users
                save_db(data)
            if "sessions" not in data:
                data["sessions"] = {}
                save_db(data)
            return data
    except Exception as e:
        print("Error loading database, returning defaults:", e)
        return DEFAULT_DATABASE

def save_db(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print("Error saving database:", e)
        return False

# AUTHENTICATION HELPERS
def authenticate(username=None, password=None, pin=None):
    data = load_db()
    users = data.get("users", [])

    # 1. PIN-based login (Fast workshop / mobile access)
    if pin is not None and str(pin).strip():
        clean_pin = str(pin).strip()
        for u in users:
            if str(u.get("pin", "")).strip() == clean_pin:
                return u
        # PIN Aliases for Manager & Admin
        if clean_pin in ("2222", "0000"):
            for u in users:
                if u.get("role") in ("manager", "technician") or u.get("username") == "sbwork":
                    return u
        if clean_pin in ("1234", "1111"):
            for u in users:
                if u.get("role") == "admin" or u.get("username") == "admin":
                    return u
        return None

    # 2. Username + Password login
    if username and password:
        clean_user = username.strip().lower()
        pwd = password.strip()
        pwd_hash = hash_password(pwd)
        
        # Direct match
        for u in users:
            if u.get("username", "").lower() == clean_user:
                if u.get("password_hash") == pwd_hash:
                    return u

        # User Aliases so Manager / Admin can never get locked out
        if clean_user in ("sbwork", "manager", "manger", "staff", "work") and pwd in ("sbwork123", "manager123", "sbwork", "2222"):
            for u in users:
                if u.get("role") in ("manager", "technician") or u.get("username") == "sbwork":
                    return u

        if clean_user in ("admin", "sajib", "owner") and pwd in ("sbadmin123", "admin123", "admin", "1234"):
            for u in users:
                if u.get("role") == "admin" or u.get("username") == "admin":
                    return u

        return None

    return None

def create_session(user):
    data = load_db()
    token = secrets.token_hex(24)
    data["sessions"][token] = {
        "user_id": user["id"],
        "username": user["username"],
        "name": user.get("name", user["username"]),
        "role": user.get("role", "manager"),
        "created_at": datetime.now().isoformat()
    }
    save_db(data)
    return token

def validate_session(token):
    if not token:
        return None
    data = load_db()
    sessions = data.get("sessions", {})
    return sessions.get(token)

def destroy_session(token):
    if not token:
        return True
    data = load_db()
    if "sessions" in data and token in data["sessions"]:
        del data["sessions"][token]
        save_db(data)
    return True

def list_users():
    data = load_db()
    users = data.get("users", [])
    safe_users = []
    for u in users:
        safe_users.append({
            "id": u["id"],
            "username": u["username"],
            "name": u.get("name"),
            "role": u.get("role"),
            "pin": u.get("pin"),
            "phone": u.get("phone", "")
        })
    return safe_users

def add_user(username, password, name, role="manager", pin="2222", phone=""):
    data = load_db()
    users = data.get("users", [])
    for u in users:
        if u["username"].lower() == username.strip().lower():
            return False, "Username already exists"
    
    new_user = {
        "id": f"USR-{len(users)+1}",
        "username": username.strip().lower(),
        "password_hash": hash_password(password),
        "pin": pin.strip() if pin else "2222",
        "name": name.strip(),
        "role": role if role in ["admin", "manager", "technician"] else "manager",
        "phone": phone.strip(),
        "created_at": datetime.now().isoformat()
    }
    users.append(new_user)
    data["users"] = users
    save_db(data)
    return True, new_user

def init_db():
    if not os.path.exists(DATA_FILE):
        save_db(DEFAULT_DATABASE)
    else:
        load_db()
    print("Database ready at:", DATA_FILE)

if __name__ == "__main__":
    init_db()
