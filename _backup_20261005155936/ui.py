"""Shared page shell. CSS is injected as a variable so Jinja never touches its braces."""
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
