"""FINAL dashboard rebuild - compact, beautiful, with free trial"""

import re

SERVER = "student_server.py"

with open(SERVER, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_final_rebuild.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# ============================================================
# Replace home route with COMPACT modern design
# ============================================================
home_pattern = re.compile(
    r'@app\.route\("/student/<int:sid>/home"\)\s*\n\s*def home\(sid\):.*?(?=\n@app\.route|\Z)',
    re.DOTALL
)

NEW_HOME = '''@app.route("/student/<int:sid>/home")
def home(sid):
    """Compact, modern student dashboard."""
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

    subject_icons = {
        "Maths": "🔢", "English": "📖", "Science": "🔬",
        "Social Studies": "🌍", "Geography": "🗺️", "History": "📜",
        "Biology": "🧬", "Chemistry": "⚗️", "Physics": "⚛️",
        "Economics": "💹", "Accounting": "🧮",
    }

    subject_list = SUBJECTS if isinstance(SUBJECTS, list) else []

    # Check if student has used free trial
    trial_used = safe_get("free_trial_used", 0)

    html = """<!doctype html>
<html><head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Home — Digital Classroom Rules</title>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:'Poppins',sans-serif;background:#f5f7fa;color:#1e2b3a;line-height:1.5;padding-bottom:80px;-webkit-font-smoothing:antialiased}
.flag{height:6px;background:linear-gradient(90deg,#009b4d 0%,#009b4d 25%,#ffc200 25%,#ffc200 50%,#de2010 50%,#de2010 75%,#1e2b3a 75%,#1e2b3a 100%)}
.wrap{max-width:520px;margin:0 auto;padding:16px}

/* Brand header - compact */
.brand-bar{display:flex;align-items:center;justify-content:space-between;padding:10px 0 14px;gap:10px}
.brand-left{display:flex;align-items:center;gap:10px;min-width:0;flex:1}
.brand-logo{width:38px;height:38px;border-radius:50%;background:#0b2a3a;display:flex;align-items:center;justify-content:center;font-size:19px;flex-shrink:0}
.brand-text{font-size:13px;font-weight:800;color:#0b2a3a;line-height:1.15;min-width:0;overflow:hidden;text-overflow:ellipsis}
.brand-text span{display:block;font-size:9px;font-weight:500;color:#5a6b7a;letter-spacing:0.8px;text-transform:uppercase;margin-top:1px}
.logout-btn{background:#dc2626;color:white;padding:8px 14px;border-radius:18px;text-decoration:none;font-size:11px;font-weight:700;white-space:nowrap;flex-shrink:0}

/* Hero */
.hero{background:linear-gradient(135deg,#0b2a3a 0%,#1a4a5e 100%);color:white;padding:22px 20px;border-radius:20px;margin-bottom:16px;position:relative;overflow:hidden}
.hero::after{content:"🇿🇼";position:absolute;font-size:6rem;opacity:0.06;right:-10px;bottom:-20px;transform:rotate(-15deg)}
.hero h1{font-size:20px;font-weight:800;letter-spacing:-0.4px;margin-bottom:2px;position:relative;z-index:1}
.hero p{opacity:0.85;font-size:12px;position:relative;z-index:1}
.tutor-badge{display:inline-flex;align-items:center;gap:6px;background:rgba(255,255,255,0.12);padding:6px 12px;border-radius:16px;font-size:11px;margin-top:10px;position:relative;z-index:1}

/* Section title */
.section-title{font-size:11px;font-weight:700;color:#5a6b7a;text-transform:uppercase;letter-spacing:0.8px;margin:18px 2px 10px;display:flex;align-items:center;gap:6px}

/* Stats row - compact */
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px}
.stat-card{background:white;padding:14px 12px;border-radius:14px;text-align:center;border:1px solid #eef2f7}
.stat-icon{font-size:20px}
.stat-value{font-size:20px;font-weight:800;color:#0b2a3a;line-height:1;margin-top:2px}
.stat-label{font-size:9px;color:#5a6b7a;text-transform:uppercase;letter-spacing:0.4px;font-weight:600;margin-top:4px}

/* Trial box - compact */
.trial-card{background:linear-gradient(135deg,#009b4d 0%,#007a3d 100%);border-radius:18px;padding:18px 20px;color:white;margin-bottom:10px;position:relative;overflow:hidden;box-shadow:0 6px 20px rgba(0,155,77,0.25)}
.trial-card::after{content:"🎁";position:absolute;font-size:5rem;opacity:0.15;right:-8px;bottom:-16px}
.trial-card .label{font-size:10px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:0.9;position:relative;z-index:1}
.trial-card .title{font-size:18px;font-weight:800;margin:2px 0 4px;position:relative;z-index:1}
.trial-card .desc{font-size:11px;opacity:0.9;margin-bottom:12px;position:relative;z-index:1}
.trial-btn{display:block;text-align:center;background:white;color:#009b4d;padding:12px;border-radius:10px;font-weight:800;font-size:14px;text-decoration:none;position:relative;z-index:1}

/* Paid box - compact */
.paid-card{background:linear-gradient(135deg,#ff6b35 0%,#e55a25 100%);border-radius:18px;padding:18px 20px;color:white;margin-bottom:10px;position:relative;overflow:hidden;box-shadow:0 6px 20px rgba(255,107,53,0.25)}
.paid-card::after{content:"💰";position:absolute;font-size:5rem;opacity:0.15;right:-8px;bottom:-16px}
.paid-card .label{font-size:10px;text-transform:uppercase;letter-spacing:1px;font-weight:600;opacity:0.9;position:relative;z-index:1}
.paid-card .title{font-size:18px;font-weight:800;margin:2px 0 4px;position:relative;z-index:1}
.paid-card .desc{font-size:11px;opacity:0.9;margin-bottom:12px;position:relative;z-index:1}
.paid-btn{display:block;text-align:center;background:white;color:#ff6b35;padding:12px;border-radius:10px;font-weight:800;font-size:14px;text-decoration:none;position:relative;z-index:1}

/* Subject grid - COMPACT */
.subject-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:8px}
.subject-card{background:white;padding:14px 10px;border-radius:14px;text-decoration:none;color:#0b2a3a;text-align:center;border:1.5px solid #eef2f7;transition:all 0.2s;display:flex;align-items:center;gap:10px}
.subject-card:hover{border-color:#009b4d;background:#f0fdf4}
.subject-icon{font-size:22px;flex-shrink:0}
.subject-name{font-size:12px;font-weight:700;color:#0b2a3a;text-align:left;line-height:1.2;flex:1}

/* Quick actions - COMPACT */
.action-card{background:white;padding:14px;border-radius:14px;margin-bottom:8px;display:flex;align-items:center;gap:12px;text-decoration:none;color:inherit;border:1.5px solid #eef2f7;transition:all 0.2s}
.action-card:hover{border-color:#009b4d;background:#f0fdf4}
.action-icon{font-size:22px;flex-shrink:0;width:32px;text-align:center}
.action-content{flex:1;min-width:0}
.action-title{font-size:13px;font-weight:700;color:#0b2a3a;line-height:1.2}
.action-desc{font-size:10px;color:#5a6b7a;margin-top:1px}
.action-arrow{color:#cbd5e1;font-size:18px}

/* Bottom nav */
.nav{position:fixed;bottom:0;left:0;right:0;background:white;display:flex;justify-content:space-around;padding:8px 0 10px;box-shadow:0 -2px 12px rgba(0,0,0,0.06);z-index:100;border-top-left-radius:16px;border-top-right-radius:16px}
.nav a{flex:1;text-align:center;text-decoration:none;color:#94a3b8;font-size:9px;font-weight:600;padding:4px 0}
.nav a.active{color:#009b4d}
.nav a i{display:block;font-size:20px;margin-bottom:2px;font-style:normal}
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
  <p>Ready to learn something new today?</p>
  <div class="tutor-badge">🧑‍🏫 {{tutor}}</div>
</div>

<div class="section-title">📊 Progress</div>
<div class="grid2">
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

{% if not trial_used %}
<div class="section-title">🎁 Free Trial Available</div>
<div class="trial-card">
  <div class="label">Free Access</div>
  <div class="title">30-Minute Trial</div>
  <div class="desc">Try ALL subjects free for 30 minutes. No payment needed.</div>
  <a href="/student/{{sid}}/trial" class="trial-btn">▶️ Start Free Trial</a>
</div>
{% else %}
<div class="section-title">🎁 Trial Used</div>
<div class="trial-card" style="background:linear-gradient(135deg,#64748b 0%,#475569 100%)">
  <div class="label">Free Trial</div>
  <div class="title">Already Used</div>
  <div class="desc">You've used your free trial. Unlock full lessons for $1.</div>
  <a href="/student/{{sid}}/paid" class="trial-btn" style="color:#64748b">💰 Unlock Full Access</a>
</div>
{% endif %}

<div class="section-title">💰 Full Lesson</div>
<div class="paid-card">
  <div class="label">Paid Session</div>
  <div class="title">$1 — 1-Hour Lesson</div>
  <div class="desc">Full 60-min lesson with pause &amp; resume.</div>
  <a href="/student/{{sid}}/paid" class="paid-btn">🔓 Start Lesson</a>
</div>

<div class="section-title">📖 Subjects</div>
<div class="subject-grid">
{% for subj in subjects %}
  <a href="/student/{{sid}}/learn?subject={{subj}}" class="subject-card">
    <span class="subject-icon">{{subject_icons.get(subj, "📘")}}</span>
    <span class="subject-name">{{subj}}</span>
  </a>
{% endfor %}
</div>

<div class="section-title">⚡ More</div>
<a href="/student/{{sid}}/centre" class="action-card">
  <div class="action-icon">🏫</div>
  <div class="action-content">
    <div class="action-title">Learning Centre</div>
    <div class="action-desc">All subjects and topics</div>
  </div>
  <div class="action-arrow">›</div>
</a>
<a href="/student/{{sid}}/homework/start" class="action-card">
  <div class="action-icon">✍️</div>
  <div class="action-content">
    <div class="action-title">Weekly Assignments</div>
    <div class="action-desc">Practice questions</div>
  </div>
  <div class="action-arrow">›</div>
</a>
<a href="/student/{{sid}}/tutor" class="action-card">
  <div class="action-icon">🧑‍🏫</div>
  <div class="action-content">
    <div class="action-title">Ask Tutor</div>
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
        subject_icons=subject_icons,
        trial_used=trial_used
    )


'''

if home_pattern.search(content):
    content = home_pattern.sub(NEW_HOME, content, count=1)
    print("✅ Home route replaced with COMPACT design")
else:
    print("❌ Could not find home route")
    exit(1)

with open(SERVER, "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*70)
print("✅ FINAL DASHBOARD REBUILT")
print("="*70)
print("\n📌 WHAT'S FIXED:")
print("   ✅ Compact stats (no giant white space)")
print("   ✅ Free Trial box (only if not used)")
print("   ✅ Paid Lesson box ($1 - 1 hour)")
print("   ✅ Compact subject cards with icons")
print("   ✅ Compact Quick Access cards")
print("   ✅ Logout button correctly positioned")
print("   ✅ All elements properly sized")
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/student/1/home")
print("="*70 + "\n")
