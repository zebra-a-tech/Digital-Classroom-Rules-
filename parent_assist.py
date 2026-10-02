"""Parent-Assist Flow for Grade 1-4 pupils.

When a Grade 1-4 pupil accesses a lesson, the parent receives
a helper prompt with clear instructions.

The parent is asked to:
1. Sit with the child
2. Read the lesson aloud
3. Help the child write in their notebook
4. Take a photo
5. Send the photo for marking
"""

import sqlite3
from datetime import datetime
from flask import request, render_template_string, redirect

DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
def get_parent_welcome_message(student_name, grade, subject, topic):
    """Return the warm welcome message for the parent."""
    return f"""
    👨‍👩‍👧 **Welcome, Parent or Guardian!**

    Your child **{student_name}** is about to learn **{subject} — {topic}** ({grade}).

    Here is what YOU need to do:

    ✅ **Step 1:** Sit with your child
    ✅ **Step 2:** Read the lesson together — slowly
    ✅ **Step 3:** Help them write the answers in their notebook
    ✅ **Step 4:** Take a clear photo of their work
    ✅ **Step 5:** Send the photo for marking

    Your support is the key to their success.
    Take your time — there is no rush.

    Ready? Let's begin! 🌟
    """


def get_parent_prompt_for_activity(topic):
    """Return the specific activity prompt."""
    return f"""
    ✍️ **Activity Time!**

    Please help your child:

    1. Open their notebook
    2. Write the answers to the activity about **{topic}**
    3. Write clearly and slowly
    4. Take a photo when finished

    We will check their work and send feedback soon.
    """


def register_parent_assist(app):
    """Register parent-assist routes."""

    @app.route("/student/<int:sid>/parent-assist/<int:lesson_id>")
    def parent_assist_view(sid, lesson_id):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        student = conn.execute(
            "SELECT * FROM students WHERE id = ?", (sid,)
        ).fetchone()

        lesson = conn.execute(
            "SELECT * FROM curriculum WHERE id = ?", (lesson_id,)
        ).fetchone()

        if not student or not lesson:
            conn.close()
            return "Not found", 404

        welcome = get_parent_welcome_message(
            student["name"],
            lesson["grade_form"],
            lesson["subject"],
            lesson["topic"],
        )
        activity = get_parent_prompt_for_activity(lesson["topic"])

        conn.close()

        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Parent-Assist Lesson</title>
            <style>
                body{font-family:Arial;background:#fff8e1;margin:0;color:#172033}
                .top{background:#f0ad4e;color:white;padding:20px}
                .wrap{max-width:850px;margin:auto;padding:18px}
                .card{background:white;padding:20px;margin:14px 0;border-radius:16px;box-shadow:0 3px 12px #0001}
                .welcome{background:#fff3cd;border-left:6px solid #f0ad4e;padding:20px;border-radius:12px;white-space:pre-wrap;line-height:1.6}
                .activity{background:#eaf7ee;border-left:6px solid #009b4d;padding:20px;border-radius:12px;white-space:pre-wrap;line-height:1.6;margin-top:15px}
                .upload{background:#eef4ff;padding:20px;border-radius:12px;margin-top:15px;text-align:center}
                button{background:#172554;color:white;padding:14px 28px;border:0;border-radius:11px;font-size:16px;font-weight:bold;cursor:pointer}
                .back{display:block;background:#222;color:white;padding:12px;border-radius:10px;text-align:center;text-decoration:none;margin-bottom:15px}
                input[type=file]{margin:10px 0;padding:10px}
            </style>
        </head>
        <body>
        <div class="top">
            <div style="font-size:22px;font-weight:bold;">👨‍👩‍👧 Parent-Assist Mode</div>
            <div>{{l['subject']}} — {{l['topic']}} ({{l['grade_form']}})</div>
        </div>
        <div class="wrap">
        <a class="back" href="/student/{{s['id']}}/home">← Back to Learning Centre</a>

        <div class="card">
            <div class="welcome">{{welcome}}</div>
            <div class="activity">{{activity}}</div>
        </div>

        <div class="card upload">
            <h3>📸 Send a Photo of Your Child's Work</h3>
            <p style="color:#5a6b7a;">Take a clear photo of the notebook page and submit it for marking.</p>
            <form method="POST" action="/student/{{s['id']}}/parent-assist/{{l['id']}}/submit" enctype="multipart/form-data">
                <input type="text" name="parent_name" placeholder="Your name (optional)" style="padding:10px;width:80%;margin:10px 0;border-radius:8px;border:1px solid #ccc;">
                <input type="file" name="work_photo" accept="image/*" required>
                <button type="submit">📤 Submit for Marking</button>
            </form>
        </div>
        </div>
        </body>
        </html>"""

        return render_template_string(html, s=student, l=lesson, welcome=welcome, activity=activity)

    @app.route("/student/<int:sid>/parent-assist/<int:lesson_id>/submit", methods=["POST"])
    def parent_assist_submit(sid, lesson_id):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        lesson = conn.execute(
            "SELECT * FROM curriculum WHERE id = ?", (lesson_id,)
        ).fetchone()

        if not lesson:
            conn.close()
            return "Lesson not found", 404

        parent_name = request.form.get("parent_name", "").strip()

        # Save the submission record (image upload handled separately)
        conn.execute("""
            INSERT INTO parent_assist_submissions
            (student_id, lesson_grade, lesson_subject, lesson_topic, parent_name)
            VALUES (?, ?, ?, ?, ?)
        """, (sid, lesson["grade_form"], lesson["subject"], lesson["topic"], parent_name))

        conn.commit()
        conn.close()

        html = """<!doctype html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width,initial-scale=1">
            <title>Submitted</title>
            <style>
                body{font-family:Arial;background:#eaf7ee;margin:0;color:#172033}
                .wrap{max-width:600px;margin:auto;padding:40px 18px;text-align:center}
                .card{background:white;padding:30px;border-radius:16px;box-shadow:0 3px 12px #0001}
                .tick{font-size:60px;margin:20px 0}
                h1{color:#155724}
                .back{display:inline-block;background:#172554;color:white;padding:12px 24px;border-radius:10px;text-decoration:none;margin-top:20px;font-weight:bold}
            </style>
        </head>
        <body>
        <div class="wrap">
        <div class="card">
            <div class="tick">✅</div>
            <h1>Thank You!</h1>
            <p>Your child's work has been submitted for marking.</p>
            <p>You will receive feedback soon.</p>
            <p style="margin-top:20px;">Keep up the great work! 🌟</p>
            <a class="back" href="/student/{{sid}}/home">Back to Home</a>
        </div>
        </div>
        </body>
        </html>"""

        return render_template_string(html, sid=sid)
