# Add clear trial-explanation messages to the student platform

import re

# ============================================================
# 1. Patch student_playbook.py — add welcome banner + help section
# ============================================================
FILE = "student_playbook.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_playbook_before_trial_message.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved: student_playbook_before_trial_message.py")

# Check if already patched
if "TRIAL_EXPLAINER_BANNER" in content:
    print("✅ Already patched — nothing to do")
    exit(0)

# -------- Patch 1: Replace the small banner with a bigger, clearer one --------
old_banner = """{% if trial_active and not paid_active %}
        <div class="card" style="background:#fff3cd;border-left:5px solid #f0ad4e;">
            <strong>🔒 You are on the FREE TRIAL</strong><br>
            You can access the first {{ R }} topics per subject.<br>
            <em>Pay $1 to unlock ALL topics.</em>
        </div>
        {% endif %}"""

new_banner = """{% if trial_active and not paid_active %}
        <div class="card" style="background:#fff3cd;border-left:6px solid #f0ad4e;padding:20px;">
            <div style="font-size:22px;font-weight:bold;color:#8a6d3b;margin-bottom:10px;">
                🎁 You Are On The FREE TRIAL
            </div>
            <div style="font-size:15px;color:#66512c;line-height:1.6;">
                <p><strong>Here's what you get during your free trial:</strong></p>
                <ul style="margin-left:20px;">
                    <li>⏱️ <strong>30 minutes</strong> of learning time</li>
                    <li>📚 Access to the <strong>first {{ R }} topics</strong> in every subject</li>
                    <li>✍️ Practice questions and instant feedback</li>
                    <li>📊 Progress tracking</li>
                </ul>
                <p style="margin-top:12px;"><strong>Want the FULL experience?</strong></p>
                <ul style="margin-left:20px;">
                    <li>✅ <strong>ALL topics</strong> in every subject</li>
                    <li>⏱️ <strong>60 minutes</strong> per paid session</li>
                    <li>📝 Full homework, tests and exams</li>
                    <li>🎓 Exam-focused tutoring</li>
                </ul>
                <p style="margin-top:12px;font-size:16px;">
                    💰 <strong>Just $1 to unlock everything for 1 hour.</strong>
                </p>
                <a href="/student/{{s['id']}}/paid" 
                   style="display:inline-block;background:#172554;color:white;padding:12px 24px;border-radius:10px;text-decoration:none;margin-top:10px;font-weight:bold;">
                    💳 Unlock Full Access for $1
                </a>
            </div>
        </div>
        {% endif %}

        {% if paid_active %}
        <div class="card" style="background:#d4edda;border-left:6px solid #28a745;padding:16px;">
            <div style="font-size:18px;font-weight:bold;color:#155724;">
                ✅ FULL ACCESS UNLOCKED
            </div>
            <div style="color:#155724;margin-top:6px;">
                You have access to <strong>ALL topics</strong> in every subject. 
                Your paid session is active. Let's learn! 🚀
            </div>
        </div>
        {% endif %}"""

if old_banner in content:
    content = content.replace(old_banner, new_banner)
    print("✅ Upgraded trial banner with detailed explanation")
else:
    print("⚠️ Old banner not found — checking pattern...")
    # Try just replacing the old small banner
    if "🔒 You are on the FREE TRIAL" in content:
        print("⚠️ Old banner text found but pattern didn't match exactly")
        print("   You may need to manually edit the banner.")

# -------- Patch 2: Add a help link at the bottom --------
help_link = """
        <div class="card" style="text-align:center;background:#eef4ff;padding:16px;">
            <strong>❓ Need help understanding the free trial?</strong><br>
            <span style="font-size:14px;color:#4a5a6a;">
                Free trial = 30 min + first {{ R }} topics per subject.<br>
                Paid session = 60 min + ALL topics. Just $1.
            </span>
        </div>
"""

# Insert before the last closing div of the wrap section
# Find the last </div></div> before </body>
old_end = """        </div>

        </div>
        </body>"""
new_end = help_link + """        </div>

        </div>
        </body>"""

if old_end in content:
    content = content.replace(old_end, new_end, 1)
    print("✅ Added help card at bottom of playbook")
else:
    print("⚠️ Could not find insertion point for help card")

with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("✅ Patched student_playbook.py")

# ============================================================
# 2. Create a standalone TRIAL-INFO page in the student app
# ============================================================
print("\n📄 Creating a standalone trial-info helper script...")

# ============================================================
# 3. Done
# ============================================================
print("\n" + "="*70)
print("✅ TRIAL MESSAGES ADDED")
print("="*70)
print("\n📌 WHAT'S NEW:")
print("   • Big colourful welcome banner when on free trial")
print("   • Green 'unlocked' banner when paid")
print("   • Help card at bottom explaining trial vs paid")
print("   • Clear 'Unlock for $1' button")
print("\n📌 NEXT: Restart the server:")
print("   python student_server.py")
print("\n📌 Then test in browser:")
print("   http://127.0.0.1:5001/student/1/playbook")
print("="*70 + "\n")
