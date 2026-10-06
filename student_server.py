import os, time, logging
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

# ---- register safe_url as a Jinja global if missing ----
def _safe_url(endpoint, **kw):
    try:
        return url_for(endpoint, **kw)
    except Exception:
        return "/"

try:
    app.jinja_env.globals.setdefault("safe_url", _safe_url)
except Exception:
    pass
# --------------------------------------------------------

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
