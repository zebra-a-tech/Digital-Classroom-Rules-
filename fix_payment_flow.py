import sqlite3, datetime, os, re

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("🔧 DIGITAL CLASSROOM — PAYMENT FLOW REPAIR")
print("="*70)

# ============================================================
# FIX 1: Clean up the corrupted 'subject' column in payment_requests
# ============================================================
print("\n1️⃣  Cleaning corrupted 'subject' values in payment_requests...")
c.execute("""
    UPDATE payment_requests
    SET subject = 'Maths'
    WHERE subject LIKE '%STUDENT_ID%' OR subject IS NULL OR subject = ''
""")
print(f"   ✅ Fixed {c.rowcount} corrupted subject rows")

# ============================================================
# FIX 2: Copy subject from payment_requests to paid_sessions
# ============================================================
print("\n2️⃣  Syncing subject from payment_requests → paid_sessions...")
c.execute("""
    UPDATE paid_sessions
    SET subject = (
        SELECT pr.subject FROM payment_requests pr
        WHERE pr.id = paid_sessions.payment_request_id
    )
    WHERE subject IS NULL OR subject = '' OR subject = '—'
""")
print(f"   ✅ Synced {c.rowcount} rows")

# ============================================================
# FIX 3: Kill all sessions linked to REJECTED payments
# ============================================================
print("\n3️⃣  Deactivating sessions tied to REJECTED payments...")
c.execute("""
    UPDATE paid_sessions
    SET active = 0
    WHERE payment_request_id IN (
        SELECT id FROM payment_requests WHERE status = 'REJECTED'
    )
""")
print(f"   ✅ Deactivated {c.rowcount} orphaned sessions")

# ============================================================
# FIX 4: Fix the expired session timer bug
# ============================================================
print("\n4️⃣  Auditing session durations (should be 60 min)...")
c.execute("""
    SELECT id, started_at, expires_at FROM paid_sessions
""")
rows = c.fetchall()
fixed_count = 0
for r in rows:
    try:
        start = datetime.datetime.fromisoformat(r[1])
        end = datetime.datetime.fromisoformat(r[2])
        duration = (end - start).total_seconds() / 60
        if duration < 55 or duration > 65:
            # Fix: set expires = start + 60 minutes
            new_expires = (start + datetime.timedelta(minutes=60)).isoformat()
            c.execute("UPDATE paid_sessions SET expires_at = ? WHERE id = ?",
                      (new_expires, r[0]))
            print(f"   🔧 Session #{r[0]}: {duration:.1f}min → fixed to 60min")
            fixed_count += 1
    except Exception as e:
        print(f"   ⚠️ Session #{r[0]}: {e}")

if fixed_count == 0:
    print("   ✓ All session durations are correct")

# ============================================================
# FIX 5: Add proper 'subject' column usage — check if config exists
# ============================================================
print("\n5️⃣  Checking for subject config files...")
config_files = [f for f in os.listdir(".") if f.endswith(".py")]
paid_files = [f for f in config_files if "paid" in f.lower()]
print(f"   • Payment-related files: {paid_files}")

# ============================================================
# FIX 6: Ensure Student 1 has valid data
# ============================================================
print("\n6️⃣  Verifying Student 1 data...")
c.execute("SELECT id, name, grade_form, subject FROM students WHERE id = 1")
student = c.fetchone()
if student:
    print(f"   ✅ Student {student[0]}: {student[1]} | {student[2]} | {student[3]}")
else:
    print("   ❌ Student 1 missing — creating...")
    c.execute("""
        INSERT INTO students (id, name, grade_form, subject, tutor)
        VALUES (1, 'Tinashe', 'Form 3', 'Maths', 'Tariro')
    """)
    print("   ✅ Student 1 created")

# ============================================================
# FIX 7: Create a clean PENDING test payment
# ============================================================
print("\n7️⃣  Creating a clean PENDING test payment...")
c.execute("""
    INSERT INTO payment_requests (student_id, subject, amount, status)
    VALUES (1, 'Maths', 1.0, 'PENDING')
""")
new_id = c.lastrowid
print(f"   ✅ Created payment request #{new_id} (PENDING, $1.00, Maths)")

# ============================================================
# VERIFY: Show the corrected state
# ============================================================
conn.commit()
print("\n" + "="*70)
print("📊 AFTER REPAIR — CURRENT STATE")
print("="*70)

print("\n💰 PAYMENT REQUESTS (last 5):")
c.execute("""
    SELECT id, student_id, subject, amount, status FROM payment_requests
    ORDER BY id DESC LIMIT 5
""")
for r in c.fetchall():
    print(f"   • Request #{r[0]} | Student {r[1]} | {r[2]} | ${r[3]} | {r[4]}")

print("\n🎫 PAID SESSIONS (last 5):")
c.execute("""
    SELECT id, student_id, subject, active, started_at, expires_at
    FROM paid_sessions ORDER BY id DESC LIMIT 5
""")
for r in c.fetchall():
    status = "🟢 ACTIVE" if r[3] == 1 else "🔴 EXPIRED"
    print(f"   • Session #{r[0]} | Student {r[1]} | {r[2]} | {status}")
    print(f"     Start: {r[4]} | Expire: {r[5]}")

print("\n🟢 ACTIVE SESSIONS RIGHT NOW:")
c.execute("SELECT COUNT(*) FROM paid_sessions WHERE active = 1")
count = c.fetchone()[0]
if count == 0:
    print("   ⚠️ No active sessions — this is expected until a new one is started")
else:
    print(f"   ✅ {count} active session(s)")

conn.close()

print("\n" + "="*70)
print("✅ PAYMENT FLOW REPAIR COMPLETE")
print("="*70)
print("\n📌 NEXT STEP: Test the full flow manually:")
print("   1. Open http://127.0.0.1:5000/founder/payments")
print("   2. Verify payment request #6")
print("   3. Open http://127.0.0.1:5001/student/1/home")
print("   4. Click 'START 1-HOUR LESSON'")
print("   5. Re-run: python verify_payment_flow.py")
print()
