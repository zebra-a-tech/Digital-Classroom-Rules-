import re, py_compile

with open("welcome_and_referrals.py", "r", encoding="utf-8") as f:
    w_code = f.read()

# Make welcome_page the direct handler for both '/' and '/welcome'
w_code = w_code.replace('@app.route("/welcome")', '@app.route("/welcome")\n    @app.route("/")')
w_code = w_code.replace(
    'def welcome_page():',
    'def welcome_page():\n        if request.cookies.get("dcr_consent") == "1":\n            return redirect("/login")'
)

with open("welcome_and_referrals.py", "w", encoding="utf-8") as f:
    f.write(w_code)

# Ensure student_server imports and registers welcome_and_referrals
with open("student_server.py", "r", encoding="utf-8") as f:
    s_code = f.read()

# Clean out any old site_index or duplicate @app.route("/")
s_code = re.sub(r'@app\.route\(["\']\/["\']\)\s+def site_index[\s\S]*?(?=\n@app|\n\ndef |\nimport |\Z)', '', s_code)

# Add registration right after app = Flask(__name__)
if "welcome_and_referrals.register_welcome_and_referrals(app)" not in s_code:
    s_code = s_code.replace(
        "app = Flask(__name__)",
        "app = Flask(__name__)\nimport welcome_and_referrals\nwelcome_and_referrals.register_welcome_and_referrals(app)\nimport novel_reader\nnovel_reader.register_novel_reader(app)\n"
    )

with open("student_server.py", "w", encoding="utf-8") as f:
    f.write(s_code)

py_compile.compile("welcome_and_referrals.py", doraise=True)
py_compile.compile("student_server.py", doraise=True)
py_compile.compile("auth.py", doraise=True)
print("🎉 Landing portal, smart cookie bypass, and novel library successfully compiled with ZERO errors!")
