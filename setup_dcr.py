#!/usr/bin/env python3
"""Digital Classroom Rules - one-shot installer.
Run from the repo root:  python setup_dcr.py          (writes, tests, commits, pushes)
                         python setup_dcr.py --no-git (writes and tests only)
"""
import os, sys, time, shutil, subprocess, py_compile

BUILD_ID = time.strftime("%Y%m%d%H%M%S")
FILES = {}

FILES["requirements.txt"] = r'''flask>=3.0
gunicorn>=22.0
'''

FILES["Procfile"] = r'''web: gunicorn student_server:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 60
'''

FILES["Dockerfile"] = r'''FROM python:3.11-slim
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
# Changing BUILD_ID on every install busts the layer cache for everything below.
ARG BUILD_ID=__BUILD_ID__
ENV BUILD_ID=$BUILD_ID
RUN echo "$BUILD_ID" > /tmp/build_id
COPY . .
CMD ["sh", "-c", "gunicorn student_server:app --bind 0.0.0.0:${PORT:-8080} --workers 1 --threads 4 --timeout 60"]
'''

FILES[".dockerignore"] = r'''.git
__pycache__
*.pyc
_backup_*
dcr_local.db
'''

FILES["railway.json"] = r'''{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {"builder": "DOCKERFILE", "dockerfilePath": "Dockerfile"},
  "deploy": {
    "healthcheckPath": "/api/health-check",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE"
  }
}
'''

FILES["dcr_db.py"] = r'''"""Tiny Turso-over-HTTPS client (stdlib only). Falls back to local SQLite if no Turso env vars."""
import os, json, sqlite3, urllib.request

URL = (os.environ.get("TURSO_DATABASE_URL") or os.environ.get("TURSO_URL") or "").replace("libsql://", "https://")
TOKEN = os.environ.get("TURSO_AUTH_TOKEN") or os.environ.get("TURSO_TOKEN") or ""
LOCAL = os.environ.get("DCR_LOCAL_DB", "dcr_local.db")


def mode():
    return "turso" if (URL and TOKEN) else "local-sqlite"


def _arg(v):
    if v is None:
        return {"type": "null"}
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": v}
    return {"type": "text", "value": str(v)}


def _cell(c):
    t, v = c.get("type"), c.get("value")
    if t == "null":
        return None
    if t == "integer":
        return int(v)
    if t == "float":
        return float(v)
    return v


def run(sql, args=()):
    """Execute one statement, return a list of dict rows."""
    if mode() == "turso":
        body = json.dumps({"requests": [
            {"type": "execute", "stmt": {"sql": sql, "args": [_arg(a) for a in args]}},
            {"type": "close"}]}).encode()
        req = urllib.request.Request(
            URL.rstrip("/") + "/v2/pipeline", data=body,
            headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json",
                     "User-Agent": "dcr-app/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.load(r)["results"][0]
        if res.get("type") == "error":
            raise RuntimeError(res["error"]["message"])
        out = res["response"]["result"]
        cols = [c["name"] for c in out["cols"]]
        return [dict(zip(cols, [_cell(c) for c in row])) for row in out["rows"]]
    con = sqlite3.connect(LOCAL)
    con.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in con.execute(sql, tuple(args)).fetchall()]
        con.commit()
        return rows
    finally:
        con.close()


SCHEMA = [
    "CREATE TABLE IF NOT EXISTS dcr_users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, "
    "pw TEXT, grade INTEGER DEFAULT 1, ecocash TEXT, ref_code TEXT UNIQUE, referred_by INTEGER, "
    "credit_cents INTEGER DEFAULT 0, created TEXT)",
    "CREATE TABLE IF NOT EXISTS dcr_referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, "
    "new_user_id INTEGER, cents INTEGER, ts TEXT)",
    "CREATE TABLE IF NOT EXISTS dcr_payouts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cents INTEGER, ts TEXT)",
    "CREATE TABLE IF NOT EXISTS dcr_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, book INTEGER, "
    "chapter INTEGER, score INTEGER, ts TEXT)",
]


def init():
    for s in SCHEMA:
        run(s)
'''

FILES["ui.py"] = r'''"""Shared page shell. CSS is injected as a variable so Jinja never touches its braces."""
from flask import render_template_string
from markupsafe import Markup

CSS = """
:root{--g:#006400;--y:#ffd200;--r:#d40000;--k:#111;--bg:#f4f6f1;
--flag:linear-gradient(90deg,#006400 0 14.28%,#ffd200 14.28% 28.56%,#d40000 28.56% 42.84%,#111 42.84% 57.12%,#d40000 57.12% 71.4%,#ffd200 71.4% 85.68%,#006400 85.68% 100%)}
*{box-sizing:border-box}
body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:#222;line-height:1.55}
.flag{height:10px;background:var(--flag)}
nav{background:#fff;padding:10px 16px;display:flex;gap:16px;flex-wrap:wrap;align-items:center;border-bottom:1px solid #ddd}
nav a{color:var(--g);font-weight:700;text-decoration:none}
main{max-width:760px;margin:0 auto;padding:12px 16px 40px}
.card{background:#fff;border-radius:14px;box-shadow:0 2px 14px rgba(0,0,0,.12);padding:22px;margin:18px auto;overflow:hidden}
.card.auth{max-width:420px}
.card.auth:before{content:"";display:block;height:8px;margin:-22px -22px 18px;background:var(--flag)}
h1,h2{color:var(--g);margin-top:0}
label{display:block;font-weight:600;margin-top:12px}
input,select{width:100%;padding:12px;border:1px solid #bbb;border-radius:8px;font-size:16px;margin-top:4px;background:#fff}
.btn{display:inline-block;background:var(--g);color:#fff;border:0;border-radius:10px;padding:12px 18px;font-size:16px;font-weight:700;text-decoration:none;cursor:pointer;margin:14px 6px 0 0}
.btn.alt{background:#333}.btn.wa{background:#25d366}.btn.warn{background:var(--r)}
.warnbox{border-left:5px solid var(--r);background:#fff3f3;padding:10px 14px;border-radius:8px;margin:12px 0}
.err{color:#b00020;font-weight:600}.ok{color:var(--g);font-weight:600}
table{width:100%;border-collapse:collapse}td,th{padding:8px;border-bottom:1px solid #eee;text-align:left}
.story{font-size:1.3rem;line-height:1.8}
.opt{display:block;padding:10px;border:1px solid #ccc;border-radius:8px;margin:8px 0;font-weight:400}
.opt input{width:auto;margin-right:8px}
.muted{color:#666;font-size:.9rem}
"""

BASE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }} | Digital Classroom Rules</title>
<style>{{ css|safe }}</style></head>
<body><div class="flag"></div>
<nav><a href="/home">Digital Classroom Rules</a>
{% if session.get('uid') %}<a href="/novels">Novels</a><a href="/referrals">Referrals</a><a href="/logout">Logout</a>
{% else %}<a href="/login">Login</a><a href="/register">Register</a>{% endif %}
</nav>
<main>{{ body }}</main></body></html>"""


def page(title, body, **ctx):
    inner = render_template_string(body, **ctx)
    return render_template_string(BASE, title=title, css=CSS, body=Markup(inner))
'''

FILES["auth.py"] = r'''import secrets, logging
from datetime import datetime
from flask import Blueprint, request, session, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import dcr_db as db
from ui import page

auth_bp = Blueprint("auth", __name__)
log = logging.getLogger("dcr.auth")

REGISTER = """
<div class="card auth"><h1>Create account</h1>
{% if err %}<p class="err">{{ err }}</p>{% endif %}
<form method="post" autocomplete="off">
<input type="hidden" name="ref" value="{{ ref }}">
<label>Full name</label><input name="name" autocomplete="off" required>
<label>Email</label><input name="email" type="email" autocomplete="off" required>
<label>Password (6+ characters)</label>
<input name="pw" type="password" autocomplete="new-password" readonly onfocus="this.removeAttribute('readonly')" required>
<label>Grade</label>
<select name="grade">{% for g in range(1,8) %}<option value="{{ g }}">Grade {{ g }}</option>{% endfor %}</select>
<label>EcoCash number (optional, for referral payouts)</label><input name="ecocash" inputmode="tel" autocomplete="off">
<button class="btn" type="submit">Register</button>
</form>
<p class="muted">Already registered? <a href="/login">Log in</a></p></div>
"""

LOGIN = """
<div class="card auth"><h1>Log in</h1>
{% if err %}<p class="err">{{ err }}</p>{% endif %}
<form method="post" autocomplete="off">
<label>Email</label><input name="email" type="email" autocomplete="off" required>
<label>Password</label>
<input name="pw" type="password" autocomplete="new-password" readonly onfocus="this.removeAttribute('readonly')" required>
<button class="btn" type="submit">Log in</button>
</form>
<p class="muted">New here? <a href="/register">Create an account</a></p></div>
"""


def _login(u):
    session["uid"] = u["id"]
    session["name"] = u["name"]
    session["grade"] = u["grade"]


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    ref = (request.values.get("ref") or "").strip()
    err = ""
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw = request.form.get("pw", "")
        eco = request.form.get("ecocash", "").strip()
        try:
            grade = max(1, min(7, int(request.form.get("grade") or 1)))
        except ValueError:
            grade = 1
        if not name or "@" not in email or len(pw) < 6:
            err = "Please enter your name, a valid email and a password of 6+ characters."
        else:
            try:
                if db.run("SELECT id FROM dcr_users WHERE email=?", (email,)):
                    err = "That email is already registered."
                else:
                    now = datetime.utcnow().isoformat()
                    rid = None
                    if ref:
                        r = db.run("SELECT id FROM dcr_users WHERE ref_code=?", (ref,))
                        rid = r[0]["id"] if r else None
                    db.run("INSERT INTO dcr_users(name,email,pw,grade,ecocash,ref_code,referred_by,credit_cents,created) "
                           "VALUES(?,?,?,?,?,?,?,0,?)",
                           (name, email, generate_password_hash(pw), grade, eco, secrets.token_hex(3), rid, now))
                    u = db.run("SELECT * FROM dcr_users WHERE email=?", (email,))[0]
                    if rid:
                        db.run("UPDATE dcr_users SET credit_cents=credit_cents+10 WHERE id=?", (rid,))
                        db.run("INSERT INTO dcr_referrals(referrer_id,new_user_id,cents,ts) VALUES(?,?,10,?)",
                               (rid, u["id"], now))
                    _login(u)
                    return redirect(url_for("home.dashboard"))
            except Exception:
                log.exception("register failed")
                err = "Server error. Please try again in a moment."
    return page("Register", REGISTER, err=err, ref=ref)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    err = ""
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        try:
            r = db.run("SELECT * FROM dcr_users WHERE email=?", (email,))
            if r and check_password_hash(r[0]["pw"], request.form.get("pw", "")):
                _login(r[0])
                return redirect(url_for("home.dashboard"))
            err = "Wrong email or password."
        except Exception:
            log.exception("login failed")
            err = "Server error. Please try again in a moment."
    return page("Log in", LOGIN, err=err)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home.dashboard"))
'''

FILES["welcome_and_referrals.py"] = r'''import os, hmac
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
'''

FILES["novel_reader.py"] = r'''import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, session, redirect, url_for, abort
import dcr_db as db
from ui import page

novel_bp = Blueprint("novels", __name__)

# STARTER CONTENT: 4 graded books x 10 chapters. Replace/extend the beats with your full chapter text.
_RAW = [
    (1, "Tendai and the Talking Baobab", "1-2", 2,
     "Tendai finds a huge baobab tree near her school.|The baobab says hello in a deep, kind voice.|"
     "Tendai promises to keep the tree's secret.|A hungry goat nibbles the baobab's low leaves.|"
     "Tendai shares her lunch with the goat.|The baobab shows her a hidden nest of eggs.|"
     "Dark clouds gather and the dry fields finally get rain.|Tendai tells her class to protect old trees.|"
     "The class plants ten small trees together.|Tendai waves goodbye as the baobab whispers thank you."),
    (2, "The Little Weaver of Mutare", "2-3", 3,
     "Farai watches his gogo weave a basket on the veranda.|He asks to learn, and Gogo hands him a bundle of reeds.|"
     "His first basket falls apart in his hands.|Farai feels sad but Gogo tells him to try again.|"
     "He practises every afternoon after school.|A neighbour orders a small basket for her market stall.|"
     "Farai finishes it just before the market opens.|The basket sells for two dollars, his first earnings.|"
     "He saves one dollar and gives one to Gogo for reeds.|Farai learns that patience turns practice into skill."),
    (3, "Rudo's River Journey", "3-4", 4,
     "Rudo's village well dries up during a long drought.|She decides to follow the river to find clean water.|"
     "Her brother Tafara insists on coming along.|They cross a rocky gorge by balancing on stones.|"
     "A kind fisherman shares his map with the children.|Night falls and they shelter in a cave and count stars.|"
     "Tafara twists his ankle and Rudo carries his bag.|At sunrise they find a spring flowing from a hill.|"
     "They lead the village elders back to the spring.|The village digs a new borehole and Rudo is thanked."),
    (4, "The Great Zimbabwe Mystery", "4-5", 5,
     "Chipo joins a school trip to the ancient stone ruins.|Her guide mentions that a carved bird has gone missing.|"
     "Chipo notices fresh footprints near the Hill Complex.|She sketches the prints and compares them with her classmates' shoes.|"
     "A torn blue cloth is snagged on a stone wall.|Chipo interviews the caretaker and spots a nervous habit.|"
     "The clues point to a hidden storeroom behind the walls.|She asks the guide to open it while a teacher watches.|"
     "They find the bird safe, moved for cleaning, with the paperwork lost.|Chipo learns that careful questions solve more than guesses."),
]
BOOKS = {b[0]: {"id": b[0], "title": b[1], "grades": b[2], "maxg": b[3], "beats": b[4].split("|")} for b in _RAW}


def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("uid"):
            return redirect(url_for("auth.login"))
        return f(*a, **k)
    return w


LIB = """
<div class="card"><h1>Novel Library</h1>
{% for b in books %}<p><strong>{{ b.title }}</strong> <span class="muted">(Grades {{ b.grades }}, 10 chapters)</span><br>
<a class="btn" href="/novels/{{ b.id }}">Open</a></p>{% endfor %}
<a class="btn alt" href="/novels/report">Weekly reading report</a></div>
"""

TOC = """
<div class="card"><h1>{{ b.title }}</h1>
{% for i in range(1, 11) %}<a class="btn alt" href="/novels/{{ b.id }}/{{ i }}">Chapter {{ i }}</a>{% endfor %}</div>
"""

READ = """
<div class="card"><h2>{{ b.title }}: Chapter {{ n }}</h2>
<p class="story" id="story">{{ text }}</p>
<button class="btn" type="button" onclick="dcrPlay()">&#9654; Play</button>
<button class="btn alt" type="button" onclick="dcrPause()">&#10074;&#10074; Pause</button>
<button class="btn warn" type="button" onclick="dcrStop()">&#9632; Stop</button>
{% if b.maxg <= 5 %}<p><button class="btn alt" type="button" onclick="document.getElementById('assist').style.display='block'">Parent assist mode</button></p>
<div id="assist" class="warnbox" style="display:none;border-color:#006400;background:#f1fbf1">
<strong>For parents:</strong> 1) Read the sentence aloud slowly. 2) Ask your child to read it back.
3) Ask: "Who is in this chapter and what happened?" 4) Ask: "What do you think happens next?" Then take the quiz together.</div>{% endif %}
</div>
<div class="card"><h2>Chapter quiz</h2><p>Which sentence happened in this chapter?</p>
<form method="post">{% for o in opts %}<label class="opt"><input type="radio" name="choice" value="{{ o }}" required>{{ beats[o] }}</label>{% endfor %}
<button class="btn" type="submit">Check answer</button></form></div>
<script>
var synth = window.speechSynthesis;
function dcrPlay(){ if(!synth){alert('Audio is not supported on this browser.');return;}
  if(synth.paused){synth.resume();return;} synth.cancel();
  var u=new SpeechSynthesisUtterance(document.getElementById('story').innerText); u.rate=0.85; synth.speak(u); }
function dcrPause(){ if(synth){synth.pause();} }
function dcrStop(){ if(synth){synth.cancel();} }
</script>
"""

RESULT = """
<div class="card"><h2>{% if ok %}<span class="ok">Correct! Well done.</span>{% else %}<span class="err">Not quite.</span>{% endif %}</h2>
<p>This chapter: <em>{{ truth }}</em></p>
{% if n < 10 %}<a class="btn" href="/novels/{{ b.id }}/{{ n + 1 }}">Next chapter</a>{% endif %}
<a class="btn alt" href="/novels/{{ b.id }}">Chapter list</a></div>
"""

REPORT = """
<div class="card"><h1>Weekly reading report</h1><p class="muted">Last 7 days for {{ name }}</p>
{% if rows %}<table><tr><th>Book</th><th>Chapters</th><th>Avg quiz</th></tr>
{% for r in rows %}<tr><td>{{ r.title }}</td><td>{{ r.chapters }}</td><td>{{ r.avg }}%</td></tr>{% endfor %}</table>
{% else %}<p>No reading yet this week. Start a chapter today!</p>{% endif %}</div>
"""


def _book(bid):
    b = BOOKS.get(bid)
    if not b:
        abort(404)
    return b


@novel_bp.route("/novels")
@login_required
def library():
    return page("Novels", LIB, books=list(BOOKS.values()))


@novel_bp.route("/novels/report")
@login_required
def report():
    since = (datetime.utcnow() - timedelta(days=7)).isoformat()
    data = db.run("SELECT book,chapter,score FROM dcr_progress WHERE user_id=? AND ts>=?", (session["uid"], since))
    agg = {}
    for d in data:
        a = agg.setdefault(d["book"], {"ch": set(), "sc": []})
        a["ch"].add(d["chapter"])
        a["sc"].append(d["score"])
    rows = [{"title": BOOKS[k]["title"], "chapters": len(v["ch"]), "avg": round(sum(v["sc"]) / len(v["sc"]))}
            for k, v in agg.items() if k in BOOKS]
    return page("Report", REPORT, rows=rows, name=session.get("name"))


@novel_bp.route("/novels/<int:bid>")
@login_required
def toc(bid):
    return page(_book(bid)["title"], TOC, b=_book(bid))


@novel_bp.route("/novels/<int:bid>/<int:n>", methods=["GET", "POST"])
@login_required
def chapter(bid, n):
    b = _book(bid)
    if not 1 <= n <= 10:
        abort(404)
    i = n - 1
    beats = b["beats"]
    if request.method == "POST":
        try:
            ok = int(request.form.get("choice", "-1")) == i
        except ValueError:
            ok = False
        db.run("INSERT INTO dcr_progress(user_id,book,chapter,score,ts) VALUES(?,?,?,?,?)",
               (session["uid"], bid, n, 100 if ok else 0, datetime.utcnow().isoformat()))
        return page("Result", RESULT, ok=ok, truth=beats[i], b=b, n=n)
    rnd = random.Random(bid * 100 + n)
    opts = rnd.sample([x for x in range(10) if x != i], 2) + [i]
    rnd.shuffle(opts)
    return page("Chapter " + str(n), READ, b=b, n=n, text=beats[i], beats=beats, opts=opts)
'''

FILES["student_server.py"] = r'''import os, time, logging
from flask import Flask, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import dcr_db
from ui import page
from auth import auth_bp
from welcome_and_referrals import home_bp
from novel_reader import novel_bp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dcr")

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dcr-dev-secret-change-me")
app.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

app.register_blueprint(home_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(novel_bp)

STARTED = time.time()
DB_STATUS = "not initialised"
try:
    dcr_db.init()
    DB_STATUS = "ok (" + dcr_db.mode() + ")"
except Exception as e:  # never crash the boot: /api/health-check must still answer
    DB_STATUS = "error: " + str(e)[:200]
    log.exception("DB init failed")


def _info():
    return {
        "app": "Digital Classroom Rules",
        "portal": "consent-v2",
        "build_id": os.environ.get("BUILD_ID", "local"),
        "db": DB_STATUS,
        "uptime_s": int(time.time() - STARTED),
        "founder_key_set": bool(os.environ.get("FOUNDER_KEY")),
        "routes": sorted(str(r) for r in app.url_map.iter_rules() if r.endpoint != "static"),
    }


@app.route("/version")
@app.route("/api/health-check")
def version():
    return jsonify(_info())


@app.errorhandler(404)
def nf(e):
    return page("Not found", '<div class="card"><h1>Page not found</h1><a class="btn" href="/home">Home</a></div>'), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
'''


def sh(*cmd, check=False):
    r = subprocess.run(cmd, capture_output=True, text=True)
    out = (r.stdout + r.stderr).strip()
    if out:
        print(out)
    if check and r.returncode:
        sys.exit("FAILED: " + " ".join(cmd))
    return r.returncode


def main():
    no_git = "--no-git" in sys.argv
    backup = "_backup_" + BUILD_ID
    os.makedirs(backup, exist_ok=True)
    for old in list(FILES) + ["railway.toml", "nixpacks.toml", "runtime.txt"]:
        if os.path.exists(old):
            shutil.copy2(old, os.path.join(backup, old))
    for junk in ("railway.toml", "nixpacks.toml"):  # these override Dockerfile settings on Railway
        if os.path.exists(junk):
            os.remove(junk)
            print("removed conflicting", junk, "(backed up)")
    for name, text in FILES.items():
        with open(name, "w", encoding="utf-8") as f:
            f.write(text.replace("__BUILD_ID__", BUILD_ID))
        print("wrote", name)
    for name in FILES:
        if name.endswith(".py"):
            py_compile.compile(name, doraise=True)
    print("syntax OK for all .py files")

    try:  # smoke test with Flask's test client (local sqlite, no network)
        os.environ.pop("TURSO_DATABASE_URL", None)
        os.environ["DCR_LOCAL_DB"] = "/tmp/dcr_smoke.db"
        if os.path.exists("/tmp/dcr_smoke.db"):
            os.remove("/tmp/dcr_smoke.db")
        sys.path.insert(0, os.getcwd())
        import student_server
        c = student_server.app.test_client()
        checks = [("/", "Welcome"), ("/register", "Create account"), ("/login", "Log in"),
                  ("/version", "consent-v2"), ("/api/health-check", "build_id")]
        for path, needle in checks:
            r = c.get(path)
            assert r.status_code == 200 and needle in r.get_data(as_text=True), "smoke test failed: " + path
        assert "<style><style>" not in c.get("/").get_data(as_text=True)
        print("smoke tests passed")
    except ImportError as e:
        print("skipped smoke test (", e, ") - run: pip install flask gunicorn")
    except AssertionError as e:
        sys.exit(str(e))

    if no_git:
        print("Done (git skipped).")
        return
    sh("git", "add", "-A")
    sh("git", "commit", "-m", "Rebuild portal: consent, auth, novels, referrals, health-check (build " + BUILD_ID + ")")
    if sh("git", "push", "origin", "main"):
        print("\nPush failed. Try: git pull --rebase origin main   then   git push origin main")
        sys.exit(1)
    print("\nPushed. Build ID:", BUILD_ID)
    print("Verify in ~2 min:  curl -s https://digital-classroom-rules-production.up.railway.app/version")


if __name__ == "__main__":
    main()
