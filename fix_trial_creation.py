"""Fix trial session creation logic + repair existing session 33"""

import re
import sqlite3
from datetime import datetime, timedelta

# ============================================================
# STEP 1: Repair Session 33
# ============================================================
print("1️⃣  Repairing Session 33...")

conn = sqlite3.connect("digital_classroom.db")
now = datetime.now()
expires = (now + timedelta(minutes=30)).isoformat()

conn.execute("""
    UPDATE student_sessions
    SET started_at = ?,
        expires_at = ?,
        paused = 0,
        paused_at = NULL
    WHERE id = 33
""", (now.isoformat(), expires))

conn.commit()
print(f"   ✅ Session 33: expires at {expires}")
print(f"   ✅ Session 33: paused = 0")
conn.close()

# ============================================================
# STEP 2: Find the session creation code
# ============================================================
print("\n2️⃣  Finding session creation code...")

with open("student_server.py", "r", encoding="utf-8") as f:
    content = f.read()

with open("student_server_before_trial_fix.py", "w", encoding="utf-8") as f:
    f.write(content)
print("   ✅ Backup saved: student_server_before_trial_fix.py")

# Look for the start_session function
start_session_match = re.search(
    r'def start_session\(sid,\s*session_type\):.*?(?=\n@app\.route|\Z)',
    content,
    re.DOTALL
)

if start_session_match:
    old_start = start_session_match.group(0)
    print(f"\n   Found start_session function ({len(old_start)} chars)")
    print("   First 30 lines:")
    for i, line in enumerate(old_start.split("\n")[:30], 1):
        print(f"      {i}: {line}")
else:
    print("   ⚠️ Could not find start_session function")

with open("student_server.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*70)
print("✅ SESSION 33 REPAIRED")
print("="*70)
print("\n📌 NEXT: Restart the server and test")
print("   python student_server.py")
print("   http://127.0.0.1:5001/student/3/trial")
print("="*70 + "\n")
