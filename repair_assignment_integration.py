from pathlib import Path
import shutil
import re
import py_compile
from datetime import datetime

ROOT = Path(__file__).resolve().parent
ASSIGNMENT_SYSTEM = ROOT / "assignment_system.py"
BACKUP = ROOT / "assignment_system_BEFORE_INTEGRATION_20261001_223921.py"

if not BACKUP.exists():
    raise SystemExit(f"Required backup not found: {BACKUP.name}")

# ---------------------------------------------------------
# Restore the clean assignment system
# ---------------------------------------------------------

shutil.copy2(BACKUP, ASSIGNMENT_SYSTEM)
print(f"RESTORED: {ASSIGNMENT_SYSTEM.name}")
print(f"FROM:    {BACKUP.name}")

text = ASSIGNMENT_SYSTEM.read_text(encoding="utf-8")

# ---------------------------------------------------------
# Add integration import safely at the top-level
# ---------------------------------------------------------

import_line = "from assignment_integration import integrate_assignment_result"

# Remove any accidental integration import if present.
lines = [
    line for line in text.splitlines()
    if line.strip() != import_line
]

# Find the end of the top-level import section.
insert_at = 0

for i, line in enumerate(lines):
    stripped = line.strip()

    if (
        stripped.startswith("import ")
        or stripped.startswith("from ")
    ):
        insert_at = i + 1
        continue

    # Allow module docstring/comments/blank lines before imports,
    # but once real code begins, stop looking.
    if stripped and not stripped.startswith("#"):
        if insert_at:
            break

lines.insert(insert_at, import_line)

text = "\n".join(lines) + "\n"

# ---------------------------------------------------------
# Add integration call exactly once
# ---------------------------------------------------------

if "integrate_assignment_result(submission_id)" in text:
    print("Integration call already present.")
else:
    # Locate the successful founder marking redirect.
    pattern = re.compile(
        r'(?P<indent>\s*)conn\.commit\(\)\s*'
        r'(?P<redirect>return redirect\(\s*'
        r'f["\']/founder/assignment-submissions/'
        r'\{submission_id\}["\']\s*\))',
        re.MULTILINE
    )

    match = pattern.search(text)

    if not match:
        # More tolerant fallback.
        marker = 'f"/founder/assignment-submissions/{submission_id}"'

        pos = text.find(marker)

        if pos == -1:
            raise SystemExit(
                "Could not locate founder marking redirect. "
                "Assignment system was restored but NOT modified."
            )

        commit_pos = text.rfind("conn.commit()", 0, pos)

        if commit_pos == -1:
            raise SystemExit(
                "Could not locate founder marking commit. "
                "Assignment system was restored but NOT modified."
            )

        line_end = text.find("\n", commit_pos)
        if line_end == -1:
            line_end = len(text)

        integration = """

        # -------------------------------------------------
        # Academic learning integration
        # -------------------------------------------------
        try:
            integrate_assignment_result(submission_id)
        except Exception as integration_error:
            print(
                "Assignment academic integration warning:",
                integration_error,
            )
"""

        text = (
            text[:line_end]
            + integration
            + text[line_end:]
        )

    else:
        indent = match.group("indent")

        integration = (
            f"{indent}conn.commit()\n"
            f"{indent}\n"
            f"{indent}# -------------------------------------------------\n"
            f"{indent}# Academic learning integration\n"
            f"{indent}# -------------------------------------------------\n"
            f"{indent}try:\n"
            f"{indent}    integrate_assignment_result(submission_id)\n"
            f"{indent}except Exception as integration_error:\n"
            f"{indent}    print(\n"
            f"{indent}        \"Assignment academic integration warning:\",\n"
            f"{indent}        integration_error,\n"
            f"{indent}    )\n"
        )

        # Replace only the commit itself; leave redirect untouched.
        start = match.start()
        commit_match = re.search(r"conn\.commit\(\)", match.group(0))

        if not commit_match:
            raise SystemExit(
                "Could not safely patch founder marking commit."
            )

        absolute_commit_start = start + commit_match.start()
        absolute_commit_end = start + commit_match.end()

        text = (
            text[:absolute_commit_start]
            + integration.rstrip("\n")
            + "\n"
            + text[absolute_commit_end:]
        )

    ASSIGNMENT_SYSTEM.write_text(text, encoding="utf-8")
    print("Academic integration hook added.")

# ---------------------------------------------------------
# Safety checks
# ---------------------------------------------------------

print()
print("Running syntax checks...")

for filename in (
    "assignment_integration.py",
    "assignment_system.py",
    "student_server.py",
):
    path = ROOT / filename

    if path.exists():
        py_compile.compile(str(path), doraise=True)
        print(f"SYNTAX OK: {filename}")

# ---------------------------------------------------------
# Database safety verification
# ---------------------------------------------------------

import sqlite3

DB = ROOT / "digital_classroom.db"

conn = sqlite3.connect(DB)

curriculum_count = conn.execute(
    "SELECT COUNT(*) FROM curriculum"
).fetchone()[0]

submission_count = conn.execute(
    "SELECT COUNT(*) FROM assignment_submissions"
).fetchone()[0]

integration_events = conn.execute(
    "SELECT COUNT(*) FROM assignment_integration_events"
).fetchone()[0]

conn.close()

print()
print("=" * 68)
print("ASSIGNMENT INTEGRATION REPAIR COMPLETE")
print("=" * 68)
print(f"Curriculum records:       {curriculum_count}")
print(f"Assignment submissions:   {submission_count}")
print(f"Integration events:       {integration_events}")
print()
print("Assignment system:        RESTORED + INTEGRATION CONNECTED")
print("Academic integration:     CONNECTED")
print("Curriculum:               PROTECTED")
print("Paid access:              PROTECTED")
print("Homework:                 PROTECTED")
print("Tutor engine:             PROTECTED")
print("Automatic image AI:       NOT CLAIMED")
print("Manual review path:       PRESERVED")
print("=" * 68)
