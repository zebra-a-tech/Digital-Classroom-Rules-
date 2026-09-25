import os
import re
import ast
import sqlite3
import py_compile
from pathlib import Path

ROOT = Path(".").resolve()

print("=" * 70)
print("DIGITAL CLASSROOM RULES — PHASE 1 DIAGNOSTIC SCAN")
print("=" * 70)
print("Project:", ROOT)
print()

# ------------------------------------------------------------
# 1. PYTHON FILES
# ------------------------------------------------------------

py_files = sorted(ROOT.rglob("*.py"))

print("=" * 70)
print("1. PYTHON FILES")
print("=" * 70)

for f in py_files:
    print(f.relative_to(ROOT))

print()
print("Python files found:", len(py_files))

# ------------------------------------------------------------
# 2. SYNTAX CHECK
# ------------------------------------------------------------

print()
print("=" * 70)
print("2. PYTHON SYNTAX CHECK")
print("=" * 70)

syntax_errors = []

for f in py_files:
    try:
        py_compile.compile(str(f), doraise=True)
    except Exception as e:
        syntax_errors.append((f, str(e)))

if not syntax_errors:
    print("✅ No Python syntax errors found.")
else:
    print("❌ SYNTAX ERRORS:")
    for f, e in syntax_errors:
        print()
        print("FILE:", f.relative_to(ROOT))
        print(e)

# ------------------------------------------------------------
# 3. FLASK ROUTE SCAN
# ------------------------------------------------------------

print()
print("=" * 70)
print("3. FLASK ROUTES")
print("=" * 70)

routes = []

route_patterns = [
    re.compile(
        r'@\s*(?:app|[A-Za-z_][A-Za-z0-9_]*)\.route\s*\(\s*'
        r'[\'"]([^\'"]+)[\'"]'
    ),
    re.compile(
        r'@\s*(?:app|[A-Za-z_][A-Za-z0-9_]*)\.route\s*\(\s*'
        r'[\'"]([^\'"]+)[\'"]\s*,\s*methods\s*=\s*\[([^\]]*)\]'
    ),
]

for f in py_files:
    try:
        text = f.read_text(errors="ignore")
    except Exception:
        continue

    for line_no, line in enumerate(text.splitlines(), 1):
        if ".route(" not in line:
            continue

        match = re.search(
            r'\.route\s*\(\s*[\'"]([^\'"]+)[\'"]',
            line
        )

        if match:
            route = match.group(1)
            methods = ""

            m2 = re.search(r'methods\s*=\s*\[([^\]]*)\]', line)
            if m2:
                methods = m2.group(1)

            routes.append(
                (
                    route,
                    methods,
                    str(f.relative_to(ROOT)),
                    line_no
                )
            )

if routes:
    for route, methods, file, line in sorted(routes):
        print(f"{route:<55} {file}:{line}")
        if methods:
            print(f"    methods: {methods}")
else:
    print("⚠️ No Flask routes detected.")

print()
print("Routes found:", len(routes))

# ------------------------------------------------------------
# 4. URL REFERENCES
# ------------------------------------------------------------

print()
print("=" * 70)
print("4. INTERNAL URL REFERENCES")
print("=" * 70)

url_refs = []

url_patterns = [
    re.compile(r'url_for\s*\(\s*[\'"]([^\'"]+)[\'"]'),
    re.compile(r'href\s*=\s*[\'"](/[^\'"]*)[\'"]'),
    re.compile(r'action\s*=\s*[\'"](/[^\'"]*)[\'"]'),
    re.compile(r'redirect\s*\(\s*[\'"](/[^\'"]*)[\'"]'),
]

for f in py_files:
    try:
        text = f.read_text(errors="ignore")
    except Exception:
        continue

    for line_no, line in enumerate(text.splitlines(), 1):
        for pattern in url_patterns:
            for match in pattern.finditer(line):
                url_refs.append(
                    (
                        match.group(1),
                        str(f.relative_to(ROOT)),
                        line_no
                    )
                )

seen_refs = set()

for url, file, line in url_refs:
    key = (url, file, line)
    if key in seen_refs:
        continue
    seen_refs.add(key)
    print(f"{url:<55} {file}:{line}")

print()
print("URL references found:", len(seen_refs))

# ------------------------------------------------------------
# 5. BLUEPRINT / ROUTE REGISTRATION
# ------------------------------------------------------------

print()
print("=" * 70)
print("5. ROUTE / MODULE REGISTRATION")
print("=" * 70)

registration_words = [
    "register_",
    "register_blueprint",
    "add_url_rule"
]

for f in py_files:
    try:
        text = f.read_text(errors="ignore")
    except Exception:
        continue

    for line_no, line in enumerate(text.splitlines(), 1):
        if any(x in line for x in registration_words):
            print(
                f"{f.relative_to(ROOT)}:{line_no}: {line.strip()}"
            )

# ------------------------------------------------------------
# 6. DATABASE SCAN
# ------------------------------------------------------------

print()
print("=" * 70)
print("6. DATABASE")
print("=" * 70)

db_path = ROOT / "digital_classroom.db"

if not db_path.exists():
    print("❌ digital_classroom.db NOT FOUND")
else:
    print("✅ Database found:", db_path)

    conn = sqlite3.connect(str(db_path))
    cur = conn.cursor()

    cur.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    tables = [r[0] for r in cur.fetchall()]

    print()
    print("TABLES:")

    for table in tables:
        print(" -", table)

    print()
    print("TABLE COUNTS:")

    for table in tables:
        try:
            cur.execute(
                'SELECT COUNT(*) FROM "' + table.replace('"', '""') + '"'
            )
            count = cur.fetchone()[0]
            print(f" {table:<35} {count}")
        except Exception as e:
            print(f" {table:<35} ERROR: {e}")

    # --------------------------------------------------------
    # IMPORTANT PAYMENT TABLES
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("PAYMENT TABLE STRUCTURE")
    print("-" * 70)

    for table in ["payment_requests", "paid_sessions"]:
        if table in tables:
            print()
            print("TABLE:", table)

            cur.execute(f'PRAGMA table_info("{table}")')

            for row in cur.fetchall():
                print(
                    f"  {row[1]:<25} "
                    f"type={row[2]:<15} "
                    f"notnull={row[3]} "
                    f"default={row[4]}"
                )

    # --------------------------------------------------------
    # PAYMENT RECORDS
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("CURRENT PAYMENT REQUESTS")
    print("-" * 70)

    if "payment_requests" in tables:
        cur.execute("""
            SELECT
                id,
                student_id,
                subject,
                amount,
                status,
                requested_at,
                verified_at,
                session_started,
                session_expires
            FROM payment_requests
            ORDER BY id DESC
            LIMIT 20
        """)

        rows = cur.fetchall()

        if not rows:
            print("No payment requests currently exist.")
        else:
            for row in rows:
                print(row)

    # --------------------------------------------------------
    # PAID SESSIONS
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("CURRENT PAID SESSIONS")
    print("-" * 70)

    if "paid_sessions" in tables:
        cur.execute("""
            SELECT
                id,
                student_id,
                payment_request_id,
                started_at,
                expires_at,
                active
            FROM paid_sessions
            ORDER BY id DESC
            LIMIT 20
        """)

        rows = cur.fetchall()

        if not rows:
            print("No paid sessions currently exist.")
        else:
            for row in rows:
                print(row)

    # --------------------------------------------------------
    # STUDENT 1
    # --------------------------------------------------------

    print()
    print("-" * 70)
    print("STUDENT 1 PAYMENT STATUS")
    print("-" * 70)

    if "students" in tables:
        cur.execute("""
            SELECT *
            FROM students
            WHERE id=1
        """)

        student = cur.fetchone()

        if student:
            print("Student 1 exists:")
            print(student)
        else:
            print("⚠️ Student 1 does not exist.")

    if "paid_sessions" in tables:
        cur.execute("""
            SELECT *
            FROM paid_sessions
            WHERE student_id=1
            ORDER BY id DESC
            LIMIT 5
        """)

        sessions = cur.fetchall()

        print()
        print("Student 1 paid sessions:")

        if sessions:
            for row in sessions:
                print(row)
        else:
            print("None.")

    conn.close()

# ------------------------------------------------------------
# 7. LESSON / CONTENT FILE DISCOVERY
# ------------------------------------------------------------

print()
print("=" * 70)
print("7. LESSON / CONTENT FILE DISCOVERY")
print("=" * 70)

content_extensions = {
    ".py",
    ".json",
    ".txt",
    ".md",
    ".html",
    ".csv",
    ".db"
}

content_files = []

for f in ROOT.rglob("*"):
    if not f.is_file():
        continue

    if any(
        part in {
            ".git",
            "__pycache__",
            ".venv",
            "venv"
        }
        for part in f.parts
    ):
        continue

    if f.suffix.lower() in content_extensions:
        content_files.append(f)

for f in sorted(content_files):
    print(f.relative_to(ROOT))

print()
print("Content files found:", len(content_files))

# ------------------------------------------------------------
# 8. GRADE / FORM + SUBJECT DETECTION
# ------------------------------------------------------------

print()
print("=" * 70)
print("8. DETECTED GRADE/FORM + SUBJECT CONTENT")
print("=" * 70)

levels = [
    *(f"Grade {i}" for i in range(1, 8)),
    *(f"Form {i}" for i in range(1, 7))
]

subjects = [
    "Maths",
    "English",
    "Science",
    "Social Studies",
    "Geography",
    "History",
    "Biology",
    "Chemistry",
    "Physics",
    "Economics",
    "Accounting"
]

detected = []

for f in content_files:
    if f.suffix.lower() not in {
        ".py", ".json", ".txt", ".md", ".html", ".csv"
    }:
        continue

    try:
        text = f.read_text(errors="ignore")
    except Exception:
        continue

    for level in levels:
        if level.lower() in text.lower() or level.lower().replace(" ", "") in text.lower():
            for subject in subjects:
                if subject.lower() in text.lower():
                    detected.append(
                        (
                            level,
                            subject,
                            str(f.relative_to(ROOT))
                        )
                    )

unique_detected = sorted(set(detected))

for level, subject, file in unique_detected:
    print(f"{level:<10} | {subject:<18} | {file}")

print()
print("Detected combinations:", len(unique_detected))

# ------------------------------------------------------------
# 9. EXPECTED COMBINATIONS
# ------------------------------------------------------------

print()
print("=" * 70)
print("9. EXPECTED LESSON MATRIX")
print("=" * 70)

expected = [
    (level, subject)
    for level in levels
    for subject in subjects
]

print("Expected level/subject combinations:", len(expected))

detected_pairs = {
    (level, subject)
    for level, subject, _ in unique_detected
}

missing_pairs = [
    pair
    for pair in expected
    if pair not in detected_pairs
]

print()
print("POSSIBLY MISSING LEVEL/SUBJECT CONTENT:")
print()

for level, subject in missing_pairs:
    print(f"❌ {level} — {subject}")

print()
print("Possible missing combinations:", len(missing_pairs))

# ------------------------------------------------------------
# 10. PAYMENT CODE CHECK
# ------------------------------------------------------------

print()
print("=" * 70)
print("10. PAYMENT CODE CHECK")
print("=" * 70)

paid_access = ROOT / "paid_access.py"

if paid_access.exists():
    text = paid_access.read_text(errors="ignore")

    checks = {
        "request_verified_paid": "def request_verified_paid",
        "founder payments": "/founder/payments",
        "verify payment": "founder_verify_payment",
        "paid session": "paid_sessions",
        "60 minutes": "60",
        "Student ID": "STUDENT_ID",
        "paid access gate": "before_request",
    }

    for name, pattern in checks.items():
        if pattern.lower() in text.lower():
            print(f"✅ {name}")
        else:
            print(f"❌ MISSING: {name}")
else:
    print("❌ paid_access.py not found.")

print()
print("=" * 70)
print("SCAN COMPLETE — NO FILES WERE MODIFIED")
print("=" * 70)
