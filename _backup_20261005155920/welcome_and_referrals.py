import os, json, sqlite3, urllib.parse
from flask import request, redirect, url_for, render_template_string, make_response, jsonify

def db():
    if os.environ.get("TURSO_DATABASE_URL") and os.environ.get("TURSO_AUTH_TOKEN"):
        try:
            import turso_db
            return turso_db.connect()
        except: pass
    return sqlite3.connect("digital_classroom.db")

def init_referral_tables():
    conn = db()
    try:
        conn.execute("""CREATE TABLE IF NOT EXISTS referral_payouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_student_id INTEGER NOT NULL,
            amount REAL DEFAULT 0.10,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_at TEXT
        )""")
        conn.commit()
    except: pass
    conn.close()

def register_welcome_and_referrals(app):
    init_referral_tables()

    @app.route("/")
    @app.route("/welcome")
    def welcome_page():
        if request.cookies.get("dcr_consent") == "1":
            return redirect("/login")

        tpl = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Welcome to Digital Classroom Rules</title>
  <style>
    :root { --p: #0f766e; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; }
    body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; line-height: 1.6; }
    .wrap { max-width: 760px; margin: 0 auto; }
    .hero { background: linear-gradient(135deg, #0f766e, #064e3b); padding: 32px 24px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4); margin-bottom: 24px; }
    .hero h1 { margin: 0 0 10px; font-size: 2rem; }
    .card { background: var(--card); border-radius: 16px; padding: 24px; margin-bottom: 20px; border: 1px solid #334155; }
    .card h2 { margin: 0 0 12px; font-size: 1.25rem; color: #38bdf8; }
    .badge { background: rgba(15,118,110,0.3); color: #2dd4bf; border: 1px solid #0f766e; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 12px; }
    .legal-box { background: rgba(239,68,68,0.1); border-left: 4px solid #ef4444; padding: 14px 18px; border-radius: 8px; margin: 16px 0; font-size: 0.92rem; color: #fca5a5; }
    .btn-agree { background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 16px 32px; border-radius: 12px; font-size: 1.15rem; font-weight: bold; width: 100%; cursor: pointer; }
    .feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }
    @media (max-width: 600px) { .feature-grid { grid-template-columns: 1fr; } }
    .feature-item { background: rgba(255,255,255,0.03); padding: 12px 14px; border-radius: 10px; font-size: 0.9rem; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="hero">
      <div style="font-size:3rem;margin-bottom:8px">🎓</div>
      <h1>Digital Classroom Rules</h1>
      <p>Zimbabwe's Premier Smart Learning Platform for Primary & Secondary Learners</p>
    </div>

    <div class="card">
      <span class="badge">🚀 Powered by Top IT & Educational Specialists</span>
      <h2>💡 Built for High-Impact Academic Success</h2>
      <p>Digital Classroom Rules provides a structured, syllabus-aligned digital environment delivering interactive lessons, audio-assisted reading, auto-marked assessments, and personalized tutor guidance.</p>
      
      <div class="feature-grid">
        <div class="feature-item">📚 <b>827+ Interactive Lessons</b><br><span style="color:#94a3b8">Maths, Science, English, Shona, Ndebele & Commerce.</span></div>
        <div class="feature-item">🎧 <b>10-Chapter Audio Novels</b><br><span style="color:#94a3b8">Voice Play/Pause read-aloud readers with comprehension quizzes.</span></div>
        <div class="feature-item">📝 <b>Auto-Marked Homework</b><br><span style="color:#94a3b8">Instant feedback with step-by-step solutions and tutor notes.</span></div>
        <div class="feature-item">👪 <b>Parent Read-Aloud Mode</b><br><span style="color:#94a3b8">Structured oversight and weekly progress report cards.</span></div>
      </div>
    </div>

    <div class="card">
      <h2>⚖️ Privacy Policy & Intellectual Property Protection</h2>
      <div class="legal-box">
        <b>🚨 STRICT LEGAL NOTICE ON COPYRIGHT & DUPLICATION:</b><br>
        All lessons, playbooks, novels, multimedia, quizzes, and software algorithms on Digital Classroom Rules are protected under domestic and international intellectual property laws. <b>Any unauthorized duplication, reproduction, digital scraping, screen recording, reverse engineering, or commercial redistribution of platform content without express written authorization will result in immediate legal action and copyright prosecution.</b>
      </div>

      <form action="/consent/agree" method="POST" style="margin-top:20px">
        <button class="btn-agree" type="submit">✅ I Agree & Continue to Classroom →</button>
      </form>
    </div>
    <div style="text-align:center;font-size:0.8rem;color:#64748b;margin-top:20px">Powered by Quick Sync IT 🇿🇼 • © 2026 Smart People Education</div>
  </div>
</body>
</html>"""
        return render_template_string(tpl)

    @app.route("/consent/agree", methods=["POST"])
    def consent_agree():
        resp = make_response(redirect("/login"))
        resp.set_cookie("dcr_consent", "1", max_age=60*60*24*365, httponly=False, samesite="Lax")
        return resp

    @app.route("/founder/login", methods=["GET", "POST"])
    def dedicated_founder_login():
        key = os.environ.get("FOUNDER_KEY", "").strip() or "7c3f5g3b1e6i8d"
        error = None
        if request.method == "POST":
            entered = request.form.get("founder_key", "").strip()
            if entered == key:
                resp = make_response(redirect("/founder/dashboard"))
                resp.set_cookie("fk", key, max_age=60*60*24*30, httponly=True, samesite="Lax")
                return resp
            error = "Invalid Founder Key."

        tpl = """<!doctype html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Founder Access</title>
<style>body{font-family:system-ui;background:#090d16;color:white;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
.box{background:#131d31;padding:32px 24px;border-radius:20px;max-width:380px;width:100%;text-align:center;border:1px solid #22324e}
input{width:100%;padding:14px;border-radius:8px;background:#090d16;color:white;border:1px solid #334b6e;margin:12px 0;box-sizing:border-box;font-size:1.1rem;text-align:center}
button{width:100%;padding:14px;border-radius:8px;background:#0f766e;color:white;border:none;font-weight:bold;cursor:pointer;font-size:1rem}
.err{background:#fee2e2;color:#991b1b;padding:8px;border-radius:6px;margin-bottom:10px}
</style></head><body><div class="box">
<div style="font-size:3rem">🔐</div><h1>Agent & Founder Portal</h1>
{% if error %}<div class="err">{{error}}</div>{% endif %}
<form method="POST"><input type="password" name="founder_key" placeholder="Enter Founder Key..." required autofocus>
<button type="submit">Unlock Dashboard →</button></form></div></body></html>"""
        return render_template_string(tpl, error=error)

    @app.route("/student/<int:sid>/referrals")
    def student_referrals(sid):
        conn = db()
        student = conn.execute("SELECT id, name, student_number FROM students WHERE id=?", (sid,)).fetchone()
        s_name = student["name"] if isinstance(student, dict) else student[1]
        s_num = student["student_number"] if isinstance(student, dict) else student[2]
        
        records = conn.execute("""
            SELECT p.amount, p.status, p.created_at, s.name as friend_name
            FROM referral_payouts p
            JOIN students s ON p.referred_student_id = s.id
            WHERE p.referrer_id=?
            ORDER BY p.created_at DESC
        """, (sid,)).fetchall()
        conn.close()

        total_earned = sum([(r["amount"] if isinstance(r, dict) else r[0]) for r in records])
        pending = sum([(r["amount"] if isinstance(r, dict) else r[0]) for r in records if (r["status"] if isinstance(r, dict) else r[1]) == 'PENDING'])
        paid = sum([(r["amount"] if isinstance(r, dict) else r[0]) for r in records if (r["status"] if isinstance(r, dict) else r[1]) == 'PAID'])

        host = request.host_url.rstrip("/")
        referral_link = f"{host}/register?ref={s_num}"
        wa_text = f"Join me on Digital Classroom Rules! Access 800+ lessons, audio novels, and past exams: {referral_link}"
        wa_url = f"https://wa.me/?text={urllib.parse.quote(wa_text)}"

        tpl = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Referrals</title>
<style>body{font-family:system-ui;background:#f8fafc;padding:16px;max-width:680px;margin:auto}
.header{background:linear-gradient(135deg,#0f766e,#047857);color:white;padding:22px;border-radius:16px}
.card{background:white;padding:20px;border-radius:14px;border:1px solid #e2e8f0;margin:16px 0}
.btn-wa{background:#25d366;color:white;text-decoration:none;padding:12px;border-radius:8px;font-weight:bold;display:block;text-align:center}
</style></head><body>
<div class="header"><h1>🎁 Earn 10¢ per Friend You Invite!</h1><a href="/student/{{sid}}/home" style="color:white;font-weight:bold">← Back to Home</a></div>
<div class="card"><h3>Your Referral Link</h3><div style="background:#f1f5f9;padding:10px;border-radius:8px;word-break:break-all;font-family:monospace">{{referral_link}}</div><br>
<a class="btn-wa" href="{{wa_url}}" target="_blank">📲 Share on WhatsApp (1-Tap)</a>
<p style="background:#fef3c7;padding:10px;border-radius:6px;color:#92400e">🗓️ <b>Friday Payouts:</b> Earn $0.10 for every registered friend. Paid to your EcoCash number every Friday!</p></div>
<div class="card"><h3>Commission: Total ${{"%.2f"|format(total_earned)}} | Pending Friday ${{"%.2f"|format(pending)}}</h3></div></body></html>"""
        return render_template_string(tpl, sid=sid, s_name=s_name, s_num=s_num, referral_link=referral_link,
                                      wa_url=wa_url, total_earned=total_earned, pending=pending, paid=paid, records=records)

    @app.route("/founder/referrals")
    def founder_referral_payouts():
        conn = db()
        pending = conn.execute("""
            SELECT p.referrer_id, s.name, s.student_number, COUNT(p.id) as friend_count, SUM(p.amount) as total_due
            FROM referral_payouts p
            JOIN students s ON p.referrer_id = s.id
            WHERE p.status = 'PENDING'
            GROUP BY p.referrer_id, s.name, s.student_number
        """).fetchall()
        conn.close()

        tpl = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Friday Payouts</title>
<style>body{font-family:system-ui;background:#0f172a;color:white;padding:20px;max-width:800px;margin:auto}
.card{background:#1e293b;padding:20px;border-radius:14px;border:1px solid #334155}
table{width:100%;border-collapse:collapse} th,td{padding:10px;border-bottom:1px solid #334155;text-align:left} th{color:#38bdf8}
.btn-pay{background:#10b981;color:white;border:none;padding:6px 14px;border-radius:6px;font-weight:bold;cursor:pointer}
</style></head><body>
<div style="display:flex;justify-content:space-between;align-items:center"><h1>💰 Friday Referral Payouts</h1><a href="/founder/dashboard" style="color:#38bdf8">← Dashboard</a></div>
<div class="card"><table><thead><tr><th>Student</th><th>DCR #</th><th>Friends</th><th>Total Due</th><th>Action</th></tr></thead>
<tbody>{% for r in pending %}
<tr><td><b>{{r[1]}}</b></td><td>{{r[2]}}</td><td>{{r[3]}}</td><td style="color:#10b981"><b>${{"%.2f"|format(r[4])}}</b></td>
<td><form action="/founder/referrals/{{r[0]}}/pay" method="POST" style="margin:0"><button class="btn-pay" type="submit">✅ Mark Paid</button></form></td></tr>
{% else %}<tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8">No pending commissions due this Friday.</td></tr>{% endfor %}</tbody></table></div></body></html>"""
        return render_template_string(tpl, pending=pending)

    @app.route("/founder/referrals/<int:referrer_id>/pay", methods=["POST"])
    def founder_mark_referrals_paid(referrer_id):
        conn = db()
        conn.execute("UPDATE referral_payouts SET status='PAID', paid_at=datetime('now') WHERE referrer_id=? AND status='PENDING'", (referrer_id,))
        conn.commit()
        conn.close()
        return redirect("/founder/referrals")
