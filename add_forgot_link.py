"""Add Forgot Password link to login page — focused fix."""

FILE = "auth.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

print("✅ auth.py loaded")
print(f"   Size: {len(content)} bytes\n")

# Backup
with open("auth_before_forgot_link.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved\n")

# ============================================================
# 1. Check if Forgot link already exists
# ============================================================
if "forgot-password" in content:
    print("✅ Forgot password link is present in auth.py")
    print("   → The issue may be browser caching.")
    print("   → Try: hard refresh (clear browser cache) OR")
    print("   → Restart the server:")
    print("     python student_server.py")
    exit(0)

print("❌ Forgot password link NOT found in auth.py")
print("   Adding it now...\n")

# ============================================================
# 2. Find the LOGIN_HTML template
# ============================================================
login_template_start = content.find("LOGIN_HTML = (")

if login_template_start == -1:
    print("❌ Could not find LOGIN_HTML template")
    exit(1)

print(f"✅ Found LOGIN_HTML at position {login_template_start}")

# Find where LOGIN_HTML ends (next double-quote-close + ")")
# Search for the closing of the LOGIN_HTML tuple
login_template_end = content.find(")\n", login_template_start)
if login_template_end == -1:
    print("❌ Could not find end of LOGIN_HTML")
    exit(1)

login_template = content[login_template_start:login_template_end + 1]
print(f"✅ LOGIN_HTML is {len(login_template)} bytes")

# ============================================================
# 3. Find the exact ending pattern in LOGIN_HTML
# ============================================================
# Look for the "new here?" divider pattern
old_pattern = '<div class=\'divider\'>new here?</div>'

if old_pattern in login_template:
    print("✅ Found 'new here?' divider in LOGIN_HTML")
    
    # Add "Forgot password?" link just before the divider
    forgot_link = (
        "<p style='text-align:center;margin-top:14px;margin-bottom:0'>"
        "<a href='/forgot-password' class='link' style='font-size:13px'>"
        "Forgot password?</a></p>"
    )
    
    new_login_template = login_template.replace(
        old_pattern,
        forgot_link + old_pattern
    )
    
    # Replace in content
    content = content[:login_template_start] + new_login_template + content[login_template_end + 1:]
    print("✅ Added 'Forgot password?' link before 'new here?'")
else:
    print("⚠️ 'new here?' divider not found — trying alternate pattern")
    
    # Try alternate: find </form> and add after it
    form_close = "</form>"
    if form_close in login_template:
        # Find the SECOND </form> (login's, not register's)
        first_form = login_template.find(form_close)
        second_form = login_template.find(form_close, first_form + 1)
        
        if second_form != -1:
            forgot_link = (
                "<p style='text-align:center;margin-top:14px'>"
                "<a href='/forgot-password' class='link' style='font-size:13px'>"
                "Forgot password?</a></p>"
            )
            new_login_template = (
                login_template[:second_form + len(form_close)] 
                + forgot_link 
                + login_template[second_form + len(form_close):]
            )
            content = content[:login_template_start] + new_login_template + content[login_template_end + 1:]
            print("✅ Added Forgot link after form close")
        else:
            print("❌ Could not find form close")
            exit(1)
    else:
        print("❌ No divider or form found")
        exit(1)

# ============================================================
# 4. Add /forgot-password route if missing
# ============================================================
if "forgot_password" not in content:
    print("\n⚠️ /forgot-password route is missing — adding it...")
    
    forgot_route = '''

    @app.route("/forgot-password")
    def forgot_password():
        return render_template_string(FORGOT_HTML)

'''

    # Insert before logout route
    if 'def logout' in content:
        content = content.replace(
            "\n    @app.route(\"/logout\")",
            forgot_route + "\n    @app.route(\"/logout\")"
        )
        print("✅ Added /forgot-password route")

# ============================================================
# 5. Add FORGOT_HTML template if missing
# ============================================================
if "FORGOT_HTML" not in content:
    print("\n⚠️ FORGOT_HTML template missing — adding it...")
    
    forgot_template = '''

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
    "To reset your password, please contact your tutor or admin on WhatsApp."
    "</div>"
    "<div style='text-align:center;padding:20px;background:#f0fdf4;border-radius:11px;margin:20px 0'>"
    "<div style='font-size:14px;color:#5a6b7a;margin-bottom:8px'>WhatsApp your tutor:</div>"
    "<div style='font-size:22px;font-weight:800;color:#009b4d'>"
    "📱 +263 719 809 683</div>"
    "</div>"
    "<p class='subtitle'>Your tutor will send you a temporary password within 24 hours. "
    "Log in with the temporary password and change it in your profile.</p>"
    "<a href='/login' style='text-decoration:none'>"
    "<button class='btn-primary'>← Back to Login</button></a>"
    "</div></div></body></html>"
)
'''

    # Insert before def register_auth_routes
    marker = "def register_auth_routes(app):"
    if marker in content:
        content = content.replace(marker, forgot_template + "\n\n" + marker)
        print("✅ Added FORGOT_HTML template")

# ============================================================
# 6. Write back
# ============================================================
with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\n✅ auth.py updated")
print(f"   New size: {len(content)} bytes")

# ============================================================
# 7. Verify
# ============================================================
with open(FILE, "r", encoding="utf-8") as f:
    verify = f.read()

checks = {
    "Forgot password link in LOGIN_HTML": "forgot-password" in verify,
    "Forgot password route defined": "def forgot_password" in verify,
    "FORGOT_HTML template exists": "FORGOT_HTML =" in verify,
}

print("\n🔍 VERIFICATION:")
for k, v in checks.items():
    print(f"   {'✅' if v else '❌'} {k}")

# Test import
import subprocess
result = subprocess.run(
    ["python", "-c", "import auth; print('import OK')"],
    capture_output=True, text=True
)
if "import OK" in result.stdout:
    print("\n✅ auth.py imports cleanly")
else:
    print(f"\n❌ Import error: {result.stderr[:300]}")

print("\n" + "="*60)
print("✅ FORGOT PASSWORD LINK ADDED")
print("="*60)
print("\n📌 RESTART THE SERVER:")
print("   python student_server.py")
print("\n📌 THEN TEST:")
print("   http://127.0.0.1:5001/login")
print("   http://127.0.0.1:5001/forgot-password")
print("\n⚠️ IMPORTANT: Clear your browser cache!")
print("   In Chrome: long-press the refresh button →")
print("   'Empty cache and hard reload'")
print("="*60 + "\n")
