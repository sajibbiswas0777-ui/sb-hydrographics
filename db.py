import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "sb_hydrographics_data.json")

DEFAULT_DATABASE = {
    "settings": {
        "shop_name": "SB HYDRO-GRAPHICS",
        "tagline": "Professional Water Transfer Printing & Specialized Coating Studio",
        "phone": "+91 98765 43210",
        "whatsapp": "919876543210",
        "gstin": "27AABCS1234F1Z5",
        "address": "Plot 12, Automobile Craft Zone, Main Highway Road, Pune, Maharashtra - 411019",
        "owner": "S. B. Verma",
        "upi_id": "sbhydro@okhdfcbank",
        "terms": "1. 1-Year coating warranty against peel-off under regular automotive use. 2. Clean surface with soft microfiber cloth. Do not use industrial acids or wire brushes.",
        "updated_at": datetime.now().isoformat()
    },
    "jobs": [
        {
            "id": "SBH-101",
            "customer_name": "Rohit Sharma",
            "phone": "9876543210",
            "item": "Royal Enfield Classic 350 Petrol Tank & Side Panels",
            "vehicle_ref": "RE Classic 350 (Black)",
            "pattern": "3D Twill Carbon Fiber",
            "base_color": "Jet Black",
            "clear_coat": "2K High Gloss Mirror",
            "total_amount": 4800,
            "advance_paid": 2500,
            "stage": "DIPPED",
            "notes": "Filled deep scratches on emblem. Customer wants deep wet-look clear gloss.",
            "created_at": "2026-11-06T10:00:00"
        },
        {
            "id": "SBH-102",
            "customer_name": "Vikas Patel",
            "phone": "9822012345",
            "item": "Studds Full Face Helmet + Visor Peak",
            "vehicle_ref": "Biker Gear",
            "pattern": "Reaper Flaming Skulls",
            "base_color": "Candy Red Base",
            "clear_coat": "2K High Gloss Mirror",
            "total_amount": 1800,
            "advance_paid": 1800,
            "stage": "READY",
            "notes": "Customer ready for pickup today evening.",
            "created_at": "2026-11-07T12:30:00"
        },
        {
            "id": "SBH-103",
            "customer_name": "Amitabh Sen",
            "phone": "9833445566",
            "item": "Toyota Fortuner Dashboard & Door Trim Set (8 Pcs)",
            "vehicle_ref": "Toyota Fortuner 2023",
            "pattern": "Dark Walnut Burl Wood",
            "base_color": "Jet Black",
            "clear_coat": "Satin Matte Stealth",
            "total_amount": 9500,
            "advance_paid": 4000,
            "stage": "BASE_COAT",
            "notes": "VIP interior luxury wood finish.",
            "created_at": "2026-11-08T15:00:00"
        },
        {
            "id": "SBH-104",
            "customer_name": "Karan Johar",
            "phone": "9819988776",
            "item": "Yamaha R15 Front Fairing & Cowl",
            "vehicle_ref": "Yamaha R15 V4",
            "pattern": "Forged Carbon Fiber",
            "base_color": "Jet Black",
            "clear_coat": "Ceramic Shield Pro",
            "total_amount": 3800,
            "advance_paid": 1500,
            "stage": "PREP",
            "notes": "Surface sanding in progress.",
            "created_at": "2026-11-09T09:15:00"
        }
    ],
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
    "bills": [
        {
            "id": "SBH-INV-1001",
            "bill_date": "2026-11-07",
            "customer_name": "Vikas Patel",
            "phone": "9822012345",
            "job_id": "SBH-102",
            "items": [
                {"desc": "Hydro Dipping: Studds Helmet (Reaper Skulls)", "qty": 1, "rate": 1400, "amount": 1400},
                {"desc": "2K High Gloss Ceramic Top Coat", "qty": 1, "rate": 400, "amount": 400}
            ],
            "subtotal": 1800,
            "gst_applied": 0,
            "gst_amount": 0,
            "total": 1800,
            "paid": 1800,
            "balance": 0,
            "payment_mode": "UPI / QR",
            "created_at": "2026-11-07T18:00:00"
        }
    ],
    "payments": []
}

def load_db():
    if not os.path.exists(DATA_FILE):
        save_db(DEFAULT_DATABASE)
        return DEFAULT_DATABASE
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
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

def init_db():
    if not os.path.exists(DATA_FILE):
        save_db(DEFAULT_DATABASE)
    print("Database ready at:", DATA_FILE)

if __name__ == "__main__":
    init_db()
