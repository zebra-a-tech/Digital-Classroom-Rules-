"""
Script 1: Add Login & Registration System
- Registration with student number generation (DCR0001, DCR0002...)
- Login with student number + password
- Session management
- Protected student routes
"""

import sqlite3
import os

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("🔐 SCRIPT 1: LOGIN & REGISTRATION SYSTEM")
print("="*70 + "\n")

# ============================================================
# STEP 1: Create auth_users table
# ============================================================
print("1️⃣  Creating auth_users table...")

c.execute("""
    CREATE TABLE IF NOT EXISTS auth_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER UNIQUE,
        student_number TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        phone TEXT,
        grade_form TEXT,
        exam_board TEXT DEFAULT 'ZIMSEC',
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        last_login TEXT,
        is_active INTEGER DEFAULT 1,
        FOREIGN KEY (student_id) REFERENCES students(id)
    )
""")
print("   ✅ auth_users table ready")

# ============================================================
# STEP 2: Add student_number column to students table
# ============================================================
print("\n2️⃣  Adding student_number column to students...")

cols = [r[1] for r in c.execute("PRAGMA table_info(students)").fetchall()]
if "student_number" not in cols:
    c.execute("ALTER TABLE students ADD COLUMN student_number TEXT")
    print("   ✅ Added student_number column")
else:
    print("   ✓ student_number already exists")

# ============================================================
# STEP 3: Generate student numbers for existing students
# ============================================================
print("\n3️⃣  Generating student numbers for existing students...")

c.execute("SELECT id, name FROM students WHERE student_number IS NULL OR student_number = ''")
existing = c.fetchall()

for student_id, name in existing:
    # Generate DCR + 4-digit number
    c.execute("SELECT COUNT(*) FROM students WHERE student_number IS NOT NULL AND student_number != ''")
    count = c.fetchone()[0]
    student_number = f"DCR{count + 1:04d}"
    c.execute("UPDATE students SET student_number = ? WHERE id = ?", (student_number, student_id))
    print(f"   ✅ Student {student_id} ({name}) → {student_number}")

conn.commit()

# ============================================================
# STEP 4: Show auth_users table structure
# ============================================================
print("\n4️⃣  Verifying auth_users structure...")
c.execute("PRAGMA table_info(auth_users)")
for col in c.fetchall():
    print(f"   • {col[1]} ({col[2]})")

conn.close()

print("\n" + "="*70)
print("✅ SCRIPT 1 — PART A COMPLETE (Database)")
print("="*70 + "\n")

# ============================================================
# STEP 5: Create the auth module file
# ============================================================
print("5️⃣  Creating auth.py module...")

AUTH_MODULE = '''"""Authentication module for Digital Classroom Rules."""

import sqlite3
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, request, flash, render_template_string

DB = "digital_classroom.db"


def _db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password):
    """Simple secure password hashing."""
    salt = secrets.token_hex(16)
    pwd_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return f"{salt}${pwd_hash}"


def verify_password(password, stored_hash):
    """Verify a password against the stored hash."""
    try:
        salt, pwd_hash = stored_hash.split('$')
        new_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000
        ).hex()
        return secrets.compare_digest(new_hash, pwd_hash)
    except Exception:
        return False


def generate_student_number():
    """Generate next DCR#### number."""
    conn = _db()
    row = conn.execute("SELECT COUNT(*) as c FROM auth_users").fetchone()
    count = row["c"] if row else 0
    conn.close()
    return f"DCR{count + 1:04d}"


def register_user(first_name, last_name, email, password, grade_form,
                  phone="", exam_board="ZIMSEC"):
    """Register a new user."""
    conn = _db()
    try:
        student_number = generate_student_number()

        # Create student record
        cur = conn.execute("""
            INSERT INTO students (name, age, school, location, grade_form, subject,
                                  exam_board, tutor, registered_at, free_trial_used,
                                  paid_lessons, streak, current_subject, student_number)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?)
        """, (
            f"{first_name} {last_name}",
            "",
            "",
            "",
            grade_form or "",
            "",
            exam_board or "ZIMSEC",
            "Sarah",
            datetime.now().isoformat(),
            "",
            student_number
        ))
        student_id = cur.lastrowid

        # Create auth record
        conn.execute("""
            INSERT INTO auth_users (student_id, student_number, email,
                                    password_hash, first_name, last_name,
                                    phone, grade_form, exam_board)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            student_id, student_number, email,
            hash_password(password), first_name, last_name,
            phone, grade_form, exam_board
        ))

        conn.commit()
        return {"success": True, "student_number": student_number, "student_id": student_id}
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "email" in str(e):
            return {"success": False, "error": "This email is already registered."}
        elif "student_number" in str(e):
            return {"success": False, "error": "Student number conflict. Please try again."}
        return {"success": False, "error": str(e)}
    except Exception as e:
        conn.rollback()
        return {"success": False, "error": str(e)}
    finally:
        conn.close()


def login_user(student_number, password):
    """Log in a user."""
    conn = _db()
    try:
        user = conn.execute("""
            SELECT * FROM auth_users WHERE student_number = ? AND is_active = 1
        """, (student_number.upper().strip(),)).fetchone()

        if not user:
            return {"success": False, "error": "Student number not found."}

        if not verify_password(password, user["password_hash"]):
            return {"success": False, "error": "Incorrect password."}

        # Update last login
        conn.execute("""
            UPDATE auth_users SET last_login = ? WHERE id = ?
        """, (datetime.now().isoformat(), user["id"]))
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
    """Decorator to protect routes that need login."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function


def current_user():
    """Get the currently logged-in user."""
    if "user_id" not in session:
        return None
    conn = _db()
    user = conn.execute(
        "SELECT * FROM auth_users WHERE id = ?", (session["user_id"],)
    ).fetchone()
    conn.close()
    return user


def register_auth_routes(app):
    """Register all authentication routes on the Flask app."""

    # ---------------- LANDING PAGE ----------------
    @app.route("/")
    def landing():
        if "user_id" in session:
            return redirect(url_for("home", sid=session["student_id"]))
        return render_template_string(LANDING_HTML)

    # ---------------- REGISTER ----------------
    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password", "")
            grade_form = request.form.get("grade_form", "").strip()
            phone = request.form.get("phone", "").strip()

            # Validation
            errors = []
            if not first_name:
                errors.append("First name is required.")
            if not last_name:
                errors.append("Last name is required.")
            if not email or "@" not in email:
                errors.append("A valid email is required.")
            if len(password) < 6:
                errors.append("Password must be at least 6 characters.")
            if not grade_form:
                errors.append("Grade/Form is required.")

            if errors:
                return render_template_string(REGISTER_HTML, errors=errors, form=request.form)

            result = register_user(first_name, last_name, email, password, grade_form, phone)

            if result["success"]:
                return render_template_string(
                    REGISTER_SUCCESS_HTML,
                    student_number=result["student_number"]
                )
            else:
                return render_template_string(
                    REGISTER_HTML,
                    errors=[result["error"]],
                    form=request.form
                )

        return render_template_string(REGISTER_HTML, errors=[], form={})

    # ---------------- LOGIN ----------------
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

    # ---------------- LOGOUT ----------------
    @app.route("/logout")
    def logout():
        session.clear()
        return redirect(url_for("landing"))


# ============================================================
# HTML TEMPLATES
# ============================================================

SHARED_CSS = """
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:#f0f4f8;color:#1e2b3a;line-height:1.6;min-height:100vh}
.flag-stripe{height:6px;background:linear-gradient(90deg,#009b4d 0%,#009b4d 25%,#ffc200 25%,#ffc200 50%,#de2010 50%,#de2010 75%,#1e2b3a 75%,#1e2b3a 100%)}
.container{max-width:480px;margin:0 auto;padding:20px}
.logo{text-align:center;padding:40px 0 20px}
.logo-icon{font-size:64px;margin-bottom:10px}
.logo h1{font-size:26px;color:#1e2b3a;font-weight:800;letter-spacing:-0.5px}
.logo p{color:#5a6b7a;font-size:14px;margin-top:4px}
.card{background:white;border-radius:20px;padding:28px;box-shadow:0 4px 24px rgba(0,0,0,0.06);margin-bottom:16px}
h2{font-size:22px;color:#1e2b3a;margin-bottom:8px;font-weight:800}
.subtitle{color:#5a6b7a;font-size:14px;margin-bottom:20px}
.form-group{margin-bottom:16px}
label{display:block;font-size:13px;font-weight:600;color:#1e2b3a;margin-bottom:6px}
input,select{width:100%;padding:13px 15px;border:1.5px solid #e2e8f0;border-radius:11px;font-size:15px;font-family:inherit;background:white;transition:border-color 0.2s}
input:focus,select:focus{outline:none;border-color:#009b4d;background:#f8fffb}
button{width:100%;padding:15px;border:none;border-radius:11px;font-size:16px;font-weight:700;cursor:pointer;font-family:inherit;transition:all 0.2s}
.btn-primary{background:#009b4d;color:white;margin-top:8px}
.btn-primary:hover{background:#00803e}
.btn-secondary{background:#1e2b3a;color:white}
.btn-secondary:hover{background:#0b1a25}
.btn-outline{background:white;color:#009b4d;border:2px solid #009b4d}
.alert{padding:14px 16px;border-radius:11px;margin-bottom:16px;font-size:14px}
.alert-error{background:#fef2f2;color:#991b1b;border-left:4px solid #dc2626}
.alert-success{background:#f0fdf4;color:#166534;border-left:4px solid #22c55e}
.alert-info{background:#eff6ff;color:#1e40af;border-left:4px solid #3b82f6}
.link{color:#009b4d;text-decoration:none;font-weight:600}
.link:hover{text-decoration:underline}
.text-center{text-align:center}
.mt-16{margin-top:16px}
.mt-24{margin-top:24px}
.divider{text-align:center;color:#94a3b8;font-size:13px;margin:20px 0;position:relative}
.divider:before,.divider:after{content:'';position:absolute;top:50%;width:42%;height:1px;background:#e2e8f0}
.divider:before{left:0}
.divider:after{right:0}
.footer{text-align:center;color:#94a3b8;font-size:12px;padding:20px;line-height:1.8}
</style>
"""

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
    "<p>Your personal learning platform 🇿🇼</p>"
    "</div>"
    "<div class='card'>"
    "<h2>Welcome!</h2>"
    "<p class='subtitle'>Grades 1–7 &amp; Forms 1–6 &middot; ZIMSEC &amp; Cambridge</p>"
    "<div class='alert alert-info'>📚 Over 800 lessons across all subjects</div>"
    "<a href='/register' style='text-decoration:none'>"
    "<button class='btn-primary'>✨ Create Account</button></a>"
    "<div class='divider'>or</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-outline'>🔑 Login</button></a>"
    "</div>"
    "<div class='footer'>"
    "Powered by Quick Sync IT 🇿🇼<br>"
    "<a href='/privacy' class='link'>Privacy</a> &middot; "
    "<a href='/terms' class='link'>Terms</a>"
    "</div>"
    "</div></body></html>"
)

REGISTER_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Register</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>📝</div>"
    "<h1>Create Account</h1>"
    "<p>Start your learning journey</p>"
    "</div>"
    "<div class='card'>"
    "{% if errors %}"
    "{% for error in errors %}"
    "<div class='alert alert-error'>⚠️ {{ error }}</div>"
    "{% endfor %}"
    "{% endif %}"
    "<form method='POST'>"
    "<div class='form-group'><label>First Name</label>"
    "<input type='text' name='first_name' value='{{ form.get(\"first_name\", \"\") }}' required></div>"
    "<div class='form-group'><label>Last Name</label>"
    "<input type='text' name='last_name' value='{{ form.get(\"last_name\", \"\") }}' required></div>"
    "<div class='form-group'><label>Email</label>"
    "<input type='email' name='email' value='{{ form.get(\"email\", \"\") }}' required></div>"
    "<div class='form-group'><label>Phone (optional)</label>"
    "<input type='tel' name='phone' value='{{ form.get(\"phone\", \"\") }}'></div>"
    "<div class='form-group'><label>Grade / Form</label>"
    "<select name='grade_form' required>"
    "<option value=''>Select...</option>"
    "<option value='Grade 1'>Grade 1</option>"
    "<option value='Grade 2'>Grade 2</option>"
    "<option value='Grade 3'>Grade 3</option>"
    "<option value='Grade 4'>Grade 4</option>"
    "<option value='Grade 5'>Grade 5</option>"
    "<option value='Grade 6'>Grade 6</option>"
    "<option value='Grade 7'>Grade 7</option>"
    "<option value='Form 1'>Form 1</option>"
    "<option value='Form 2'>Form 2</option>"
    "<option value='Form 3'>Form 3</option>"
    "<option value='Form 4'>Form 4</option>"
    "<option value='Form 5'>Form 5</option>"
    "<option value='Form 6'>Form 6</option>"
    "</select></div>"
    "<div class='form-group'><label>Password (min 6 characters)</label>"
    "<input type='password' name='password' minlength='6' required></div>"
    "<button type='submit' class='btn-primary'>Create My Account →</button>"
    "</form>"
    "<div class='divider'>already have an account?</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-outline'>🔑 Login Instead</button></a>"
    "</div></div></body></html>"
)

REGISTER_SUCCESS_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Registration Successful</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>🎉</div>"
    "<h1>Welcome!</h1>"
    "<p>Your account is ready</p>"
    "</div>"
    "<div class='card'>"
    "<div class='alert alert-success'>✅ Registration successful!</div>"
    "<p class='subtitle text-center'>Your student number is</p>"
    "<div style='text-align:center;font-size:32px;font-weight:800;color:#009b4d;letter-spacing:3px;padding:20px;background:#f0fdf4;border-radius:11px;margin:16px 0'>{{ student_number }}</div>"
    "<div class='alert alert-info'>📌 Save this number. You'll need it to log in.</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-primary'>Continue to Login →</button></a>"
    "</div></div></body></html>"
)

LOGIN_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Login</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>🔑</div>"
    "<h1>Welcome Back</h1>"
    "<p>Log in to continue learning</p>"
    "</div>"
    "<div class='card'>"
    "{% if error %}"
    "<div class='alert alert-error'>⚠️ {{ error }}</div>"
    "{% endif %}"
    "<form method='POST'>"
    "<div class='form-group'><label>Student Number</label>"
    "<input type='text' name='student_number' placeholder='DCR0001' required autofocus></div>"
    "<div class='form-group'><label>Password</label>"
    "<input type='password' name='password' required></div>"
    "<button type='submit' class='btn-primary'>Login →</button>"
    "</form>"
    "<div class='divider'>new here?</div>"
    "<a href='/register' style='text-decoration:none'>"
    "<button class='btn-outline'>✨ Create Account</button></a>"
    "</div></div></body></html>"
)
'''

with open("auth.py", "w", encoding="utf-8") as f:
    f.write(AUTH_MODULE)

print("   ✅ auth.py created")

# ============================================================
# STEP 6: Connect auth to student_server.py
# ============================================================
print("\n6️⃣  Connecting auth to student_server.py...")

SERVER = "student_server.py"
with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_auth.py", "w", encoding="utf-8") as f:
    f.write(content)
print("   ✅ Backup saved: student_server_before_auth.py")

if "register_auth_routes" in content:
    print("   ✓ Auth already connected")
else:
    # Add import
    if "from auth import register_auth_routes" not in content:
        # Find last import
        lines = content.split("\n")
        last_import = 0
        for i, line in enumerate(lines[:80]):
            if line.strip().startswith(("import ", "from ")):
                last_import = i
        lines.insert(last_import + 1, "from auth import register_auth_routes, login_required, current_user")
        content = "\n".join(lines)
        print("   ✅ Added auth imports")

    # Add session secret key if not present
    if "app.secret_key" not in content:
        import re
        app_match = re.search(r"app\s*=\s*Flask\s*\([^)]*\)", content)
        if app_match:
            insert_pos = app_match.end()
            secret_setup = "\n\napp.secret_key = 'dcr-secret-key-2026-change-this-later'\napp.permanent_session_lifetime = __import__('datetime').timedelta(days=7)\n"
            content = content[:insert_pos] + secret_setup + content[insert_pos:]
            print("   ✅ Added app.secret_key")

    # Register auth routes before app.run()
    if "register_auth_routes(app)" not in content:
        run_pos = content.rfind("app.run(")
        if run_pos > 0:
            content = content[:run_pos] + "register_auth_routes(app)\n\n" + content[run_pos:]
            print("   ✅ Registered auth routes")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*70)
print("✅ SCRIPT 1 — COMPLETE")
print("="*70)
print("\n📌 NEW ROUTES ADDED:")
print("   GET  /             — Landing page")
print("   GET  /register     — Registration form")
print("   POST /register     — Create account")
print("   GET  /login        — Login form")
print("   POST /login        — Authenticate")
print("   GET  /logout       — End session")
print("\n📌 NEXT: Test locally, then push:")
print("   python student_server.py")
print("   (test in browser at http://127.0.0.1:5001/)")
print("   git add . && git commit -m 'Add auth system' && git push origin main")
print("="*70 + "\n")
