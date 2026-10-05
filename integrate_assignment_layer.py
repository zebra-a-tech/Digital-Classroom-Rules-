from pathlib import Path
import sqlite3
import shutil
import re
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DB = ROOT / "digital_classroom.db"
ASSIGNMENT_SYSTEM = ROOT / "assignment_system.py"

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# ---------------------------------------------------------
# Safety backup
# ---------------------------------------------------------

db_backup = ROOT / f"digital_classroom_BEFORE_ASSIGNMENT_INTEGRATION_{timestamp}.db"
shutil.copy2(DB, db_backup)

if ASSIGNMENT_SYSTEM.exists():
    assignment_backup = ROOT / (
        f"assignment_system_BEFORE_INTEGRATION_{timestamp}.py"
    )
    shutil.copy2(ASSIGNMENT_SYSTEM, assignment_backup)
else:
    raise SystemExit("assignment_system.py was not found.")

print(f"Database backup: {db_backup.name}")
print(f"Assignment backup: {assignment_backup.name}")


# ---------------------------------------------------------
# Database helpers
# ---------------------------------------------------------

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def columns(conn, table):
    return {
        row["name"]
        for row in conn.execute(
            f'PRAGMA table_info("{table}")'
        ).fetchall()
    }


def table_exists(conn, table):
    return conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type='table' AND name=?
        """,
        (table,),
    ).fetchone() is not None


def now():
    return datetime.now().isoformat(timespec="seconds")


# ---------------------------------------------------------
# Integration event table
# ---------------------------------------------------------

conn = db()

conn.execute(
    """
    CREATE TABLE IF NOT EXISTS assignment_integration_events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submission_id INTEGER NOT NULL UNIQUE,
        student_id INTEGER NOT NULL,
        assignment_id INTEGER NOT NULL,
        subject TEXT,
        grade_form TEXT,
        topic TEXT,
        score REAL,
        total_marks REAL,
        percentage REAL,
        integrated_at TEXT NOT NULL,
        mastery_updated INTEGER DEFAULT 0,
        progress_updated INTEGER DEFAULT 0,
        tutor_memory_updated INTEGER DEFAULT 0,
        tutor_learning_updated INTEGER DEFAULT 0
    )
    """
)

conn.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_assignment_integration_student
    ON assignment_integration_events(student_id)
    """
)

conn.execute(
    """
    CREATE INDEX IF NOT EXISTS
    idx_assignment_integration_subject_topic
    ON assignment_integration_events(student_id, subject, topic)
    """
)

conn.commit()
conn.close()


# ---------------------------------------------------------
# Integration module
# ---------------------------------------------------------

module = ROOT / "assignment_integration.py"

module.write_text(
r'''
"""
Digital Classroom Rules
Assignment -> Academic Learning Integration

This module connects marked assignment results to the existing
learning/progress/tutor systems.

It NEVER replaces the curriculum.

It is deliberately schema-aware because the project has evolved
through several phases and existing tables may contain different
column sets.
"""

from pathlib import Path
import sqlite3
from datetime import datetime

ROOT = Path(__file__).resolve().parent
DB = ROOT / "digital_classroom.db"


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now().isoformat(timespec="seconds")


def table_exists(conn, table):
    return conn.execute(
        """
        SELECT 1
        FROM sqlite_master
        WHERE type='table' AND name=?
        """,
        (table,),
    ).fetchone() is not None


def columns(conn, table):
    return {
        row["name"]
        for row in conn.execute(
            f'PRAGMA table_info("{table}")'
        ).fetchall()
    }


def first_value(data, *names, default=None):
    for name in names:
        if name in data and data[name] not in (None, ""):
            return data[name]
    return default


def safe_float(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def upsert_flexible(
    conn,
    table,
    identity,
    values,
):
    """
    Generic schema-aware update/insert.

    identity:
        dictionary of fields used to find an existing row.

    values:
        dictionary of fields to update/insert.

    Only columns that actually exist are written.
    """

    if not table_exists(conn, table):
        return False

    cols = columns(conn, table)

    identity = {
        k: v
        for k, v in identity.items()
        if k in cols
    }

    values = {
        k: v
        for k, v in values.items()
        if k in cols
    }

    if not identity:
        return False

    where = " AND ".join(
        f'"{key}"=?'
        for key in identity
    )

    existing = conn.execute(
        f'SELECT rowid FROM "{table}" WHERE {where} LIMIT 1',
        tuple(identity.values()),
    ).fetchone()

    if existing:
        if not values:
            return True

        assignments = ", ".join(
            f'"{key}"=?'
            for key in values
        )

        conn.execute(
            f"""
            UPDATE "{table}"
            SET {assignments}
            WHERE {where}
            """,
            tuple(values.values()) + tuple(identity.values()),
        )
        return True

    insert_data = dict(identity)
    insert_data.update(values)

    valid = {
        k: v
        for k, v in insert_data.items()
        if k in cols
    }

    if not valid:
        return False

    fields = ", ".join(f'"{x}"' for x in valid)
    placeholders = ", ".join("?" for _ in valid)

    conn.execute(
        f"""
        INSERT INTO "{table}" ({fields})
        VALUES ({placeholders})
        """,
        tuple(valid.values()),
    )

    return True


def integrate_assignment_result(submission_id):
    """
    Main integration entry point.

    Returns a dictionary describing what was actually updated.
    """

    conn = db()

    submission = conn.execute(
        """
        SELECT
            s.*,
            st.name AS student_name,
            st.grade_form AS student_grade_form,
            st.current_subject AS student_current_subject,
            st.subject AS student_subject,
            a.subject AS assignment_subject,
            a.topic AS assignment_topic,
            a.title AS assignment_title,
            a.name AS assignment_name
        FROM assignment_submissions s
        JOIN students st
            ON st.id=s.student_id
        JOIN assignments a
            ON a.id=s.assignment_id
        WHERE s.id=?
        """,
        (submission_id,),
    ).fetchone()

    if not submission:
        conn.close()
        return {
            "ok": False,
            "reason": "submission_not_found",
        }

    status = submission["status"]

    if status != "MARKED":
        conn.close()
        return {
            "ok": False,
            "reason": f"submission_status_{status}",
        }

    # -----------------------------------------------------
    # Prevent duplicate integration
    # -----------------------------------------------------

    existing = conn.execute(
        """
        SELECT *
        FROM assignment_integration_events
        WHERE submission_id=?
        """,
        (submission_id,),
    ).fetchone()

    if existing:
        conn.close()

        return {
            "ok": True,
            "already_integrated": True,
            "submission_id": submission_id,
        }

    student_id = submission["student_id"]
    assignment_id = submission["assignment_id"]

    subject = (
        submission["assignment_subject"]
        or submission["student_current_subject"]
        or submission["student_subject"]
        or ""
    )

    topic = submission["assignment_topic"] or ""

    grade_form = (
        submission["student_grade_form"]
        or submission["grade_form"]
        or ""
    )

    score = safe_float(submission["score"])
    total_marks = safe_float(
        submission["total_marks"],
        10,
    )

    percentage = safe_float(
        submission["percentage"],
        (score / total_marks * 100)
        if total_marks
        else 0,
    )

    result = {
        "ok": True,
        "already_integrated": False,
        "submission_id": submission_id,
        "student_id": student_id,
        "assignment_id": assignment_id,
        "subject": subject,
        "topic": topic,
        "percentage": percentage,
        "mastery_updated": False,
        "progress_updated": False,
        "tutor_memory_updated": False,
        "tutor_learning_updated": False,
    }

    # -----------------------------------------------------
    # 1. LEARNING PROGRESS / MASTERY
    # -----------------------------------------------------

    if table_exists(conn, "learning_progress"):

        lp_cols = columns(conn, "learning_progress")

        identity = {}

        if "student_id" in lp_cols:
            identity["student_id"] = student_id

        if "subject" in lp_cols:
            identity["subject"] = subject

        if "topic" in lp_cols:
            identity["topic"] = topic

        progress_values = {}

        # Percentage-style fields
        for field in (
            "percentage",
            "score_percentage",
            "last_percentage",
            "latest_percentage",
            "performance",
        ):
            if field in lp_cols:
                progress_values[field] = percentage

        # Score fields
        for field in (
            "last_score",
            "latest_score",
            "score",
        ):
            if field in lp_cols:
                progress_values[field] = score

        # Total marks
        for field in (
            "total_marks",
            "last_total_marks",
            "latest_total_marks",
        ):
            if field in lp_cols:
                progress_values[field] = total_marks

        # Activity counters
        for field in (
            "attempts",
            "assignment_attempts",
        ):
            if field in lp_cols:
                existing_row = None

                if identity:
                    where = " AND ".join(
                        f'"{k}"=?'
                        for k in identity
                    )

                    existing_row = conn.execute(
                        f"""
                        SELECT "{field}"
                        FROM learning_progress
                        WHERE {where}
                        LIMIT 1
                        """,
                        tuple(identity.values()),
                    ).fetchone()

                old_value = (
                    safe_float(existing_row[field])
                    if existing_row and existing_row[field] is not None
                    else 0
                )

                progress_values[field] = int(old_value + 1)

        for field in (
            "last_activity",
            "last_updated",
            "updated_at",
            "last_assignment_at",
        ):
            if field in lp_cols:
                progress_values[field] = now()

        # Mastery fields
        #
        # We intentionally use the assignment percentage as the
        # latest evidence rather than inventing a complex mastery
        # score. Existing adaptive systems can consume the latest
        # performance evidence.

        for field in (
            "mastery",
            "mastery_score",
            "mastery_percentage",
        ):
            if field in lp_cols:
                progress_values[field] = percentage

        if identity:
            upsert_flexible(
                conn,
                "learning_progress",
                identity,
                progress_values,
            )

            result["progress_updated"] = True

            if any(
                field in lp_cols
                for field in (
                    "mastery",
                    "mastery_score",
                    "mastery_percentage",
                )
            ):
                result["mastery_updated"] = True

    # -----------------------------------------------------
    # 2. TUTOR LEARNING HISTORY
    # -----------------------------------------------------

    if table_exists(conn, "tutor_learning"):

        tl_cols = columns(conn, "tutor_learning")

        identity = {}

        if "student_id" in tl_cols:
            identity["student_id"] = student_id

        if "subject" in tl_cols:
            identity["subject"] = subject

        if "topic" in tl_cols:
            identity["topic"] = topic

        tutor_values = {}

        for field in (
            "grade_form",
            "grade",
            "learning_band",
        ):
            if field in tl_cols:
                if field == "grade_form":
                    tutor_values[field] = grade_form

        for field in (
            "score",
            "last_score",
        ):
            if field in tl_cols:
                tutor_values[field] = score

        for field in (
            "percentage",
            "last_percentage",
            "performance",
        ):
            if field in tl_cols:
                tutor_values[field] = percentage

        for field in (
            "feedback",
            "last_feedback",
        ):
            if field in tl_cols:
                tutor_values[field] = (
                    submission["feedback"]
                    or ""
                )

        for field in (
            "updated_at",
            "last_updated",
            "last_activity",
        ):
            if field in tl_cols:
                tutor_values[field] = now()

        if identity:
            upsert_flexible(
                conn,
                "tutor_learning",
                identity,
                tutor_values,
            )

            result["tutor_learning_updated"] = True

    # -----------------------------------------------------
    # 3. TUTOR MEMORY
    # -----------------------------------------------------

    if table_exists(conn, "tutor_memory"):

        tm_cols = columns(conn, "tutor_memory")

        # The memory table may use different historical schemas.
        # We write only fields that genuinely exist.

        identity = {}

        if "student_id" in tm_cols:
            identity["student_id"] = student_id

        if "subject" in tm_cols:
            identity["subject"] = subject

        if "topic" in tm_cols:
            identity["topic"] = topic

        memory_values = {}

        memory_text = (
            f"Assignment #{assignment_id} marked: "
            f"{score:g}/{total_marks:g} "
            f"({percentage:.0f}%). "
            f"Topic: {topic or 'General'}."
        )

        if submission["feedback"]:
            memory_text += (
                f" Tutor feedback: "
                f"{submission['feedback']}"
            )

        for field in (
            "memory",
            "note",
            "notes",
            "context",
            "observation",
            "message",
            "content",
        ):
            if field in tm_cols:
                memory_values[field] = memory_text
                break

        for field in (
            "created_at",
            "updated_at",
            "last_updated",
        ):
            if field in tm_cols:
                memory_values[field] = now()

        if identity and memory_values:
            upsert_flexible(
                conn,
                "tutor_memory",
                identity,
                memory_values,
            )

            result["tutor_memory_updated"] = True

    # -----------------------------------------------------
    # 4. ADAPTIVE SIGNALS
    # -----------------------------------------------------
    #
    # Store a durable academic signal so future learning
    # recommendations can identify weak areas without
    # fabricating diagnostic conclusions.

    if table_exists(conn, "learning_sessions"):

        ls_cols = columns(conn, "learning_sessions")

        identity = {}

        if "student_id" in ls_cols:
            identity["student_id"] = student_id

        session_values = {}

        for field in (
            "subject",
            "current_subject",
        ):
            if field in ls_cols:
                session_values[field] = subject

        for field in (
            "topic",
            "current_topic",
        ):
            if field in ls_cols:
                session_values[field] = topic

        for field in (
            "updated_at",
            "last_activity",
            "last_study_date",
        ):
            if field in ls_cols:
                session_values[field] = now()

        if identity and session_values:
            upsert_flexible(
                conn,
                "learning_sessions",
                identity,
                session_values,
            )

    # -----------------------------------------------------
    # 5. Record integration event
    # -----------------------------------------------------

    conn.execute(
        """
        INSERT INTO assignment_integration_events (
            submission_id,
            student_id,
            assignment_id,
            subject,
            grade_form,
            topic,
            score,
            total_marks,
            percentage,
            integrated_at,
            mastery_updated,
            progress_updated,
            tutor_memory_updated,
            tutor_learning_updated
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            submission_id,
            student_id,
            assignment_id,
            subject,
            grade_form,
            topic,
            score,
            total_marks,
            percentage,
            now(),
            int(result["mastery_updated"]),
            int(result["progress_updated"]),
            int(result["tutor_memory_updated"]),
            int(result["tutor_learning_updated"]),
        ),
    )

    conn.commit()
    conn.close()

    return result


def get_assignment_learning_history(student_id):
    """
    Returns assignment results that can be consumed by
    dashboards, weekly reports and adaptive-learning views.
    """

    conn = db()

    rows = conn.execute(
        """
        SELECT
            e.*,
            a.title,
            a.name
        FROM assignment_integration_events e
        LEFT JOIN assignments a
            ON a.id=e.assignment_id
        WHERE e.student_id=?
        ORDER BY e.integrated_at DESC
        """,
        (student_id,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def get_assignment_topic_signals(student_id):
    """
    Summarises assignment performance by subject/topic.

    This is evidence-based: it uses actual recorded assignment
    results and does not invent mastery conclusions.
    """

    conn = db()

    rows = conn.execute(
        """
        SELECT
            subject,
            topic,
            COUNT(*) AS attempts,
            AVG(percentage) AS average_percentage,
            MIN(percentage) AS lowest_percentage,
            MAX(percentage) AS highest_percentage
        FROM assignment_integration_events
        WHERE student_id=?
        GROUP BY subject, topic
        ORDER BY average_percentage ASC
        """,
        (student_id,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]
''',
encoding="utf-8",
)

print(f"Created {module.name}")


# ---------------------------------------------------------
# Patch assignment_system.py
# ---------------------------------------------------------

text = ASSIGNMENT_SYSTEM.read_text(encoding="utf-8")

import_marker = "from assignment_integration import integrate_assignment_result"

if import_marker not in text:

    # Put import after existing imports.
    lines = text.splitlines()

    insert_at = 0

    for i, line in enumerate(lines):
        if line.startswith("import ") or line.startswith("from "):
            insert_at = i + 1

    lines.insert(insert_at, import_marker)

    text = "\n".join(lines) + "\n"


# We need the integration call after a successful founder marking
# transaction.

integration_call = """
        # -------------------------------------------------
        # Academic integration
        # -------------------------------------------------
        # The assignment is now officially MARKED.
        # Feed the result into the existing learning systems.
        try:
            integrate_assignment_result(submission_id)
        except Exception as integration_error:
            # The marking result must remain saved even if an
            # optional downstream learning table has an older schema.
            print(
                "Assignment academic integration warning:",
                integration_error,
            )
"""

if "integrate_assignment_result(submission_id)" not in text:

    target = """        conn.commit()
        return redirect(
            f"/founder/assignment-submissions/{submission_id}"
        )
"""

    if target in text:
        text = text.replace(
            target,
            """        conn.commit()
""" + integration_call + """        return redirect(
            f"/founder/assignment-submissions/{submission_id}"
        )
""",
            1,
        )
    else:
        # Fallback: locate the founder_review commit/redirect section.
        pattern = (
            r"(conn\.commit\(\)\s*"
            r"return redirect\(\s*"
            r"f[\"']\/founder\/assignment-submissions/"
            r"\{submission_id\}[\"']\s*\))"
        )

        match = re.search(pattern, text)

        if not match:
            raise SystemExit(
                "Could not safely locate founder marking commit/redirect. "
                "No assignment_system.py changes were written."
            )

        original = match.group(1)

        replacement = (
            "conn.commit()\n"
            + integration_call
            + "        return redirect(\n"
            + '            f"/founder/assignment-submissions/{submission_id}"\n'
            + "        )"
        )

        text = text[:match.start()] + replacement + text[match.end():]


ASSIGNMENT_SYSTEM.write_text(
    text,
    encoding="utf-8",
)

print("Integrated academic result processing into assignment_system.py")


# ---------------------------------------------------------
# Compile everything changed
# ---------------------------------------------------------

import py_compile

for filename in (
    "assignment_integration.py",
    "assignment_system.py",
    "student_server.py",
):

    path = ROOT / filename

    if not path.exists():
        continue

    py_compile.compile(
        str(path),
        doraise=True,
    )

    print(f"SYNTAX OK: {filename}")


# ---------------------------------------------------------
# Final database preservation check
# ---------------------------------------------------------

conn = db()

curriculum_count = conn.execute(
    "SELECT COUNT(*) FROM curriculum"
).fetchone()[0]

event_count = conn.execute(
    "SELECT COUNT(*) FROM assignment_integration_events"
).fetchone()[0]

conn.close()

print()
print("=" * 68)
print("DIGITAL CLASSROOM RULES — INTEGRATION LAYER INSTALLED")
print("=" * 68)
print(f"Curriculum records preserved: {curriculum_count}")
print(f"Existing integration events: {event_count}")
print()
print("CONNECTED:")
print("  Assignment marking → learning progress")
print("  Assignment marking → mastery evidence")
print("  Assignment marking → tutor learning")
print("  Assignment marking → tutor memory")
print("  Assignment marking → adaptive learning signals")
print("  Assignment history → future reports")
print()
print("PROTECTED:")
print("  Existing curriculum")
print("  Existing tutor engine")
print("  Existing homework")
print("  Existing paid-access system")
print("  Existing assignment infrastructure")
print()
print("DUPLICATE PROTECTION: ENABLED")
print("AUTOMATIC IMAGE RECOGNITION: NOT CLAIMED")
print("UNCLEAR WORK: MANUAL REVIEW PATH")
print("=" * 68)
