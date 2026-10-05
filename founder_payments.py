"""
founder_payments.py — Digital Classroom Rules
----------------------------------------------

Founder-only dashboard for:
  * Approving / rejecting pending payment requests
  * Revoking a mistaken approval
  * Seeing key business stats at a glance
  * Viewing all registered students
  * Manually adding a student (for WhatsApp-sourced sign-ups)

Auth: FOUNDER_KEY env var + ?key=... query parameter, or X-Founder-Key header.
If FOUNDER_KEY is not set in the environment, the entire module 404s.

Routes:
  GET  /founder/dashboard
  POST /founder/payments/<int:rid>/approve
  POST /founder/payments/<int:rid>/reject
  POST /founder/payments/<int:rid>/revoke
  POST /founder/students/add          (manual add)

Add to student_server.py:
    from founder_payments import register_founder_payments
    register_founder_payments(app)
"""

import os
import sqlite3
import datetime
import html as _html
from flask import request, redirect, url_for, abort


def _db_path():
    return os.environ.get("DB_PATH", "digital_classroom.db")


def _db():
    con = sqlite3.connect(_db_path())
    con.row_factory = sqlite3.Row
    return con


def _esc(v):
    return _html.escape(str(v if v is not None else ""))


def _founder_key():
    return (os.environ.get("FOUNDER_KEY") or "").strip()


def _key_ok():
    """True if the request presents the correct founder key."""
    expected = _founder_key()
    if not expected:
        return False
    provided = (
        ((request.args.get("key") or request.cookies.get("fk")) or "").strip()
        or (request.headers.get("X-Founder-Key") or "").strip()
    )
    return provided == expected


# ---------------------------------------------------------------
# HTML helpers
# ---------------------------------------------------------------
PAGE_HEAD = """<!doctype html>
<html><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only">
<title>Founder Dashboard — Digital Classroom Rules</title>
<style>
* { box-sizing: border-box; }
body { margin:0; background:#FAF6EF; color:#1A1815;
       font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;
       line-height:1.5; }
header { background:#3B2A1A; color:#FAF6EF; padding:16px 20px; }
header h1 { margin:0; font-size:20px; }
header .sub { opacity:.8; font-size:13px; margin-top:4px; }
main { max-width:900px; margin:auto; padding:16px; }
h2 { font-size:16px; text-transform:uppercase; letter-spacing:.06em;
     color:#5C5448; margin:28px 0 10px; }
.stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(140px,1fr));
         gap:12px; margin-top:16px; }
.stat { background:#FFF; border:1px solid #E8DFCF; border-radius:12px;
        padding:16px; }
.stat .num { font-size:26px; font-weight:700; color:#3B2A1A; }
.stat .lbl { font-size:12px; text-transform:uppercase; letter-spacing:.06em;
             color:#5C5448; margin-top:4px; }
table { width:100%; border-collapse:collapse; background:#FFF;
        border:1px solid #E8DFCF; border-radius:12px; overflow:hidden;
        font-size:14px; }
th, td { padding:10px 12px; text-align:left; border-bottom:1px solid #E8DFCF; }
th { background:#F4EDE0; font-weight:600; font-size:12px; color:#5C5448;
     text-transform:uppercase; letter-spacing:.06em; }
tr:last-child td { border-bottom:0; }
.btn { display:inline-block; padding:8px 14px; border-radius:8px;
       text-decoration:none; font-weight:600; font-size:13px;
       border:1px solid transparent; cursor:pointer; margin-right:6px; }
.btn.green  { background:#2F6B3E; color:#FFF; }
.btn.red    { background:#B23A2C; color:#FFF; }
.btn.amber  { background:#C9861F; color:#FFF; }
.btn.ghost  { background:#FFF; color:#3B2A1A; border:1px solid #E8DFCF; }
.chip { display:inline-block; padding:3px 9px; border-radius:999px;
        font-size:12px; font-weight:600; }
.chip.pending  { background:rgba(201,134,31,.16); color:#8a5b10; }
.chip.verified { background:rgba(47,107,62,.14); color:#2F6B3E; }
.chip.rejected { background:rgba(178,58,44,.14); color:#B23A2C; }
.empty { background:#FFF; border:1px dashed #E8DFCF; border-radius:12px;
         padding:22px; text-align:center; color:#5C5448; font-size:14px; }
footer { text-align:center; color:#5C5448; font-size:12px; padding:30px 16px; }
form.add { background:#FFF; border:1px solid #E8DFCF; border-radius:12px;
           padding:16px; display:grid; grid-template-columns:1fr 1fr;
           gap:10px; }
form.add input, form.add select { padding:9px 11px; border:1px solid #E8DFCF;
           border-radius:8px; font-size:14px; width:100%; }
form.add button { grid-column:1/-1; padding:10px; border-radius:8px;
           border:0; background:#3B2A1A; color:#FAF6EF; font-weight:600;
           cursor:pointer; font-size:14px; }
</style>
</head><body>
"""

PAGE_FOOT = """
<footer>Digital Classroom Rules · Founder Console</footer>
</body></html>
"""


def _chip(status):
    s = (status or "PENDING").upper()
    cls = {"PENDING": "pending", "VERIFIED": "verified",
           "REJECTED": "rejected"}.get(s, "pending")
    return f'<span class="chip {cls}">{_esc(s)}</span>'


# ---------------------------------------------------------------
# Action helpers
# ---------------------------------------------------------------
def _approve(rid):
    """Mark a payment VERIFIED, spin up a 60-minute paid session, idempotent."""
    con = _db()
    try:
        row = con.execute(
            "SELECT * FROM payment_requests WHERE id=?", (rid,)
        ).fetchone()
        if not row:
            return False, "no such payment"
        if row["status"] == "VERIFIED":
            return True, "already verified"

        sid = row["student_id"]
        subj = row["subject"] or "Lesson"
        now = datetime.datetime.now()
        now_iso = now.isoformat(timespec="seconds")
        expires_iso = (now + datetime.timedelta(minutes=60)).isoformat(timespec="seconds")

        con.execute(
            "UPDATE payment_requests SET status='VERIFIED', verified_at=? WHERE id=?",
            (now_iso, rid),
        )

        # Deactivate any existing active paid sessions for this student
        con.execute(
            "UPDATE paid_sessions SET active=0, paused=0 WHERE student_id=? AND active=1",
            (sid,),
        )

        # Create the new 60-minute session
        con.execute(
            "INSERT INTO paid_sessions "
            "(student_id, payment_request_id, started_at, expires_at, "
            " active, paused, subject, total_paused_seconds) "
            "VALUES (?, ?, ?, ?, 1, 0, ?, 0)",
            (sid, rid, now_iso, expires_iso, subj),
        )

        con.execute(
            "UPDATE students SET paid_lessons=COALESCE(paid_lessons,0)+1 WHERE id=?",
            (sid,),
        )
        con.commit()
        return True, "approved"
    finally:
        con.close()


def _reject(rid):
    con = _db()
    try:
        cur = con.execute(
            "UPDATE payment_requests SET status='REJECTED' WHERE id=?",
            (rid,),
        )
        con.commit()
        return cur.rowcount > 0, "rejected"
    finally:
        con.close()


def _revoke(rid):
    """Undo a mistaken approval."""
    con = _db()
    try:
        row = con.execute(
            "SELECT * FROM payment_requests WHERE id=?", (rid,)
        ).fetchone()
        if not row:
            return False, "no such payment"

        con.execute(
            "UPDATE payment_requests SET status='REJECTED' WHERE id=?", (rid,)
        )
        con.execute(
            "UPDATE paid_sessions SET active=0, paused=0 "
            "WHERE payment_request_id=?",
            (rid,),
        )
        con.commit()
        return True, "revoked"
    finally:
        con.close()


# ---------------------------------------------------------------
# Route registration
# ---------------------------------------------------------------
def register_founder_payments(app):
    """Attach founder routes. Called from student_server.py."""

    @app.route("/founder/dashboard")
    def founder_dashboard():
        # 404 if the key isn't configured, 403 if it's wrong.
        if not _founder_key():
            abort(404)
        if not _key_ok():
            abort(403)

        key = _founder_key()
        con = _db()
        try:
            # --- stats ---
            total_students = con.execute(
                "SELECT COUNT(*) FROM students"
            ).fetchone()[0]

            pending = con.execute(
                "SELECT COUNT(*) FROM payment_requests WHERE status='PENDING'"
            ).fetchone()[0]

            active_paid = con.execute(
                "SELECT COUNT(*) FROM paid_sessions "
                "WHERE active=1 AND expires_at > ?",
                (datetime.datetime.now().isoformat(timespec="seconds"),),
            ).fetchone()[0]

            week_ago = (datetime.datetime.now() - datetime.timedelta(days=7)).isoformat(timespec="seconds")
            revenue_week = con.execute(
                "SELECT COALESCE(SUM(amount), 0) FROM payment_requests "
                "WHERE status='VERIFIED' AND verified_at > ?",
                (week_ago,),
            ).fetchone()[0]

            # --- pending payments ---
            pending_rows = con.execute("""
                SELECT pr.id, pr.student_id, pr.subject, pr.amount,
                       pr.requested_at, s.name AS student_name, s.student_number
                FROM payment_requests pr
                LEFT JOIN students s ON s.id = pr.student_id
                WHERE pr.status='PENDING'
                ORDER BY pr.id DESC
            """).fetchall()

            # --- recent history ---
            recent = con.execute("""
                SELECT pr.id, pr.student_id, pr.subject, pr.amount, pr.status,
                       pr.requested_at, pr.verified_at,
                       s.name AS student_name, s.student_number
                FROM payment_requests pr
                LEFT JOIN students s ON s.id = pr.student_id
                ORDER BY pr.id DESC LIMIT 20
            """).fetchall()

            # --- all students ---
            students = con.execute("""
                SELECT id, name, student_number, grade_form, current_subject,
                       paid_lessons, streak
                FROM students ORDER BY id
            """).fetchall()

            # --- recent registrations ---
            new_students = con.execute(
                "SELECT id, name, student_number, grade_form, registered_at "
                "FROM students WHERE registered_at > ? ORDER BY id DESC",
                (week_ago,),
            ).fetchall()

            # ------------- build HTML -------------
            body = []
            body.append(PAGE_HEAD)
            body.append(
                '<header><h1>Founder Dashboard</h1>'
                f'<div class="sub">Digital Classroom Rules · '
                f'{datetime.datetime.now().strftime("%d %b %Y %H:%M")}</div>'
                '</header><main>'
            )

            # stats
            body.append('<div class="stats">')
            for num, lbl in [
                (total_students, "Students"),
                (pending, "Pending payments"),
                (active_paid, "Active paid sessions"),
                (f"${revenue_week:.2f}", "Revenue this week"),
            ]:
                body.append(
                    f'<div class="stat"><div class="num">{_esc(num)}</div>'
                    f'<div class="lbl">{_esc(lbl)}</div></div>'
                )
            body.append('</div>')

            # pending payments
            body.append('<h2>Pending payments</h2>')
            if not pending_rows:
                body.append('<div class="empty">No pending payments right now.</div>')
            else:
                body.append(
                    '<table><tr><th>#</th><th>Student</th><th>Subject</th>'
                    '<th>Amount</th><th>Requested</th><th>Actions</th></tr>'
                )
                for r in pending_rows:
                    sid = r["student_id"]
                    name = r["student_name"] or f"Student #{sid}"
                    dcr = r["student_number"] or ""
                    subj = r["subject"] or "Lesson"
                    body.append(
                        f'<tr>'
                        f'<td>{r["id"]}</td>'
                        f'<td>{_esc(name)}<br>'
                        f'<span class="chip pending">{_esc(dcr)}</span></td>'
                        f'<td>{_esc(subj)}</td>'
                        f'<td>${r["amount"]:.2f}</td>'
                        f'<td>{_esc(r["requested_at"] or "")}</td>'
                        f'<td>'
                        f'<form method="POST" style="display:inline" '
                        f'action="/founder/payments/{r["id"]}/approve?key={key}">'
                        f'<button class="btn green" type="submit">Approve</button></form>'
                        f'<form method="POST" style="display:inline" '
                        f'action="/founder/payments/{r["id"]}/reject?key={key}">'
                        f'<button class="btn red" type="submit">Reject</button></form>'
                        f'</td></tr>'
                    )
                body.append('</table>')

            # recent history
            body.append('<h2>Recent payment requests</h2>')
            if not recent:
                body.append('<div class="empty">No history yet.</div>')
            else:
                body.append(
                    '<table><tr><th>#</th><th>Student</th><th>Subject</th>'
                    '<th>Amount</th><th>Status</th><th>Verified</th><th></th></tr>'
                )
                for r in recent:
                    sid = r["student_id"]
                    name = r["student_name"] or f"Student #{sid}"
                    body.append(
                        f'<tr>'
                        f'<td>{r["id"]}</td>'
                        f'<td>{_esc(name)}</td>'
                        f'<td>{_esc(r["subject"] or "Lesson")}</td>'
                        f'<td>${r["amount"]:.2f}</td>'
                        f'<td>{_chip(r["status"])}</td>'
                        f'<td>{_esc((r["verified_at"] or "")[:19])}</td>'
                        f'<td>'
                        f'<form method="POST" style="display:inline" '
                        f'action="/founder/payments/{r["id"]}/revoke?key={key}">'
                        f'<button class="btn ghost" type="submit" '
                        f'onclick="return confirm(\'Revoke payment #{r["id"]}?\')">Revoke</button>'
                        f'</form>'
                        f'</td></tr>'
                    )
                body.append('</table>')

            # students
            body.append('<h2>All students</h2>')
            body.append(
                '<table><tr><th>#</th><th>DCR</th><th>Name</th>'
                '<th>Grade/Form</th><th>Subject</th><th>Paid</th>'
                '<th>Streak</th><th></th></tr>'
            )
            for s in students:
                body.append(
                    f'<tr>'
                    f'<td>{s["id"]}</td>'
                    f'<td>{_esc(s["student_number"] or "")}</td>'
                    f'<td>{_esc(s["name"])}</td>'
                    f'<td>{_esc(s["grade_form"] or "")}</td>'
                    f'<td>{_esc(s["current_subject"] or "")}</td>'
                    f'<td>{s["paid_lessons"] or 0}</td>'
                    f'<td>{s["streak"] or 0}</td>'
                    f'<td><a class="btn ghost" '
                    f'href="/student/{s["id"]}/v2">View</a></td>'
                    f'</tr>'
                )
            body.append('</table>')

            # manual add student
            body.append('<h2>Add a student manually</h2>')
            body.append(
                '<form class="add" method="POST" '
                f'action="/founder/students/add?key={key}">'
                '<input name="first_name" placeholder="First name" required>'
                '<input name="last_name" placeholder="Last name" required>'
                '<input name="phone" placeholder="Phone (07...)" required>'
                '<input name="grade_form" placeholder="Grade 5 / Form 3" required>'
                '<input name="school" placeholder="School (optional)">'
                '<input name="location" placeholder="City (optional)">'
                '<input name="subjects" placeholder="Subjects, comma-separated" required>'
                '<input name="age" placeholder="Age" type="number" min="4" max="99">'
                '<button type="submit">Create student + DCR number + password</button>'
                '</form>'
            )

            body.append('</main>')
            body.append(PAGE_FOOT)
            return "".join(body)
        finally:
            con.close()

    # ---------------- action routes ----------------
    @app.route("/founder/payments/<int:rid>/approve", methods=["POST"])
    def founder_approve(rid):
        if not _founder_key() or not _key_ok():
            abort(403)
        ok, _ = _approve(rid)
        return redirect(url_for("founder_dashboard", key=_founder_key()))

    @app.route("/founder/payments/<int:rid>/reject", methods=["POST"])
    def founder_reject(rid):
        if not _founder_key() or not _key_ok():
            abort(403)
        ok, _ = _reject(rid)
        return redirect(url_for("founder_dashboard", key=_founder_key()))

    @app.route("/founder/payments/<int:rid>/revoke", methods=["POST"])
    def founder_revoke(rid):
        if not _founder_key() or not _key_ok():
            abort(403)
        ok, _ = _revoke(rid)
        return redirect(url_for("founder_dashboard", key=_founder_key()))

    # ---------------- manual add student ----------------
    @app.route("/founder/students/add", methods=["POST"])
    def founder_add_student():
        if not _founder_key() or not _key_ok():
            abort(403)

        first = (request.form.get("first_name") or "").strip()
        last  = (request.form.get("last_name") or "").strip()
        phone = (request.form.get("phone") or "").strip()
        grade = (request.form.get("grade_form") or "").strip()
        school = (request.form.get("school") or "").strip()
        city = (request.form.get("location") or "").strip()
        subs_raw = (request.form.get("subjects") or "").strip()
        age = (request.form.get("age") or "").strip()

        if not (first and last and phone and grade and subs_raw):
            return "first_name, last_name, phone, grade_form, subjects required", 400

        # Reuse auth.register_user for password hashing + student_number.
        try:
            import auth as _auth
            from importlib import reload
            # ensure SUBJECTS list is up to date
            subjects = [s.strip() for s in subs_raw.split(",") if s.strip()]
            if not subjects:
                return "no valid subjects", 400

            # auth.register_user signature: (first, last, email, password,
            #                                grade_form, phone, city, school)
            import secrets as _secrets
            temp_password = _secrets.token_urlsafe(9)
            result = _auth.register_user(
                first, last, "", temp_password, grade, phone, city or "", school or ""
            )
            if not result.get("success"):
                return f"register_user failed: {result.get('error')}", 500

            snum = result["student_number"]

            # Save subjects + age
            con = _db()
            try:
                row = con.execute(
                    "SELECT id FROM students WHERE student_number=?", (snum,)
                ).fetchone()
                if row:
                    sid = row["id"]
                    if age.isdigit():
                        con.execute("UPDATE students SET age=? WHERE id=?", (int(age), sid))
                    con.execute(
                        "UPDATE students SET subject=?, current_subject=? WHERE id=?",
                        (subjects[0], subjects[0], sid),
                    )
                    now = datetime.datetime.now().isoformat(timespec="seconds")
                    for s in subjects:
                        con.execute(
                            "INSERT INTO student_subjects "
                            "(student_id, subject, active, added_at) VALUES (?,?,1,?)",
                            (sid, s, now),
                        )
                    con.commit()
            finally:
                con.close()

            return redirect(url_for("founder_dashboard", key=_founder_key()))
        except Exception as e:
            return f"add student failed: {type(e).__name__}: {e}", 500

    return app
