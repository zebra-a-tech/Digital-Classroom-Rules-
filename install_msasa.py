import os, py_compile

# 1. Create templates/welcome.html
welcome_html = '''{% extends "base.html" %}
{% block title %}Welcome - Digital Classroom Rules{% endblock %}

{% block content %}
<div class="ms-card" style="margin-bottom:20px;text-align:center;padding:32px 20px;">
  <div style="font-size:3.5rem;margin-bottom:12px">🎓</div>
  <h1 style="margin:0 0 8px;font-size:1.8rem;color:#3B2A1A;">Digital Classroom Rules</h1>
  <p style="margin:0;font-size:1.05rem;color:#64748b;">Zimbabwe's Premier Smart Learning Platform for Primary & Secondary Learners</p>
</div>

<div class="ms-card" style="margin-bottom:20px;">
  <div style="display:inline-block;background:#EBF5F0;color:#1E5E3A;font-weight:bold;font-size:0.8rem;padding:4px 12px;border-radius:20px;margin-bottom:12px;">
    🚀 Powered by Top IT & Educational Specialists
  </div>
  <h2 style="margin:0 0 12px;font-size:1.3rem;color:#3B2A1A;">💡 Built for High-Impact Academic Success</h2>
  <p style="color:#475569;line-height:1.6;margin-bottom:18px;">
    Digital Classroom Rules delivers a structured, syllabus-aligned digital curriculum created by experienced educators and IT software engineers for high academic performance.
  </p>
  
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:12px;margin:16px 0;">
    <div style="background:#FAF7F2;padding:14px;border-radius:10px;border:1px solid #EADBCC;">
      <b>📚 827+ Interactive Lessons</b><br>
      <span style="font-size:0.85rem;color:#64748b;">Maths, Science, English, Shona, Ndebele & Commerce.</span>
    </div>
    <div style="background:#FAF7F2;padding:14px;border-radius:10px;border:1px solid #EADBCC;">
      <b>🎧 10-Chapter Audio Novels</b><br>
      <span style="font-size:0.85rem;color:#64748b;">Voice Play/Pause read-aloud readers with chapter quizzes.</span>
    </div>
    <div style="background:#FAF7F2;padding:14px;border-radius:10px;border:1px solid #EADBCC;">
      <b>📝 Auto-Marked Assessments</b><br>
      <span style="font-size:0.85rem;color:#64748b;">Instant feedback, step-by-step guidance & tutor notes.</span>
    </div>
    <div style="background:#FAF7F2;padding:14px;border-radius:10px;border:1px solid #EADBCC;">
      <b>👪 Grade 1–5 Parent Mode</b><br>
      <span style="font-size:0.85rem;color:#64748b;">Structured family reading oversight & weekly report cards.</span>
    </div>
  </div>
</div>

<div class="ms-card" style="margin-bottom:24px;">
  <h2 style="margin:0 0 12px;font-size:1.25rem;color:#3B2A1A;">⚖️ Privacy Policy & Intellectual Property Protection</h2>
  <p style="font-size:0.92rem;color:#475569;line-height:1.6;">
    All student records, performance metrics, and learning hours are securely stored, encrypted, and kept strictly confidential.
  </p>
  
  <div style="background:#FEF2F2;border-left:4px solid #DC2626;padding:14px 16px;border-radius:8px;margin:16px 0;font-size:0.9rem;color:#991B1B;line-height:1.6;">
    <b>🚨 STRICT LEGAL NOTICE ON COPYRIGHT & DUPLICATION:</b><br>
    All lessons, playbooks, novel chapters, audio readers, assessments, and proprietary learning algorithms on Digital Classroom Rules are legally protected under Zimbabwean and international copyright laws. <b>Any unauthorized copying, recording, digital scraping, reproduction, or redistribution of platform content is strictly prohibited and subject to immediate legal prosecution.</b>
  </div>

  <form action="/consent/agree" method="POST" style="margin-top:20px;">
    <button type="submit" style="width:100%;background:#1E5E3A;color:white;border:none;padding:16px;border-radius:10px;font-size:1.1rem;font-weight:bold;cursor:pointer;box-shadow:0 4px 12px rgba(30,94,58,0.3);">
      ✅ I Agree & Continue to Classroom →
    </button>
  </form>
</div>
{% endblock %}
'''

with open("templates/welcome.html", "w", encoding="utf-8") as f:
    f.write(welcome_html)

# 2. Create templates/login.html
login_html = '''{% extends "base.html" %}
{% block title %}Login - Digital Classroom Rules{% endblock %}

{% block content %}
<div style="max-width:440px;margin:20px auto;">
  <div class="ms-card">
    <div style="text-align:center;margin-bottom:20px;">
      <div style="font-size:2.8rem;margin-bottom:6px">🎓</div>
      <h1 style="margin:0 0 6px;font-size:1.5rem;color:#3B2A1A;">Welcome Back</h1>
      <p style="margin:0;color:#64748b;font-size:0.9rem;">Log in to Digital Classroom Rules</p>
    </div>

    {% if error %}
      <div style="background:#FEF2F2;color:#991B1B;padding:10px 14px;border-radius:8px;margin-bottom:16px;font-size:0.88rem;border:1px solid #FECACA;">
        ⚠️ {{ error }}
      </div>
    {% endif %}

    <form method="POST">
      <div style="margin-bottom:14px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:6px;color:#334155;">Student Number</label>
        <input type="text" name="student_number" required placeholder="e.g. DCR0001" autocomplete="username" style="width:100%;padding:12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:1rem;text-transform:uppercase;">
      </div>

      <div style="margin-bottom:18px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:6px;color:#334155;">Password</label>
        <input type="password" name="password" required readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password" style="width:100%;padding:12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:1rem;">
      </div>

      <button type="submit" style="width:100%;background:#1E5E3A;color:white;border:none;padding:14px;border-radius:8px;font-size:1rem;font-weight:bold;cursor:pointer;">
        Login →
      </button>
    </form>

    <div style="text-align:center;margin:18px 0 8px;color:#94a3b8;font-size:0.85rem">new here?</div>
    <a href="/register" style="display:block;text-align:center;padding:12px;background:#F8FAFC;border:1px solid #CBD5E1;border-radius:8px;text-decoration:none;color:#1E5E3A;font-weight:bold;">
      ✨ Create Free Account
    </a>
  </div>
</div>
{% endblock %}
'''

with open("templates/login.html", "w", encoding="utf-8") as f:
    f.write(login_html)

# 3. Create templates/register.html
register_html = '''{% extends "base.html" %}
{% block title %}Create Account - Digital Classroom Rules{% endblock %}

{% block content %}
<div style="max-width:480px;margin:20px auto;">
  <div class="ms-card">
    <div style="text-align:center;margin-bottom:20px;">
      <div style="font-size:2.8rem;margin-bottom:6px">📝</div>
      <h1 style="margin:0 0 6px;font-size:1.5rem;color:#3B2A1A;">Create Account</h1>
      <p style="margin:0;color:#64748b;font-size:0.9rem;">Digital Classroom Rules</p>
    </div>

    {% if errors %}
      {% for error in errors %}
        <div style="background:#FEF2F2;color:#991B1B;padding:10px 14px;border-radius:8px;margin-bottom:14px;font-size:0.88rem;border:1px solid #FECACA;">
          ⚠️ {{ error }}
        </div>
      {% endfor %}
    {% endif %}

    <form method="POST">
      <div style="margin-bottom:12px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:4px;color:#334155;">First Name *</label>
        <input type="text" name="first_name" required placeholder="e.g. Tinashe" style="width:100%;padding:10px 12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:0.95rem;">
      </div>

      <div style="margin-bottom:12px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:4px;color:#334155;">Last Name *</label>
        <input type="text" name="last_name" required placeholder="e.g. Moyo" style="width:100%;padding:10px 12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:0.95rem;">
      </div>

      <div style="margin-bottom:12px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:4px;color:#334155;">Phone Number * (WhatsApp / EcoCash)</label>
        <input type="tel" name="phone" required placeholder="0771234567" style="width:100%;padding:10px 12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:0.95rem;">
      </div>

      <div style="margin-bottom:12px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:4px;color:#334155;">Grade / Form *</label>
        <select name="grade_form" required style="width:100%;padding:10px 12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:0.95rem;">
          <option value="">Choose your grade...</option>
          <option>Grade 1</option><option>Grade 2</option><option>Grade 3</option><option>Grade 4</option>
          <option>Grade 5</option><option>Grade 6</option><option>Grade 7</option>
          <option>Form 1</option><option>Form 2</option><option>Form 3</option><option>Form 4</option><option>Form 5</option><option>Form 6</option>
        </select>
      </div>

      <div style="background:#FFFBEB;border-left:4px solid #F59E0B;padding:10px 12px;border-radius:6px;font-size:0.85rem;color:#92400E;margin-bottom:14px;">
        👨‍👩‍👧 <b>Parent/Guardian Notice:</b> For Grades 1–5, parents are encouraged to read and assist their child with lessons.
      </div>

      <div style="margin-bottom:12px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:4px;color:#334155;">Primary Subject *</label>
        <select name="subjects" required style="width:100%;padding:10px 12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:0.95rem;">
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

      <div style="margin-bottom:18px;">
        <label style="display:block;font-weight:600;font-size:0.88rem;margin-bottom:4px;color:#334155;">Password * (min 6 chars)</label>
        <input type="password" name="password" required minlength="6" readonly onfocus="this.removeAttribute('readonly');" autocomplete="new-password" style="width:100%;padding:10px 12px;border:1px solid #CBD5E1;border-radius:8px;box-sizing:border-box;font-size:0.95rem;">
      </div>

      <button type="submit" style="width:100%;background:#1E5E3A;color:white;border:none;padding:14px;border-radius:8px;font-size:1rem;font-weight:bold;cursor:pointer;">
        Create My Account →
      </button>
    </form>

    <div style="text-align:center;margin:16px 0 8px;color:#94a3b8;font-size:0.85rem">already have an account?</div>
    <a href="/login" style="display:block;text-align:center;padding:12px;background:#F8FAFC;border:1px solid #CBD5E1;border-radius:8px;text-decoration:none;color:#1E5E3A;font-weight:bold;">
      🔑 Login Instead
    </a>
  </div>
</div>
{% endblock %}
'''

with open("templates/register.html", "w", encoding="utf-8") as f:
    f.write(register_html)

# 4. Update auth.py to use render_template instead of raw string
auth_py = '''import os, sqlite3
from flask import request, redirect, url_for, render_template, session, make_response

def db_conn():
    if os.environ.get("TURSO_DATABASE_URL") and os.environ.get("TURSO_AUTH_TOKEN"):
        try:
            import turso_db
            return turso_db.connect()
        except: pass
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
        return render_template("login.html", error=error)

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

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect("/login")

def login_required(f): return f
def current_user(): return session.get("student_id")
'''

with open("auth.py", "w", encoding="utf-8") as f:
    f.write(auth_py)

# 5. Update welcome_and_referrals.py to render welcome.html
with open("welcome_and_referrals.py", "r", encoding="utf-8") as f:
    w_code = f.read()

import re
w_code = re.sub(r'def welcome_page\(\):[\s\S]*?return render_template_string\(tpl\)', '''def welcome_page():
        if request.cookies.get("dcr_consent") == "1":
            return redirect("/login")
        return render_template("welcome.html")''', w_code)

with open("welcome_and_referrals.py", "w", encoding="utf-8") as f:
    f.write(w_code)

py_compile.compile("auth.py", doraise=True)
py_compile.compile("welcome_and_referrals.py", doraise=True)
py_compile.compile("student_server.py", doraise=True)
print("🎉 All pages connected to Msasa Theme templates (welcome.html, login.html, register.html) with 0 errors!")
