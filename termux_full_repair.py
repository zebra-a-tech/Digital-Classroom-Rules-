#!/usr/bin/env python3

"""
DIGITAL CLASSROOM RULES
FULL TERMUX REPAIR + INTEGRATION AUDIT

IMPORTANT:
- Uses the existing project.
- Uses digital_classroom.db as the live database.
- Does NOT rebuild the curriculum.
- Does NOT delete existing curriculum.
- Does NOT run historical fix/rebuild scripts.
- Creates a database backup before making changes.
- Only applies safe, evidence-based fixes.
"""

from pathlib import Path
import sqlite3
import shutil
import datetime
import ast
import re
import sys

ROOT = Path(__file__).resolve().parent
DB = ROOT / "digital_classroom.db"

timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
BACKUP = ROOT / f"digital_classroom_BEFORE_REPAIR_{timestamp}.db"

print("=" * 70)
print(" DIGITAL CLASSROOM RULES — FULL TERMUX REPAIR")
print("=" * 70)

# ------------------------------------------------------------
# 1. VERIFY ENVIRONMENT
# ------------------------------------------------------------

print("\n[1] VERIFYING TERMUX ENVIRONMENT")

print("Project:", ROOT)
print("Python:", sys.version.split()[0])

try:
    import flask
    print("Flask:", flask.__version__)
except Exception as e:
    print("Flask import problem:", e)

if not DB.exists():
    raise SystemExit("ERROR: digital_classroom.db was not found.")

print("Database:", DB)
print("Database size:", DB.stat().st_size, "bytes")


# ------------------------------------------------------------
# 2. BACKUP DATABASE
# ------------------------------------------------------------

print("\n[2] CREATING DATABASE BACKUP")

shutil.copy2(DB, BACKUP)

if not BACKUP.exists():
    raise SystemExit("ERROR: Database backup was not created.")

print("Backup created:")
print(BACKUP.name)


# ------------------------------------------------------------
# 3. DATABASE INTEGRITY
# ------------------------------------------------------------

print("\n[3] CHECKING DATABASE INTEGRITY")

con = sqlite3.connect(DB)
cur = con.cursor()

integrity = cur.execute("PRAGMA integrity_check").fetchone()[0]
print("SQLite integrity:", integrity)

if integrity != "ok":
    con.close()
    raise SystemExit(
        "STOP: Database integrity check failed. "
        "No repair changes were made."
    )


# ------------------------------------------------------------
# 4. PROTECT REAL CURRICULUM
# ------------------------------------------------------------

curriculum_count = cur.execute(
    "SELECT COUNT(*) FROM curriculum"
).fetchone()[0]

print("\n[4] PROTECTING CURRICULUM")
print("Existing curriculum records:", curriculum_count)

if curriculum_count != 827:
    print(
        "WARNING: Expected current inventory is 827 records, "
        "but database currently contains:",
        curriculum_count
    )

print("No curriculum deletion/rebuild will be performed.")


# ------------------------------------------------------------
# 5. INSPECT CORE TABLES
# ------------------------------------------------------------

print("\n[5] LIVE DATABASE INVENTORY")

tables = [
    "students",
    "curriculum",
    "lessons",
    "homework",
    "homework_bank",
    "assignments",
    "assignment_questions",
    "student_subjects",
    "learning_progress",
    "learning_sessions",
    "tutor_memory",
    "tutor_sessions",
    "paid_sessions",
    "payment_requests",
    "parent_assist_submissions",
    "weekly_assignments",
    "weekly_assignment_questions",
]

existing_tables = {
    row[0]
    for row in cur.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
}

for table in tables:
    if table in existing_tables:
        count = cur.execute(
            f"SELECT COUNT(*) FROM {table}"
        ).fetchone()[0]
        print(f"{table:32} {count}")
    else:
        print(f"{table:32} MISSING")


# ------------------------------------------------------------
# 6. VERIFY CURRICULUM IS REAL / NON-EMPTY
# ------------------------------------------------------------

print("\n[6] VERIFYING CURRICULUM CONTENT")

empty_content = cur.execute("""
    SELECT COUNT(*)
    FROM curriculum
    WHERE content IS NULL
       OR TRIM(content) = ''
""").fetchone()[0]

empty_goals = cur.execute("""
    SELECT COUNT(*)
    FROM curriculum
    WHERE lesson_goal IS NULL
       OR TRIM(lesson_goal) = ''
""").fetchone()[0]

empty_intro = cur.execute("""
    SELECT COUNT(*)
    FROM curriculum
    WHERE tutor_intro IS NULL
       OR TRIM(tutor_intro) = ''
""").fetchone()[0]

print("Empty content:", empty_content)
print("Empty goals:", empty_goals)
print("Empty tutor introductions:", empty_intro)

if empty_content:
    print(
        "WARNING: Some curriculum records have empty content."
        " No fabricated content will be inserted."
    )


# ------------------------------------------------------------
# 7. CORE PYTHON SYNTAX CHECK
# ------------------------------------------------------------

print("\n[7] CHECKING CORE PYTHON FILES")

core_files = [
    "app.py",
    "auth.py",
    "database.py",
    "student_server.py",
    "student_learning.py",
    "student_playbook.py",
    "student_academy.py",
    "student_portal.py",
    "student_flow.py",
    "student_app.py",
    "paid_access.py",
    "parent_assist.py",
    "marking_flow.py",
    "curriculum_expansion.py",
]

syntax_errors = []

for filename in core_files:
    path = ROOT / filename

    if not path.exists():
        print(f"MISSING: {filename}")
        continue

    try:
        ast.parse(path.read_text(errors="ignore"))
        print(f"OK: {filename}")
    except SyntaxError as e:
        print(
            f"SYNTAX ERROR: {filename} "
            f"line {e.lineno}: {e.msg}"
        )
        syntax_errors.append(filename)

if syntax_errors:
    print("\nSyntax errors detected:")
    for filename in syntax_errors:
        print(" -", filename)

    print(
        "\nNo automatic destructive rewrite will be performed."
        "\nFixes must be made against the actual traceback."
    )


# ------------------------------------------------------------
# 8. CHECK FOR DANGEROUS DEFAULT MATHS LOGIC
# ------------------------------------------------------------

print("\n[8] CHECKING FOR SUBJECT DEFAULTS")

subject_problem_files = []

for filename in [
    "student_server.py",
    "student_academy.py",
    "student_portal.py",
    "student_flow.py",
    "student_learning.py",
    "student_playbook.py",
]:
    path = ROOT / filename

    if not path.exists():
        continue

    text = path.read_text(errors="ignore")

    patterns = [
        'get("subject", "Maths")',
        "get('subject', 'Maths')",
        'get("subject","Maths")',
        "get('subject','Maths')",
    ]

    found = []

    for pattern in patterns:
        if pattern in text:
            found.append(pattern)

    if found:
        subject_problem_files.append(filename)
        print(
            f"REVIEW: {filename} contains a Maths subject fallback."
        )

if not subject_problem_files:
    print("No direct Maths fallback detected in core files.")

print(
    "IMPORTANT: Existing selected subject must always take priority."
)


# ------------------------------------------------------------
# 9. VERIFY GRADE/FORM BANDS
# ------------------------------------------------------------

print("\n[9] VERIFYING GRADE/FORM BANDS")

expected_bands = {
    "Grade 1": "G1_G3",
    "Grade 2": "G1_G3",
    "Grade 3": "G1_G3",
    "Grade 4": "G4_G5",
    "Grade 5": "G4_G5",
    "Grade 6": "G6_G7",
    "Grade 7": "G6_G7",
    "Form 1": "F1_F2",
    "Form 2": "F1_F2",
    "Form 3": "F3_F4",
    "Form 4": "F3_F4",
    "Form 5": "F5_F6",
    "Form 6": "F5_F6",
}

print("Expected learning bands:")

for grade, band in expected_bands.items():
    print(f"{grade:10} -> {band}")


# ------------------------------------------------------------
# 10. CHECK GRADE-AWARE ENGINE
# ------------------------------------------------------------

print("\n[10] CHECKING GRADE-AWARE LEARNING ENGINE")

learning_path = ROOT / "student_learning.py"

if learning_path.exists():
    text = learning_path.read_text(errors="ignore")

    required_functions = [
        "get_grade_aware_question",
        "get_grade_aware_lesson",
    ]

    for function in required_functions:
        if f"def {function}" in text:
            print(f"OK: {function}")
        else:
            print(f"REVIEW: {function} not found")
else:
    print("student_learning.py missing")


# ------------------------------------------------------------
# 11. CHECK PAID ACCESS
# ------------------------------------------------------------

print("\n[11] CHECKING PAID LESSON ACCESS")

paid_path = ROOT / "paid_access.py"

if paid_path.exists():
    paid_text = paid_path.read_text(errors="ignore")

    for keyword in [
        "payment",
        "approved",
        "paid",
        "unlock",
    ]:
        if keyword in paid_text.lower():
            print(f"Found paid-access logic: {keyword}")

    print(
        "Paid lessons must remain locked until verified access."
    )
else:
    print("WARNING: paid_access.py not found.")


# ------------------------------------------------------------
# 12. CHECK ONBOARDING / MULTI-SUBJECT SUPPORT
# ------------------------------------------------------------

print("\n[12] CHECKING MULTI-SUBJECT SUPPORT")

subject_table_exists = "student_subjects" in existing_tables

if subject_table_exists:
    print("student_subjects table: PRESENT")

    columns = [
        row[1]
        for row in cur.execute(
            "PRAGMA table_info(student_subjects)"
        ).fetchall()
    ]

    print("Columns:", ", ".join(columns))

    if "subject" in columns:
        print("Subject selection storage: PRESENT")
    else:
        print("REVIEW: subject column missing")
else:
    print("WARNING: student_subjects table missing")


# ------------------------------------------------------------
# 13. CHECK PARENT ASSIST / MARKING
# ------------------------------------------------------------

print("\n[13] CHECKING PARENT ASSIST / MARKING")

if "parent_assist_submissions" in existing_tables:

    columns = [
        row[1]
        for row in cur.execute(
            "PRAGMA table_info(parent_assist_submissions)"
        ).fetchall()
    ]

    print("parent_assist_submissions columns:")
    print(", ".join(columns))

    expected = [
        "student_id",
        "lesson_grade",
        "lesson_subject",
        "lesson_topic",
        "parent_name",
    ]

    for col in expected:
        if col in columns:
            print(f"OK: {col}")
        else:
            print(f"REVIEW: missing {col}")

else:
    print(
        "parent_assist_submissions table is not currently present."
    )


# ------------------------------------------------------------
# 14. CHECK PAYMENT DATA
# ------------------------------------------------------------

print("\n[14] PAYMENT DATA CHECK")

if "payment_requests" in existing_tables:

    rows = cur.execute("""
        SELECT id, student_id, status
        FROM payment_requests
        ORDER BY id
    """).fetchall()

    for row in rows:
        print(
            f"Payment request {row[0]} "
            f"student={row[1]} status={row[2]}"
        )


# ------------------------------------------------------------
# 15. CHECK ACTIVE FLASK APPLICATIONS
# ------------------------------------------------------------

print("\n[15] FLASK APPLICATION CHECK")

for filename in [
    "app.py",
    "student_server.py",
    "student_portal.py",
    "student_app.py",
    "student_academy.py",
]:
    path = ROOT / filename

    if not path.exists():
        continue

    text = path.read_text(errors="ignore")

    flask_count = (
        text.count("Flask(")
        + text.count("Flask (")
    )

    route_count = text.count("@app.route")

    print(
        f"{filename:25} "
        f"Flask apps={flask_count} "
        f"routes={route_count}"
    )


# ------------------------------------------------------------
# 16. VERIFY DATABASE AFTER AUDIT
# ------------------------------------------------------------

print("\n[16] FINAL DATABASE VERIFICATION")

after_count = cur.execute(
    "SELECT COUNT(*) FROM curriculum"
).fetchone()[0]

print("Curriculum before:", curriculum_count)
print("Curriculum after :", after_count)

if after_count != curriculum_count:
    print(
        "STOP: Curriculum count changed unexpectedly."
    )
    con.rollback()
    con.close()
    raise SystemExit(1)

print("Curriculum unchanged.")

con.close()


# ------------------------------------------------------------
# 17. FINAL REPORT
# ------------------------------------------------------------

print("\n" + "=" * 70)
print(" REPAIR/AUDIT COMPLETE")
print("=" * 70)

print()
print("Database backup:")
print(BACKUP.name)

print()
print("IMPORTANT:")
print("This pass intentionally did NOT:")
print("- delete curriculum")
print("- recreate curriculum")
print("- fabricate lessons")
print("- run historical fix scripts")
print("- replace the live database")
print("- download an AI model")
print("- install third-party integrations")

print()
print("Existing real curriculum remains protected.")
print()
print("Next step: use the actual application behavior/traceback")
print("to make targeted repairs rather than guessing.")
print("=" * 70)
