
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
DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
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



def _fill_required(conn, table, valid):
    """Give NOT NULL columns with no default a safe value so inserts cannot fail."""
    stamp = now()
    for _cid, name, ctype, notnull, dflt, pk in conn.execute(f'PRAGMA table_info("{table}")'):
        if notnull and dflt is None and not pk and name not in valid:
            low = name.lower()
            if low == "session_type":
                valid[name] = "assignment_review"
            elif low.endswith("_at") or "date" in low or "time" in low:
                valid[name] = stamp
            elif "INT" in (ctype or "").upper() or "REAL" in (ctype or "").upper():
                valid[name] = 0
            else:
                valid[name] = ""
    if table == "learning_sessions":
        cols_now = {r[1] for r in conn.execute('PRAGMA table_info("learning_sessions")')}
        if "completed" in cols_now:
            valid["completed"] = 1


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

    _fill_required(conn, table, valid)
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


def _integrate_inner(submission_id):
    """
    Main integration entry point.

    Returns a dictionary describing what was actually updated.
    """

    conn = db()
    _TRACK['conn'] = conn

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


_TRACK = {}

def integrate_assignment_result(submission_id):
    """Safe wrapper: on any failure roll back and close so the DB is never left locked."""
    _TRACK.pop("conn", None)
    try:
        return _integrate_inner(submission_id)
    except Exception:
        c = _TRACK.pop("conn", None)
        if c is not None:
            try: c.rollback()
            except Exception: pass
            try: c.close()
            except Exception: pass
        raise
