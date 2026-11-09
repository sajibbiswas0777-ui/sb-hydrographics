import http.server
import socketserver
import json
import os
import urllib.parse
from datetime import datetime
import db

PORT = int(os.environ.get("PORT", 5000))

# Support both public folder and root folder fallback so Render never throws 404
PUBLIC_DIR = os.path.join(os.path.dirname(__file__), "public")
if not os.path.exists(PUBLIC_DIR) or not os.path.exists(os.path.join(PUBLIC_DIR, "index.html")):
    PUBLIC_DIR = os.path.dirname(__file__)

UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

class HydroHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=PUBLIC_DIR, **kwargs)

    def _set_headers(self, status=200, content_type="application/json"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(200)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        # 1. Direct root / index.html serving fallback
        if path in ("/", "/index.html"):
            for candidate in [
                os.path.join(PUBLIC_DIR, "index.html"),
                os.path.join(os.path.dirname(__file__), "index.html"),
                os.path.join(os.path.dirname(__file__), "public", "index.html"),
            ]:
                if os.path.exists(candidate):
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    with open(candidate, "rb") as f:
                        self.wfile.write(f.read())
                    return

        # 2. API Endpoints
        if path.startswith("/api/"):
            return self.handle_api_get(path, urllib.parse.parse_qs(parsed.query))

        # 3. Serve uploaded photos
        if path.startswith("/uploads/"):
            filename = os.path.basename(path)
            filepath = os.path.join(UPLOADS_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-Type", "image/jpeg")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
                return
            else:
                self.send_error(404, "File not found")
                return

        return super().do_GET()

    def handle_api_get(self, path, query):
        data = db.load_db()

        # 1. Health check
        if path == "/api/health":
            self._set_headers(200)
            self.wfile.write(json.dumps({
                "status": "ok", 
                "app": "SB HYDRO-GRAPHICS Server", 
                "auth_enabled": True,
                "time": datetime.now().isoformat()
            }).encode())
            return

        # 2. Auth: Check Current User (/api/auth/me)
        if path == "/api/auth/me":
            auth_header = self.headers.get("Authorization", "")
            token = ""
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1].strip()
            elif "token" in query:
                token = query["token"][0]

            session = db.validate_session(token)
            if session:
                self._set_headers(200)
                self.wfile.write(json.dumps({"authenticated": True, "user": session}).encode())
            else:
                self._set_headers(200)
                self.wfile.write(json.dumps({"authenticated": False}).encode())
            return

        # 3. List Users (/api/users)
        if path == "/api/users":
            users = db.list_users()
            self._set_headers(200)
            self.wfile.write(json.dumps(users).encode())
            return

        # 4. Settings
        if path == "/api/settings":
            self._set_headers(200)
            self.wfile.write(json.dumps(data.get("settings", {})).encode())
            return

        # 5. Jobs
        if path == "/api/jobs":
            self._set_headers(200)
            self.wfile.write(json.dumps(data.get("jobs", [])).encode())
            return

        # 6. Stock
        if path == "/api/stock":
            self._set_headers(200)
            self.wfile.write(json.dumps(data.get("stock", [])).encode())
            return

        # 7. Bills
        if path == "/api/bills":
            self._set_headers(200)
            self.wfile.write(json.dumps(data.get("bills", [])).encode())
            return

        # 8. Dues
        if path == "/api/dues":
            dues = [j for j in data.get("jobs", []) if (j.get("total_amount", 0) - j.get("advance_paid", 0)) > 0]
            self._set_headers(200)
            self.wfile.write(json.dumps(dues).encode())
            return

        # 9. Dashboard Stats
        if path == "/api/stats":
            bills = data.get("bills", [])
            jobs = data.get("jobs", [])
            stock = data.get("stock", [])

            today_sales = sum(b.get("paid", 0) for b in bills)
            active_jobs = len([j for j in jobs if j.get("stage") != "DELIVERED"])
            ready_jobs = len([j for j in jobs if j.get("stage") == "READY"])
            stock_count = len(stock)
            film_meters = sum(s.get("qty", 0) for s in stock if s.get("cat") == "FILM")
            pending_dues = sum(max(0, j.get("total_amount", 0) - j.get("advance_paid", 0)) for j in jobs)
            due_customers = len([j for j in jobs if (j.get("total_amount", 0) - j.get("advance_paid", 0)) > 0])

            stats = {
                "today_sales": today_sales,
                "active_jobs": active_jobs,
                "ready_jobs": ready_jobs,
                "stock_count": stock_count,
                "film_meters": round(film_meters, 1),
                "pending_dues": pending_dues,
                "due_customers": due_customers
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(stats).encode())
            return

        # 10. Export Backup JSON
        if path == "/api/backup/export":
            backup = {
                "version": "2.0",
                "app": "SB HYDRO-GRAPHICS",
                "exported_at": datetime.now().isoformat(),
                **data
            }
            self._set_headers(200)
            self.wfile.write(json.dumps(backup, indent=2).encode())
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length) if content_length > 0 else b"{}"

        try:
            payload = json.loads(body.decode("utf-8"))
        except:
            payload = {}

        data = db.load_db()

        # 1. AUTH: Login (/api/auth/login) - Supports PIN or Username+Password
        if path == "/api/auth/login":
            username = payload.get("username")
            password = payload.get("password")
            pin = payload.get("pin")

            user = db.authenticate(username=username, password=password, pin=pin)
            if user:
                token = db.create_session(user)
                self._set_headers(200)
                self.wfile.write(json.dumps({
                    "success": True,
                    "token": token,
                    "user": {
                        "id": user["id"],
                        "username": user["username"],
                        "name": user.get("name", user["username"]),
                        "role": user.get("role", "technician")
                    }
                }).encode())
            else:
                self._set_headers(401)
                self.wfile.write(json.dumps({
                    "success": False,
                    "error": "Galat Username, Password ya PIN! Kripya dobara check karein."
                }).encode())
            return

        # 2. AUTH: Logout (/api/auth/logout)
        if path == "/api/auth/logout":
            token = payload.get("token") or self.headers.get("Authorization", "").replace("Bearer ", "").strip()
            db.destroy_session(token)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True}).encode())
            return

        # 3. Add New User (/api/users)
        if path == "/api/users":
            username = payload.get("username", "")
            password = payload.get("password", "")
            name = payload.get("name", "")
            role = payload.get("role", "technician")
            pin = payload.get("pin", "0000")
            phone = payload.get("phone", "")

            if not username or not password or not name:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": "Username, password and name are required"}).encode())
                return

            ok, res = db.add_user(username, password, name, role, pin, phone)
            if ok:
                self._set_headers(201)
                self.wfile.write(json.dumps({"success": True, "user": res}).encode())
            else:
                self._set_headers(400)
                self.wfile.write(json.dumps({"success": False, "error": res}).encode())
            return

        # 4. Create Job Card
        if path == "/api/jobs":
            count = len(data["jobs"]) + 1
            job_id = payload.get("id") or f"SBH-{100 + count}"

            job = {
                "id": job_id,
                "customer_name": payload.get("customer_name", "").strip(),
                "phone": payload.get("phone", "").strip(),
                "item": payload.get("item", "").strip(),
                "vehicle_ref": payload.get("vehicle_ref", "").strip(),
                "pattern": payload.get("pattern", "3D Twill Carbon Fiber"),
                "base_color": payload.get("base_color", "Jet Black"),
                "clear_coat": payload.get("clear_coat", "2K High Gloss Mirror"),
                "total_amount": float(payload.get("total_amount", 0)),
                "advance_paid": float(payload.get("advance_paid", 0)),
                "stage": payload.get("stage", "RECEIVED"),
                "notes": payload.get("notes", "").strip(),
                "created_at": datetime.now().isoformat()
            }
            data["jobs"].insert(0, job)
            db.save_db(data)
            self._set_headers(201)
            self.wfile.write(json.dumps({"success": True, "id": job_id}).encode())
            return

        # 5. Update Stage
        if path.startswith("/api/jobs/") and path.endswith("/stage"):
            job_id = path.split("/")[3]
            new_stage = payload.get("stage")
            for j in data["jobs"]:
                if j["id"] == job_id:
                    j["stage"] = new_stage
                    j["updated_at"] = datetime.now().isoformat()
                    break
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "id": job_id, "stage": new_stage}).encode())
            return

        # 6. Add Stock
        if path == "/api/stock":
            count = len(data["stock"]) + 1
            stock_id = payload.get("id") or f"STK-{count}"
            item = {
                "id": stock_id,
                "name": payload.get("name", "").strip(),
                "cat": payload.get("cat", "FILM"),
                "sku": payload.get("sku", f"SB-{count}").strip(),
                "qty": float(payload.get("qty", 0)),
                "unit": payload.get("unit", "Meters"),
                "price": float(payload.get("price", 0))
            }
            data["stock"].insert(0, item)
            db.save_db(data)
            self._set_headers(201)
            self.wfile.write(json.dumps({"success": True, "id": stock_id}).encode())
            return

        # 7. Adjust Stock
        if path.startswith("/api/stock/") and path.endswith("/adjust"):
            stock_id = path.split("/")[3]
            delta = float(payload.get("delta", 0))
            for s in data["stock"]:
                if s["id"] == stock_id:
                    s["qty"] = max(0, s.get("qty", 0) + delta)
                    break
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "id": stock_id}).encode())
            return

        # 8. Create Bill
        if path == "/api/bills":
            count = len(data["bills"]) + 1
            bill_id = f"SBH-INV-{1000 + count}"
            items = payload.get("items", [])
            subtotal = float(payload.get("subtotal", 0))
            gst_applied = 1 if payload.get("gst_applied") else 0
            gst_amount = float(payload.get("gst_amount", 0))
            total = float(payload.get("total", 0))
            paid = float(payload.get("paid", 0))
            balance = max(0.0, total - paid)

            bill = {
                "id": bill_id,
                "bill_date": datetime.now().strftime("%Y-%m-%d"),
                "customer_name": payload.get("customer_name", "").strip(),
                "phone": payload.get("phone", "").strip(),
                "job_id": payload.get("job_id", ""),
                "items": items,
                "subtotal": subtotal,
                "gst_applied": gst_applied,
                "gst_amount": gst_amount,
                "total": total,
                "paid": paid,
                "balance": balance,
                "payment_mode": payload.get("payment_mode", "UPI / QR"),
                "created_at": datetime.now().isoformat()
            }
            data["bills"].insert(0, bill)

            job_id = payload.get("job_id")
            if job_id:
                for j in data["jobs"]:
                    if j["id"] == job_id:
                        j["advance_paid"] = paid
                        break

            db.save_db(data)
            self._set_headers(201)
            self.wfile.write(json.dumps({"success": True, "id": bill_id}).encode())
            return

        # 9. Collect Due Payment
        if path == "/api/dues/collect":
            job_id = payload.get("job_id")
            amount = float(payload.get("amount", 0))
            mode = payload.get("payment_mode", "UPI")

            for j in data["jobs"]:
                if j["id"] == job_id:
                    j["advance_paid"] = j.get("advance_paid", 0) + amount
                    break

            data.setdefault("payments", []).append({
                "job_id": job_id,
                "amount": amount,
                "payment_mode": mode,
                "date": datetime.now().isoformat()
            })
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "job_id": job_id, "amount_collected": amount}).encode())
            return

        # 10. Update Settings
        if path == "/api/settings":
            data["settings"] = {
                "shop_name": payload.get("shop_name", "SB HYDRO-GRAPHICS"),
                "tagline": payload.get("tagline", ""),
                "phone": payload.get("phone", ""),
                "whatsapp": payload.get("whatsapp", ""),
                "gstin": payload.get("gstin", ""),
                "address": payload.get("address", ""),
                "owner": payload.get("owner", ""),
                "upi_id": payload.get("upi_id", ""),
                "terms": payload.get("terms", ""),
                "updated_at": datetime.now().isoformat()
            }
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "message": "Settings updated"}).encode())
            return

        # 11. Restore Backup
        if path == "/api/backup/restore":
            if "jobs" in payload and "settings" in payload:
                db.save_db(payload)
                self._set_headers(200)
                self.wfile.write(json.dumps({"success": True, "message": "Backup restored"}).encode())
                return

        # 12. Clear All Demo Records (Start Fresh Workshop)
        if path == "/api/reset-data":
            data["jobs"] = []
            data["bills"] = []
            data["payments"] = []
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "message": "Demo data cleared successfully"}).encode())
            return

        self._set_headers(404)
        self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())

    def do_DELETE(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path
        data = db.load_db()

        if path.startswith("/api/jobs/"):
            job_id = path.split("/")[3]
            data["jobs"] = [j for j in data["jobs"] if j["id"] != job_id]
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "deleted_id": job_id}).encode())
            return

        if path.startswith("/api/stock/"):
            stock_id = path.split("/")[3]
            data["stock"] = [s for s in data["stock"] if s["id"] != stock_id]
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "deleted_id": stock_id}).encode())
            return

        if path.startswith("/api/bills/"):
            bill_id = path.split("/")[3]
            data["bills"] = [b for b in data["bills"] if b["id"] != bill_id]
            db.save_db(data)
            self._set_headers(200)
            self.wfile.write(json.dumps({"success": True, "deleted_id": bill_id}).encode())
            return

        self._set_headers(404)

def run_server():
    db.init_db()
    with socketserver.ThreadingTCPServer(("", PORT), HydroHandler) as httpd:
        print(f"============================================================")
        print(f"🌊 SB HYDRO-GRAPHICS Full-Stack Studio Server Live!")
        print(f"🌐 Access Dashboard & Billing: http://localhost:{PORT}")
        print(f"💾 Database: Local JSON Store (sb_hydrographics_data.json)")
        print(f"🔐 Role-Based Auth: Admin (PIN 1234) & Karigar (PIN 0000)")
        print(f"============================================================")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nShutting down server cleanly...")

if __name__ == "__main__":
    run_server()
