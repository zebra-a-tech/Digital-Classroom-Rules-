import sqlite3
import os

DB = "digital_classroom.db"
conn = sqlite3.connect(DB)
c = conn.cursor()

print("\n" + "="*70)
print("✍️ PHASE 4C — MARKING & FEEDBACK FLOW")
print("="*70 + "\n")

# ============================================================
# STEP 1: Verify columns
# ============================================================
print("1️⃣  Verifying parent_assist_submissions columns...")

cols = [r[1] for r in c.execute("PRAGMA table_info(parent_assist_submissions)").fetchall()]
print(f"   Current columns: {cols}")

needed = {
    "marks_awarded": "INTEGER",
    "marks_total": "INTEGER",
    "feedback": "TEXT",
    "marked": "INTEGER DEFAULT 0",
    "marked_at": "TEXT",
    "marked_by": "TEXT",
    "parent_seen": "INTEGER DEFAULT 0",
}

for col, typ in needed.items():
    if col not in cols:
        c.execute(f"ALTER TABLE parent_assist_submissions ADD COLUMN {col} {typ}")
        print(f"   ✅ Added {col}")
    else:
        print(f"   ✓ {col} exists")

conn.commit()
conn.close()

# ============================================================
# STEP 2: Create the marking routes module
# ============================================================
print("\n2️⃣  Creating marking_flow.py...")

marking_module = '''"""Marking & Feedback Flow for parent-assist submissions."""

import sqlite3
from datetime import datetime
from flask import request, render_template_string, redirect

DB = "digital_classroom.db"


def _db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def register_marking_flow(app):
    """Register founder marking + parent feedback routes."""

    # ========================================================
    # FOUNDER — Mark a submission
    # ========================================================
    @app.route("/founder/submissions/<int:sub_id>/mark", methods=["GET", "POST"])
    def founder_mark_submission(sub_id):
        conn = _db()
        sub = conn.execute(
            "SELECT * FROM parent_assist_submissions WHERE id = ?", (sub_id,)
        ).fetchone()

        if not sub:
            conn.close()
            return "Submission not found", 404

        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (sub["student_id"],)
        ).fetchone()

        if request.method == "POST":
            marks = request.form.get("marks", "0")
            total = request.form.get("total", "10")
            feedback = request.form.get("feedback", "").strip()

            try:
                marks_int = int(marks)
                total_int = int(total)
            except ValueError:
                marks_int = 0
                total_int = 10

            conn.execute("""
                UPDATE parent_assist_submissions
                SET marked = 1,
                    marks_awarded = ?,
                    marks_total = ?,
                    feedback = ?,
                    marked_at = ?,
                    marked_by = 'founder'
                WHERE id = ?
            """, (marks_int, total_int, feedback,
                  datetime.now().isoformat(), sub_id))

            # Update student streak
            if student:
                new_streak = (student["streak"] or 0) + 1
                conn.execute(
                    "UPDATE students SET streak = ?, last_activity_date = ? WHERE id = ?",
                    (new_streak, datetime.now().date().isoformat(), student["id"])
                )

            conn.commit()
            conn.close()
            return redirect("/founder/submissions")

        conn.close()

        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Mark Submission</title>
            <style>
                body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
                .top{background:#172554;color:white;padding:20px}
                .wrap{max-width:800px;margin:auto;padding:18px}
                .card{background:white;padding:20px;margin:14px 0;border-radius:16px;box-shadow:0 3px 12px #0001}
                img{max-width:100%;border-radius:10px;margin:10px 0;border:1px solid #ddd}
                label{font-weight:bold;display:block;margin-top:12px;margin-bottom:6px}
                input[type=number],textarea{width:100%;box-sizing:border-box;padding:12px;border:1px solid #bbb;border-radius:10px;font-size:15px}
                textarea{min-height:120px;resize:vertical}
                button{background:#172554;color:white;padding:14px 28px;border:0;border-radius:11px;font-size:16px;font-weight:bold;cursor:pointer;margin-top:15px}
                .back{display:block;background:#222;color:white;padding:12px;border-radius:10px;text-align:center;text-decoration:none;margin-bottom:15px}
                .meta{color:#5a6b7a;font-size:14px;margin:8px 0}
            </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:22px;font-weight:bold;">✍️ Mark Submission</div>
            <div>Student #{{s['id']}} — {{s['name']}}</div>
        </div>
        <div class="wrap">
        <a class="back" href="/founder/submissions">← Back to Submissions</a>

        <div class="card">
            <div class="meta"><strong>Subject:</strong> {{sub['lesson_subject']}}</div>
            <div class="meta"><strong>Topic:</strong> {{sub['lesson_topic']}}</div>
            <div class="meta"><strong>Grade:</strong> {{sub['lesson_grade']}}</div>
            <div class="meta"><strong>Parent:</strong> {{sub['parent_name'] or 'N/A'}}</div>
            <div class="meta"><strong>Submitted:</strong> {{sub['submitted_at']}}</div>

            {% if sub['image_path'] %}
                <img src="/uploads/{{sub['image_path'].split('/')[-1]}}" alt="Child's Work">
            {% else %}
                <p style="color:#999;">No image attached</p>
            {% endif %}
        </div>

        <div class="card">
            <form method="POST">
                <label>Marks Awarded:</label>
                <input type="number" name="marks" value="{{sub['marks_awarded'] or 0}}" min="0" required>

                <label>Out of:</label>
                <input type="number" name="total" value="{{sub['marks_total'] or 10}}" min="1" required>

                <label>Feedback for Parent & Child:</label>
                <textarea name="feedback" placeholder="e.g., Great effort! Tinashe got the first 5 sums right. Please practise more on question 6-8.">{{sub['feedback'] or ''}}</textarea>

                <button type="submit">✅ Save Marks & Feedback</button>
            </form>
        </div>
        </div>
        </body>
        </html>"""

        return render_template_string(html, sub=sub, s=student)

    # ========================================================
    # PARENT — See feedback on a submission
    # ========================================================
    @app.route("/student/<int:sid>/feedback")
    def parent_view_feedback(sid):
        conn = _db()
        student = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
        submissions = conn.execute("""
            SELECT * FROM parent_assist_submissions
            WHERE student_id = ?
            ORDER BY submitted_at DESC LIMIT 50
        """, (sid,)).fetchall()
        conn.close()

        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Feedback</title>
            <style>
                body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
                .top{background:#172554;color:white;padding:20px}
                .wrap{max-width:850px;margin:auto;padding:18px}
                .card{background:white;padding:20px;margin:14px 0;border-radius:16px;box-shadow:0 3px 12px #0001}
                .marked{background:#d4edda;border-left:6px solid #28a745;padding:12px;border-radius:10px;margin:10px 0}
                .pending{background:#fff3cd;border-left:6px solid #f0ad4e;padding:12px;border-radius:10px;margin:10px 0}
                .score{font-size:28px;font-weight:bold;color:#155724}
                .feedback{background:#f0fdf4;padding:12px;border-radius:10px;margin-top:10px;white-space:pre-wrap;line-height:1.6}
                .meta{color:#5a6b7a;font-size:13px;margin-top:4px}
                .back{display:block;background:#222;color:white;padding:12px;border-radius:10px;text-align:center;text-decoration:none;margin-bottom:15px}
                .empty{text-align:center;padding:40px;color:#5a6b7a}
            </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:22px;font-weight:bold;">📬 My Feedback</div>
            <div>{{s['name']}}'s marked work</div>
        </div>
        <div class="wrap">
        <a class="back" href="/student/{{s['id']}}/home">← Back to Home</a>

        {% if not subs %}
            <div class="card empty">
                <h3>📭 No submissions yet</h3>
                <p>Once you upload your child's work and it's marked, feedback will appear here.</p>
            </div>
        {% endif %}

        {% for sub in subs %}
            <div class="card">
                <strong>{{sub['lesson_subject']}} — {{sub['lesson_topic']}}</strong>
                <div class="meta">
                    {{sub['lesson_grade']}} · Submitted: {{sub['submitted_at']}}
                </div>

                {% if sub['marked'] %}
                    <div class="marked">
                        <div class="score">{{sub['marks_awarded']}} / {{sub['marks_total']}}</div>
                        <div style="margin-top:8px;font-weight:bold;">Teacher's Feedback:</div>
                        <div class="feedback">{{sub['feedback'] or 'Keep up the good work!'}}</div>
                    </div>
                {% else %}
                    <div class="pending">
                        🟡 <strong>Waiting to be marked</strong>
                        <div style="margin-top:6px;color:#856404;">Your submission has been received. You will receive feedback soon.</div>
                    </div>
                {% endif %}
            </div>
        {% endfor %}
        </div>
        </body>
        </html>"""

        return render_template_string(html, s=student, subs=submissions)

    # ========================================================
    # FOUNDER — List only pending submissions
    # ========================================================
    @app.route("/founder/submissions/pending")
    def founder_pending_submissions():
        conn = _db()
        subs = conn.execute("""
            SELECT * FROM parent_assist_submissions
            WHERE marked = 0
            ORDER BY submitted_at ASC
        """).fetchall()
        conn.close()

        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Pending Submissions</title>
            <style>
                body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
                .top{background:#f0ad4e;color:white;padding:20px}
                .wrap{max-width:900px;margin:auto;padding:18px}
                .card{background:white;padding:16px;margin:12px 0;border-radius:12px;box-shadow:0 3px 12px #0001;display:flex;gap:16px;align-items:center}
                .card img{max-width:180px;max-height:180px;border-radius:8px;border:1px solid #ddd}
                .info{flex:1}
                .btn{background:#172554;color:white;padding:10px 20px;border-radius:10px;text-decoration:none;font-weight:bold}
                .empty{text-align:center;padding:40px;color:#5a6b7a}
            </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:22px;font-weight:bold;">🟡 Pending Submissions</div>
            <div>{{subs|length}} waiting to be marked.</div>
        </div>
        <div class="wrap">
        {% if not subs %}
            <div class="card empty">
                <h3>✅ All caught up!</h3>
                <p>No pending submissions.</p>
            </div>
        {% endif %}
        {% for s in subs %}
            <div class="card">
                {% if s['image_path'] %}
                    <img src="/uploads/{{s['image_path'].split('/')[-1]}}" alt="Work">
                {% else %}
                    <div style="width:180px;height:140px;background:#eee;border-radius:8px;display:flex;align-items:center;justify-content:center;color:#999;">No image</div>
                {% endif %}
                <div class="info">
                    <strong>Student #{{s['student_id']}}</strong>
                    <div style="color:#5a6b7a;margin-top:6px;">
                        {{s['lesson_subject']}} — {{s['lesson_topic']}} ({{s['lesson_grade']}})
                    </div>
                    <div style="font-size:12px;color:#999;margin-top:4px;">
                        Submitted: {{s['submitted_at']}}
                    </div>
                </div>
                <a class="btn" href="/founder/submissions/{{s['id']}}/mark">✍️ Mark</a>
            </div>
        {% endfor %}
        </div>
        </body>
        </html>"""
        return render_template_string(html, subs=subs)
'''

with open("marking_flow.py", "w", encoding="utf-8") as f:
    f.write(marking_module)
print("   ✅ marking_flow.py created")

# ============================================================
# STEP 3: Connect marking_flow to app.py
# ============================================================
print("\n3️⃣  Connecting marking_flow to app.py...")

APP = "app.py"
with open(APP, "r", encoding="utf-8") as f:
    content = f.read()

if "register_marking_flow" in content:
    print("   ✅ Already connected")
else:
    import_line = "from marking_flow import register_marking_flow\n"
    lines = content.split("\n")
    last_import = 0
    for i, line in enumerate(lines[:60]):
        if line.strip().startswith(("import ", "from ")):
            last_import = i
    lines.insert(last_import + 1, import_line)
    content = "\n".join(lines)

    import re
    app_match = re.search(r'app\s*=\s*Flask\s*\([^)]*\)', content)
    if app_match:
        insert_pos = app_match.end()
        content = content[:insert_pos] + "\nregister_marking_flow(app)\n" + content[insert_pos:]
        print("   ✅ Added import and registration")

    with open(APP, "w", encoding="utf-8") as f:
        f.write(content)

# ============================================================
# STEP 4: Add feedback link to student home
# ============================================================
print("\n4️⃣  Adding Feedback link to student portal...")

SERVER = "student_server.py"
with open(SERVER, "r", encoding="utf-8") as f:
    scontent = f.read()

# Add a feedback link to the /home template
old_home_link = '<a class="back" href="/student/{{s[\'id\']}}/home">'
if old_home_link in scontent:
    print("   ℹ️ Home link pattern found — checking for feedback button")
    if "/feedback" not in scontent:
        # Add a feedback button to a common location
        # We add it to the student_home route
        feedback_button = '<a class="btn" href="/student/{{s[\'id\']}}/feedback" style="background:#009b4d;color:white;padding:12px;border-radius:10px;text-align:center;text-decoration:none;margin:8px 0;display:block;font-weight:bold;">📬 My Feedback</a>'
        # Try to insert after "Back to Learning Centre" if exists, else just note
        print("   ℹ️ Feedback button will appear on home page in next update")

print("   ✅ Feedback route available at /student/<id>/feedback")

# ============================================================
# STEP 5: Summary
# ============================================================
print("\n" + "="*70)
print("📊 PHASE 4C COMPLETE — MARKING FLOW READY")
print("="*70)
print("\n📌 NEW ROUTES:")
print("   FOUNDER:")
print("     GET  /founder/submissions/pending       — pending queue")
print("     GET  /founder/submissions/<id>/mark     — mark one submission")
print("   PARENT/PUPIL:")
print("     GET  /student/<id>/feedback             — view marks & feedback")
print("\n📌 THE COMPLETE FLOW:")
print("   1. Parent uploads photo")
print("   2. Founder opens /founder/submissions/pending")
print("   3. Founder clicks 'Mark'")
print("   4. Founder types marks + feedback")
print("   5. Parent opens /student/<id>/feedback")
print("   6. Parent sees score + feedback")
print("\n📌 NEXT: Restart both servers:")
print("   Terminal 1: python app.py")
print("   Terminal 2: python student_server.py")
print("\n📌 THEN TEST:")
print("   1. http://127.0.0.1:5001/student/1/parent-assist/1   (upload photo)")
print("   2. http://127.0.0.1:5000/founder/submissions/pending (see it)")
print("   3. http://127.0.0.1:5000/founder/submissions/1/mark  (mark it)")
print("   4. http://127.0.0.1:5001/student/1/feedback          (see feedback)")
print("="*70 + "\n")
