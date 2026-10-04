import os, sqlite3, re, hashlib
from datetime import datetime
from flask import request, redirect, url_for, render_template_string, session, jsonify, make_response

SHARED_CSS = """
:root { --p: #0f766e; --p-dark: #115e59; --bg: #f8fafc; --card: #ffffff; --text: #1e293b; --border: #e2e8f0; }
body { font-family: system-ui, -apple-system, sans-serif; background: #f1f5f9; color: var(--text); margin: 0; padding: 16px; min-height: 100vh; display: flex; align-items: center; justify-content: center; }
.container { max-width: 480px; width: 100%; margin: 20px auto; }
.flag-stripe { height: 6px; background: linear-gradient(90deg, #006400 0%, #FFD700 25%, #D40000 50%, #000000 75%, #006400 100%); border-radius: 4px 4px 0 0; }
.card { background: white; padding: 28px 24px; border-radius: 0 0 16px 16px; box-shadow: 0 10px 25px rgba(0,0,0,0.06); border: 1px solid var(--border); }
.logo { text-align: center; margin-bottom: 20px; }
.logo-icon { font-size: 2.8rem; margin-bottom: 6px; }
h1 { margin: 0 0 6px; font-size: 1.5rem; color: #0f172a; text-align: center; }
p.sub { margin: 0 0 20px; color: #64748b; font-size: 0.9rem; text-align: center; }
.form-group { margin-bottom: 16px; }
label { display: block; font-size: 0.88rem; font-weight: 600; margin-bottom: 6px; color: #334155; }
input, select { width: 100%; padding: 12px 14px; border-radius: 8px; border: 1px solid #cbd5e1; font-size: 0.95rem; box-sizing: border-box; background: #f8fafc; }
input:focus, select:focus { outline: none; border-color: var(--p); background: white; }
.btn-submit { width: 100%; padding: 14px; border-radius: 8px; background: var(--p); color: white; border: none; font-size: 1rem; font-weight: bold; cursor: pointer; margin-top: 8px; }
.btn-submit:hover { background: var(--p-dark); }
.btn-alt { display: block; text-align: center; padding: 12px; border-radius: 8px; background: #f1f5f9; color: var(--p); text-decoration: none; font-weight: 600; margin-top: 10px; border: 1px solid #cbd5e1; }
.alert { padding: 12px; border-radius: 8px; font-size: 0.88rem; margin-bottom: 16px; }
.alert-error { background: #fee2e2; color: #991b1b; border: 1px solid #fca5a5; }
.footer { text-align: center; font-size: 0.8rem; color: #64748b; margin-top: 20px; }
.subj-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; max-height: 160px; overflow-y: auto; padding: 8px; border: 1px solid #e2e8f0; border-radius: 8px; background: #f8fafc; }
"""

LOGIN_HTML = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Login - Digital Classroom Rules</title>
  <style>{SHARED_CSS}</style>
</head>
<body>
  <div class="container">
    <div class="flag-stripe"></div>
    <div class="card">
      <div class="logo">
        <div class="logo-icon">🎓</div>
        <h1>Welcome Back</h1>
        <p class="sub">Log in to Digital Classroom Rules</p>
      </div>
      {{% if error %}}<div class="alert alert-error">⚠️ {{{{ error }}}}</div>{{% endif %}}
      <form method="POST">
        <div class="form-group">
          <label>Student Number</label>
          <input type="text" name="student_number" required placeholder="e.g. DCR0001" autocomplete="username" style="text-transform:uppercase">
        </div>
        <div class="form-group">
          <label>Password</label>
          <input type="password" name="password" required readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password">
        </div>
        <button type="submit" class="btn-submit">Login →</button>
      </form>
      <div style="text-align:center;margin:16px 0 6px;color:#94a3b8;font-size:0.85rem">new here?</div>
      <a class="btn-alt" href="/register">✨ Create Free Account</a>
    </div>
    <div class="footer">Powered by Quick Sync IT 🇿🇼 • © 2026 Smart People Education</div>
  </div>
</body>
</html>"""

REGISTER_HTML = f"""<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Create Account - Digital Classroom Rules</title>
  <style>{SHARED_CSS}</style>
</head>
<body>
  <div class="container">
    <div class="flag-stripe"></div>
    <div class="card">
      <div class="logo">
        <div class="logo-icon">📝</div>
        <h1>Create Account</h1>
        <p class="sub">Digital Classroom Rules</p>
      </div>
      {{% if errors %}}{{% for error in errors %}}<div class="alert alert-error">⚠️ {{{{ error }}}}</div>{{% endfor %}}{{% endif %}}
      <form method="POST">
        <div class="form-group">
          <label>First Name *</label>
          <input type="text" name="first_name" required>
        </div>
        <div class="form-group">
          <label>Last Name *</label>
          <input type="text" name="last_name" required>
        </div>
        <div class="form-group">
          <label>Phone Number * (WhatsApp)</label>
          <input type="tel" name="phone" required placeholder="0771234567">
        </div>
        <div class="form-group">
          <label>Grade / Form *</label>
          <select name="grade_form" required>
            <option value="">Choose your grade...</option>
            <option>Grade 1</option><option>Grade 2</option><option>Grade 3</option><option>Grade 4</option>
            <option>Grade 5</option><option>Grade 6</option><option>Grade 7</option>
            <option>Form 1</option><option>Form 2</option><option>Form 3</option><option>Form 4</option><option>Form 5</option><option>Form 6</option>
          </select>
        </div>
        <div class="form-group">
          <label>Subjects * (Select primary subject)</label>
          <select name="subjects" required>
            <option value="English">English</option>
            <option value="Maths">Maths</option>
            <option value="Science">Science</option>
            <option value="Social Studies">Social Studies</option>
            <option value="Shona">Shona</option>
            <option value="Ndebele">Ndebele</option>
            <option value="Commerce">Commerce</option>
            <option value="Geography">Geography</option>
            <option value="History">History</option>
          </select>
        </div>
        <div class="form-group">
          <label>Password * (min 6 chars)</label>
          <input type="password" name="password" required minlength="6" readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password">
        </div>
        <button type="submit" class="btn-submit">Create My Account →</button>
      </form>
      <div style="text-align:center;margin:16px 0 6px;color:#94a3b8;font-size:0.85rem">already have an account?</div>
      <a class="btn-alt" href="/login">🔑 Login Instead</a>
    </div>
    <div class="footer">Powered by Quick Sync IT 🇿🇼 • © 2026 Smart People Education</div>
  </div>
</body>
</html>"""

def db_conn():
    if os.environ.get("TURSO_DATABASE_URL") and os.environ.get("TURSO_AUTH_TOKEN"):
        try:
            import turso_db
            return turso_db.connect()
        except Exception: pass
    return sqlite3.connect("digital_classroom.db")

def register_auth_routes(app):
    @app.route("/login", methods=["GET", "POST"])
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
        return render_template_string(LOGIN_HTML, error=error)

    @app.route("/register", methods=["GET", "POST"])
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
            # Generate DCR number
            last = conn.execute("SELECT MAX(id) FROM students").fetchone()
            next_id = ((last[0] if isinstance(last, (tuple, list)) else last.get("MAX(id)", 0)) or 0) + 1
            s_num = f"DCR{next_id:04d}"
            
            cur = conn.execute(
                "INSERT INTO students (name, grade_form, current_subject, student_number, registered_at, free_trial_used) VALUES (?, ?, ?, ?, datetime('now'), 0)",
                (f"{fn} {ln}", gf, subj, s_num)
            )
            sid = cur.lastrowid
            conn.commit()

            # Referral commission check
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
        return render_template_string(REGISTER_HTML, errors=errors)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

def login_required(f):
    return f

def current_user():
    return session.get("student_id")
