import os, json, sqlite3, urllib.parse
from flask import request, redirect, url_for, render_template_string, make_response, jsonify

def db():
    if os.environ.get("TURSO_DATABASE_URL") and os.environ.get("TURSO_AUTH_TOKEN"):
        try:
            import turso_db
            return turso_db.connect()
        except Exception:
            pass
    return sqlite3.connect("digital_classroom.db")

def init_referral_tables():
    conn = db()
    queries = [
        """CREATE TABLE IF NOT EXISTS referral_payouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            referrer_id INTEGER NOT NULL,
            referred_student_id INTEGER NOT NULL,
            amount REAL DEFAULT 0.10,
            status TEXT DEFAULT 'PENDING',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            paid_at TEXT
        )"""
    ]
    for q in queries:
        try:
            conn.execute(q)
            conn.commit()
        except Exception:
            pass
    conn.close()

def register_welcome_and_referrals(app):
    init_referral_tables()

    # ========================================================
    # 1. WELCOME & LEGAL CONSENT LANDING PAGE
    # ========================================================
    @app.route("/welcome")
    @app.route("/")
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
    :root { --p: #0f766e; --p-dark: #115e59; --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --gold: #f59e0b; }
    body { font-family: system-ui, -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; line-height: 1.6; }
    .wrap { max-width: 760px; margin: 0 auto; }
    .hero { background: linear-gradient(135deg, #0f766e, #064e3b); padding: 32px 24px; border-radius: 20px; text-align: center; box-shadow: 0 10px 30px rgba(0,0,0,0.4); margin-bottom: 24px; border: 1px solid rgba(255,255,255,0.1); }
    .hero h1 { margin: 0 0 10px; font-size: 2rem; }
    .hero p { margin: 0; font-size: 1.05rem; opacity: 0.95; }
    .card { background: var(--card); border-radius: 16px; padding: 24px; margin-bottom: 20px; border: 1px solid #334155; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
    .card h2 { margin: 0 0 12px; font-size: 1.25rem; color: #38bdf8; display: flex; align-items: center; gap: 8px; }
    .badge { background: rgba(15,118,110,0.3); color: #2dd4bf; border: 1px solid #0f766e; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: bold; display: inline-block; margin-bottom: 12px; }
    .legal-box { background: rgba(239,68,68,0.1); border-left: 4px solid #ef4444; padding: 14px 18px; border-radius: 8px; margin: 16px 0; font-size: 0.92rem; color: #fca5a5; }
    .btn-agree { background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 16px 32px; border-radius: 12px; font-size: 1.15rem; font-weight: bold; width: 100%; cursor: pointer; box-shadow: 0 4px 15px rgba(16,185,129,0.4); transition: transform 0.1s; }
    .btn-agree:active { transform: scale(0.98); }
    .feature-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin: 16px 0; }
    @media (max-width: 600px) { .feature-grid { grid-template-columns: 1fr; } }
    .feature-item { background: rgba(255,255,255,0.03); padding: 12px 14px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.06); font-size: 0.9rem; }
    .footer-note { text-align: center; font-size: 0.82rem; color: #64748b; margin-top: 24px; }
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
      <p>Digital Classroom Rules provides a structured, syllabus-aligned digital environment built by experienced educators and IT software engineers. We deliver interactive lessons, audio-assisted reading, auto-marked assessments, and personalized tutor guidance.</p>
      
      <div class="feature-grid">
        <div class="feature-item">📚 <b>827+ Interactive Lessons</b><br><span style="color:#94a3b8">Covering Maths, Science, English, Shona, Ndebele & Commerce.</span></div>
        <div class="feature-item">🎧 <b>10-Chapter Audio Novels</b><br><span style="color:#94a3b8">Voice Play/Pause read-aloud readers with comprehension quizzes.</span></div>
        <div class="feature-item">📝 <b>Auto-Marked Homework</b><br><span style="color:#94a3b8">Instant feedback with step-by-step solutions and tutor notes.</span></div>
        <div class="feature-item">👪 <b>Parent Read-Aloud Mode</b><br><span style="color:#94a3b8">Structured oversight and weekly progress report cards.</span></div>
      </div>
    </div>

    <div class="card">
      <h2>⚖️ Privacy Policy & Intellectual Property Protection</h2>
      <p>We are dedicated to safeguarding student privacy. All academic records, study hours, and assessment results are securely stored and encrypted.</p>
      
      <div class="legal-box">
        <b>🚨 STRICT LEGAL NOTICE ON COPYRIGHT & DUPLICATION:</b><br>
        All lessons, playbooks, novels, multimedia, quizzes, and software algorithms on Digital Classroom Rules are protected under domestic and international intellectual property laws. <b>Any unauthorized duplication, reproduction, digital scraping, screen recording, reverse engineering, or commercial redistribution of platform content without express written authorization will result in immediate legal action and copyright prosecution.</b>
      </div>

      <p style="font-size:0.9rem;color:#94a3b8">By clicking "I Agree & Enter", you confirm that you accept our Terms of Service, consent to our Privacy Policy, and agree to uphold all platform academic integrity rules.</p>
      
      <form action="/consent/agree" method="POST" style="margin-top:20px">
        <button class="btn-agree" type="submit">✅ I Agree & Continue to Classroom →</button>
      </form>
    </div>

    <div class="footer-note">
      Powered by Quick Sync IT 🇿🇼 • © 2026 Smart People Education. All rights reserved.
    </div>
  </div>
</body>
</html>"""
        return render_template_string(tpl)

    @app.route("/consent/agree", methods=["POST"])
    def consent_agree():
        # Set 1-year consent cookie
        resp = make_response(redirect("/login"))
        resp.set_cookie("dcr_consent", "1", max_age=60*60*24*365, httponly=False, samesite="Lax")
        return resp

    # Root route handler: Check consent & login state
    @app.route("/gate")
    def entry_gate():
        has_consent = request.cookies.get("dcr_consent") == "1"
        if not has_consent:
            return redirect("/welcome")
        return redirect("/login")

    # ========================================================
    # 2. DEDICATED FOUNDER/AGENT LOGIN SCREEN (KEY ONLY)
    # ========================================================
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
            error = "Invalid Founder Key. Please enter the authorized key."

        tpl = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Founder & Agent Portal</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #090d16; color: #f8fafc; display: flex; align-items: center; justify-content: center; min-height: 100vh; margin: 0; padding: 16px; box-sizing: border-box; }
    .box { background: #131d31; border: 1px solid #22324e; padding: 32px 24px; border-radius: 20px; max-width: 400px; width: 100%; box-shadow: 0 12px 40px rgba(0,0,0,0.6); text-align: center; }
    .icon { font-size: 3rem; margin-bottom: 12px; }
    h1 { margin: 0 0 6px; font-size: 1.6rem; color: #f8fafc; }
    p { color: #94a3b8; font-size: 0.9rem; margin: 0 0 20px; }
    input { width: 100%; padding: 14px 16px; border-radius: 10px; border: 1px solid #334b6e; background: #090d16; color: white; font-size: 1.1rem; box-sizing: border-box; margin-bottom: 16px; text-align: center; letter-spacing: 2px; }
    input:focus { outline: none; border-color: #0f766e; }
    button { width: 100%; padding: 14px; border-radius: 10px; background: #0f766e; color: white; border: none; font-size: 1rem; font-weight: bold; cursor: pointer; transition: background 0.2s; }
    button:hover { background: #115e59; }
    .err { background: #fee2e2; color: #991b1b; padding: 10px; border-radius: 8px; font-size: 0.88rem; margin-bottom: 14px; font-weight: 500; }
    .features-list { text-align: left; background: rgba(0,0,0,0.25); border-radius: 10px; padding: 14px; margin-top: 20px; font-size: 0.85rem; color: #94a3b8; }
    .features-list div { margin: 6px 0; }
  </style>
</head>
<body>
  <div class="box">
    <div class="icon">🔐</div>
    <h1>Agent & Founder Portal</h1>
    <p>Enter your secret key to manage payment approvals and operations.</p>
    {% if error %}<div class="err">⚠️ {{error}}</div>{% endif %}
    <form method="POST">
      <input type="password" name="founder_key" placeholder="Enter Founder Key..." required autofocus>
      <button type="submit">Unlock Dashboard →</button>
    </form>
    <div class="features-list">
      <div>💳 <b>$1 EcoCash Approvals:</b> One-tap unlock</div>
      <div>🎁 <b>Friday Referral Payouts:</b> Settle 10¢ commissions</div>
      <div>📝 <b>Assignment Marking:</b> Review homework</div>
    </div>
  </div>
</body>
</html>"""
        return render_template_string(tpl, error=error)

    # ========================================================
    # 3. STUDENT REFERRAL & COMMISSION HUB ($0.10 / Friday)
    # ========================================================
    @app.route("/student/<int:sid>/referrals")
    def student_referrals(sid):
        conn = db()
        student = conn.execute("SELECT id, name, student_number FROM students WHERE id=?", (sid,)).fetchone()
        s_name = student["name"] if isinstance(student, dict) else student[1]
        s_num = student["student_number"] if isinstance(student, dict) else student[2]
        
        # Payouts calculation
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

        tpl = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>🎁 Referral Rewards & Friday Payouts</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #f8fafc; color: #1e293b; margin: 0; padding: 16px; }
    .wrap { max-width: 680px; margin: auto; }
    .header { background: linear-gradient(135deg, #0f766e, #047857); color: white; padding: 22px; border-radius: 16px; margin-bottom: 16px; }
    .card { background: white; border-radius: 14px; padding: 20px; border: 1px solid #e2e8f0; margin-bottom: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.04); }
    .stat-row { display: flex; gap: 10px; margin: 16px 0; }
    .stat-box { flex: 1; background: #f0fdfa; border: 1px solid #ccfbf1; padding: 14px; border-radius: 10px; text-align: center; }
    .stat-num { font-size: 1.6rem; font-weight: bold; color: #0f766e; }
    .stat-lbl { font-size: 0.75rem; color: #64748b; font-weight: bold; }
    .link-box { background: #f1f5f9; padding: 12px; border-radius: 8px; border: 1px dashed #cbd5e1; word-break: break-all; font-family: monospace; font-size: 0.9rem; margin: 10px 0; }
    .btn-wa { background: #25d366; color: white; text-decoration: none; padding: 12px 18px; border-radius: 8px; font-weight: bold; display: block; text-align: center; margin-top: 8px; font-size: 1rem; }
    .rule-note { background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; border-radius: 6px; font-size: 0.88rem; color: #92400e; margin: 12px 0; }
    table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.88rem; }
    th, td { padding: 8px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }
    th { background: #f8fafc; color: #475569; }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="header">
      <h1 style="margin:0 0 6px;font-size:1.5rem">🎁 Earn 10¢ for Every Friend You Invite!</h1>
      <p style="margin:0;font-size:0.95rem;opacity:0.9">Share the platform with classmates. All commissions paid via EcoCash every Friday.</p>
      <div style="margin-top:10px">
        <a href="/student/{{sid}}/home" style="color:white;font-weight:bold;font-size:0.85rem">← Back to Home</a>
      </div>
    </div>

    <div class="card">
      <h3 style="margin:0 0 8px">🔗 Your Personal Referral Link</h3>
      <div class="link-box">{{referral_link}}</div>
      <a class="btn-wa" href="{{wa_url}}" target="_blank">📲 Share on WhatsApp (1-Tap)</a>
      
      <div class="rule-note">
        🗓️ <b>Friday Payout Schedule:</b> You earn <b>$0.10 (10 cents)</b> for every student who registers using your link. Accumulated commissions are sent directly to your registered WhatsApp/EcoCash number every Friday afternoon!
      </div>
    </div>

    <div class="card">
      <h3 style="margin:0">💰 Your Commission Summary</h3>
      <div class="stat-row">
        <div class="stat-box"><div class="stat-num">${{"%.2f"|format(total_earned)}}</div><div class="stat-lbl">TOTAL EARNED</div></div>
        <div class="stat-box"><div class="stat-num" style="color:#d97706">${{"%.2f"|format(pending)}}</div><div class="stat-lbl">PENDING THIS FRIDAY</div></div>
        <div class="stat-box"><div class="stat-num" style="color:#2563eb">${{"%.2f"|format(paid)}}</div><div class="stat-lbl">PAID TO ECOCASH</div></div>
      </div>

      <h4 style="margin:16px 0 8px">👥 Referred Friends ({{records|length}})</h4>
      <table>
        <thead><tr><th>Friend Name</th><th>Commission</th><th>Status</th><th>Date</th></tr></thead>
        <tbody>
          {% for r in records %}
          {% set fn = r.friend_name if r.friend_name is defined else r[3] %}
          {% set am = r.amount if r.amount is defined else r[0] %}
          {% set st = r.status if r.status is defined else r[1] %}
          {% set dt = r.created_at if r.created_at is defined else r[2] %}
          <tr>
            <td><b>{{fn}}</b></td>
            <td>+${{"%.2f"|format(am)}}</td>
            <td><span style="background:{% if st=='PAID' %}#dcfce7;color:#15803d{% else %}#fef3c7;color:#b45309{% endif %};padding:3px 8px;border-radius:12px;font-size:0.75rem;font-weight:bold">{{st}}</span></td>
            <td style="color:#64748b">{{dt[:10]}}</td>
          </tr>
          {% else %}
          <tr><td colspan="4" style="text-align:center;color:#94a3b8;padding:16px">No referrals yet. Share your link on WhatsApp above to start earning!</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>"""
        return render_template_string(tpl, sid=sid, s_name=s_name, s_num=s_num, referral_link=referral_link,
                                      wa_url=wa_url, total_earned=total_earned, pending=pending, paid=paid, records=records)

    # ========================================================
    # 4. FOUNDER FRIDAY REFERRAL PAYOUT DASHBOARD
    # ========================================================
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

        history = conn.execute("""
            SELECT p.referrer_id, s.name, s.student_number, COUNT(p.id) as friend_count, SUM(p.amount) as total_paid, p.paid_at
            FROM referral_payouts p
            JOIN students s ON p.referrer_id = s.id
            WHERE p.status = 'PAID'
            GROUP BY p.referrer_id, s.name, s.student_number, p.paid_at
            ORDER BY p.paid_at DESC
        """).fetchall()
        conn.close()

        tpl = """<!doctype html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>Friday Referral Payouts</title>
  <style>
    body { font-family: system-ui, sans-serif; background: #0f172a; color: #f8fafc; margin: 0; padding: 20px; }
    .wrap { max-width: 800px; margin: auto; }
    .card { background: #1e293b; border-radius: 16px; padding: 24px; margin-bottom: 20px; border: 1px solid #334155; }
    table { width: 100%; border-collapse: collapse; margin-top: 14px; font-size: 0.9rem; }
    th, td { padding: 10px 12px; border-bottom: 1px solid #334155; text-align: left; }
    th { background: #0f172a; color: #38bdf8; }
    .btn-pay { background: #10b981; color: white; border: none; padding: 6px 14px; border-radius: 6px; font-weight: bold; cursor: pointer; }
  </style>
</head>
<body>
  <div class="wrap">
    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px">
      <div>
        <h1 style="margin:0;font-size:1.6rem">💰 Friday EcoCash Referral Payouts</h1>
        <p style="margin:4px 0 0;color:#94a3b8">Pay 10¢ commissions to students every Friday.</p>
      </div>
      <a href="/founder/dashboard" style="color:#38bdf8;text-decoration:none;font-weight:bold">← Dashboard</a>
    </div>

    <div class="card">
      <h2 style="margin:0;color:#f59e0b">🗓️ Pending Payouts Due This Friday</h2>
      <table>
        <thead><tr><th>Student</th><th>DCR #</th><th>Friends</th><th>Amount Due</th><th>Action</th></tr></thead>
        <tbody>
          {% for r in pending %}
          {% set sid = r.referrer_id if r.referrer_id is defined else r[0] %}
          {% set name = r.name if r.name is defined else r[1] %}
          {% set dcr = r.student_number if r.student_number is defined else r[2] %}
          {% set phone = r.phone if r.phone is defined else r[3] %}
          {% set cnt = r.friend_count if r.friend_count is defined else r[4] %}
          {% set due = r.total_due if r.total_due is defined else r[5] %}
          <tr>
            <td><b>{{name}}</b></td>
            <td>{{dcr}}</td>
            
            <td>{{cnt}}</td>
            <td><b style="color:#10b981">${{"%.2f"|format(due)}}</b></td>
            <td>
              <form action="/founder/referrals/{{sid}}/pay" method="POST" style="margin:0">
                <button class="btn-pay" type="submit">✅ Mark Paid</button>
              </form>
            </td>
          </tr>
          {% else %}
          <tr><td colspan="6" style="text-align:center;color:#94a3b8;padding:16px">No pending referral commissions due right now.</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </div>
  </div>
</body>
</html>"""
        return render_template_string(tpl, pending=pending, history=history)

    @app.route("/founder/referrals/<int:referrer_id>/pay", methods=["POST"])
    def founder_mark_referrals_paid(referrer_id):
        conn = db()
        conn.execute("UPDATE referral_payouts SET status='PAID', paid_at=datetime('now') WHERE referrer_id=? AND status='PENDING'", (referrer_id,))
        conn.commit()
        conn.close()
        return redirect("/founder/referrals")
