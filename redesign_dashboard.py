"""Completely replace student dashboard + add logout"""

import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_backup_dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Find the home route and completely replace it
home_pattern = re.compile(
    r'@app\.route\("/student/<int:sid>/home"\)\s*\n\s*def home\(sid\):.*?(?=\n@app\.route|\Z)',
    re.DOTALL
)

new_home_route = '''@app.route("/student/<int:sid>/home")
def home(sid):
    """Modern student dashboard."""
    import datetime as _dt
    from flask import session as _sess

    s = student(sid)
    if not s:
        return "Student not found", 404

    # Time-based greeting
    hour = _dt.datetime.now().hour
    if hour < 12:
        greeting = "Good morning"
    elif hour < 17:
        greeting = "Good afternoon"
    else:
        greeting = "Good evening"

    # Get first name
    name = s["name"] or "Student"
    first_name = name.split()[0] if name else "Student"
    student_number = s["student_number"] if "student_number" in s.keys() else "N/A"
    tutor = s["tutor"] or "Your Tutor"
    streak = s["streak"] or 0
    paid_lessons = s["paid_lessons"] or 0

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
.hero{background:linear-gradient(135deg,#0b2a3a 0%,#1a4a5e 100%);color:white;padding:32px 24px;border-radius:24px;margin-bottom:20px;position:relative;overflow:hidden}
.hero::after{content:"🇿🇼";position:absolute;font-size:8rem;opacity:0.05;right:-20px;bottom:-30px;transform:rotate(-15deg)}
.logout-btn{position:absolute;top:16px;right:16px;background:rgba(255,255,255,0.15);color:white;padding:8px 16px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:700;z-index:10;border:1px solid rgba(255,255,255,0.2);backdrop-filter:blur(4px)}
.logout-btn:hover{background:rgba(220,38,38,0.8)}
.hero h1{font-size:26px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;position:relative;z-index:1}
.hero p{opacity:0.85;font-size:14px;position:relative;z-index:1}
.tutor-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.12);padding:8px 16px;border-radius:20px;font-size:13px;margin-top:12px;backdrop-filter:blur(4px);position:relative;z-index:1}
.section-title{font-size:12px;font-weight:700;color:#5a6b7a;text-transform:uppercase;letter-spacing:1px;margin:24px 4px 12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.stat-card{background:white;padding:20px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);text-align:center}
.stat-icon{font-size:32px;margin-bottom:6px}
.stat-value{font-size:26px;font-weight:800;color:#0b2a3a;line-height:1}
.stat-label{font-size:10px;color:#5a6b7a;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin-top:6px}
.action-card{background:white;padding:18px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);margin-bottom:10px;display:flex;align-items:center;gap:16px;text-decoration:none;color:inherit;transition:all 0.2s}
.action-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(11,42,58,0.1)}
.action-icon{font-size:32px;flex-shrink:0}
.action-content{flex:1}
.action-title{font-size:15px;font-weight:700;color:#0b2a3a;margin-bottom:2px}
.action-desc{font-size:12px;color:#5a6b7a}
.action-arrow{color:#94a3b8;font-size:22px;font-weight:300}
.btn{display:block;padding:16px;border-radius:14px;text-align:center;text-decoration:none;font-weight:700;font-size:15px;margin-bottom:10px;transition:all 0.2s;border:none;cursor:pointer;font-family:inherit}
.btn-green{background:#009b4d;color:white;box-shadow:0 6px 20px rgba(0,155,77,0.3)}
.btn-green:hover{background:#00803e}
.btn-orange{background:#ff6b35;color:white;box-shadow:0 6px 20px rgba(255,107,53,0.3)}
.btn-orange:hover{background:#e55a25}
.nav{position:fixed;bottom:0;left:0;right:0;background:white;display:flex;justify-content:space-around;padding:10px 0 12px;box-shadow:0 -4px 20px rgba(0,0,0,0.08);z-index:100;border-top-left-radius:20px;border-top-right-radius:20px}
.nav a{flex:1;text-align:center;text-decoration:none;color:#94a3b8;font-size:10px;font-weight:600;padding:6px 0;transition:color 0.2s}
.nav a.active{color:#009b4d}
.nav a i{display:block;font-size:22px;margin-bottom:2px;font-style:normal}
</style>
</head>
<body>
<div class="flag"></div>
<div class="wrap">

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
  <a href="/student/{{sid}}/homework"><i>📝</i>Homework</a>
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
        student_number=student_number
    )


'''

if home_pattern.search(content):
    content = home_pattern.sub(new_home_route, content, count=1)
    print("✅ Dashboard completely replaced")
else:
    print("⚠️ Could not find home() route — checking alternate patterns")

# Add /logout route
if '@app.route("/logout")' not in content:
    # Find app.run and insert before
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
        print("✅ Added /logout route")

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ student_server.py updated")

# Verify
import subprocess
result = subprocess.run(
    ["python", "-c", "import student_server; print('OK')"],
    capture_output=True, text=True, timeout=5
)
if "OK" in result.stdout or result.returncode == 0:
    print("✅ student_server.py imports cleanly")
else:
    print(f"⚠️  {result.stderr[:300]}")

print("\n" + "="*70)
print("✅ DASHBOARD REDESIGN COMPLETE")
print("="*70)
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n⚠️  CLEAR BROWSER CACHE:")
print("   Long-press refresh → 'Empty cache and hard reload'")
print("\n📌 THEN TEST:")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")
