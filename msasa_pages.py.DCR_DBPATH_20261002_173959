"""
msasa_pages.py — Digital Classroom Rules
----------------------------------------

Additive routes that render the Msasa design system against real
student data. Nothing here replaces existing functionality. Existing
routes in student_server.py continue unchanged.

Routes registered:
    GET /student/<int:sid>/v2             — modern dashboard
    GET /student/<int:sid>/v2/report      — printable weekly report

Data sources (all real, no fabricated numbers):
    learning_bridge.get_student, get_active_subjects, get_current_subject
    reports.weekly_report
    students, student_subjects, learning_progress, student_sessions, paid_sessions
"""

import sqlite3
import os
import datetime
from flask import render_template, abort, redirect, url_for, session


_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, "digital_classroom.db")


def _ro():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def _student_row(sid):
    con = _ro()
    try:
        return con.execute("""
            SELECT id, name, student_number, grade_form, school, location,
                   tutor, current_subject, streak, free_trial_used,
                   paid_lessons, exam_board
            FROM students WHERE id=?
        """, (sid,)).fetchone()
    finally:
        con.close()


def _subjects_for(sid):
    con = _ro()
    try:
        return [r["subject"] for r in con.execute("""
            SELECT subject FROM student_subjects
            WHERE student_id=? AND active=1
            ORDER BY subject
        """, (sid,))]
    finally:
        con.close()


def _recent_activity(sid, limit=5):
    con = _ro()
    try:
        return [dict(r) for r in con.execute("""
            SELECT subject, topic, attempts, correct, mastery, last_activity
            FROM learning_progress
            WHERE student_id=?
            ORDER BY (last_activity IS NULL), last_activity DESC
            LIMIT ?
        """, (sid, limit))]
    finally:
        con.close()


def _trial_state(sid):
    """Return (used: bool, active: bool, expires_at: str or None)."""
    con = _ro()
    try:
        row = con.execute("""
            SELECT started_at, expires_at, completed, paused
            FROM student_sessions
            WHERE student_id=? AND session_type='trial'
            ORDER BY id DESC LIMIT 1
        """, (sid,)).fetchone()
    finally:
        con.close()

    stu = _student_row(sid)
    used = bool(stu and stu["free_trial_used"])
    if not row:
        return {"used": used, "active": False, "expires_at": None}
    try:
        exp = datetime.datetime.fromisoformat(row["expires_at"])
        active = (not row["completed"]) and exp > datetime.datetime.now()
    except Exception:
        active = False
    return {"used": used or bool(row["completed"]), "active": active,
            "expires_at": row["expires_at"] if active else None}


def _paid_state(sid):
    """Return (active: bool, paused: bool, expires_at: str or None, subject: str or None)."""
    con = _ro()
    try:
        row = con.execute("""
            SELECT subject, active, paused, expires_at
            FROM paid_sessions
            WHERE student_id=? AND active=1
            ORDER BY id DESC LIMIT 1
        """, (sid,)).fetchone()
    finally:
        con.close()
    if not row:
        return {"active": False, "paused": False, "expires_at": None, "subject": None}
    return {
        "active": bool(row["active"]),
        "paused": bool(row["paused"]),
        "expires_at": row["expires_at"],
        "subject": row["subject"],
    }


def register_msasa_pages(app):
    """Attach the additive routes. Returns the app for chaining."""

    # --- Safe url_for: never crash a page because an endpoint is missing ---
    from flask import url_for as _url_for
    from werkzeug.routing import BuildError as _BuildError

    @app.context_processor
    def _inject_safe_url():
        def safe_url(endpoint, **values):
            try:
                return _url_for(endpoint, **values)
            except _BuildError:
                return "#"
        return {"safe_url": safe_url}

    @app.route("/student/<int:sid>/v2")
    def msasa_dashboard(sid):
        stu = _student_row(sid)
        if not stu:
            abort(404)

        # Ownership check: if a session has a logged-in student id, enforce it.
        logged = session.get("student_id")
        if logged is not None and int(logged) != sid:
            abort(403)

        subjects = _subjects_for(sid)
        current = (stu["current_subject"] or "").strip()
        if current not in subjects:
            current = subjects[0] if subjects else ""

        trial = _trial_state(sid)
        paid = _paid_state(sid)
        recent = _recent_activity(sid, limit=5)

        # Weakest subject (for the ring) — highest mastery? No: weakest studied topic.
        weakest = None
        if recent:
            weakest = min(recent, key=lambda r: r["mastery"] or 0)

        # Weekly report (read-only; safe if module isn't imported elsewhere)
        report = None
        try:
            import reports as _reports
            report = _reports.weekly_report(sid)
        except Exception:
            report = None

        return render_template(
            "msasa_dashboard.html",
            sid=sid,
            student=dict(stu),
            subjects=subjects,
            current_subject=current,
            trial=trial,
            paid=paid,
            recent=recent,
            weakest=weakest,
            report=report,
        )

    @app.route("/student/<int:sid>/v2/report")
    def msasa_report(sid):
        stu = _student_row(sid)
        if not stu:
            abort(404)

        logged = session.get("student_id")
        if logged is not None and int(logged) != sid:
            abort(403)

        try:
            import reports as _reports
            rep = _reports.weekly_report(sid)
        except Exception as e:
            rep = {"error": str(e)}

        return render_template("msasa_report.html", sid=sid, report=rep)

    return app
