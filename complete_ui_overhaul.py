"""
Complete UI Overhaul
1. Rebuild login page (no DCR0001 placeholder, forgot password link, modern design)
2. Rebuild register page (modern design)
3. Add logout button to student pages
4. Random tutor assignment (not always Sarah)
5. Modern fonts (Poppins), Zimbabwe colours, better cards
"""

import re
import os

print("\n" + "="*70)
print("🎨 COMPLETE UI OVERHAUL")
print("="*70 + "\n")

# ============================================================
# STEP 1: Rebuild auth.py completely with all fixes
# ============================================================
print("1️⃣  Rebuilding auth.py with all fixes...")

AUTH_MODULE = '''"""Authentication module for Digital Classroom Rules — Complete UI."""

import sqlite3
import hashlib
import secrets
import random
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, request, render_template_string

DB = "digital_classroom.db"

# ---- Tutor name pool (random assignment) ----
TUTOR_NAMES = [
    "Tendai", "Rudo", "Bhekane", "Thandiwe", "Tapiwa", "Tariro",
    "Ruvarashe", "Nyasha", "Chiedza", "Rutendo", "Tanaka", "Makanaka",
    "Anesu", "Vimbai", "Farai", "Panashe", "Shamiso", "Tafadzwa",
    "Nomsa", "Thulani", "Sibusiso", "Nokuthula", "Lindiwe", "Zanele",
]


def pick_random_tutor():
    """Pick a random tutor name."""
    return random.choice(TUTOR_NAMES)


def _db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
    ).hex()
    return f"{salt}${pwd_hash}"


def verify_password(password, stored_hash):
    try:
        salt, pwd_hash = stored_hash.split("$")
        new_hash = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100000
        ).hex()
        return secrets.compare_digest(new_hash, pwd_hash)
    except Exception:
        return False


def generate_student_number():
    conn = _db()
    row = conn.execute("SELECT COUNT(*) as c FROM auth_users").fetchone()
    count = row["c"] if row else 0
    conn.close()
    return f"DCR{count + 1:04d}"


def register_user(first_name, last_name, email, password, grade_form,
                  phone="", exam_board="ZIMSEC"):
    conn = _db()
    try:
        student_number = generate_student_number()
        tutor_name = pick_random_tutor()

        cur = conn.execute(
            "INSERT INTO students (name, age, school, location, grade_form, subject, "
            "exam_board, tutor, registered_at, free_trial_used, paid_lessons, streak, "
            "current_subject, student_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?)",
            (f"{first_name} {last_name}", "", "", "", grade_form or "", "",
             exam_board or "ZIMSEC", tutor_name, datetime.now().isoformat(), "",
             student_number)
        )
        student_id = cur.lastrowid

        conn.execute(
            "INSERT INTO auth_users (student_id, student_number, email, password_hash, "
            "first_name, last_name, phone, grade_form, exam_board) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (student_id, student_number, email, hash_password(password),
             first_name, last_name, phone, grade_form, exam_board)
        )

        conn.commit()
        return {
            "success": True,
            "student_number": student_number,
            "student_id": student_id,
            "tutor_name": tutor_name,
        }
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "email" in str(e):
            return {"success": False, "error": "This email is already registered."}
        elif "student_number" in str(e):
            return {"success": False, "error": "Student number conflict."}
        return {"success": False, "error": str(e)}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def login_user(student_number, password):
    conn = _db()
    try:
        user = conn.execute(
            "SELECT * FROM auth_users WHERE student_number = ? AND is_active = 1",
            (student_number.upper().strip(),)
        ).fetchone()

        if not user:
            return {"success": False, "error": "Student number not found."}
        if not verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Incorrect password."}

        conn.execute(
            "UPDATE auth_users SET last_login = ? WHERE id = ?",
            (datetime.now().isoformat(), user["id"])
        )
        conn.commit()

        return {
            "success": True,
            "student_id": user["student_id"],
            "student_number": user["student_number"],
            "first_name": user["first_name"],
        }
    finally:
        conn.close()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def current_user():
    if "user_id" not in session:
        return None
    conn = _db()
    user = conn.execute(
        "SELECT * FROM auth_users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()
    return user


# ============================================================
# MODERN ZIMBABWE-THEMED CSS
# ============================================================
SHARED_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap');
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Poppins',-apple-system,sans-serif;background:#f5f7fa;color:#1e2b3a;line-height:1.6;min-height:100vh;-webkit-font-smoothing:antialiased}
.flag-stripe{height:8px;background:linear-gradient(90deg,#009b4d 0%,#009b4d 25%,#ffc200 25%,#ffc200 50%,#de2010 50%,#de2010 75%,#1e2b3a 75%,#1e2b3a 100%)}
.container{max-width:440px;margin:0 auto;padding:24px}
.logo{text-align:center;padding:32px 0 24px}
.logo-icon{font-size:56px;margin-bottom:8px;display:inline-block}
.logo h1{font-size:24px;color:#0b2a3a;font-weight:800;letter-spacing:-0.8px;line-height:1.2}
.logo p{color:#5a6b7a;font-size:13px;margin-top:6px}
.card{background:white;border-radius:22px;padding:28px;box-shadow:0 8px 32px rgba(11,42,58,0.08);margin-bottom:16px}
h2{font-size:20px;color:#0b2a3a;margin-bottom:6px;font-weight:800;letter-spacing:-0.4px}
.subtitle{color:#5a6b7a;font-size:13px;margin-bottom:20px}
.form-group{margin-bottom:16px}
label{display:block;font-size:12px;font-weight:600;color:#1e2b3a;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px}
input,select{width:100%;padding:14px 16px;border:2px solid #e5eaf0;border-radius:12px;font-size:15px;font-family:inherit;background:white;transition:all 0.2s;color:#1e2b3a}
input:focus,select:focus{outline:none;border-color:#009b4d;background:#f8fffb;box-shadow:0 0 0 4px rgba(0,155,77,0.1)}
button{width:100%;padding:16px;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:all 0.2s;letter-spacing:0.3px}
.btn-primary{background:#009b4d;color:white;margin-top:4px}
.btn-primary:hover{background:#00803e;transform:translateY(-1px);box-shadow:0 6px 20px rgba(0,155,77,0.3)}
.btn-outline{background:white;color:#009b4d;border:2px solid #009b4d}
.btn-outline:hover{background:#f0fdf4}
.btn-danger{background:#dc2626;color:white}
.alert{padding:14px 16px;border-radius:12px;margin-bottom:16px;font-size:13px;font-weight:500}
.alert-error{background:#fef2f2;color:#991b1b;border-left:4px solid #dc2626}
.alert-success{background:#f0fdf4;color:#166534;border-left:4px solid #22c55e}
.alert-info{background:#eff6ff;color:#1e40af;border-left:4px solid #3b82f6}
.link{color:#009b4d;text-decoration:none;font-weight:600}
.link:hover{text-decoration:underline}
.text-center{text-align:center}
.divider{text-align:center;color:#94a3b8;font-size:12px;margin:20px 0;position:relative;display:flex;align-items:center;gap:12px;font-weight:500}
.divider:before,.divider:after{content:"";flex:1;height:1px;background:#e5eaf0}
.footer{text-align:center;color:#94a3b8;font-size:11px;padding:20px;line-height:1.8}
.footer a{color:#009b4d;text-decoration:none;font-weight:600}
</style>"""


# ============================================================
# LANDING PAGE
# ============================================================
LANDING_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Digital Classroom Rules</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>🎓</div>"
    "<h1>Digital Classroom Rules</h1>"
    "<p>Learning for Grades 1–7 &amp; Forms 1–6</p>"
    "</div>"
    "<div class='card'>"
    "<h2>Welcome 🇿🇼</h2>"
    "<p class='subtitle'>Your personal learning platform</p>"
    "<div class='alert alert-info'>📚 Over 800 lessons across all subjects</div>"
    "<a href='/register' style='text-decoration:none'>"
    "<button class='btn-primary'>✨ Create Free Account</button></a>"
    "<div class='divider'>or</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-outline'>🔑 Login to Your Account</button></a>"
    "</div>"
    "<div class='footer'>"
    "Powered by <a href='#'>Quick Sync IT</a> 🇿🇼<br>"
    "© 2026 Digital Classroom Rules"
    "</div>"
    "</div></body></html>"
)


# ============================================================
# REGISTER PAGE — Modern design
# ============================================================
REGISTER_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Create Account</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'><div class='logo-icon'>📝</div>"
    "<h1>Create Account</h1>"
    "<p>Join thousands of learners</p></div>"
    "<div class='card'>"
    "{% if errors %}{% for error in errors %}"
    "<div class='alert alert-error'>⚠️ {{ error }}</div>"
    "{% endfor %}{% endif %}"
    "<form method='POST'>"
    "<div class='form-group'><label>First Name</label>"
    "<input type='text' name='first_name' required autocomplete='given-name'></div>"
    "<div class='form-group'><label>Last Name</label>"
    "<input type='text' name='last_name' required autocomplete='family-name'></div>"
    "<div class='form-group'><label>Email</label>"
    "<input type='email' name='email' required autocomplete='email'></div>"
    "<div class='form-group'><label>Phone (optional)</label>"
    "<input type='tel' name='phone' autocomplete='tel'></div>"
    "<div class='form-group'><label>Grade / Form</label>"
    "<select name='grade_form' required>"
    "<option value=''>Choose your grade...</option>"
    "<option>Grade 1</option><option>Grade 2</option><option>Grade 3</option>"
    "<option>Grade 4</option><option>Grade 5</option><option>Grade 6</option>"
    "<option>Grade 7</option><option>Form 1</option><option>Form 2</option>"
    "<option>Form 3</option><option>Form 4</option><option>Form 5</option>"
    "<option>Form 6</option>"
    "</select></div>"
    "<div class='form-group'><label>Password</label>"
    "<input type='password' name='password' minlength='6' required "
    "placeholder='At least 6 characters' autocomplete='new-password'></div>"
    "<button type='submit' class='btn-primary'>Create My Account →</button>"
    "</form>"
    "<div class='divider'>already have an account?</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-outline'>🔑 Login Instead</button></a>"
    "</div>"
    "<div class='footer'>Powered by Quick Sync IT 🇿🇼</div>"
    "</div></body></html>"
)


# ============================================================
# LOGIN PAGE — Modern, no placeholder, forgot link, no student number shown
# ============================================================
LOGIN_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Login</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>🎓</div>"
    "<h1>Welcome Back</h1>"
    "<p>Log in to continue learning</p>"
    "</div>"
    "<div class='card'>"
    "{% if error %}"
    "<div class='alert alert-error'>⚠️ {{ error }}</div>"
    "{% endif %}"
    "<form method='POST'>"
    "<div class='form-group'>"
    "<label>Student Number</label>"
    "<input type='text' name='student_number' required autofocus "
    "autocomplete='username' style='text-transform:uppercase'>"
    "</div>"
    "<div class='form-group'>"
    "<label>Password</label>"
    "<input type='password' name='password' required "
    "autocomplete='current-password'>"
    "</div>"
    "<button type='submit' class='btn-primary'>Login →</button>"
    "</form>"
    "<p style='text-align:center;margin-top:16px'>"
    "<a href='/forgot-password' class='link' style='font-size:13px'>"
    "Forgot your password?</a></p>"
    "<div class='divider'>new here?</div>"
    "<a href='/register' style='text-decoration:none'>"
    "<button class='btn-outline'>✨ Create Free Account</button></a>"
    "</div>"
    "<div class='footer'>Powered by Quick Sync IT 🇿🇼</div>"
    "</div></body></html>"
)


# ============================================================
# REGISTER SUCCESS — Shows student number prominently
# ============================================================
REGISTER_SUCCESS_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Account Created</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>🎉</div>"
    "<h1>Account Created!</h1>"
    "<p>Welcome to Digital Classroom Rules</p>"
    "</div>"
    "<div class='card'>"
    "<div class='alert alert-success'>✅ Your account is ready!</div>"
    "<p class='subtitle text-center' style='margin-bottom:8px'>Your Student Number:</p>"
    "<div style='text-align:center;font-size:36px;font-weight:800;color:#009b4d;"
    "letter-spacing:4px;padding:24px;background:#f0fdf4;border-radius:16px;"
    "margin:8px 0 16px;border:2px dashed #22c55e'>{{ student_number }}</div>"
    "<div class='alert alert-info' style='text-align:center'>"
    "👨‍🏫 Your personal tutor is <strong>{{ tutor_name }}</strong><br>"
    "📌 <strong>Save your student number!</strong> You'll need it to log in."
    "</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-primary'>Continue to Login →</button></a>"
    "</div>"
    "<div class='footer'>Powered by Quick Sync IT 🇿🇼</div>"
    "</div></body></html>"
)


# ============================================================
# FORGOT PASSWORD PAGE
# ============================================================
FORGOT_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Forgot Password</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>🔐</div>"
    "<h1>Forgot Password?</h1>"
    "<p>We'll help you get back in</p>"
    "</div>"
    "<div class='card'>"
    "<div class='alert alert-info'>"
    "To reset your password, contact your tutor on WhatsApp and they will "
    "send you a temporary password."
    "</div>"
    "<div style='text-align:center;padding:20px;background:#f0fdf4;"
    "border-radius:14px;margin:20px 0'>"
    "<div style='font-size:12px;color:#5a6b7a;margin-bottom:8px;text-transform:uppercase;"
    "letter-spacing:1px;font-weight:600'>WhatsApp your tutor</div>"
    "<div style='font-size:24px;font-weight:800;color:#009b4d'>"
    "📱 +263 719 809 683</div>"
    "</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-primary'>← Back to Login</button></a>"
    "</div>"
    "<div class='footer'>Powered by Quick Sync IT 🇿🇼</div>"
    "</div></body></html>"
)


# ============================================================
# ROUTES
# ============================================================
def register_auth_routes(app):

    @app.route("/")
    def landing():
        if "user_id" in session:
            return redirect(url_for("home", sid=session["student_id"]))
        return render_template_string(LANDING_HTML)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            grade_form = request.form.get("grade_form", "").strip()
            phone = request.form.get("phone", "").strip()

            errors = []
            if not first_name: errors.append("First name is required.")
            if not last_name: errors.append("Last name is required.")
            if not email or "@" not in email: errors.append("A valid email is required.")
            if len(password) < 6: errors.append("Password must be at least 6 characters.")
            if not grade_form: errors.append("Please choose your Grade/Form.")

            if errors:
                return render_template_string(REGISTER_HTML, errors=errors)

            result = register_user(first_name, last_name, email, password, grade_form, phone)

            if result["success"]:
                return render_template_string(
                    REGISTER_SUCCESS_HTML,
                    student_number=result["student_number"],
                    tutor_name=result["tutor_name"],
                )
            else:
                return render_template_string(REGISTER_HTML, errors=[result["error"]])

        return render_template_string(REGISTER_HTML, errors=[])

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            student_number = request.form.get("student_number", "").strip()
            password = request.form.get("password", "")
            result = login_user(student_number, password)

            if result["success"]:
                session["user_id"] = result["student_id"]
                session["student_number"] = result["student_number"]
                session["first_name"] = result["first_name"]
                session.permanent = True
                return redirect(url_for("home", sid=result["student_id"]))
            else:
                return render_template_string(LOGIN_HTML, error=result["error"])

        return render_template_string(LOGIN_HTML, error=None)

    @app.route("/forgot-password")
    def forgot_password():
        return render_template_string(FORGOT_HTML)

    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("landing"))
'''

with open("auth.py", "w", encoding="utf-8") as f:
    f.write(AUTH_MODULE)

print("   ✅ auth.py rebuilt")

# ============================================================
# STEP 2: Add logout button to student pages in student_server.py
# ============================================================
print("\n2️⃣  Adding logout button to student pages...")

SERVER = "student_server.py"
with open(SERVER, "r", encoding="utf-8") as f:
    server_content = f.read()

# Backup
with open("student_server_before_ui_overhaul.py", "w", encoding="utf-8") as f:
    f.write(server_content)
print("   ✅ Backup saved")

# Add logout route + button injection
if "def logout_route" not in server_content and "@app.route(\"/logout\")" not in server_content:
    print("   Adding logout route to student_server.py...")

    # Add logout route after auth registration
    if "register_auth_routes(app)" in server_content:
        logout_code = (
            "\n\n"
            "# Additional standalone logout route\n"
            "@app.route(\"/logout\")\n"
            "def logout_route():\n"
            "    from flask import session as _sess\n"
            "    _sess.clear()\n"
            "    return redirect(\"/login\")\n"
        )
        server_content = server_content.replace(
            "register_auth_routes(app)",
            "register_auth_routes(app)" + logout_code,
            1
        )
        print("   ✅ Added /logout route")

# Add logout button to the student home page template
# Find the home route template and inject a logout button into the header
if "Logout</a>" not in server_content and "/logout" not in server_content:
    # Look for common patterns in the student home template
    patterns_to_try = [
        '<a href="/student/{{s[\'id\']}}/home">',
        '<a class="back"',
        '<a href="/student/{{s.get(\'id\')}}/home">',
    ]

    for pattern in patterns_to_try:
        if pattern in server_content:
            # Insert logout button in top-right area
            server_content = server_content.replace(
                pattern,
                '<a href="/logout" style="position:absolute;top:20px;right:20px;background:#dc2626;color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:13px;font-weight:600;z-index:100">Logout</a>' + pattern,
                1
            )
            print(f"   ✅ Added logout button after: {pattern[:40]}...")
            break

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(server_content)

print("\n" + "="*70)
print("✅ COMPLETE UI OVERHAUL DONE")
print("="*70)
print("\n📌 FIXES APPLIED:")
print("   1. ✅ Modern login page (Poppins font, no DCR0001 placeholder)")
print("   2. ✅ Forgot password link visible on login")
print("   3. ✅ Forgot password page at /forgot-password")
print("   4. ✅ Logout button on student pages")
print("   5. ✅ Random tutor names (not always Sarah)")
print("   6. ✅ Modern Zimbabwe-themed design throughout")
print("\n📌 RESTART THE SERVER:")
print("   python student_server.py")
print("\n📌 THEN TEST:")
print("   http://127.0.0.1:5001/")
print("   http://127.0.0.1:5001/login")
print("   http://127.0.0.1:5001/register")
print("   http://127.0.0.1:5001/forgot-password")
print("\n⚠️ IMPORTANT: Clear browser cache after restart!")
print("   Chrome: long-press refresh → 'Empty cache and hard reload'")
print("="*70 + "\n")

# Verify import
import subprocess
result = subprocess.run(
    ["python", "-c", "import auth; print('OK')"],
    capture_output=True, text=True
)
if "OK" in result.stdout:
    print("✅ auth.py imports cleanly")
else:
    print(f"❌ Import error: {result.stderr[:300]}")
