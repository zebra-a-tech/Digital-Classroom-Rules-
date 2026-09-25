

from .intelligence import (
    teach,
    detect_topic,
    get_subjects
)


def register_intelligence_routes(app):

    @app.route(
        "/tutor/<int:student_id>/learn",
        methods=["POST"]
    )
    def intelligent_tutor(student_id):

        subject = request.form.get(
            "subject",
            ""
        ).strip()

        message = request.form.get(
            "message",
            ""
        ).strip()

        if not subject:

            subjects = get_subjects(student_id)

            if subjects:
                subject = subjects[0]

        response = teach(
            student_id,
            subject,
            message
        )

        return f"""
<!DOCTYPE html>

<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Digital Classroom Tutor</title>

<style>

body {{
    font-family:Arial,sans-serif;
    background:#f4f6f8;
    padding:15px;
}}

.box {{
    background:white;
    padding:20px;
    border-radius:16px;
}}

.response {{
    background:#eef2ff;
    padding:18px;
    border-radius:12px;
    white-space:pre-line;
    line-height:1.65;
}}

input, textarea {{
    width:100%;
    box-sizing:border-box;
    padding:13px;
    margin-top:10px;
    border:1px solid #ddd;
    border-radius:9px;
    font-size:16px;
}}

button {{
    width:100%;
    padding:15px;
    margin-top:12px;
    background:#111827;
    color:white;
    border:0;
    border-radius:9px;
    font-weight:bold;
}}

a {{
    display:block;
    text-align:center;
    margin-top:15px;
}}

</style>

</head>

<body>

<div class="box">

<h1>👨‍🏫 Digital Classroom Tutor</h1>

<div class="response">
{response}
</div>

<form method="POST"
action="/tutor/{student_id}/learn">

<input
name="subject"
value="{subject}"
placeholder="Subject">

<textarea
name="message"
rows="4"
placeholder="Ask your tutor..."></textarea>

<button>
📚 CONTINUE LEARNING
</button>

</form>

<a href="/student/{student_id}">
⬅ Student Profile
</a>

</div>

</body>

</html>
"""
