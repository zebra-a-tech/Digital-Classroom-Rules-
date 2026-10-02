import os
from flask import request, abort

def register_founder_guard(app):
    @app.before_request
    def _guard():
        if not request.path.startswith("/founder"):
            return
        key = os.environ.get("FOUNDER_KEY", "")
        if key:
            if (request.args.get("key") == key or request.cookies.get("fk") == key
                    or request.headers.get("X-Founder-Key") == key):
                return
            abort(403)
        if request.remote_addr not in ("127.0.0.1", "::1"):
            abort(403)

    @app.after_request
    def _cookie(resp):
        key = os.environ.get("FOUNDER_KEY", "")
        if key and request.path.startswith("/founder") and request.args.get("key") == key:
            resp.set_cookie("fk", key, httponly=True, samesite="Lax")
        return resp
