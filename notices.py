import re, sqlite3, os
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "digital_classroom.db")
PAT = re.compile(r"^/student/(\d+)/(home|trial|trial-lesson|paid|paid-lessons|centre)/?$")
LESSON_PAGES = {"trial", "trial-lesson", "paid", "paid-lessons", "centre", "home"}

def build(sid, page):
    from assignment_system import younger_grade, preparation_message
    c = sqlite3.connect(DB)
    try:
        row = c.execute("select grade_form, current_subject from students where id=?", (sid,)).fetchone()
    finally:
        c.close()
    if not row: return ""
    grade, subject = row[0], row[1]
    out = ""
    if younger_grade(grade):
        out += ("<div style='background:#fff7e6;border:1px solid #f5c26b;border-radius:14px;padding:12px 14px;margin:12px;color:#7a4b00'>"
                "👨‍👩‍👧 <b>Parent/Guardian Notice</b><br>For Grades 1–4, a parent or responsible adult should be present during the lesson "
                "to help the pupil follow instructions, read questions when necessary, and support the learning process.</div>")
    if page != "home" and subject:
        out += ("<div style='background:#f2fbf6;border:1px solid #b7dfc6;border-radius:14px;padding:12px 14px;margin:12px;color:#14532d'>"
                "🎒 <b>Before You Start</b><br>" + preparation_message(subject, "") + "</div>")
    return out

def register_notices(app):
    @app.after_request
    def _inject(resp):
        try:
            m = PAT.match(__import__("flask").request.path)
            if not m or resp.status_code != 200 or "text/html" not in (resp.content_type or ""):
                return resp
            html = resp.get_data(as_text=True)
            if "Parent/Guardian Notice" in html and "Before You Start" in html:
                return resp
            block = build(int(m.group(1)), m.group(2))
            if not block or block in html: return resp
            for anchor in ('<div class="hero">', '<div class="card">'):
                if anchor in html:
                    resp.set_data(html.replace(anchor, block + anchor, 1)); break
        except Exception as e:
            print("notice injection skipped:", e)
        return resp
