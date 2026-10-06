import os, time, logging
from flask import Flask, request, redirect, url_for, render_template, session, make_response, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
import dcr_db
from ui import page
from auth import auth_bp
from welcome_and_referrals import home_bp
from novel_reader import novel_bp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("dcr")


app = Flask(__name__)

import auth
if "auth" not in app.blueprints:
    app.register_blueprint(auth.auth_bp)

@app.context_processor
def _msasa_helpers():
    return {"safe_url": lambda ep, **kw: url_for(ep if ep in app.view_functions else "site_index", **kw)}

@app.route("/")
@app.route("/welcome")
def site_index():
    if request.cookies.get("dcr_consent") == "1":
        return redirect("/login")
    return render_template("welcome.html")

@app.route("/consent/agree", methods=["GET", "POST"])
def consent_agree():
    resp = make_response(redirect("/register"))
    resp.set_cookie("dcr_consent", "1", max_age=60*60*24*365, samesite="Lax")
    return resp

import auth
if "auth" not in app.blueprints:
    app.register_blueprint(auth.auth_bp)

@app.context_processor
def _msasa_helpers():
    return {"safe_url": lambda ep, **kw: url_for(ep if ep in app.view_functions else "site_index", **kw)}

import auth
if "auth" not in app.blueprints:
    app.register_blueprint(auth.auth_bp)


@app.context_processor
def _msasa_helpers():
    return {"safe_url": lambda ep, **kw: url_for(ep if ep in app.view_functions else "site_index", **kw)}

@app.context_processor
def _msasa_helpers():
    return {"safe_url": lambda ep, **kw: url_for(ep if ep in app.view_functions else "site_index", **kw)}



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
