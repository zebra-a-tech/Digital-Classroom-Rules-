"""
Verify db_bootstrap works in isolation. Uses a throwaway DB file in /tmp-ish
local dir. Never touches the live digital_classroom.db.
"""
import os, tempfile, sqlite3, pathlib, sys

# Use a temporary path
tmpdir = tempfile.mkdtemp(prefix="dcr_bootstrap_test_")
test_db = os.path.join(tmpdir, "test.db")
os.environ["DB_PATH"] = test_db

import importlib
import db_bootstrap
importlib.reload(db_bootstrap)

print("Testing bootstrap at:", test_db)

# First run — should create
p = db_bootstrap.ensure_db()
con = sqlite3.connect(test_db)
con.row_factory = sqlite3.Row
cur = con.cursor()

# Check all critical tables exist
required = [
    "students", "auth_users", "curriculum", "student_subjects",
    "learning_progress", "homework", "assignments",
    "assignment_questions", "assignment_submissions",
    "student_sessions", "paid_sessions", "payment_requests",
    "tutor_memory", "learning_sessions",
    "weekly_assignments", "weekly_assignment_questions",
    "academic_tests", "academic_exams", "whatsapp_users",
]
missing = []
for t in required:
    r = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)
    ).fetchone()
    if not r:
        missing.append(t)
print(f"[1] all required tables: {'PASS' if not missing else 'FAIL ' + str(missing)}")

# Curriculum count
n = cur.execute("SELECT COUNT(*) FROM curriculum").fetchone()[0]
print(f"[2] curriculum rows: {n}  ({'PASS' if n > 0 else 'FAIL'})")

# Second run — should be idempotent
db_bootstrap.ensure_db()
n2 = cur.execute("SELECT COUNT(*) FROM curriculum").fetchone()[0]
print(f"[3] idempotent re-run: {n2} rows (expected {n}) — {'PASS' if n2 == n else 'FAIL'}")

con.close()

# Cleanup
import shutil
shutil.rmtree(tmpdir, ignore_errors=True)
print("Cleaned up:", tmpdir)

# Ensure we don't leave DB_PATH set
os.environ.pop("DB_PATH", None)
