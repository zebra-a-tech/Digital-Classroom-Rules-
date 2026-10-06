import os, sqlite3
from flask import Blueprint, request, redirect, url_for, render_template, session, make_response

auth_bp = Blueprint('auth', __name__)

def db_conn():
    if os.environ.get("TURSO_DATABASE_URL") and os.environ.get("TURSO_AUTH_TOKEN"):
        try:
            import turso_db
            return turso_db.connect()
        except Exception: pass
    return sqlite3.connect("digital_classroom.db")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        s_num = request.form.get("student_number", "").strip().upper()
        pw = request.form.get("password", "").strip()
        conn = db_conn()
        user = conn.execute("SELECT id, name, student_number FROM students WHERE UPPER(student_number)=?", (s_num,)).fetchone()
        conn.close()
        if user:
            sid = user["id"] if isinstance(user, dict) else user[0]
            session["student_id"] = sid
            session["student_number"] = s_num
            resp = make_response(redirect(f"/student/{sid}/home"))
            resp.set_cookie("dcr_consent", "1", max_age=60*60*24*365, samesite="Lax")
            return resp
        error = "Invalid Student Number or Password."
    return render_template("login.html", error=error)

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    errors = []
    if request.method == "POST":
        fn = request.form.get("first_name", "").strip()
        ln = request.form.get("last_name", "").strip()
        phone = request.form.get("phone", "").strip()
        gf = request.form.get("grade_form", "").strip()
        subj = request.form.get("subjects", "English").strip()
        pw = request.form.get("password", "").strip()

        conn = db_conn()
        last = conn.execute("SELECT MAX(id) FROM students").fetchone()
        next_id = ((last[0] if isinstance(last, (tuple, list)) else last.get("MAX(id)", 0)) or 0) + 1
        s_num = f"DCR{next_id:04d}"

        cur = conn.execute(
            "INSERT INTO students (name, grade_form, current_subject, student_number, registered_at, free_trial_used) VALUES (?, ?, ?, ?, datetime('now'), 0)",
            (f"{fn} {ln}", gf, subj, s_num)
        )
        sid = cur.lastrowid
        conn.commit()

        ref_code = (request.args.get("ref") or request.form.get("ref_code") or "").strip().upper()
        if ref_code:
            try:
                ref_stu = conn.execute("SELECT id FROM students WHERE UPPER(student_number)=?", (ref_code,)).fetchone()
                if ref_stu:
                    ref_id = ref_stu["id"] if isinstance(ref_stu, dict) else ref_stu[0]
                    conn.execute("INSERT INTO referral_payouts (referrer_id, referred_student_id, amount, status) VALUES (?, ?, 0.10, 'PENDING')", (ref_id, sid))
                    conn.commit()
            except Exception: pass
        conn.close()

        session["student_id"] = sid
        session["student_number"] = s_num
        resp = make_response(redirect(f"/student/{sid}/home"))
        resp.set_cookie("dcr_consent", "1", max_age=60*60*24*365, samesite="Lax")
        return resp
    return render_template("register.html", errors=errors)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

def register_auth_routes(app):
    if "auth" not in app.blueprints:
        app.register_blueprint(auth_bp)

def login_required(f): return f
def current_user(): return session.get("student_id")
