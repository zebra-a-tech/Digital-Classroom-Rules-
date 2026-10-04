import os
from flask import request, abort, redirect, url_for, render_template_string, make_response

def register_founder_guard(app):
    @app.route("/founder/login", methods=["GET", "POST"])
    def founder_login():
        key = os.environ.get("FOUNDER_KEY", "").strip() or "7c3f5g3b1e6i8d"
        error = None
        if request.method == "POST":
            entered = request.form.get("founder_key", "").strip()
            if entered == key:
                resp = make_response(redirect("/founder/dashboard"))
                resp.set_cookie("fk", key, max_age=60*60*24*30, httponly=True, samesite="Lax")
                return resp
            error = "Invalid Key. Expected key from Railway Variables."
        
        tpl = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Founder Access</title>
        <style>body{font-family:system-ui,sans-serif;background:#0f172a;color:#f8fafc;display:flex;align-items:center;justify-content:center;height:100vh;margin:0}
        .box{background:#1e293b;padding:24px;border-radius:14px;max-width:340px;width:100%;box-shadow:0 8px 24px rgba(0,0,0,0.4);border:1px solid #334155}
        input{width:100%;padding:12px;border-radius:8px;border:1px solid #475569;background:#0f172a;color:white;margin:10px 0;box-sizing:border-box;font-size:1rem}
        button{width:100%;padding:12px;border-radius:8px;background:#0f766e;color:white;border:none;font-weight:bold;cursor:pointer;font-size:1rem}
        .err{background:#fee2e2;color:#991b1b;padding:8px;border-radius:6px;font-size:0.85rem;margin-bottom:8px}
        </style></head><body>
        <div class="box"><h2 style="margin:0 0 6px">🔐 Founder Access</h2><p style="color:#94a3b8;font-size:0.85rem;margin:0 0 14px">Enter your founder key to access dashboard & approvals.</p>
        {% if error %}<div class="err">{{error}}</div>{% endif %}
        <form method="POST"><input type="password" name="founder_key" placeholder="Enter Founder Key..." required autofocus>
        <button type="submit">Unlock Dashboard →</button></form></div></body></html>"""
        return render_template_string(tpl, error=error)

    @app.before_request
    def _guard():
        if not request.path.startswith("/founder"):
            return
        if request.path == "/founder/login":
            return
        key = os.environ.get("FOUNDER_KEY", "").strip() or "7c3f5g3b1e6i8d"
        if (request.args.get("key") == key or 
            request.cookies.get("fk") == key or 
            request.headers.get("X-Founder-Key") == key):
            return
        return redirect("/founder/login")

    @app.after_request
    def _cookie(resp):
        key = os.environ.get("FOUNDER_KEY", "").strip() or "7c3f5g3b1e6i8d"
        if request.path.startswith("/founder") and request.args.get("key") == key:
            resp.set_cookie("fk", key, max_age=60*60*24*30, httponly=True, samesite="Lax")
        return resp
