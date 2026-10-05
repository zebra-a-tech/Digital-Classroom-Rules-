"""Rebuild dashboard with Free Trial, Paid Lesson, pause/play, subjects"""

import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_full_dashboard.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# ============================================================
# Find and replace the home route
# ============================================================
home_pattern = re.compile(
    r'@app\.route\("/student/<int:sid>/home"\)\s*\n\s*def home\(sid\):.*?(?=\n@app\.route|\Z)',
    re.DOTALL
)

NEW_HOME = '''@app.route("/student/<int:sid>/home")
def home(sid):
    """Complete student dashboard with free trial, paid lessons, subjects."""
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

    # Subject icons mapping
    subject_icons = {
        "Maths": "🔢",
        "English": "📖",
        "Science": "🔬",
        "Social Studies": "🌍",
        "Geography": "🗺️",
        "History": "📜",
        "Biology": "🧬",
        "Chemistry": "⚗️",
        "Physics": "⚛️",
        "Economics": "💹",
        "Accounting": "🧮",
    }

    subject_list = SUBJECTS if isinstance(SUBJECTS, list) else []

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
.brand-bar{display:flex;align-items:center;justify-content:space-between;padding:12px 0 20px;gap:12px}
.brand-left{display:flex;align-items:center;gap:12px;flex:1}
.brand-logo{width:44px;height:44px;border-radius:50%;background:#0b2a3a;display:flex;align-items:center;justify-content:center;font-size:22px;flex-shrink:0;box-shadow:0 4px 12px rgba(11,42,58,0.2)}
.brand-text{font-size:14px;font-weight:800;color:#0b2a3a;letter-spacing:-0.3px;line-height:1.2}
.brand-text span{display:block;font-size:9px;font-weight:500;color:#5a6b7a;letter-spacing:1px;text-transform:uppercase;margin-top:2px}
.logout-btn{background:#dc2626;color:white;padding:10px 16px;border-radius:20px;text-decoration:none;font-size:12px;font-weight:700;box-shadow:0 4px 12px rgba(220,38,38,0.3);white-space:nowrap}
.logout-btn:hover{background:#b91c1c}
.hero{background:linear-gradient(135deg,#0b2a3a 0%,#1a4a5e 100%);color:white;padding:28px 24px;border-radius:24px;margin-bottom:20px;position:relative;overflow:hidden}
.hero::after{content:"🇿🇼";position:absolute;font-size:8rem;opacity:0.05;right:-20px;bottom:-30px;transform:rotate(-15deg)}
.hero h1{font-size:24px;font-weight:800;letter-spacing:-0.5px;margin-bottom:4px;position:relative;z-index:1}
.hero p{opacity:0.85;font-size:13px;position:relative;z-index:1}
.tutor-badge{display:inline-flex;align-items:center;gap:8px;background:rgba(255,255,255,0.12);padding:8px 16px;border-radius:20px;font-size:12px;margin-top:12px;backdrop-filter:blur(4px);position:relative;z-index:1}
.section-title{font-size:12px;font-weight:700;color:#5a6b7a;text-transform:uppercase;letter-spacing:1px;margin:24px 4px 12px;display:flex;align-items:center;gap:8px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.stat-card{background:white;padding:18px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);text-align:center}
.stat-icon{font-size:28px;margin-bottom:4px}
.stat-value{font-size:24px;font-weight:800;color:#0b2a3a;line-height:1}
.stat-label{font-size:10px;color:#5a6b7a;text-transform:uppercase;letter-spacing:0.5px;font-weight:600;margin-top:6px}
.action-card{background:white;padding:18px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);margin-bottom:10px;display:flex;align-items:center;gap:16px;text-decoration:none;color:inherit;transition:all 0.2s;border:2px solid transparent}
.action-card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(11,42,58,0.1);border-color:#009b4d}
.action-icon{font-size:32px;flex-shrink:0;width:44px;text-align:center}
.action-content{flex:1}
.action-title{font-size:15px;font-weight:700;color:#0b2a3a;margin-bottom:2px}
.action-desc{font-size:12px;color:#5a6b7a}
.action-arrow{color:#94a3b8;font-size:22px;font-weight:300}

/* Subject cards - larger, prettier */
.subject-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:12px}
.subject-card{background:linear-gradient(135deg,#ffffff 0%,#f8fafb 100%);padding:20px 14px;border-radius:18px;box-shadow:0 4px 16px rgba(11,42,58,0.06);text-decoration:none;color:#0b2a3a;text-align:center;transition:all 0.25s;border:2px solid #e5eaf0;position:relative;overflow:hidden}
.subject-card:hover{transform:translateY(-4px);box-shadow:0 12px 28px rgba(0,155,77,0.15);border-color:#009b4d;background:linear-gradient(135deg,#f0fdf4 0%,#ffffff 100%)}
.subject-icon{font-size:38px;margin-bottom:8px;display:block}
.subject-name{font-size:14px;font-weight:700;color:#0b2a3a;line-height:1.2}

/* Free trial + paid buttons */
.trial-box{background:linear-gradient(135deg,#009b4d 0%,#00803e 100%);border-radius:20px;padding:22px;color:white;margin-bottom:12px;box-shadow:0 8px 24px rgba(0,155,77,0.3);position:relative;overflow:hidden}
.trial-box::after{content:"🎁";position:absolute;font-size:6rem;opacity:0.15;right:-10px;bottom:-20px;transform:rotate(-15deg)}
.trial-box .label{font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:0.9;position:relative;z-index:1}
.trial-box .title{font-size:22px;font-weight:800;margin:4px 0 8px;position:relative;z-index:1}
.trial-box .desc{font-size:13px;opacity:0.9;margin-bottom:14px;position:relative;z-index:1}
.trial-btn{display:block;text-align:center;background:white;color:#009b4d;padding:14px;border-radius:12px;font-weight:800;font-size:15px;text-decoration:none;position:relative;z-index:1;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
.trial-btn:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(0,0,0,0.15)}

.paid-box{background:linear-gradient(135deg,#ff6b35 0%,#e55a25 100%);border-radius:20px;padding:22px;color:white;margin-bottom:12px;box-shadow:0 8px 24px rgba(255,107,53,0.3);position:relative;overflow:hidden}
.paid-box::after{content:"💰";position:absolute;font-size:6rem;opacity:0.15;right:-10px;bottom:-20px;transform:rotate(-15deg)}
.paid-box .label{font-size:12px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:0.9;position:relative;z-index:1}
.paid-box .title{font-size:22px;font-weight:800;margin:4px 0 8px;position:relative;z-index:1}
.paid-box .desc{font-size:13px;opacity:0.9;margin-bottom:14px;position:relative;z-index:1}
.paid-btn{display:block;text-align:center;background:white;color:#ff6b35;padding:14px;border-radius:12px;font-weight:800;font-size:15px;text-decoration:none;position:relative;z-index:1;box-shadow:0 4px 12px rgba(0,0,0,0.1)}
.paid-btn:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(0,0,0,0.15)}

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
  <div class="brand-left">
    <div class="brand-logo">🎓</div>
    <div class="brand-text">Digital Classroom Rules<span>Smart People Education</span></div>
  </div>
  <a href="/logout" class="logout-btn">🚪 Logout</a>
</div>

<div class="hero">
  <h1>{{greeting}}, {{first}}! 👋</h1>
  <p>Welcome back to learning</p>
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
    <div class="stat-label">Lessons Done</div>
  </div>
</div>

<div class="section-title">🎁 Try It Free</div>
<div class="trial-box">
  <div class="label">Free Sample</div>
  <div class="title">30-Minute Trial Lesson</div>
  <div class="desc">Experience how our lessons work — completely free, no payment needed.</div>
  <a href="/student/{{sid}}/trial" class="trial-btn">▶️ Start Free Trial</a>
</div>

<div class="section-title">💰 Unlock Full Lesson</div>
<div class="paid-box">
  <div class="label">Paid Session</div>
  <div class="title">$1 — 1-Hour Lesson</div>
  <div class="desc">Full 60-minute lesson with pause, resume &amp; complete tutor support.</div>
  <a href="/student/{{sid}}/paid" class="paid-btn">🔓 Start Paid Lesson</a>
</div>

<div class="section-title">📖 Choose a Subject</div>
<div class="subject-grid">
{% for subj in subjects %}
  <a href="/student/{{sid}}/learn?subject={{subj}}" class="subject-card">
    <span class="subject-icon">{{subject_icons.get(subj, "📘")}}</span>
    <span class="subject-name">{{subj}}</span>
  </a>
{% endfor %}
</div>

<div class="section-title">⚡ Quick Access</div>
<a href="/student/{{sid}}/centre" class="action-card">
  <div class="action-icon">🏫</div>
  <div class="action-content">
    <div class="action-title">Learning Centre</div>
    <div class="action-desc">All subjects &amp; topics</div>
  </div>
  <div class="action-arrow">›</div>
</a>
<a href="/student/{{sid}}/homework/start" class="action-card">
  <div class="action-icon">✍️</div>
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
        subjects=subject_list,
        subject_icons=subject_icons
    )


'''

if home_pattern.search(content):
    content = home_pattern.sub(NEW_HOME, content, count=1)
    print("✅ Home route replaced with COMPLETE dashboard")
else:
    print("❌ Could not find home route")
    exit(1)

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*70)
print("✅ COMPLETE DASHBOARD REBUILT")
print("="*70)
print("\n📌 WHAT'S BACK:")
print("   ✅ Free Trial button (30-min)")
print("   ✅ Paid Lesson button ($1 - 1-hour)")
print("   ✅ Beautiful subject cards (larger, prettier)")
print("   ✅ Logout button in correct position (top-right)")
print("   ✅ Modern Zimbabwe-themed design")
print("   ✅ Bottom navigation")
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")
