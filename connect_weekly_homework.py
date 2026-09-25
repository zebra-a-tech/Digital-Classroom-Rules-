import re

FILE = "student_server.py"

with open(FILE, "r", encoding="utf-8") as f:
    content = f.read()

# Backup
with open("student_server_before_weekly_homework.py", "w", encoding="utf-8") as f:
    f.write(content)
print("✅ Backup saved: student_server_before_weekly_homework.py")

# Check if already patched
if "WEEKLY_HOMEWORK_ROUTE" in content:
    print("✅ Already patched — nothing to do")
    exit(0)

# ---------- Find the homework route ----------
homework_pattern = r'@app\.route\("/student/<int:sid>/homework"\)\s*\ndef homework\(sid\):'
match = re.search(homework_pattern, content)

if not match:
    print("❌ Could not find the /homework route")
    print("   Searching for any homework-related routes...")
    for m in re.finditer(r'@app\.route\("([^"]*homework[^"]*)"\)', content):
        print(f"   Found: {m.group(1)}")
    exit(1)

print(f"✅ Found /homework route at character {match.start()}")

# ---------- Prepare the NEW homework route ----------
NEW_HOMEWORK_ROUTE = '''
    @app.route("/student/<int:sid>/homework")
    def homework(sid):
        # WEEKLY_HOMEWORK_ROUTE — shows weekly assignments from the database
        s = student(sid)
        if not s:
            return "Student not found", 404

        conn = db()
        conn.row_factory = sqlite3.Row

        # Get all weekly assignments for this student
        assignments = conn.execute("""
            SELECT id, week_number, subject, topic, grade_form,
                   total_questions, score, percentage, completed,
                   generated_at, completed_at
            FROM weekly_assignments
            WHERE student_id = ?
            ORDER BY week_number DESC, subject ASC
        """, (sid,)).fetchall()

        conn.close()

        # Group by week
        weeks = {}
        for a in assignments:
            week = a["week_number"]
            if week not in weeks:
                weeks[week] = []
            weeks[week].append(a)

        # Build HTML
        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Weekly Assignments</title>
            <style>
                body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
                .top{background:#172554;color:white;padding:20px}
                .wrap{max-width:850px;margin:auto;padding:18px}
                .card{background:white;padding:18px;margin:12px 0;border-radius:16px;box-shadow:0 3px 12px #0001}
                .week-title{font-size:20px;font-weight:bold;color:#172554;margin:15px 0 8px}
                .assignment{background:#eef4ff;padding:14px;border-radius:12px;margin:8px 0}
                .assignment a{text-decoration:none;color:#172554;font-weight:bold}
                .meta{color:#5a6b7a;font-size:13px;margin-top:4px}
                .badge{display:inline-block;padding:3px 8px;border-radius:8px;font-size:11px;font-weight:bold;margin-left:8px}
                .badge.done{background:#d4edda;color:#155724}
                .badge.pending{background:#fff3cd;color:#856404}
                .back{display:block;background:#222;color:white;padding:12px;border-radius:10px;text-align:center;margin-bottom:15px;text-decoration:none}
                .empty{text-align:center;padding:30px;color:#5a6b7a}
                .stats{background:#f0f4ff;padding:12px;border-radius:10px;margin:10px 0}
            </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:24px;font-weight:bold;">📝 Weekly Assignments</div>
            <div>Complete your assignments to build mastery.</div>
        </div>
        <div class="wrap">
        <a class="back" href="/student/{{s['id']}}/home">← Back to Learning Centre</a>

        <div class="card">
            <h2>👋 {{s['name']}}'s Assignments</h2>
            <div class="stats">
                <strong>Total assignments:</strong> {{total_assignments}} |
                <strong>Completed:</strong> {{completed_count}} |
                <strong>Pending:</strong> {{pending_count}}
            </div>
        </div>

        {% if not weeks %}
            <div class="card empty">
                <h3>📚 No assignments yet</h3>
                <p>Your weekly assignments will appear here.</p>
                <p>Check back soon!</p>
            </div>
        {% endif %}

        {% for week_num, week_assignments in weeks.items() %}
            <div class="week-title">📅 Week {{week_num}}</div>
            {% for a in week_assignments %}
                <div class="assignment">
                    <a href="/student/{{s['id']}}/homework/{{a['id']}}">
                        📘 {{a['subject']}} — {{a['topic']}}
                    </a>
                    <div class="meta">
                        {{a['total_questions']}} questions · Grade: {{a['grade_form']}}
                        {% if a['completed'] %}
                            <span class="badge done">✅ Completed ({{a['percentage']}}%)</span>
                        {% else %}
                            <span class="badge pending">🟡 Not started</span>
                        {% endif %}
                    </div>
                </div>
            {% endfor %}
        {% endfor %}

        </div>
        </body>
        </html>"""

        return render_template_string(
            html,
            s=s,
            weeks=weeks,
            total_assignments=len(assignments),
            completed_count=sum(1 for a in assignments if a["completed"]),
            pending_count=sum(1 for a in assignments if not a["completed"])
        )

    # ====================================================
    # INDIVIDUAL ASSIGNMENT VIEW
    # ====================================================
    @app.route("/student/<int:sid>/homework/<int:assignment_id>")
    def homework_view(sid, assignment_id):
        # WEEKLY_HOMEWORK_ROUTE — shows one assignment's questions
        s = student(sid)
        if not s:
            return "Student not found", 404

        conn = db()
        conn.row_factory = sqlite3.Row

        assignment = conn.execute("""
            SELECT * FROM weekly_assignments
            WHERE id = ? AND student_id = ?
        """, (assignment_id, sid)).fetchone()

        if not assignment:
            conn.close()
            return "Assignment not found", 404

        questions = conn.execute("""
            SELECT * FROM weekly_assignment_questions
            WHERE assignment_id = ?
            ORDER BY question_number ASC
        """, (assignment_id,)).fetchall()

        conn.close()

        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>{{a['subject']}} — {{a['topic']}}</title>
            <style>
                body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
                .top{background:#172554;color:white;padding:20px}
                .wrap{max-width:800px;margin:auto;padding:18px}
                .card{background:white;padding:20px;margin:14px 0;border-radius:16px;box-shadow:0 3px 12px #0001}
                .question{background:#eef4ff;padding:16px;border-radius:12px;margin:12px 0}
                .qnum{font-weight:bold;color:#172554;margin-bottom:8px}
                input[type=text]{width:100%;box-sizing:border-box;padding:12px;border:1px solid #bbb;border-radius:10px;font-size:15px}
                button{width:100%;padding:14px;border:0;border-radius:11px;background:#172554;color:white;font-size:16px;margin-top:15px;font-weight:bold}
                .back{display:block;background:#222;color:white;padding:12px;border-radius:10px;text-align:center;text-decoration:none;margin-bottom:15px}
            </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:20px;font-weight:bold;">📝 {{a['subject']}} — {{a['topic']}}</div>
            <div>Week {{a['week_number']}} · {{a['total_questions']}} questions</div>
        </div>
        <div class="wrap">
        <a class="back" href="/student/{{s['id']}}/homework">← Back to Assignments</a>

        <form method="POST" action="/student/{{s['id']}}/homework/{{a['id']}}/submit">
        {% for q in questions %}
            <div class="card">
                <div class="question">
                    <div class="qnum">Q{{q['question_number']}}. {{q['question']}}</div>
                    <input type="text" name="q{{q['id']}}" placeholder="Your answer...">
                </div>
            </div>
        {% endfor %}
            <button type="submit">✅ Submit Assignment</button>
        </form>
        </div>
        </body>
        </html>"""

        return render_template_string(html, s=s, a=assignment, questions=questions)

    # ====================================================
    # SUBMIT ASSIGNMENT (auto-marking)
    # ====================================================
    @app.route("/student/<int:sid>/homework/<int:assignment_id>/submit", methods=["POST"])
    def homework_submit(sid, assignment_id):
        s = student(sid)
        if not s:
            return "Student not found", 404

        conn = db()
        conn.row_factory = sqlite3.Row

        assignment = conn.execute("""
            SELECT * FROM weekly_assignments WHERE id = ? AND student_id = ?
        """, (assignment_id, sid)).fetchone()

        if not assignment:
            conn.close()
            return "Assignment not found", 404

        questions = conn.execute("""
            SELECT * FROM weekly_assignment_questions
            WHERE assignment_id = ? ORDER BY question_number ASC
        """, (assignment_id,)).fetchall()

        # Mark each question
        total_marks = 0
        awarded = 0

        for q in questions:
            total_marks += 1
            student_answer = (request.form.get(f"q{q['id']}", "") or "").strip().lower()
            correct = (q["correct_answer"] or "").strip().lower()

            # Simple matching — check if the student answer contains the correct answer
            awarded_this = 0
            if student_answer:
                if student_answer == correct:
                    awarded_this = 1
                elif correct in student_answer or student_answer in correct:
                    awarded_this = 1

            awarded += awarded_this

            conn.execute("""
                UPDATE weekly_assignment_questions
                SET student_answer = ?, awarded_marks = ?
                WHERE id = ?
            """, (student_answer, awarded_this, q["id"]))

        percentage = (awarded / total_marks * 100) if total_marks > 0 else 0

        conn.execute("""
            UPDATE weekly_assignments
            SET score = ?, percentage = ?, completed = 1, completed_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (awarded, percentage, assignment_id))

        conn.commit()
        conn.close()

        # Show results
        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Assignment Result</title>
            <style>
                body{font-family:Arial;background:#f4f7fb;margin:0;color:#172033}
                .top{background:#172554;color:white;padding:20px}
                .wrap{max-width:800px;margin:auto;padding:18px}
                .card{background:white;padding:25px;margin:14px 0;border-radius:16px;box-shadow:0 3px 12px #0001;text-align:center}
                .score{font-size:48px;font-weight:bold;color:#172554}
                .pct{font-size:24px;color:#009b4d;font-weight:bold}
                .message{font-size:18px;margin:15px 0}
                .back{display:block;background:#172554;color:white;padding:14px;border-radius:10px;text-align:center;text-decoration:none;margin-top:20px;font-weight:bold}
            </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:22px;font-weight:bold;">📊 Assignment Complete</div>
        </div>
        <div class="wrap">
        <div class="card">
            <div class="score">{{awarded}} / {{total}}</div>
            <div class="pct">{{percentage}}%</div>
            <div class="message">
                {% if percentage >= 80 %}
                    🌟 Excellent! You're mastering this topic!
                {% elif percentage >= 60 %}
                    👍 Good work! Keep practising.
                {% else %}
                    💪 Keep going! Review the topic and try again.
                {% endif %}
            </div>
            <a class="back" href="/student/{{sid}}/homework">← Back to Assignments</a>
        </div>
        </div>
        </body>
        </html>"""

        return render_template_string(
            html,
            sid=sid,
            awarded=awarded,
            total=total_marks,
            percentage=round(percentage, 1)
        )
'''

# ---------- Replace the old homework route ----------
# Find where the old function ends (next @app.route)
old_start = match.start()
# Find the next @app.route after the match
next_route = content.find("@app.route", match.end())
if next_route == -1:
    # If it's the last route, replace to the end
    new_content = content[:old_start] + NEW_HOMEWORK_ROUTE
else:
    new_content = content[:old_start] + NEW_HOMEWORK_ROUTE + "\n\n" + content[next_route:]

with open(FILE, "w", encoding="utf-8") as f:
    f.write(new_content)

print("✅ Replaced /homework route with the weekly assignment system")
print("\n" + "="*70)
print("✅ WEEKLY HOMEWORK CONNECTED")
print("="*70)
print("\n📌 NEW ROUTES:")
print("   GET  /student/<sid>/homework")
print("   GET  /student/<sid>/homework/<assignment_id>")
print("   POST /student/<sid>/homework/<assignment_id>/submit")
print("\n📌 NEXT: Restart the server:")
print("   python student_server.py")
print("\n📌 Then open:")
print("   http://127.0.0.1:5001/student/1/homework")
print("="*70 + "\n")
