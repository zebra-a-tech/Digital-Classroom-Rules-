# Implement Model B: Restricted Free Trial
# - Free trial: only first 3 topics per subject
# - Paid session: all topics

import re

FILE = "student_playbook.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_playbook_before_trial_restrict.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved")

# Check if already patched
if "RESTRICTED_TRIAL_TOPICS_PER_SUBJECT" in content:
    print("✅ Already patched — nothing to do")
    exit(0)

# -------- Patch 1: Add constant at the top --------
# Insert after imports (find first non-import line)
lines = content.split("\n")
last_import = 0
for i, line in enumerate(lines[:50]):
    if line.strip().startswith(("import ", "from ")):
        last_import = i

constant = """

# ============================================================
# RESTRICTED TRIAL SETTINGS
# ============================================================
# During the free trial, students can access ONLY the first N topics
# per subject. Paid sessions unlock ALL topics.
RESTRICTED_TRIAL_TOPICS_PER_SUBJECT = 3
"""
lines.insert(last_import + 1, constant)
content = "\n".join(lines)

# -------- Patch 2: Filter topics in playbook_home --------
# Find the section that lists topics and add filtering
old_section = "subjects=SUBJECTS,\n            topics=topics_for"
new_section = """subjects=SUBJECTS,
            topics=topics_for,
            trial_active=trial_active,
            paid_active=bool(paid)"""

if old_section in content:
    content = content.replace(old_section, new_section, 1)
    print("✅ Added trial/paid context to playbook_home template")

# -------- Patch 3: Filter topics in template --------
# The template uses topics(subject) — we need to make it aware
# We add a helper function to filter trial topics
helper = """

def _filter_topics_for_trial(subject, topics_list, trial_active, paid_active):
    \"\"\"During trial (not paid), only show first N topics per subject.\"\"\"
    if paid_active:
        return topics_list  # full access
    if trial_active:
        return topics_list[:RESTRICTED_TRIAL_TOPICS_PER_SUBJECT]
    return []  # neither trial nor paid → nothing
"""

# Insert helper right before register_student_playbook
helper_insert_point = content.find("def register_student_playbook(app):")
if helper_insert_point > 0:
    content = content[:helper_insert_point] + helper + "\n" + content[helper_insert_point:]
    print("✅ Added _filter_topics_for_trial helper")

# -------- Patch 4: Modify the template to use filtered topics --------
# The template does `{% for topic in topics(subject) %}`
# We change it to `{% for topic in _filter_topics_for_trial(subject, topics(subject), trial_active, paid_active) %}`
old_template_loop = "{% for topic in topics(subject) %}"
new_template_loop = "{% for topic in _filter_topics_for_trial(subject, topics(subject), trial_active, paid_active) %}"

if old_template_loop in content:
    content = content.replace(old_template_loop, new_template_loop)
    print("✅ Updated template loop to use filtered topics")
else:
    print("⚠️ Template loop pattern not found — manual patch may be needed")

# -------- Patch 5: Add banner to trial page --------
# Show a "You're on trial — only 3 topics visible" banner
trial_banner = """
        {% if trial_active and not paid_active %}
        <div class="card" style="background:#fff3cd;border-left:5px solid #f0ad4e;">
            <strong>🔒 You are on the FREE TRIAL</strong><br>
            You can access the first {{ R }} topics per subject.<br>
            <em>Pay $1 to unlock ALL topics.</em>
        </div>
        {% endif %}
"""

# Insert banner right after <div class="wrap">
old_wrap = '<div class="wrap">'
new_wrap = '<div class="wrap">\n' + trial_banner

if old_wrap in content and trial_banner not in content:
    content = content.replace(old_wrap, new_wrap, 1)
    print("✅ Added trial banner to playbook")

# Pass R to template
old_render = "return render_template_string(\n            html,\n            s=s,\n            subjects=SUBJECTS,\n            topics=topics_for,\n            trial_active=trial_active,\n            paid_active=bool(paid)"
new_render = "return render_template_string(\n            html,\n            s=s,\n            subjects=SUBJECTS,\n            topics=topics_for,\n            trial_active=trial_active,\n            paid_active=bool(paid),\n            R=RESTRICTED_TRIAL_TOPICS_PER_SUBJECT"

if old_render in content:
    content = content.replace(old_render, new_render)
    print("✅ Passed R to template")

# Write back
with open(FILE, "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*70)
print("✅ RESTRICTED TRIAL IMPLEMENTED")
print("="*70)
print("\n📌 WHAT CHANGED:")
print("   • Free trial: only 3 topics per subject visible")
print("   • Paid session: ALL topics visible")
print("   • Trial banner shows at top of playbook")
print("\n📌 NEXT: Restart the server:")
print("   python student_server.py")
print("\n📌 Then test in browser:")
print("   http://127.0.0.1:5001/student/1/playbook")
print("="*70 + "\n")
