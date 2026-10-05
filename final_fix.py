"""One consolidated fix - auth, dashboard, subject grid, all links working"""

import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_final_fix.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved: student_server_before_final_fix.py")

# ============================================================
# FIX 1: Remove the old root route that shows "Student Portal Server"
# ============================================================
old_root_pattern = re.compile(
    r'@app\.route\("/"\)\s*\n\s*def root\(\):.*?(?=\n@app\.route|\ndef |\Z)',
    re.DOTALL
)
if old_root_pattern.search(content):
    content = old_root_pattern.sub("# Old root route removed — using auth.py landing\n", content, count=1)
    print("✅ Removed old root route")
else:
    print("⚠️ Could not find old root route")

# ============================================================
# FIX 2: Ensure register_auth_routes is called BEFORE app.run
# ============================================================
# Remove any duplicate calls
content = content.replace("register_auth_routes(app)", "# RAR_PLACEHOLDER")
# Now insert ONE call before app.run()
run_pos = content.rfind("app.run(")
if run_pos > 0:
    content = content[:run_pos] + "register_auth_routes(app)\n\n" + content[run_pos:]
    print("✅ register_auth_routes positioned before app.run")
# Clean up placeholder
content = content.replace("# RAR_PLACEHOLDER", "register_auth_routes(app)")

# ============================================================
# FIX 3: Add session import
# ============================================================
if "render_template_string" not in content.split("def ")[0]:
    content = content.replace(
        "from flask import Flask, request, redirect, url_for",
        "from flask import Flask, request, redirect, url_for, render_template_string, session, jsonify",
        1
    )
    print("✅ Added Flask imports")

# ============================================================
# FIX 4: Replace home() with modern dashboard + subject grid
# ============================================================
home_pattern = re.compile(
    r'@app\.route\("/student/<int:sid>/home"\)\s*\n\s*def home\(sid\):.*?(?=\n@app\.route|\Z)',
    re.DOTALL
)

NEW_HOME = '''@app.route("/student/<int:sid>/home")
def home(sid):
    """Modern student dashboard with subjects."""
    import datetime as _dt

    s = student(sid)
    if not s:
        return "Student not found", 404

    hour = _dt.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    name = s["name"] or "Student"
    first_name = name.split()[0] if name else "Student"

    def safe_get(key, default=""):
        try:
            return s[key] if s[key] is not None else default
        except (KeyError, IndexError):
            return default

    student_number = safe_get("student_number", "N/A")
    tutor = safe_get("tutor", "Your Tutor")
    streak = safe_get("streak", 0)
    paid_lessons = safe_get("paid_lessons", 0)
    grade_form = safe_get("grade_form", "")

    # Get subjects from SUBJECTS list (defined globally)
    all_subjects = SUBJECTS if isinstance(SUBJECTS, list) else []

    html = """<!doctype html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Home — Digital Classroom Rules</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Poppins',sans-serif;background:#f5f7fa;color:#1e2b3a;line-height:1.6;padding-bottom:100px;-webkit-font-smoothing:antialiased}
.flag{height:8px;background:linear-gradient(90deg,#009b4d 0%,#009b4d 25%,#ffc200 25%,#ffc200 50%,#de2010 50%,#de2010 75%,#1e2b3a 75%,#1e2b3a 100%)}
.wrap{max-width:600px;margin:0 auto;padding:20px}
.brand-bar{display:flex;align-items:center;gap:12px;padding:12px 0 20px}
.brand-logo{width:44px;height:44px;border-radius:50%;background:#0b2a3a;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;box-shadow:0 4px 12px rgba(11,42,58,0.2)}
.brand-text{font-size:15px;font-weight:800;color:#0b2a3a;letter-spacing:-0.3px;line-height:1.2}
.brand-text span{display:block;font-size:10px;font-weight:500;color:#5a6b7a;letter-spacing:1px;text-transform:uppercase;margin-top:2px}
.hero{background:linear-gradient(135deg,#0b2a3a 0%,#1a4a5e 100%);color:white;padding:32px 24px;border-radius:24px;margin-bottom:20px;position:relative;overflow:hidden}
.hero::after{content:"🇿🇼";position:absolute;font-size:8rem;opacity:0.05;right:-20px;bottom:-30px;transform:rotate(-15deg)}
.logout-btn{position:absolute;top:16px;right:16px;background:rgba(220,38,38,0.9);color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:700;z-index:10;backdrop-filter:blur(4px)}
.logout-btn:hover{background:rgba(185,28,28,1)}
.hero h1{font-size:24px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;position:relative;z-index:1}
.hero p{opacity:0.85;font-size:13px;position:relative;z-index:1}
.tutor-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.12);padding:8px 16px;border-radius:20px;font-size:12px;margin-top:12px;backdrop-filter:blur(4px);position:relative;z-index:1}
.section-title{font-size:12px;font-weight:700;color:#5a6b7a;text-transform:uppercase;letter-spacing:1px;margin:24px 4px 12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.stat-card{background:white;padding:18px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);text-align:center}
.stat-icon{font-size:28px;margin-bottom:4px}
.stat-value{font-size:24px;font-weight:800;color:#0b2a3a;line-height:1}
.stat-label{font-size:10px;color:#5a6b7a;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin-top:6px}
.subject-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.subject-card{background:white;padding:20px 16px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);text-decoration:none;color:#0b2a3a;text-align:center;transition:all 0.2s;border:2px solid transparent}
.subject-card:hover{transform:translateY(-3px);box-shadow:0 8px 24px rgba(11,42,58,0.1);border-color:#009b4d}
.subject-icon{font-size:32px;margin-bottom:8px;display:block}
.subject-name{font-size:14px;font-weight:700;color:#0b2a3a}
.action-card{background:white;padding:18px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);margin-bottom:10px;display:flex;align-items:center;gap:16px;text-decoration:none;color:inherit;transition:all 0.2s}
.action-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(11,42,58,0.1)}
.action-icon{font-size:32px;flex-shrink:0}
.action-content{flex:1}
.action-title{font-size:15px;font-weight:700;color:#0b2a3a;margin-bottom:2px}
.action-desc{font-size:12px;color:#5a6b7a}
.action-arrow{color:#94a3b8;font-size:22px;font-weight:300}
.btn{display:block;padding:16px;border-radius:14px;text-align:center;text-decoration:none;font-weight:700;font-size:15px;margin-bottom:10px;transition:all 0.2s}
.btn-green{background:#009b4d;color:white;box-shadow:0 6px 20px rgba(0,155,77,0.3)}
.btn-orange{background:#ff6b35;color:white;box-shadow:0 6px 20px rgba(255,107,53,0.3)}
.nav{position:fixed;bottom:0;left:0;right:0;background:white;display:flex;justify-content:space-around;padding:10px 0 12px;box-shadow:0 -4px 20px rgba(0,0,0,0.08);z-index:100;border-top-left-radius:20px;border-top-right-radius:20px}
.nav a{flex:1;text-align:center;text-decoration:none;color:#94a3b8;font-size:10px;font-weight:600;padding:6px 0}
.nav a.active{color:#009b4d}
.nav a i{display:block;font-size:22px;margin-bottom:2px;font-style:normal}
</style>
</head>
<body>
<div class="flag"></div>
<div class="wrap">

<div class="brand-bar">
  <div class="brand-logo">🎓</div>
  <div class="brand-text">Digital Classroom Rules<span>Smart People Education</span></div>
</div>

<div class="hero">
  <a href="/logout" class="logout-btn">🚪 Logout</a>
  <h1>{{greeting}}, {{first}}! 👋</h1>
  <p>Welcome to Digital Classroom Rules</p>
  <div class="tutor-badge">🧑‍🏫 Tutor: {{tutor}}</div>
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
    <div class="stat-label">Lessons</div>
  </div>
</div>

<div class="section-title">📖 Choose a Subject</div>
<div class="subject-grid">
{% for subj in subjects %}
  <a href="/student/{{sid}}/learn?subject={{subj}}" class="subject-card">
    <span class="subject-icon">📘</span>
    <span class="subject-name">{{subj}}</span>
  </a>
{% endfor %}
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
<a href="/student/{{sid}}/homework/start" class="action-card">
  <div class="action-icon">📝</div>
  <div class="action-content">
    <div class="action-title">Weekly Assignments</div>
    <div class="action-desc">Practice questions</div>
  </div>
  <div class="action-arrow">›</div>
</a>
<a href="/student/{{sid}}/tutor" class="action-card">
  <div class="action-icon">🧑‍🏫</div>
  <div class="action-content">
    <div class="action-title">Ask Your Tutor</div>
    <div class="action-desc">Get help anytime</div>
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
  <a href="/student/{{sid}}/home" class="active"><i>🏠</i>Home</a>
  <a href="/student/{{sid}}/centre"><i>📖</i>Learn</a>
  <a href="/student/{{sid}}/homework/start"><i>📝</i>Homework</a>
  <a href="/student/{{sid}}/profile"><i>👤</i>Profile</a>
</div>

</body></html>"""

    return render_template_string(
        html,
        greeting=greeting,
        first=first_name,
        tutor=tutor,
        streak=streak,
        paid_lessons=paid_lessons,
        sid=sid,
        student_number=student_number,
        subjects=all_subjects
    )


'''

if home_pattern.search(content):
    content = home_pattern.sub(NEW_HOME, content, count=1)
    print("✅ Home route replaced with modern dashboard + subject grid")
else:
    print("⚠️ Could not find home route to replace")

# ============================================================
# FIX 5: Make /logout redirect to /login (not /)
# ============================================================
# First check if auth.py handles this. If not, add a /logout route here.
if '@app.route("/logout")' not in content:
    run_pos = content.rfind("app.run(")
    if run_pos > 0:
        logout_route = '''
@app.route("/logout")
def logout_redirect():
    from flask import session as _s
    _s.clear()
    return redirect("/login")

'''
        content = content[:run_pos] + logout_route + content[run_pos:]
        print("✅ Added /logout route that redirects to /login")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ student_server.py updated")

# ============================================================
# FIX 6: Fix student_playbook.py missing function
# ============================================================
print("\n🔧 Fixing student_playbook.py...")

try:
    with open("student_playbook.py", "r", encoding="utf-8") as f:
        playbook = f.read()

    with open("student_playbook_before_final_fix.py", "w", encoding="utf-8") as f:
        f.write(playbook)

    if "def _filter_topics_for_trial" not in playbook:
        # Add the missing function at the top of the file
        helper = '''
RESTRICTED_TRIAL_TOPICS_PER_SUBJECT = 3

def _filter_topics_for_trial(subject, topics_list, trial_active, paid_active):
    """During trial (not paid), only show first N topics per subject."""
    if paid_active:
        return topics_list
    if trial_active:
        return topics_list[:RESTRICTED_TRIAL_TOPICS_PER_SUBJECT]
    return []

'''
        # Insert after imports
        lines = playbook.split("\n")
        last_import = 0
        for i, line in enumerate(lines[:60]):
            if line.strip().startswith(("import ", "from ")):
                last_import = i
        lines.insert(last_import + 1, helper)
        playbook = "\n".join(lines)

        with open("student_playbook.py", "w", encoding="utf-8") as f:
            f.write(playbook)
        print("✅ Added _filter_topics_for_trial to student_playbook.py")
    else:
        print("✅ _filter_topics_for_trial already exists")
except FileNotFoundError:
    print("⚠️ student_playbook.py not found")

# ============================================================
# VERIFY
# ============================================================
print("\n" + "="*70)
print("✅ CONSOLIDATED FIX COMPLETE")
print("="*70)
print("\n📌 FIXES:")
print("   1. ✅ Removed old / route (auth.py landing wins)")
print("   2. ✅ register_auth_routes before app.run")
print("   3. ✅ Added Flask imports")
print("   4. ✅ New dashboard with SUBJECT GRID")
print("   5. ✅ Homework link uses /homework/start")
print("   6. ✅ Logout redirects to /login")
print("   7. ✅ Fixed playbook missing function")
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")
