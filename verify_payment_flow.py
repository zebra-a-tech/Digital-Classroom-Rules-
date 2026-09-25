import sqlite3, datetime

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("💰 DIGITAL CLASSROOM — PAYMENT FLOW VERIFICATION")
print("="*70)

# ---------- 1. PAYMENT REQUESTS ----------
print("\n1️⃣  PAYMENT REQUESTS")
c.execute("""
    SELECT id, student_id, subject, amount, status,
           requested_at, verified_at, session_started, session_expires
    FROM payment_requests
    ORDER BY id DESC LIMIT 10
""")
rows = c.fetchall()
if rows:
    for r in rows:
        print(f"   • Request #{r[0]} | Student {r[1]} | {r[2]} | ${r[3]}")
        print(f"     Status: {r[4]}")
        print(f"     Requested: {r[5]}")
        print(f"     Verified:  {r[6] or '—'}")
        print(f"     Session Start: {r[7] or '—'}")
        print(f"     Session End:   {r[8] or '—'}")
        print()
else:
    print("   ⚠️ No payment requests found")

# ---------- 2. PAID SESSIONS ----------
print("2️⃣  PAID SESSIONS")
c.execute("""
    SELECT id, student_id, payment_request_id, started_at, expires_at,
           active, paused, paused_at, total_paused_seconds, subject
    FROM paid_sessions
    ORDER BY id DESC LIMIT 10
""")
rows = c.fetchall()
if rows:
    for r in rows:
        status = "🟢 ACTIVE" if r[5] == 1 else "🔴 EXPIRED"
        paused = "⏸️ PAUSED" if r[6] == 1 else "▶️ RUNNING"
        print(f"   • Session #{r[0]} | Student {r[1]} | Payment #{r[2]}")
        print(f"     Subject: {r[9] or '—'} | {status} | {paused}")
        print(f"     Started:  {r[3]}")
        print(f"     Expires:  {r[4]}")
        if r[7]:
            print(f"     Paused At: {r[7]} | Total Paused: {r[8]}s")
        print()
else:
    print("   ⚠️ No paid sessions found")

# ---------- 3. LIVE SESSION CHECK ----------
print("3️⃣  CURRENTLY ACTIVE SESSIONS")
now = datetime.datetime.now()
c.execute("""
    SELECT id, student_id, subject, started_at, expires_at
    FROM paid_sessions
    WHERE active = 1
""")
active = c.fetchall()
if active:
    for a in active:
        try:
            exp = datetime.datetime.fromisoformat(a[4])
            remaining = (exp - now).total_seconds() / 60
            print(f"   🟢 Student {a[1]} | {a[2]} | {remaining:.1f} minutes remaining")
        except:
            print(f"   🟢 Student {a[1]} | {a[2]} | expires {a[4]}")
else:
    print("   ⚠️ No active sessions right now")

# ---------- 4. NEXT STEP FOR TESTING ----------
print("\n4️⃣  NEXT TEST — DO THIS:")
print("   1. Student submits payment request (should be PENDING)")
print("   2. Open founder payments page")
print("   3. Click VERIFY on the PENDING request")
print("   4. Student clicks START 1-HOUR LESSON")
print("   5. Re-run this script to see the active session")

conn.close()
print("\n" + "="*70)
print("✅ PAYMENT FLOW CHECK COMPLETE")
print("="*70 + "\n")
