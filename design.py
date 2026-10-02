CSS = """
:root{--ink:#10281d;--moss:#14532d;--leaf:#1f7a4d;--mint:#e8f5ee;--gold:#e0a526;--cream:#fbf8f1;--card:#fff;--line:#dfe8e2;--bad:#b42318;--r:20px;--sh:0 10px 30px -12px rgba(16,40,29,.28)}
@media not all and (prefers-color-scheme: dark){:root{--ink:#e9f3ed;--cream:#0e1a14;--card:#16261d;--line:#27402f;--mint:#1b3326}}
html body{background:var(--cream)!important;color:var(--ink)!important;font-family:'Segoe UI',system-ui,-apple-system,Roboto,sans-serif!important;line-height:1.55}
h1,h2{font-family:Georgia,'Times New Roman',serif!important;letter-spacing:-.01em}
.hero,.hero-card{background:linear-gradient(135deg,var(--moss),#0b3a21 70%)!important;color:#fff!important;border-radius:var(--r)!important;padding:26px 22px!important;margin:14px!important;box-shadow:var(--sh);position:relative;overflow:hidden;animation:dcrise .5s ease both}
.hero:after,.hero-card:after{content:"";position:absolute;right:-40px;top:-40px;width:150px;height:150px;border-radius:50%;background:radial-gradient(var(--gold),transparent 70%);opacity:.35}
.hero h1,.hero-card h1{color:#fff!important;margin:0 0 6px}
.card,.content-card,.upload-panel{background:var(--card)!important;border:1px solid var(--line)!important;border-radius:var(--r)!important;box-shadow:var(--sh);padding:18px!important;margin:14px!important;animation:dcrise .5s ease both}
.eyebrow{display:inline-block;font-size:11px;font-weight:800;letter-spacing:.14em;text-transform:uppercase;color:var(--gold)}
.subject{border:1px solid var(--line);border-radius:16px;padding:12px 14px;margin:10px 0;background:var(--mint);transition:transform .15s}
.subject.current{border-color:var(--leaf);box-shadow:inset 4px 0 0 var(--leaf)}
.subject:hover{transform:translateY(-2px)}
.btn,.primary-button{display:inline-block;border:0!important;border-radius:14px!important;padding:13px 18px!important;font-weight:800!important;text-decoration:none!important;color:#fff!important;background:var(--leaf)!important;margin:6px 6px 6px 0;cursor:pointer;min-height:44px;box-shadow:0 6px 14px -8px rgba(0,0,0,.5);transition:transform .12s,filter .12s}
.btn:hover,.primary-button:hover{transform:translateY(-1px);filter:brightness(1.07)}
.btn:active,.primary-button:active{transform:scale(.97)}
.btn.orange{background:var(--gold)!important;color:#2b1d00!important}
.btn.purple{background:#4c3a8f!important}
.btn.gray{background:#6b7a72!important}
.btn:focus-visible,a:focus-visible,input:focus-visible,textarea:focus-visible{outline:3px solid var(--gold);outline-offset:2px}
.warning{background:#fff4e5;border-left:4px solid var(--gold);padding:10px 12px;border-radius:10px;color:#6b4300}
.parent-notice{display:flex;gap:12px;background:#fff7e6;border:1px solid #f5c26b;color:#7a4b00;border-radius:var(--r);padding:14px;margin:14px}
.requirement-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:10px}
.requirement-grid div{background:var(--mint);border-radius:14px;padding:10px}
.requirement-grid span{display:block;font-size:12px;opacity:.7}
.error-state,.dc-empty,.dc-success,.dc-loading{text-align:center;border-radius:var(--r);padding:28px 18px;margin:14px;animation:dcrise .4s ease both}
.error-state{background:#fef3f2;border:1px solid #fecdca;color:var(--bad)}
.dc-empty{background:var(--mint);border:2px dashed var(--line)}
.dc-success{background:#ecfdf3;border:1px solid #abefc6;color:#067647}
.error-state>div,.dc-empty>div,.dc-success>div{font-size:42px}
.dc-loading:before{content:"";display:block;width:34px;height:34px;margin:0 auto 10px;border:4px solid var(--line);border-top-color:var(--leaf);border-radius:50%;animation:dcspin .8s linear infinite}
input,select,textarea{border-radius:12px!important;border:1px solid var(--line)!important;padding:11px!important;font:inherit;max-width:100%;box-sizing:border-box}
@keyframes dcrise{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}
@keyframes dcspin{to{transform:rotate(360deg)}}
@media(max-width:480px){.hero,.card,.content-card{margin:10px!important}.btn{width:100%;text-align:center;margin-right:0}}
@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
"""
def register_design(app):
    from flask import request
    @app.after_request
    def _design(resp):
        try:
            p = request.path
            if not (p.startswith("/student/") or p.startswith("/founder/")): return resp
            if resp.status_code != 200 or "text/html" not in (resp.content_type or ""): return resp
            html = resp.get_data(as_text=True)
            if 'id="dc-design"' in html: return resp
            tag = '<meta name="viewport" content="width=device-width,initial-scale=1"><style id="dc-design">' + CSS + "</style>"
            html = html.replace("</head>", tag + "</head>", 1)
            if p.startswith("/student/") and "dc-logout" not in html:
                btn = '<a id="dc-logout" href="/logout" style="position:fixed;top:10px;right:10px;z-index:9999;background:#14532d;color:#fff;padding:8px 14px;border-radius:999px;font:700 13px sans-serif;text-decoration:none;box-shadow:0 4px 12px rgba(0,0,0,.3)">Log out</a>'
                html = html.replace("</body>", btn + "</body>", 1) if "</body>" in html else html + btn if "</head>" in html else tag + html
            resp.set_data(html)
        except Exception as e:
            print("design skipped:", e)
        return resp
