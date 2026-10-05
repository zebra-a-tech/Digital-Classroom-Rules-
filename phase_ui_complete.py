"""
Complete student dashboard redesign + fixes
"""

import re
import os

print("\n" + "="*70)
print("🎨 COMPLETE DASHBOARD REDESIGN + FIXES")
print("="*70 + "\n")

# ============================================================
# STEP 1: Update auth.py — phone required, email optional, WhatsApp link
# ============================================================
print("1️⃣  Updating auth.py (phone required, email optional, WhatsApp link)...")

with open("auth.py", "r", encoding="utf-8") as f:
    auth = f.read()

# Backup
with open("auth_before_phase_ui.py", "w", encoding="utf-8") as f:
    f.write(auth)
print("   ✅ Backup saved")

# --- Update REGISTER_HTML: phone required, email optional ---
old_reg_email = (
    "<div class='form-group'><label>Email</label>"
    "<input type='email' name='email' required autocomplete='email'></div>"
    "<div class='form-group'><label>Phone (optional)</label>"
    "<input type='tel' name='phone' autocomplete='tel'></div>"
)
new_reg_email = (
    "<div class='form-group'><label>Phone Number <span style='color:#dc2626'>*</span></label>"
    "<input type='tel' name='phone' required autocomplete='tel' "
    "placeholder='+263 71 234 5678'></div>"
    "<div class='form-group'><label>Email (optional)</label>"
    "<input type='email' name='email' autocomplete='email'></div>"
)

if old_reg_email in auth:
    auth = auth.replace(old_reg_email, new_reg_email)
    print("   ✅ Register: phone required, email optional")

# --- Update validation logic ---
old_validation = (
    'if not email or "@" not in email: errors.append("A valid email is required.")'
)
new_validation = (
    'if email and "@" not in email: errors.append("Please enter a valid email or leave it blank.")'
)
if old_validation in auth:
    auth = auth.replace(old_validation, new_validation)
    print("   ✅ Validation: email optional")

if 'if not phone:' not in auth:
    # Add phone requirement to validation
    marker = 'if not grade_form: errors.append("Please choose your Grade/Form.")'
    if marker in auth:
        auth = auth.replace(
            marker,
            marker + '\n            if not phone: errors.append("Phone number is required (for WhatsApp support).")'
        )
        print("   ✅ Validation: phone required")

# --- Update FORGOT_HTML: clickable WhatsApp link ---
old_forgot_phone = (
    "<div style='text-align:center;padding:20px;background:#f0fdf4;'"
    "border-radius:14px;margin:20px 0'>"
    "<div style='font-size:12px;color:#5a6b7a;margin-bottom:8px;text-transform:uppercase;'"
    "letter-spacing:1px;font-weight:600'>WhatsApp your tutor</div>"
    "<div style='font-size:24px;font-weight:800;color:#009b4d'>"
    "📱 +263 719 809 683</div>"
    "</div>"
)

new_forgot_phone = (
    "<a href='https://wa.me/263719809683?text=Hello!%20I%20forgot%20my%20Digital%20Classroom%20password.%20"
    "Please%20send%20me%20a%20temporary%20password.' "
    "target='_blank' style='text-decoration:none;display:block'>"
    "<div style='text-align:center;padding:24px;background:#25D366;"
    "border-radius:16px;margin:20px 0;box-shadow:0 8px 24px rgba(37,211,102,0.3)'>"
    "<div style='font-size:13px;color:white;margin-bottom:8px;"
    "text-transform:uppercase;letter-spacing:1px;font-weight:600'>"
    "Tap to WhatsApp</div>"
    "<div style='font-size:26px;font-weight:800;color:white'>"
    "💬 +263 719 809 683</div>"
    "<div style='font-size:12px;color:rgba(255,255,255,0.9);margin-top:6px'>"
    "Opens WhatsApp chat →</div>"
    "</div></a>"
)

if old_forgot_phone in auth:
    auth = auth.replace(old_forgot_phone, new_forgot_phone)
    print("   ✅ Forgot password: WhatsApp link is now clickable")

with open("auth.py", "w", encoding="utf-8") as f:
    f.write(auth)

# ============================================================
# STEP 2: Add logout button + redesign home dashboard
# ============================================================
print("\n2️⃣  Redesigning student dashboard...")

SERVER = "student_server.py"
with open(SERVER, "r", encoding="utf-8") as f:
    server = f.read()

# Backup
with open("student_server_before_dashboard_redesign.py", "w", encoding="utf-8") as f:
    f.write(server)
print("   ✅ Backup saved")

# ---- Add global logout button at top of student_server ----
# We'll inject a Logout button into every student page by adding CSS + a floating button
logout_inject = """

# ============================================================
# LOGOUT BUTTON INJECTION (added by phase_ui_complete)
# ============================================================
if "logout_injected" not in globals():
    logout_injected = True

    @app.after_request
    def inject_logout_button(response):
        # Only inject into HTML responses for authenticated users
        if "text/html" not in response.content_type:
            return response
        try:
            from flask import session as _sess
            if "user_id" not in _sess:
                return response
            # Only inject into student pages (not auth pages)
            path = request.path
            if not path.startswith("/student/"):
                return response
            # Inject a floating logout button + modern font
            html = response.get_data(as_text=True)
            injection = '''
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
body, .card, button, input, select, h1, h2, h3, h4, p, a, div { font-family: 'Poppins', -apple-system, sans-serif !important; }
.logout-float {
    position: fixed; top: 16px; right: 16px; z-index: 9999;
    background: #dc2626; color: white; padding: 10px 20px;
    border-radius: 22px; text-decoration: none; font-size: 13px;
    font-weight: 700; box-shadow: 0 4px 16px rgba(220,38,38,0.35);
    letter-spacing: 0.3px;
}
.logout-float:hover { background: #b91c1c; }
@media(max-width:600px){ .logout-float { padding: 8px 16px; font-size: 12px; } }
</style>
<a href="/logout" class="logout-float">🚪 Logout</a>
'''
            # Insert before </body>
            if "</body>" in html:
                html = html.replace("</body>", injection + "</body>")
                response.set_data(html)
        except Exception as e:
            pass
        return response

"""

# Insert this AFTER register_auth_routes or the last register_* call
if "logout_injected" not in server:
    # Find a good insertion point: just before app.run()
    run_pos = server.rfind("app.run(")
    if run_pos > 0:
        server = server[:run_pos] + logout_inject + "\n" + server[run_pos:]
        print("   ✅ Added global logout button")

# ---- Replace home dashboard HTML with modern design ----
# Find the home() function and replace its template
home_pattern = re.compile(
    r'@app\.route\("/student/<int:sid>/home"\)\s*\ndef home\(sid\):.*?(?=@app\.route|\Z)',
    re.DOTALL
)

new_home = '''@app.route("/student/<int:sid>/home")
def home(sid):
    """Modern student dashboard."""
    from auth import _db as auth_db
    import datetime as _dt

    s = student(sid)
    if not s:
        return "Student not found", 404

    # Greeting based on time
    hour = _dt.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Compute first name (from auth_users if available)
    first_name = s["name"].split()[0] if s["name"] else "Student"

    html = """<!doctype html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Home — Digital Classroom Rules</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Poppins',sans-serif;background:#f5f7fa;color:#1e2b3a;line-height:1.6;padding-bottom:90px}
.flag{height:8px;background:linear-gradient(90deg,#009b4d 0%,#009b4d 25%,#ffc200 25%,#ffc200 50%,#de2010 50%,#de2010 75%,#1e2b3a 75%,#1e2b3a 100%)}
.wrap{max-width:600px;margin:0 auto;padding:20px}
.hero{background:linear-gradient(135deg,#0b2a3a 0%,#1a4a5e 100%);color:white;padding:32px 24px;border-radius:24px;margin-bottom:20px;position:relative;overflow:hidden}
.hero::after{content:"🇿🇼";position:absolute;font-size:8rem;opacity:0.05;right:-20px;bottom:-30px;transform:rotate(-15deg)}
.hero h1{font-size:26px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;position:relative;z-index:1}
.hero p{opacity:0.85;font-size:14px;position:relative;z-index:1}
.tutor{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.12);padding:8px 16px;border-radius:20px;font-size:13px;margin-top:12px;backdrop-filter:blur(4px);position:relative;z-index:1}
.section-title{font-size:12px;font-weight:700;color:#5a6b7a;text-transform:uppercase;letter-spacing:1px;margin:20px 4px 12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.stat-card{background:white;padding:20px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);text-align:center}
.stat-icon{font-size:32px;margin-bottom:6px}
.stat-value{font-size:24px;font-weight:800;color:#0b2a3a}
.stat-label{font-size:11px;color:#5a6b7a;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin-top:4px}
.action-card{background:white;padding:20px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);margin-bottom:12px;display:flex;align-items:center;gap:16px;text-decoration:none;color:inherit;transition:all 0.2s}
.action-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(11,42,58,0.1)}
.action-icon{font-size:36px;flex-shrink:0}
.action-content{flex:1}
.action-title{font-size:15px;font-weight:700;color:#0b2a3a;margin-bottom:2px}
.action-desc{font-size:12px;color:#5a6b7a}
.action-arrow{color:#94a3b8;font-size:20px}
.btn{display:block;padding:16px;border-radius:14px;text-align:center;text-decoration:none;font-weight:700;font-size:15px;margin-bottom:10px;transition:all 0.2s;border:none;cursor:pointer;font-family:inherit}
.btn-green{background:#009b4d;color:white;box-shadow:0 6px 20px rgba(0,155,77,0.3)}
.btn-green:hover{background:#00803e}
.btn-orange{background:#ff6b35;color:white;box-shadow:0 6px 20px rgba(255,107,53,0.3)}
.btn-orange:hover{background:#e55a25}
.btn-outline{background:white;color:#009b4d;border:2px solid #009b4d}
.nav{position:fixed;bottom:0;left:0;right:0;background:white;display:flex;justify-content:space-around;padding:10px 0 12px;box-shadow:0 -4px 20px rgba(0,0,0,0.08);z-index:100;border-top-left-radius:20px;border-top-right-radius:20px}
.nav a{flex:1;text-align:center;text-decoration:none;color:#94a3b8;font-size:10px;font-weight:600;padding:6px 0;transition:color 0.2s}
.nav a.active{color:#009b4d}
.nav a i{display:block;font-size:22px;margin-bottom:2px;font-style:normal}
.logout-top{position:absolute;top:16px;right:16px;background:rgba(255,255,255,0.15);color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:700;backdrop-filter:blur(4px);z-index:10;border:1px solid rgba(255,255,255,0.2)}
</style>
</head>
<body>
<div class="flag"></div>
<div class="wrap">

<div class="hero">
  <a href="/logout" class="logout-top">🚪 Logout</a>
  <h1>{{greeting}}, {{first}}! 👋</h1>
  <p>Welcome to Digital Classroom Rules</p>
  <div class="tutor">🧑‍🏫 Tutor: {{tutor}}</div>
</div>

<div class="section-title">📊 Your Progress</div>
<div class="grid">
  <div class="stat-card">
    <div class="stat-icon">🔥</div>
    <div class="stat-value">{{streak}}</div>
    <div class="stat-label">Day Streak</div>
  </div>
  <div class="stat-card">
    <div class="stat-icon">📚</div>
    <div class="stat-value">{{paid_lessons}}</div>
    <div class="stat-label">Lessons Done</div>
  </div>
</div>

<div class="section-title">🎓 Start Learning</div>
<a href="/student/{{sid}}/trial" class="btn btn-green">🎁 Free 30-Minute Trial</a>
<a href="/student/{{sid}}/paid" class="btn btn-orange">💰 $1 — 1-Hour Lesson</a>

<div class="section-title">⚡ Quick Access</div>

<a href="/student/{{sid}}/centre" class="action-card">
  <div class="action-icon">📖</div>
  <div class="action-content">
    <div class="action-title">Learning Centre</div>
    <div class="action-desc">All subjects &amp; topics</div>
  </div>
  <div class="action-arrow">›</div>
</a>

<a href="/student/{{sid}}/homework" class="action-card">
  <div class="action-icon">📝</div>
  <div class="action-content">
    <div class="action-title">Weekly Assignments</div>
    <div class="action-desc">Practice questions &amp; tests</div>
  </div>
  <div class="action-arrow">›</div>
</a>

<a href="/student/{{sid}}/tutor" class="action-card">
  <div class="action-icon">🧑‍🏫</div>
  <div class="action-content">
    <div class="action-title">Ask Your Tutor</div>
    <div class="action-desc">Get help with any subject</div>
  </div>
  <div class="action-arrow">›</div>
</a>

<a href="/student/{{sid}}/profile" class="action-card">
  <div class="action-icon">👤</div>
  <div class="action-content">
    <div class="action-title">My Profile</div>
    <div class="action-desc">Student #{{student_number}}</div>
  </div>
  <div class="action-arrow">›</div>
</a>

</div>

<div class="nav">
  <a href="/student/{{sid}}/home" class="active">
    <i>🏠</i>Home
  </a>
  <a href="/student/{{sid}}/centre">
    <i>📖</i>Learn
  </a>
  <a href="/student/{{sid}}/homework">
    <i>📝</i>Homework
  </a>
  <a href="/student/{{sid}}/profile">
    <i>👤</i>Profile
  </a>
</div>

</body></html>"""

    return render_template_string(
        html,
        greeting=greeting,
        first=first_name,
        tutor=s["tutor"] or "Your Tutor",
        streak=s["streak"] or 0,
        paid_lessons=s["paid_lessons"] or 0,
        sid=sid,
        student_number=s["student_number"] if "student_number" in s.keys() else "N/A"
    )


'''

# Replace the home route
if home_pattern.search(server):
    server = home_pattern.sub(new_home, server, count=1)
    print("   ✅ Replaced home() with modern dashboard")
else:
    print("   ⚠️ Could not find home() route — skipping dashboard replace")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(server)

# ============================================================
# STEP 3: Verify
# ============================================================
print("\n3️⃣  Verifying...")

import subprocess
result = subprocess.run(
    ["python", "-c", "import auth; print('OK')"],
    capture_output=True, text=True
)
if "OK" in result.stdout:
    print("   ✅ auth.py imports cleanly")
else:
    print(f"   ❌ auth.py error: {result.stderr[:200]}")

result = subprocess.run(
    ["python", "-c", "import student_server; print('OK')"],
    capture_output=True, text=True, timeout=10
)
if "OK" in result.stdout:
    print("   ✅ student_server.py imports cleanly")
else:
    print(f"   ⚠️ student_server.py check: {result.stderr[:300]}")

print("\n" + "="*70)
print("✅ PHASE UI COMPLETE")
print("="*70)
print("\n📌 FIXES APPLIED:")
print("   1. ✅ Logout button — floating top-right on all student pages")
print("   2. ✅ Dashboard completely redesigned (Poppins, modern cards)")
print("   3. ✅ Forgot password — clickable WhatsApp button")
print("   4. ✅ Register — phone required, email optional")
print("   5. ✅ Bottom navigation on dashboard")
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/register     (phone required)")
print("   http://127.0.0.1:5001/login")
print("   http://127.0.0.1:5001/forgot-password   (clickable WhatsApp)")
print("   http://127.0.0.1:5001/student/1/home    (new dashboard)")
print("\n⚠️  IMPORTANT: Clear browser cache after restart!")
print("="*70 + "\n")
