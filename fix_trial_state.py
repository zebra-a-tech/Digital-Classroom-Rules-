"""Fix trial state + show what the gate is doing"""

import sqlite3
from datetime import datetime, timedelta

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
conn.row_factory = sqlite3.Row
c = conn.cursor()

print("="*70)
print("🔍 TRIAL STATE DIAGNOSTIC + FIX")
print("="*70 + "\n")

# ============================================================
# STEP 1: Show current trial sessions
# ============================================================
print("1️⃣  Current trial sessions:")
c.execute("""
    SELECT id, student_id, started_at, expires_at, completed, paused
    FROM student_sessions
    WHERE session_type='trial'
    ORDER BY id DESC
""")
rows = c.fetchall()
for r in rows:
    print(f"   Session #{r['id']}: Student {r['student_id']}")
    print(f"      Started:  {r['started_at']}")
    print(f"      Expires:  {r['expires_at']}")
    print(f"      Completed: {r['completed']}, Paused: {r['paused']}")
    print()

if not rows:
    print("   ⚠️ No trial sessions found\n")

# ============================================================
# STEP 2: Delete expired trial sessions
# ============================================================
print("2️⃣  Cleaning up OLD trial sessions...")

now = datetime.now().isoformat()
c.execute("""
    DELETE FROM student_sessions
    WHERE session_type='trial'
    AND expires_at < ?
""", (now,))
deleted = c.rowcount
print(f"   ✅ Deleted {deleted} expired trial sessions\n")

# ============================================================
# STEP 3: Reset free_trial_used for all students
# ============================================================
print("3️⃣  Resetting free_trial_used for all students...")
c.execute("UPDATE students SET free_trial_used = 0")
reset = c.rowcount
print(f"   ✅ Reset {reset} students\n")

# ============================================================
# STEP 4: Show what's in paid_sessions
# ============================================================
print("4️⃣  Paid sessions:")
c.execute("""
    SELECT id, student_id, payment_request_id, started_at, expires_at, active
    FROM paid_sessions
    ORDER BY id DESC LIMIT 5
""")
rows = c.fetchall()
for r in rows:
    print(f"   Session #{r['id']}: Student {r['student_id']}, Active: {r['active']}")
    print(f"      Expires: {r['expires_at']}")
    print()

# ============================================================
# STEP 5: Show what "active trial" looks like now
# ============================================================
print("5️⃣  Testing active_paid_session for Student 3...")
try:
    from paid_access import active_paid_session, paid_access
    for sid in [1, 2, 3]:
        paid = active_paid_session(sid)
        has_access = paid_access(sid)
        print(f"   Student {sid}: active_paid_session = {paid}, paid_access = {has_access}")
except Exception as e:
    print(f"   ⚠️ Error: {e}")

print()
print("="*70)
print("✅ CLEANUP COMPLETE")
print("="*70)
print("\n📌 NOW RESTART:")
print("   python student_server.py")
print("\n📌 THEN TEST:")
print("   http://127.0.0.1:5001/student/3/trial")
print("="*70 + "\n")

conn.commit()
conn.close()
