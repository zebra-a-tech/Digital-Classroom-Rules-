"""Digital Classroom Rules - Complete Auth Module"""

import sqlite3
import hashlib
import secrets
import random
from datetime import datetime
from functools import wraps
from flask import session, redirect, url_for, request, render_template_string

DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
TUTOR_NAMES = [
    "Tendai", "Rudo", "Bhekane", "Thandiwe", "Tapiwa", "Tariro",
    "Ruvarashe", "Nyasha", "Chiedza", "Rutendo", "Tanaka", "Makanaka",
    "Anesu", "Vimbai", "Farai", "Panashe", "Shamiso", "Tafadzwa",
    "Nomsa", "Thulani", "Sibusiso", "Nokuthula", "Lindiwe", "Zanele",
]

# All major Zimbabwean cities and towns
ZIMBABWE_CITIES = [
    "Harare", "Bulawayo", "Chitungwiza", "Mutare", "Gweru",
    "Kwekwe", "Kadoma", "Masvingo", "Chinhoyi", "Marondera",
    "Norton", "Chegutu", "Bindura", "Beitbridge", "Hwange",
    "Victoria Falls", "Rusape", "Chiredzi", "Zvishavane", "Gwanda",
    "Plumtree", "Kariba", "Karoi", "Chipinge", "Shurugwi",
    "Esigodini", "Filabusi", "Lupane", "Tsholotsho", "Kezi",
    "Maphisa", "Nkayi", "Gokwe", "Mvurwi", "Centenary",
    "Mount Darwin", "Rushinga", "Mudzi", "Nyanga", "Juliasdale",
    "Mutoko", "Murewa", "Wedza", "Chivhu", "Gutu",
    "Zvishavane", "Mberengwa", "Mwenezi", "Triangle", "Chimanimani",
    "Biriri", "Birchenough Bridge", "Buhera", "Sadza", "Bikita",
    "Nyika", "Jerera", "Ngundu", "Rutenga", "Mashava",
    "Shurugwi", "Zhombe", "Silobela", "Gokwe North", "Gokwe South",
    "Nembudziya", "Sanyati", "Chakari", "Kadoma Rural", "Ngezi",
    "Banket", "Raffingora", "Guruve", "Mazowe", "Glendale",
    "Shamva", "Madziwa", "Mvurwi", "Concession", "Christon Bank",
    "Harare Rural", "Epworth", "Chitungwiza Rural", "Ruwa", "Goromonzi",
    "Other (please specify)"
]


# Load the full subject list from the curriculum DB at import time.
# Falls back to a sensible default if the DB is unavailable.
def _load_allowed_subjects():
    try:
        import sqlite3 as _sq, os as _os
        _db = _os.environ.get("DB_PATH") or _os.path.join(
            _os.path.dirname(_os.path.abspath(__file__)),
            "digital_classroom.db",
        )
        _c = _sq.connect(_db)
        rows = _c.execute(
            "SELECT DISTINCT subject FROM curriculum "
            "WHERE subject IS NOT NULL AND subject != '' ORDER BY subject"
        ).fetchall()
        _c.close()
        if rows:
            return [r[0] for r in rows]
    except Exception as _e:
        print("SUBJECTS_ALLOWED: DB load failed, using default:", _e)
    return ["Maths","English","Science","Social Studies","Geography","History",
            "Biology","Chemistry","Physics","Economics","Accounting",
            "Shona","Ndebele","Agriculture","Commerce","Computer Studies",
            "Heritage Studies","Religious Studies"]

SUBJECTS_ALLOWED = _load_allowed_subjects()

def pick_random_tutor():
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
                  phone="", city="", school="", exam_board="ZIMSEC"):
    conn = _db()
    try:
        student_number = generate_student_number()
        tutor_name = pick_random_tutor()

        cur = conn.execute(
            "INSERT INTO students (name, age, school, location, grade_form, subject, "
            "exam_board, tutor, registered_at, free_trial_used, paid_lessons, streak, "
            "current_subject, student_number) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0, 0, 0, ?, ?)",
            (f"{first_name} {last_name}", "", school or "", city or "",
             grade_form or "", "", exam_board or "ZIMSEC", tutor_name,
             datetime.now().isoformat(), "", student_number)
        )
        student_id = cur.lastrowid

        conn.execute(
            "INSERT INTO auth_users (student_id, student_number, email, password_hash, "
            "first_name, last_name, phone, grade_form, exam_board) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (student_id, student_number, email or "", hash_password(password),
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
# CSS
# ============================================================
SHARED_CSS = """<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-font-smoothing:antialiased}
body{font-family:'Poppins',-apple-system,sans-serif;background:#f5f7fa;color:#1e2b3a;line-height:1.6;min-height:100vh}
.flag-stripe{height:8px;background:linear-gradient(90deg,#009b4d 0%,#009b4d 25%,#ffc200 25%,#ffc200 50%,#de2010 50%,#de2010 75%,#1e2b3a 75%,#1e2b3a 100%)}
.container{max-width:440px;margin:0 auto;padding:24px}
.brand-header{text-align:center;padding:24px 0 16px}
.brand-logo{width:80px;height:80px;border-radius:50%;background:white;box-shadow:0 8px 24px rgba(0,0,0,0.1);display:inline-flex;align-items:center;justify-content:center;overflow:hidden;border:3px dashed #1e2b3a}
.brand-logo img{width:100%;height:100%;object-fit:cover}
.logo{text-align:center;padding:16px 0 24px}
.logo-icon{font-size:48px;margin-bottom:8px;display:inline-block}
.logo h1{font-size:22px;color:#0b2a3a;font-weight:800;letter-spacing:-0.5px;line-height:1.2}
.logo p{color:#5a6b7a;font-size:13px;margin-top:6px}
.card{background:white;border-radius:22px;padding:28px;box-shadow:0 8px 32px rgba(11,42,58,0.08);margin-bottom:16px}
h2{font-size:20px;color:#0b2a3a;margin-bottom:6px;font-weight:800}
.subtitle{color:#5a6b7a;font-size:13px;margin-bottom:20px}
.form-group{margin-bottom:16px}
label{display:block;font-size:12px;font-weight:600;color:#1e2b3a;margin-bottom:6px;text-transform:uppercase;letter-spacing:0.5px}
input,select{width:100%;padding:14px 16px;border:2px solid #e5eaf0;border-radius:12px;font-size:15px;font-family:inherit;background:white;transition:all 0.2s;color:#1e2b3a}
input:focus,select:focus{outline:none;border-color:#009b4d;background:#f8fffb;box-shadow:0 0 0 4px rgba(0,155,77,0.1)}
button{width:100%;padding:16px;border:none;border-radius:12px;font-size:15px;font-weight:700;cursor:pointer;font-family:inherit;transition:all 0.2s;letter-spacing:0.3px}
.btn-primary{background:#009b4d;color:white;margin-top:4px}
.btn-primary:hover{background:#00803e}
.btn-outline{background:white;color:#009b4d;border:2px solid #009b4d}
.btn-outline:hover{background:#f0fdf4}
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
.wa-button{display:block;text-decoration:none;background:#25D366;color:white;padding:22px;border-radius:16px;text-align:center;margin:20px 0;box-shadow:0 8px 24px rgba(37,211,102,0.3)}
.wa-button .wa-label{font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:0.9}
.wa-button .wa-number{font-size:24px;font-weight:800;margin-top:6px}
.wa-button .wa-hint{font-size:12px;opacity:0.9;margin-top:4px}
</style>"""


# ============================================================
# BRAND HEADER (with logo)
# ============================================================
BRAND_HEADER = (
    "<div class='brand-header'>"
    "<div class='brand-logo'>"
    "<img src='https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Flag_of_Zimbabwe.svg/320px-Flag_of_Zimbabwe.svg.png' alt='Logo' onerror=\"this.style.display='none';this.parentElement.innerHTML='<div style=&quot;font-size:42px&quot;>🎓</div>'\">"
    "</div>"
    "</div>"
)

BRAND_HEADER_HTML = (
    "<div class='brand-header'>"
    "<div class='brand-logo'>🎓</div>"
    "</div>"
)


# ============================================================
# LANDING
# ============================================================
LANDING_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Digital Classroom Rules</title>" + SHARED_CSS + "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'>"
    "<div class='logo-icon'>🎓</div>"
    "<h1>Digital Classroom Rules</h1>"
    "<p>Smart People Education 🇿🇼</p></div>"
    "<div class='card'>"
    "<h2>Welcome!</h2>"
    "<p class='subtitle'>Grades 1–7 &amp; Forms 1–6 · ZIMSEC &amp; Cambridge</p>"
    "<div class='alert alert-info'>📚 Over 800 lessons across all subjects</div>"
    "<a href='/register' style='text-decoration:none'>"
    "<button class='btn-primary'>✨ Create Free Account</button></a>"
    "<div class='divider'>or</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-outline'>🔑 Login</button></a>"
    "</div>"
    "<div class='footer'>Powered by Quick Sync IT 🇿🇼<br>© 2026 Smart People Education</div>"
    "</div></body></html>"
)


# ============================================================
# REGISTER (with School Name, all Zimbabwe cities)
# ============================================================
REGISTER_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Create Account</title>" + SHARED_CSS + "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'><div class='logo-icon'>📝</div>"
    "<h1>Create Account</h1><p>Digital Classroom Rules</p></div>"
    "<div class='card'>"
    "{% if errors %}{% for error in errors %}"
    "<div class='alert alert-error'>⚠️ {{ error }}</div>"
    "{% endfor %}{% endif %}"
    "<form method='POST'>"
    "<div class='form-group'><label>First Name *</label>"
    "<input type='text' name='first_name' required></div>"
    "<div class='form-group'><label>Last Name *</label>"
    "<input type='text' name='last_name' required></div>"
    "<div class='form-group'><label>Phone Number * (WhatsApp)</label>"
    "<input type='tel' name='phone' required ></div>"
    "<div class='form-group'><label>Email (optional)</label>"
    "<input type='email' name='email'></div>"
    "<div class='form-group'><label>School Name *</label>"
    "<input type='text' name='school' required placeholder='e.g. Mbare High School'></div>"
    "<div class='form-group'><label>City / Town *</label>"
    "<select name='city' required>"
    "<option value=''>Choose your city...</option>"
    "{% for city in cities %}<option>{{city}}</option>{% endfor %}"
    "</select></div>"
    "<div class='form-group'><label>Grade / Form *</label>"
    "<select name='grade_form' required>"
    "<option value=''>Choose your grade...</option>"
    "<option>Grade 1</option><option>Grade 2</option><option>Grade 3</option>"
    "<option>Grade 4</option><option>Grade 5</option><option>Grade 6</option>"
    "<option>Grade 7</option><option>Form 1</option><option>Form 2</option>"
    "<option>Form 3</option><option>Form 4</option><option>Form 5</option>"
    "<option>Form 6</option>"
    "</select></div>"
    "<div class='form-group'><label>Age *</label><input type='number' name='age' min='4' max='99' required></div>"
    "<div class='form-group'><label>Subjects you want to study * (choose one or more)</label>"
    + "".join(
        "<label style='display:block;margin:6px 0'>"
        f"<input type='checkbox' name='subjects' value='{s}' style='width:auto;margin-right:8px'>{s}"
        "</label>"
        for s in SUBJECTS_ALLOWED
    )
    + "</div>"
    "<div id='parent-notice' style='display:none;background:#fff7e6;border:1px solid #f5c26b;border-radius:14px;padding:12px 14px;margin:12px 0;color:#7a4b00'>👨\u200d👩\u200d👧 <b>Parent/Guardian Notice</b><br>For Grades 1–4, a parent or responsible adult should be present during the lesson to help the pupil follow instructions, read questions when necessary, and support the learning process.</div>"
    "<script>(function(){var g=document.querySelector('select[name=grade_form]'),n=document.getElementById('parent-notice');function u(){n.style.display=/^Grade [1-4]$/.test(g.value)?'block':'none'}g.addEventListener('change',u);u()})()</script>"
    "<div class='form-group'><label>Password * (min 6 chars)</label>"
    "<input type='password' name='password' minlength='6' required></div>"
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
# LOGIN (no placeholder)
# ============================================================
LOGIN_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Login</title>" + SHARED_CSS + "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'><div class='logo-icon'>🎓</div>"
    "<h1>Welcome Back</h1><p>Log in to Digital Classroom Rules</p></div>"
    "<div class='card'>"
    "{% if error %}<div class='alert alert-error'>⚠️ {{ error }}</div>{% endif %}"
    "<form method='POST'>"
    "<div class='form-group'><label>Student Number</label>"
    "<input type='text' name='student_number' required autofocus "
    "autocomplete='username' style='text-transform:uppercase'></div>"
    "<div class='form-group'><label>Password</label>"
    "<input type='password' name='password' required></div>"
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
# REGISTER SUCCESS
# ============================================================
REGISTER_SUCCESS_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Account Created</title>" + SHARED_CSS + "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'><div class='logo-icon'>🎉</div>"
    "<h1>Account Created!</h1><p>Welcome to Digital Classroom Rules</p></div>"
    "<div class='card'>"
    "<div class='alert alert-success'>✅ You're registered!</div>"
    "<p class='subtitle text-center' style='margin-bottom:8px'>Your Student Number:</p>"
    "<div style='text-align:center;font-size:36px;font-weight:800;color:#009b4d;"
    "letter-spacing:4px;padding:24px;background:#f0fdf4;border-radius:16px;"
    "margin:8px 0 16px;border:2px dashed #22c55e'>{{ student_number }}</div>"
    "<div class='alert alert-info' style='text-align:center'>"
    "👨‍🏫 Your personal tutor is <strong>{{ tutor_name }}</strong><br>"
    "📌 Save your student number!"
    "</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-primary'>Continue to Login →</button></a>"
    "</div>"
    "<div class='footer'>Powered by Quick Sync IT 🇿🇼</div>"
    "</div></body></html>"
)


# ============================================================
# FORGOT PASSWORD
# ============================================================
FORGOT_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Forgot Password</title>" + SHARED_CSS + "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'><div class='logo-icon'>🔐</div>"
    "<h1>Forgot Password?</h1><p>We'll help you get back in</p></div>"
    "<div class='card'>"
    "<div class='alert alert-info'>"
    "To reset your password, tap the WhatsApp button below and your tutor "
    "will send you a temporary password."
    "</div>"
    "<a href='https://wa.me/263719809683?text=Hello%21%20I%20forgot%20my%20Digital%20Classroom%20password.%20Please%20send%20me%20a%20temporary%20password.' "
    "target='_blank' class='wa-button'>"
    "<div class='wa-label'>Tap to WhatsApp</div>"
    "<div class='wa-number'>💬 +263 719 809 683</div>"
    "<div class='wa-hint'>Opens WhatsApp chat →</div>"
    "</a>"
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
        if "user_id" in session and "student_id" in session:
            return redirect(url_for("home", sid=session["student_id"]))
        return render_template_string(LANDING_HTML)

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            first_name = request.form.get("first_name", "").strip()
            last_name = request.form.get("last_name", "").strip()
            email = request.form.get("email", "").strip().lower()
            if not email:
                import secrets as _sec
                email = "nomail-" + _sec.token_hex(5) + "@noemail.local"
            password = request.form.get("password", "")
            grade_form = request.form.get("grade_form", "").strip()
            phone = request.form.get("phone", "").strip()
            city = request.form.get("city", "").strip()
            school = request.form.get("school", "").strip()

            errors = []
            if not first_name: errors.append("First name is required.")
            if not last_name: errors.append("Last name is required.")
            if not phone: errors.append("Phone number is required.")
            if email and "@" not in email: errors.append("Please enter a valid email or leave blank.")
            if not school: errors.append("School name is required.")
            if not city: errors.append("Please choose your city.")
            if len(password) < 6: errors.append("Password must be at least 6 characters.")
            if not grade_form: errors.append("Please choose your Grade/Form.")

            age_raw = request.form.get("age", "").strip()
            subjects = [x for x in request.form.getlist("subjects") if x in SUBJECTS_ALLOWED]
            if not age_raw.isdigit() or not (4 <= int(age_raw) <= 99): errors.append("Please enter a valid age.")
            if not subjects: errors.append("Please choose at least one subject.")
            if errors:
                return render_template_string(REGISTER_HTML, errors=errors, cities=ZIMBABWE_CITIES)

            result = register_user(first_name, last_name, email, password,
                                   grade_form, phone, city, school)

            if result["success"]:

                save_onboarding(result["student_number"], age_raw, subjects)
                return render_template_string(
                    REGISTER_SUCCESS_HTML,
                    student_number=result["student_number"],
                    tutor_name=result["tutor_name"],
                )
            else:
                return render_template_string(REGISTER_HTML, errors=[result["error"]], cities=ZIMBABWE_CITIES)

        return render_template_string(REGISTER_HTML, errors=[], cities=ZIMBABWE_CITIES)

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




def save_onboarding(student_number, age, subjects):
    """Save age and ALL chosen subjects for a newly registered pupil."""
    import os, sqlite3
    from datetime import datetime
    # Honour DB_PATH so we always write to the same DB the rest of the app uses.
    path = os.environ.get("DB_PATH") or os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "digital_classroom.db",
    )
    # Ensure parent dir exists (e.g. /data on Railway)
    _parent = os.path.dirname(path)
    if _parent:
        os.makedirs(_parent, exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        row = conn.execute("SELECT id FROM students WHERE student_number=?", (student_number,)).fetchone()
        if not row:
            return
        sid = row[0]
        conn.execute("UPDATE students SET age=?, subject=?, current_subject=? WHERE id=?",
                     (int(age), subjects[0], subjects[0], sid))
        for sub in subjects:
            conn.execute("INSERT INTO student_subjects (student_id, subject, active, added_at) VALUES (?,?,1,?)",
                         (sid, sub, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    finally:
        conn.close()
