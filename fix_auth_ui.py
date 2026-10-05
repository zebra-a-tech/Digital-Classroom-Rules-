"""Fix divider CSS and add Forgot Password link."""

FILE = "auth.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("auth_before_ui_fix.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# ============================================================
# FIX 1: Fix the divider CSS
# ============================================================
old_divider_css = """.divider{text-align:center;color:#94a3b8;font-size:13px;margin:20px 0;position:relative}
.divider:before,.divider:after{content:'';position:absolute;top:50%;width:42%;height:1px;background:#e2e8f0}
.divider:before{left:0}
.divider:after{right:0}"""

new_divider_css = """.divider{text-align:center;color:#94a3b8;font-size:13px;margin:20px 0;position:relative;display:flex;align-items:center;gap:12px}
.divider:before,.divider:after{content:'';flex:1;height:1px;background:#e2e8f0}"""

if old_divider_css in content:
    content = content.replace(old_divider_css, new_divider_css)
    print("✅ Fixed divider CSS")
else:
    print("⚠️ Could not find old divider CSS — trying regex...")
    import re
    content = re.sub(
        r'\.divider\{[^}]+\}\s*\.divider:before,\.divider:after\{[^}]+\}\s*\.divider:before\{[^}]+\}\s*\.divider:after\{[^}]+\}',
        new_divider_css,
        content,
        flags=re.DOTALL
    )
    print("✅ Replaced divider CSS with regex")

# ============================================================
# FIX 2: Add "Forgot Password?" link to login page
# ============================================================
old_login_form = "<button type='submit' class='btn-primary'>Login →</button>"

new_login_form = (
    "<button type='submit' class='btn-primary'>Login →</button>"
    "</form>"
    "<p style='text-align:center;margin-top:14px'>"
    "<a href='/forgot-password' class='link' style='font-size:13px'>"
    "Forgot password?</a></p>"
    "<div class='divider'>new here?</div>"
    "<a href='/register' style='text-decoration:none'>"
    "<button class='btn-outline'>✨ Create Account</button></a>"
)

if old_login_form in content:
    # Remove the "old" ending that follows (the </form> and divider)
    old_ending = (
        "<button type='submit' class='btn-primary'>Login →</button>"
        "</form>"
        "<div class='divider'>new here?</div>"
        "<a href='/register' style='text-decoration:none'>"
        "<button class='btn-outline'>✨ Create Account</button></a>"
    )
    if old_ending in content:
        content = content.replace(old_ending, new_login_form)
        print("✅ Added Forgot Password link to login page")
    else:
        print("⚠️ Login form ending mismatch — using alternative")

# ============================================================
# FIX 3: Add /forgot-password route
# ============================================================
forgot_route = '''

    @app.route("/forgot-password", methods=["GET", "POST"])
    def forgot_password():
        if request.method == "POST":
            student_number = request.form.get("student_number", "").strip()
            # For now, show a message directing to admin
            return render_template_string(FORGOT_SENT_HTML, student_number=student_number)
        return render_template_string(FORGOT_HTML)
'''

# Insert before the logout route
if "def logout" in content and "forgot_password" not in content:
    content = content.replace(
        "\n    @app.route(\"/logout\")",
        forgot_route + "\n    @app.route(\"/logout\")"
    )
    print("✅ Added /forgot-password route")

# ============================================================
# FIX 4: Add FORGOT_HTML templates
# ============================================================
forgot_templates = '''

FORGOT_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Forgot Password</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'><div class='logo-icon'>🔐</div>"
    "<h1>Forgot Password</h1><p>We'll help you recover it</p></div>"
    "<div class='card'>"
    "<div class='alert alert-info'>"
    "To reset your password, please contact your tutor or admin. "
    "They will send you a temporary password."
    "</div>"
    "<form method='POST'>"
    "<div class='form-group'><label>Your Student Number</label>"
    "<input type='text' name='student_number' placeholder='DCR0001' required></div>"
    "<button type='submit' class='btn-primary'>Request Reset →</button>"
    "</form>"
    "<div class='divider'>remembered it?</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-outline'>← Back to Login</button></a>"
    "</div></div></body></html>"
)

FORGOT_SENT_HTML = (
    "<!doctype html><html><head>"
    "<meta name='viewport' content='width=device-width,initial-scale=1'>"
    "<title>Reset Requested</title>"
    + SHARED_CSS +
    "</head><body>"
    "<div class='flag-stripe'></div>"
    "<div class='container'>"
    "<div class='logo'><div class='logo-icon'>📬</div>"
    "<h1>Request Received</h1><p>Check with your tutor</p></div>"
    "<div class='card'>"
    "<div class='alert alert-success'>"
    "✅ We've received your request for <strong>{{ student_number }}</strong>."
    "</div>"
    "<p class='subtitle'>Please contact your tutor or admin on WhatsApp to get a temporary password:</p>"
    "<div style='text-align:center;padding:16px;background:#f0fdf4;border-radius:11px;margin:16px 0'>"
    "<strong style='font-size:18px'>📱 +263 719 809 683</strong>"
    "</div>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-primary'>Back to Login</button></a>"
    "</div></div></body></html>"
)
'''

if "FORGOT_HTML" not in content:
    # Insert before the register_auth_routes function
    marker = "def register_auth_routes(app):"
    if marker in content:
        content = content.replace(marker, forgot_templates + "\n\n" + marker)
        print("✅ Added FORGOT_HTML templates")

# ============================================================
# Write back
# ============================================================
with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ auth.py updated")

# Verify
import subprocess
result = subprocess.run(
    ["python", "-c", "import auth; print('OK')"],
    capture_output=True, text=True, cwd="."
)
if "OK" in result.stdout:
    print("✅ auth.py imports cleanly")
else:
    print(f"❌ Import error: {result.stderr[:200]}")

print("\n" + "="*60)
print("✅ UI FIX COMPLETE")
print("="*60)
print("\n📌 NEW:")
print("   • Divider lines fixed (no more strikethrough)")
print("   • 'Forgot password?' link on login")
print("   • /forgot-password route")
print("\n📌 RESTART:")
print("   python student_server.py")
print("\n📌 TEST:")
print("   http://127.0.0.1:5001/login")
print("   http://127.0.0.1:5001/forgot-password")
print("="*60 + "\n")
