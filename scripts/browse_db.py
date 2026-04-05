import sqlite3

conn = sqlite3.connect("callmycar.db")
cursor = conn.cursor()

print("=== TABLES ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for r in cursor.fetchall():
    print(f"  {r[0]}")

print("\n=== QR CODES ===")
cursor.execute("SELECT qr_code_id, is_active, vehicle_id FROM qr_codes")
for r in cursor.fetchall():
    print(f"  {r}")

print("\n=== USERS ===")
cursor.execute("SELECT id, phone_number, is_active FROM users")
rows = cursor.fetchall()
if not rows:
    print("  (none)")
else:
    for r in rows:
        print(f"  {r}")

print("\n=== VEHICLES ===")
cursor.execute("SELECT id, user_id, vehicle_number FROM vehicles")
rows = cursor.fetchall()
if not rows:
    print("  (none)")
else:
    for r in rows:
        print(f"  {r}")

print("\n=== CALL LOGS ===")
cursor.execute("SELECT qr_code_id, caller_ip, status, created_at FROM call_logs")
rows = cursor.fetchall()
if not rows:
    print("  (none)")
else:
    for r in rows:
        print(f"  {r}")

conn.close()
