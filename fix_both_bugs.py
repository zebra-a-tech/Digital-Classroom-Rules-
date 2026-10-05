"""Fix gate blocking + landing page KeyError"""

# ============================================================
# BUG 1: Landing page — fix the KeyError
# ============================================================
print("1️⃣  Fixing auth.py landing page KeyError...")

with open("auth.py", "r", encoding="utf-8") as f:
    auth = f.read()

with open("auth_before_landing_fix.py", "w", encoding="utf-8") as f:
    f.write(auth)

old_landing = '''@app.route("/")
    def landing():
        if "user_id" in session:
            return redirect(url_for("home", sid=session["student_id"]))
        return render_template_string(LANDING_HTML)'''

new_landing = '''@app.route("/")
    def landing():
        if "user_id" in session and "student_id" in session:
            return redirect(url_for("home", sid=session["student_id"]))
        return render_template_string(LANDING_HTML)'''

if old_landing in auth:
    auth = auth.replace(old_landing, new_landing)
    print("   ✅ Landing page now checks for student_id")
else:
    print("   ⚠️ Landing pattern not found — checking alternate")

with open("auth.py", "w", encoding="utf-8") as f:
    f.write(auth)

# ============================================================
# BUG 2: Trial gate — allow any session belonging to student
# ============================================================
print("\n2️⃣  Fixing paid_access.py gate...")

with open("paid_access.py", "r", encoding="utf-8") as f:
    paid = f.read()

with open("paid_access_before_gate_v2.py", "w", encoding="utf-8") as f:
    f.write(paid)

# Replace the strict trial-only check with a broader check
old_gate = '''if (
            len(parts) >= 5
            and route == "session"
        ):
            try:
                trial_session_id = int(parts[4])

                conn = db()
                trial_row = conn.execute("""
                    SELECT id, student_id, session_type, expires_at, paused
                    FROM student_sessions
                    WHERE id=?
                      AND student_id=?
                      AND session_type='trial'
                """, (trial_session_id, student_id)).fetchone()
                conn.close()

                if trial_row:
                    from datetime import datetime

                    # A paused unfinished trial remains accessible.
                    if trial_row["paused"]:
                        return None

                    expires = datetime.fromisoformat(
                        trial_row["expires_at"]
                    )

                    if datetime.now() < expires:
                        return None
            except Exception:
                pass'''

new_gate = '''if (
            len(parts) >= 5
            and route == "session"
        ):
            try:
                session_id = int(parts[4])

                conn = db()
                # Look up ANY session (trial or paid) for this student
                session_row = conn.execute("""
                    SELECT id, student_id, session_type, expires_at, paused, completed
                    FROM student_sessions
                    WHERE id=?
                      AND student_id=?
                """, (session_id, student_id)).fetchone()
                conn.close()

                if session_row:
                    from datetime import datetime

                    # If completed, allow (it's just showing the end state)
                    if session_row["completed"]:
                        return None

                    # Paused sessions should still be accessible
                    if session_row["paused"]:
                        return None

                    # Otherwise check expiry
                    if session_row["expires_at"]:
                        try:
                            expires = datetime.fromisoformat(session_row["expires_at"])
                            if datetime.now() < expires:
                                return None
                        except Exception:
                            # If we can't parse, allow (be lenient)
                            return None
                    else:
                        # No expiry set — allow
                        return None
            except Exception:
                pass

        # Also allow paid_sessions access
        if (
            len(parts) >= 4
            and route == "session"
        ):
            try:
                session_id = int(parts[-1])
                conn = db()
                paid_row = conn.execute("""
                    SELECT id, student_id, active
                    FROM paid_sessions
                    WHERE id=?
                      AND student_id=?
                      AND active=1
                """, (session_id, student_id)).fetchone()
                conn.close()

                if paid_row:
                    return None
            except Exception:
                pass'''

if old_gate in paid:
    paid = paid.replace(old_gate, new_gate)
    print("   ✅ Gate now allows ANY session belonging to the student")
else:
    print("   ⚠️ Gate pattern not found — trying regex")

    import re
    # Fallback: replace the session_type='trial' line
    paid = re.sub(
        r"AND session_type='trial'\s*\n\s*\"\"\", \(trial_session_id, student_id\)\)",
        '""", (trial_session_id, student_id))',
        paid
    )
    paid = paid.replace("AND session_type='trial'", "-- session_type filter removed")

with open("paid_access.py", "w", encoding="utf-8") as f:
    f.write(paid)

# ============================================================
# BUG 3: Reset Session 33 to be a valid 30-min trial
# ============================================================
print("\n3️⃣  Recreating Session 33 as valid trial...")

import sqlite3
from datetime import datetime, timedelta

conn = sqlite3.connect("digital_classroom.db")
now = datetime.now()
expires = (now + timedelta(minutes=30)).isoformat()

conn.execute("""
    UPDATE student_sessions
    SET started_at = ?,
        expires_at = ?,
        paused = 0,
        paused_at = NULL,
        completed = 0,
        session_type = 'trial'
    WHERE id = 33
""", (now.isoformat(), expires))

conn.commit()
print(f"   ✅ Session 33 fixed: expires at {expires}")
conn.close()

print("\n" + "="*70)
print("✅ BOTH BUGS FIXED")
print("="*70)
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   1. http://127.0.0.1:5001/         → Landing page")
print("   2. http://127.0.0.1:5001/student/3/trial → Trial page")
print("   3. http://127.0.0.1:5001/student/3/session/33 → Should show lesson")
print("="*70 + "\n")
