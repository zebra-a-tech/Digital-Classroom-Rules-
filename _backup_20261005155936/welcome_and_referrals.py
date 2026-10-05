import os, hmac
from datetime import datetime
from urllib.parse import quote
from flask import Blueprint, request, session, redirect, url_for, make_response
import dcr_db as db
from ui import page

home_bp = Blueprint("home", __name__)

CONSENT = """
<div class="card"><h1>Welcome to Digital Classroom Rules</h1>
<p class="big">A structured learning platform with lessons, a graded novel library, quizzes and weekly reading reports.</p>
<h2>Built by IT professionals</h2>
<p>This platform was designed, written and is maintained by IT professionals. Every lesson, story, quiz and line of code
is original work, stored on secured cloud infrastructure and monitored for misuse.</p>
<h2>Legal consent: anti-piracy notice</h2>
<div class="warnbox"><strong>All content is protected by copyright.</strong>
Copying, duplicating, screen-scraping, re-uploading, reselling or sharing lessons, novels, quizzes or login details
with anyone outside your own household is strictly prohibited. Accounts found duplicating content will be
suspended and the matter may be pursued under copyright law.</div>
<p>By continuing you confirm that you will use this platform for personal learning only and will not reproduce or
distribute any of its material.</p>
<form method="post" action="/agree"><button class="btn" type="submit">I Agree &amp; Continue</button></form>
<p class="muted">Your choice is remembered on this device for one year.</p></div>
"""

DASH = """
<div class="card"><h1>{% if name %}Welcome back, {{ name }}!{% else %}Digital Classroom Rules{% endif %}</h1>
{% if name %}
<a class="btn" href="/novels">Novel Library</a><a class="btn alt" href="/novels/report">Weekly report</a>
<a class="btn wa" href="/referrals">Refer &amp; earn</a>
{% else %}<p>Create a free account to start reading and learning.</p>
<a class="btn" href="/register">Register</a><a class="btn alt" href="/login">Log in</a>{% endif %}</div>
"""

REFERRALS = """
<div class="card"><h1>Refer &amp; earn</h1>
<p>You earn <strong>$0.10</strong> for every student who signs up with your link.</p>
<p><strong>Your link:</strong><br><span style="word-break:break-all">{{ link }}</span></p>
<a class="btn wa" href="https://wa.me/?text={{ wa }}" target="_blank" rel="noopener">Share on WhatsApp</a>
<h2>Your earnings</h2>
<p class="big">{{ count }} sign-ups &middot; <strong>${{ '%.2f' % (credit/100) }}</strong> pending</p>
<p class="muted">Payouts are sent by EcoCash every Friday. Your number on file: {{ eco or 'none yet' }}.</p></div>
"""

F_LOGIN = """
<div class="card auth"><h1>Founder login</h1>{% if err %}<p class="err">{{ err }}</p>{% endif %}
<form method="post"><label>Founder key</label>
<input name="key" type="password" autocomplete="new-password" required>
<button class="btn" type="submit">Enter</button></form></div>
"""

F_DASH = """
<div class="card"><h1>Founder payouts</h1>
<p>{% if friday %}<span class="ok">It is Friday: payout day.</span>{% else %}Payouts are due every Friday.{% endif %}</p>
<p class="big">Total owed: <strong>${{ '%.2f' % (total/100) }}</strong></p>
{% if rows %}<table><tr><th>Student</th><th>EcoCash</th><th>Owed</th><th></th></tr>
{% for r in rows %}<tr><td>{{ r.name }}</td><td>{{ r.ecocash or '-' }}</td><td>${{ '%.2f' % (r.credit_cents/100) }}</td>
<td><form method="post" action="/founder/pay/{{ r.id }}"><button class="btn" type="submit">Mark paid</button></form></td></tr>{% endfor %}
</table>{% else %}<p>Nobody is owed anything right now.</p>{% endif %}</div>
"""


@home_bp.route("/")
def index():
    if request.cookies.get("dcr_consent") == "1":
        return redirect(url_for("home.dashboard"))
    return page("Welcome", CONSENT)


@home_bp.route("/agree", methods=["POST"])
def agree():
    resp = make_response(redirect(url_for("home.dashboard")))
    resp.set_cookie("dcr_consent", "1", max_age=31536000, httponly=True, samesite="Lax", secure=request.is_secure)
    return resp


@home_bp.route("/home")
def dashboard():
    return page("Home", DASH, name=session.get("name"))


@home_bp.route("/referrals")
def referrals():
    if not session.get("uid"):
        return redirect(url_for("auth.login"))
    u = db.run("SELECT * FROM dcr_users WHERE id=?", (session["uid"],))[0]
    n = db.run("SELECT COUNT(*) AS c FROM dcr_referrals WHERE referrer_id=?", (u["id"],))[0]["c"]
    link = request.url_root + "register?ref=" + u["ref_code"]
    wa = quote("Join me on Digital Classroom Rules - free lessons and graded novels: " + link)
    return page("Referrals", REFERRALS, link=link, wa=wa, count=n, credit=u["credit_cents"] or 0, eco=u["ecocash"])


@home_bp.route("/founder/login", methods=["GET", "POST"])
def founder_login():
    key = request.values.get("key", "")
    fk = os.environ.get("FOUNDER_KEY", "")
    err = ""
    if key:
        if fk and hmac.compare_digest(key, fk):
            session["founder"] = True
            return redirect(url_for("home.founder"))
        err = "Invalid key."
    return page("Founder login", F_LOGIN, err=err)


@home_bp.route("/founder")
def founder():
    if not session.get("founder"):
        return redirect(url_for("home.founder_login"))
    rows = db.run("SELECT id,name,ecocash,credit_cents FROM dcr_users WHERE credit_cents>0 ORDER BY credit_cents DESC")
    total = sum(r["credit_cents"] for r in rows)
    return page("Founder", F_DASH, rows=rows, total=total, friday=datetime.utcnow().weekday() == 4)


@home_bp.route("/founder/pay/<int:uid>", methods=["POST"])
def founder_pay(uid):
    if not session.get("founder"):
        return redirect(url_for("home.founder_login"))
    r = db.run("SELECT credit_cents FROM dcr_users WHERE id=?", (uid,))
    if r and r[0]["credit_cents"]:
        db.run("INSERT INTO dcr_payouts(user_id,cents,ts) VALUES(?,?,?)",
               (uid, r[0]["credit_cents"], datetime.utcnow().isoformat()))
        db.run("UPDATE dcr_users SET credit_cents=0 WHERE id=?", (uid,))
    return redirect(url_for("home.founder"))
