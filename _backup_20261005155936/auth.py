import secrets, logging
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
