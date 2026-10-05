
"""
Digital Classroom Rules
Premium Assignment + Handwritten Work System

This module extends the existing platform.

It does NOT replace the curriculum, tutor engine, homework,
progress system or paid-access system.
"""

from pathlib import Path
import sqlite3
import secrets
import mimetypes
from datetime import datetime
from assignment_integration import integrate_assignment_result
from flask import (
    Blueprint,
    request,
    redirect,
    url_for,
    render_template_string,
    abort,
)

ROOT = Path(__file__).resolve().parent
DB = ROOT / "digital_classroom.db"

UPLOAD_ROOT = ROOT / "student_work_uploads"
UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)

MAX_DEFAULT_MB = 10

ALLOWED_EXTENSIONS = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


bp = Blueprint("assignment_system", __name__)


def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def now():
    return datetime.now().isoformat(timespec="seconds")


def student_or_404(conn, sid):
    student = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (sid,),
    ).fetchone()

    if not student:
        abort(404)

    return student


def younger_grade(grade_form):
    value = (grade_form or "").strip().upper()

    return value in {
        "GRADE 1",
        "GRADE 2",
        "GRADE 3",
        "GRADE 4",
        "1",
        "2",
        "3",
        "4",
        "G1",
        "G2",
        "G3",
        "G4",
    }


def preparation_materials(subject="", topic="", calculator_allowed=False,
                           calculator_required=False):
    subject = (subject or "").strip().lower()

    materials = [
        "📕 Dedicated exercise/book",
        "✏️ Pen/pencil",
    ]

    if subject in {
        "maths",
        "mathematics",
        "science",
        "geography",
        "physics",
        "chemistry",
        "accounting",
    }:
        materials.append("📏 Ruler")

    if calculator_required:
        materials.append("🧮 Calculator")

    elif calculator_allowed:
        materials.append("🧮 Calculator if useful for this activity")

    return materials


def preparation_message(subject, topic, calculator_allowed=False,
                        calculator_required=False):

    subject = (subject or "").strip()

    if subject.lower() in {"maths", "mathematics"}:
        text = (
            "Please have your dedicated Maths book, pen/pencil and ruler "
            "ready."
        )

    elif subject.lower() == "english":
        text = "Please have your English exercise book and pen/pencil ready."

    elif subject.lower() == "science":
        text = (
            "Please have your Science book, pen/pencil and ruler "
            "where required."
        )

    elif subject.lower() == "geography":
        text = (
            "Please have your Geography book, pen/pencil and ruler "
            "where required."
        )

    elif subject.lower() == "accounting":
        text = (
            "Please have your Accounting book, pen/pencil and calculator "
            "where required."
        )

    elif subject.lower() in {"physics", "chemistry"}:
        text = (
            f"Please have your {subject} exercise book, pen/pencil, "
            "ruler and calculator where required."
        )

    else:
        text = (
            f"Please have your {subject or 'subject'} exercise book "
            "and pen/pencil ready."
        )

    if calculator_required:
        text += " A calculator is required for this activity."
    elif calculator_allowed:
        text += " A calculator may be used where appropriate."

    return text


def parent_notice(grade_form):
    if not younger_grade(grade_form):
        return ""

    return """
    <div class="parent-notice">
        <div class="notice-icon">👨‍👩‍👧</div>
        <div>
            <strong>Parent/Guardian Notice</strong>
            <p>
                For Grades 1–4, a parent or responsible adult should be
                present during the lesson to help the pupil follow
                instructions, read questions when necessary, and support
                the learning process.
            </p>
        </div>
    </div>
    """


def table_columns(conn, table):
    return {
        row[1]
        for row in conn.execute(
            f'PRAGMA table_info("{table}")'
        ).fetchall()
    }


def assignment_info(conn, assignment_id):
    cols = table_columns(conn, "assignments")

    row = conn.execute(
        "SELECT * FROM assignments WHERE id=?",
        (assignment_id,),
    ).fetchone()

    if not row:
        abort(404)

    data = dict(row)

    def first(*names, default=None):
        for name in names:
            if name in cols and data.get(name) not in (None, ""):
                return data.get(name)
        return default

    data["_subject"] = first("subject", "lesson_subject", default="")
    data["_topic"] = first("topic", "lesson_topic", default="")
    data["_grade"] = first("grade_form", "lesson_grade", default="")
    data["_title"] = first(
        "title",
        "name",
        "assignment_name",
        default=f"Assignment #{assignment_id}",
    )

    data["_instructions"] = first(
        "instructions",
        "description",
        "content",
        default="Complete the assignment carefully.",
    )

    data["_requires_work"] = bool(
        first("requires_work_upload", default=0)
    )

    data["_requires_photo"] = bool(
        first("requires_photo_upload", default=0)
    )

    data["_max_photos"] = int(
        first("max_photos", default=1) or 1
    )

    data["_max_upload_mb"] = int(
        first("max_upload_mb", default=MAX_DEFAULT_MB)
        or MAX_DEFAULT_MB
    )

    data["_calculator_allowed"] = bool(
        first("calculator_allowed", default=0)
    )

    data["_calculator_required"] = bool(
        first("calculator_required", default=0)
    )

    data["_materials"] = first(
        "required_materials",
        default=""
    )

    data["_max_marks"] = float(
        first("max_marks", "total_marks", default=10)
        or 10
    )

    data["_resubmission"] = bool(
        first("resubmission_allowed", default=1)
    )

    return data


def ensure_student_owns_submission(conn, sid, submission_id):
    row = conn.execute(
        """
        SELECT s.*, a.id AS assignment_real_id
        FROM assignment_submissions s
        JOIN assignments a ON a.id=s.assignment_id
        WHERE s.id=? AND s.student_id=?
        """,
        (submission_id, sid),
    ).fetchone()

    if not row:
        abort(404)

    return row


def render_page(title, body):
    return render_template_string(
        PAGE,
        title=title,
        body=body,
    )


@bp.route("/student/<int:sid>/assignments")
def student_assignments(sid):

    conn = db()

    student = student_or_404(conn, sid)

    rows = conn.execute(
        "SELECT * FROM assignments ORDER BY id DESC"
    ).fetchall()

    cards = []

    for row in rows:
        assignment = dict(row)

        cols = set(row.keys())

        subject = assignment.get("subject", "")
        topic = assignment.get("topic", "")
        title = (
            assignment.get("title")
            or assignment.get("name")
            or assignment.get("assignment_name")
            or f"Assignment #{assignment['id']}"
        )

        cards.append(
            f"""
            <a class="assignment-card"
               href="/student/{sid}/assignment/{assignment['id']}">

                <div class="card-top">
                    <span class="subject-pill">
                        {subject or 'Learning'}
                    </span>
                </div>

                <h3>{title}</h3>

                <p>{topic or 'Practice and demonstrate your learning.'}</p>

                <div class="card-arrow">→</div>
            </a>
            """
        )

    if not cards:
        content = """
        <div class="empty-state">
            <div class="empty-icon">📚</div>
            <h2>No assignments yet</h2>
            <p>Your tutor will add assignments here when they are ready.</p>
        </div>
        """
    else:
        content = f"""
        <section class="hero-card">
            <span class="eyebrow">STUDENT WORK</span>
            <h1>Your assignments</h1>
            <p>
                Complete your work carefully and show your working where
                required.
            </p>
        </section>

        <div class="assignment-grid">
            {''.join(cards)}
        </div>
        """

    conn.close()

    return render_page("Assignments", content)


@bp.route("/student/<int:sid>/assignment/<int:assignment_id>")
def assignment_detail(sid, assignment_id):

    conn = db()

    student = student_or_404(conn, sid)
    assignment = assignment_info(conn, assignment_id)

    # Ownership is based on the student's actual assignment context.
    # If the existing assignment system has a student-specific ownership
    # column, honour it.
    cols = table_columns(conn, "assignments")

    for field in ("student_id", "assigned_to"):
        if field in cols:
            value = assignment.get(field)

            if value not in (None, "", sid, str(sid)):
                abort(403)

    materials = preparation_materials(
        assignment["_subject"],
        assignment["_topic"],
        assignment["_calculator_allowed"],
        assignment["_calculator_required"],
    )

    materials_html = "".join(
        f"<li>{item}</li>" for item in materials
    )

    work_block = ""

    if assignment["_requires_work"] or assignment["_requires_photo"]:
        work_block = f"""
        <section class="upload-panel">
            <div class="upload-icon">📷</div>

            <div>
                <span class="eyebrow">WRITTEN WORK REQUIRED</span>

                <h2>Show your working</h2>

                <p>
                    Complete this work in your dedicated exercise book,
                    then photograph your completed pages.
                </p>

                <div class="photo-tips">
                    <p>📷 Make sure your whole page is visible.</p>
                    <p>💡 Take the photo in good lighting.</p>
                    <p>📐 Keep the phone directly above the page.</p>
                    <p>✍️ Make sure your handwriting is readable.</p>
                    <p>🚫 Do not cover your work with your hand.</p>
                </div>

                <form
                    method="post"
                    action="/student/{sid}/assignment/{assignment_id}/submit"
                    enctype="multipart/form-data"
                >

                    {upload_widget(assignment["_max_photos"], assignment["_max_upload_mb"])}

                    <button class="primary-button" type="submit">
                        📷 Upload & Submit Work
                    </button>

                </form>
            </div>
        </section>
        """

    notice = parent_notice(student["grade_form"])

    content = f"""
    {notice}

    <section class="hero-card">
        <span class="eyebrow">
            {assignment["_subject"] or "ASSIGNMENT"}
        </span>

        <h1>{assignment["_title"]}</h1>

        <p>{assignment["_topic"] or ""}</p>
    </section>

    <section class="content-card">
        <h2>Before you begin</h2>

        <div class="preparation">
            <ul>
                {materials_html}
                <li>☐ I understand the instructions.</li>
                {'<li>☐ I have a parent/guardian with me.</li>'
                    if younger_grade(student["grade_form"]) else ''}
            </ul>
        </div>

        <div class="instructions">
            <h3>Instructions</h3>
            <p>{assignment["_instructions"]}</p>
        </div>
    </section>

    {work_block}

    <section class="content-card">
        <h2>Assignment requirements</h2>

        <div class="requirement-grid">

            <div>
                <span>Maximum marks</span>
                <strong>{assignment["_max_marks"]}</strong>
            </div>

            <div>
                <span>Calculator</span>
                <strong>
                    {
                        "Required"
                        if assignment["_calculator_required"]
                        else
                        "Allowed"
                        if assignment["_calculator_allowed"]
                        else
                        "Not specified"
                    }
                </strong>
            </div>

            <div>
                <span>Written work</span>
                <strong>
                    {"Required" if assignment["_requires_work"] else "Not required"}
                </strong>
            </div>

            <div>
                <span>Resubmission</span>
                <strong>
                    {"Allowed" if assignment["_resubmission"] else "Not allowed"}
                </strong>
            </div>

        </div>
    </section>
    """

    conn.close()

    return render_page(assignment["_title"], content)


@bp.route(
    "/student/<int:sid>/assignment/<int:assignment_id>/submit",
    methods=["POST"],
)
def submit_assignment(sid, assignment_id):

    conn = db()

    student = student_or_404(conn, sid)
    assignment = assignment_info(conn, assignment_id)

    files = request.files.getlist("work_photo")

    if not files:
        return render_page(
            "Upload required",
            """
            <section class="error-state">
                <div>⚠️</div>
                <h2>No photograph was selected</h2>
                <p>Please photograph your completed work and try again.</p>
            </section>
            """,
        ), 400

    max_photos = assignment["_max_photos"]

    if len(files) > max_photos:
        return render_page(
            "Too many photos",
            f"""
            <section class="error-state">
                <div>⚠️</div>
                <h2>Too many photographs</h2>
                <p>
                    This assignment allows a maximum of
                    {max_photos} photograph(s).
                </p>
            </section>
            """,
        ), 400

    submission_time = now()

    cursor = conn.execute(
        """
        INSERT INTO assignment_submissions
        (
            student_id,
            assignment_id,
            status,
            created_at,
            updated_at
        )
        VALUES (?, ?, 'SUBMITTED', ?, ?)
        """,
        (
            sid,
            assignment_id,
            submission_time,
            submission_time,
        ),
    )

    submission_id = cursor.lastrowid

    max_bytes = assignment["_max_upload_mb"] * 1024 * 1024

    saved = 0

    for page_number, uploaded in enumerate(files, start=1):

        original = uploaded.filename or ""

        suffix = Path(original).suffix.lower()

        if suffix not in ALLOWED_EXTENSIONS:
            conn.rollback()
            return render_page(
                "Invalid file",
                """
                <section class="error-state">
                    <div>⚠️</div>
                    <h2>Unsupported file type</h2>
                    <p>
                        Please upload JPG, JPEG, PNG or WEBP photographs only.
                    </p>
                </section>
                """,
            ), 400

        content = uploaded.read()

        _ok, _msg = check_upload(original, content, assignment["_max_upload_mb"])

        if not _ok:

            conn.rollback()

            return render_page(

                "Photo problem",

                '<section class="error-state"><div>⚠️</div><h2>Photo problem</h2><p>' + _msg + '</p><p><a href="/student/%s/assignment/%s">Go back and try again</a></p></section>' % (sid, assignment_id),

            ), 400
        if not content:
            conn.rollback()
            return render_page(
                "Empty file",
                """
                <section class="error-state">
                    <div>⚠️</div>
                    <h2>The photograph is empty</h2>
                    <p>Please choose another photograph.</p>
                </section>
                """,
            ), 400

        if len(content) > max_bytes:
            conn.rollback()
            return render_page(
                "File too large",
                f"""
                <section class="error-state">
                    <div>⚠️</div>
                    <h2>Photograph too large</h2>
                    <p>
                        Each photograph must be no larger than
                        {assignment["_max_upload_mb"]} MB.
                    </p>
                </section>
                """,
            ), 400

        # Generated storage name.
        token = secrets.token_hex(24)
        stored_name = f"{sid}_{submission_id}_{page_number}_{token}{suffix}"

        student_dir = UPLOAD_ROOT / str(sid)
        student_dir.mkdir(parents=True, exist_ok=True)

        destination = student_dir / stored_name

        destination.write_bytes(content)

        mime = ALLOWED_EXTENSIONS[suffix]

        conn.execute(
            """
            INSERT INTO assignment_submission_images
            (
                submission_id,
                original_name,
                stored_name,
                storage_path,
                mime_type,
                file_size,
                page_number
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submission_id,
                original[:255],
                stored_name,
                str(destination.relative_to(ROOT)),
                mime,
                len(content),
                page_number,
            ),
        )

        saved += 1

    conn.execute(
        """
        UPDATE assignment_submissions
        SET submitted_at=?,
            status='MARKING',
            updated_at=?
        WHERE id=?
        """,
        (
            submission_time,
            submission_time,
            submission_id,
        ),
    )

    conn.commit()
    conn.close()

    try:

        auto_mark_submission(submission_id, request.form.get("typed_working", ""))

    except Exception as _e:

        print("auto-mark failed:", _e)

    return redirect(f"/student/{sid}/submission/{submission_id}")


@bp.route("/student/<int:sid>/submission/<int:submission_id>")
def submission_status(sid, submission_id):

    conn = db()

    student = student_or_404(conn, sid)

    submission = ensure_student_owns_submission(
        conn,
        sid,
        submission_id,
    )

    images = conn.execute(
        """
        SELECT *
        FROM assignment_submission_images
        WHERE submission_id=?
        ORDER BY page_number
        """,
        (submission_id,),
    ).fetchall()

    result = conn.execute(
        """
        SELECT *
        FROM assignment_marking_results
        WHERE submission_id=?
        ORDER BY id
        """,
        (submission_id,),
    ).fetchall()

    feedback = conn.execute(
        """
        SELECT *
        FROM assignment_feedback_history
        WHERE submission_id=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (submission_id,),
    ).fetchone()

    status = submission["status"]

    if status == "MARKED":
        status_title = "Marked"
        status_text = "Your assignment has been marked."

    elif status == "NEEDS_REVIEW":
        status_title = "Manual review recommended"
        status_text = (
            "Your work needs a tutor/founder review before the result "
            "can be confirmed."
        )

    elif status == "RESUBMISSION_REQUIRED":
        status_title = "Resubmission required"
        status_text = "Please review the feedback and submit your work again."

    else:
        status_title = "Submitted"
        status_text = (
            "Your work has been submitted. The marking workflow will "
            "process it."
        )

    score_html = ""

    if status == "MARKED" and feedback:
        score_html = f"""
        <section class="score-card">
            <span class="eyebrow">RESULT</span>
            <div class="score">
                {feedback["score"]}/{feedback["total_marks"]}
            </div>
            <strong>{feedback["percentage"]:.0f}%</strong>
        </section>
        """

    feedback_html = ""

    if feedback:
        feedback_html = f"""
        <section class="content-card">
            <h2>Feedback</h2>

            <p>{feedback["feedback"] or ""}</p>

            <div class="feedback-columns">

                <div>
                    <h3>Strong areas</h3>
                    <p>{feedback["weak_topics"] or "Keep building on your progress."}</p>
                </div>

                <div>
                    <h3>Recommended practice</h3>
                    <p>{feedback["recommended_topics"] or "Continue practising your current topic."}</p>
                </div>

            </div>
        </section>
        """

    question_html = ""

    for item in result:
        question_html += f"""
        <div class="marking-row">
            <div>
                <strong>
                    Question {item["question_number"] or "—"}
                </strong>
                <p>{item["feedback"] or ""}</p>
            </div>

            <strong>
                {item["marks_awarded"] or 0}/{item["marks_total"] or 0}
            </strong>
        </div>
        """

    if not question_html:
        question_html = """
        <div class="muted-box">
            Question-level results will appear here when marking is complete.
        </div>
        """

    content = f"""
    <section class="hero-card">
        <span class="eyebrow">SUBMISSION STATUS</span>
        <h1>{status_title}</h1>
        <p>{status_text}</p>

        <div class="status-chip">
            {status}
        </div>
    </section>

    {score_html}

    <section class="content-card">
        <h2>Uploaded pages</h2>
        <p>{len(images)} page(s) submitted.</p>

        <div class="page-list">
            {
                ''.join(
                    f'<div class="page-chip">📄 Page {x["page_number"]}</div>'
                    for x in images
                )
            }
        </div>
    </section>

    <section class="content-card">
        <h2>Question results</h2>
        {question_html}
    </section>

    {feedback_html}
    """

    conn.close()

    return render_page("Submission", content)


# ---------------------------------------------------------
# Founder/manual review
# ---------------------------------------------------------

@bp.route("/founder/assignment-submissions")
def founder_submissions():

    conn = db()

    rows = conn.execute(
        """
        SELECT
            s.*,
            st.name AS student_name
        FROM assignment_submissions s
        JOIN students st ON st.id=s.student_id
        ORDER BY s.created_at DESC
        """
    ).fetchall()

    cards = []

    for row in rows:
        cards.append(
            f"""
            <a class="review-card"
               href="/founder/assignment-submissions/{row['id']}">

                <div>
                    <strong>{row["student_name"]}</strong>
                    <span>Submission #{row["id"]}</span>
                </div>

                <span class="status-chip">
                    {row["status"]}
                </span>
            </a>
            """
        )

    content = f"""
    <section class="hero-card">
        <span class="eyebrow">FOUNDER REVIEW</span>
        <h1>Assignment submissions</h1>
        <p>
            Review uploaded work and confirm results when automatic marking
            cannot reliably interpret the submission.
        </p>
    </section>

    <div class="review-list">
        {
            ''.join(cards)
            or
            '<div class="empty-state"><h2>No submissions</h2></div>'
        }
    </div>
    """

    conn.close()

    return render_page("Founder Review", content)


@bp.route(
    "/founder/assignment-submissions/<int:submission_id>",
    methods=["GET", "POST"],
)
def founder_review(submission_id):

    conn = db()

    submission = conn.execute(
        """
        SELECT
            s.*,
            st.name AS student_name,
            a.*
        FROM assignment_submissions s
        JOIN students st ON st.id=s.student_id
        JOIN assignments a ON a.id=s.assignment_id
        WHERE s.id=?
        """,
        (submission_id,),
    ).fetchone()

    if not submission:
        abort(404)

    if request.method == "POST":

        score = float(request.form.get("score") or 0)
        total = float(
            request.form.get("total_marks")
            or submission["max_marks"]
            or 10
        )

        percentage = (
            (score / total) * 100
            if total > 0 else 0
        )

        feedback = request.form.get("feedback", "").strip()
        strengths = request.form.get("strengths", "").strip()
        weaknesses = request.form.get("weaknesses", "").strip()
        recommendations = request.form.get(
            "recommended_topics",
            "",
        ).strip()

        timestamp = now()

        conn.execute(
            """
            UPDATE assignment_submissions
            SET
                status='MARKED',
                score=?,
                total_marks=?,
                percentage=?,
                automatic_marked=0,
                manual_review_required=0,
                marked_at=?,
                feedback=?,
                updated_at=?
            WHERE id=?
            """,
            (
                score,
                total,
                percentage,
                timestamp,
                feedback,
                timestamp,
                submission_id,
            ),
        )

        conn.execute(
            """
            INSERT INTO assignment_feedback_history
            (
                student_id,
                assignment_id,
                submission_id,
                subject,
                grade_form,
                topic,
                score,
                total_marks,
                percentage,
                feedback,
                weak_topics,
                recommended_topics
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                submission["student_id"],
                submission["assignment_id"],
                submission_id,
                submission["subject"],
                submission["grade_form"],
                submission["topic"],
                score,
                total,
                percentage,
                feedback,
                weaknesses,
                recommendations,
            ),
        )

        

        conn.commit()


        


        # -------------------------------------------------


        # Academic learning integration


        # -------------------------------------------------


        try:


            integrate_assignment_result(submission_id)


        except Exception as integration_error:


            print(


                "Assignment academic integration warning:",


                integration_error,


            )


        return redirect(
            f"/founder/assignment-submissions/{submission_id}"
        )

    images = conn.execute(
        """
        SELECT *
        FROM assignment_submission_images
        WHERE submission_id=?
        ORDER BY page_number
        """,
        (submission_id,),
    ).fetchall()

    image_list = "".join(
        f"""
        <div class="review-image">
            <div>📄 Page {image["page_number"]}</div>
            <p>{image["original_name"] or image["stored_name"]}</p>
            <small>
                Stored securely at:
                {image["storage_path"]}
            </small>
        </div>
        """
        for image in images
    )

    content = f"""
    <section class="hero-card">
        <span class="eyebrow">MANUAL REVIEW</span>
        <h1>{submission["student_name"]}</h1>
        <p>Submission #{submission_id}</p>

        <div class="status-chip">
            {submission["status"]}
        </div>
    </section>

    <section class="content-card">
        <h2>Uploaded work</h2>
        {image_list or "<p>No images.</p>"}
    </section>

    <section class="content-card">
        <h2>Confirm marking</h2>

        <form method="post" class="review-form">

            <label>
                Score
                <input
                    type="number"
                    name="score"
                    min="0"
                    step="0.5"
                    required
                >
            </label>

            <label>
                Total marks
                <input
                    type="number"
                    name="total_marks"
                    min="1"
                    step="0.5"
                    value="{submission["max_marks"] or 10}"
                    required
                >
            </label>

            <label>
                Feedback
                <textarea name="feedback" required></textarea>
            </label>

            <label>
                Strengths
                <textarea name="strengths"></textarea>
            </label>

            <label>
                Areas needing improvement
                <textarea name="weaknesses"></textarea>
            </label>

            <label>
                Recommended practice
                <textarea name="recommended_topics"></textarea>
            </label>

            <button class="primary-button" type="submit">
                ✓ Save Marking Result
            </button>

        </form>
    </section>
    """

    conn.close()

    return render_page("Manual Review", content)


PAGE = """
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport"
      content="width=device-width, initial-scale=1,
               maximum-scale=1">

<title>{{ title }} · Digital Classroom Rules</title>

<style>

:root {
    --ink: #101828;
    --muted: #667085;
    --surface: #ffffff;
    --soft: #f5f7fb;
    --line: #e7eaf0;
    --accent: #5b5bd6;
    --accent-dark: #4444b8;
    --success: #16845b;
    --warning: #b56b00;
    --danger: #c24141;
    --radius: 22px;
    --shadow: 0 14px 45px rgba(16,24,40,.08);
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    background:
        radial-gradient(
            circle at top right,
            rgba(91,91,214,.10),
            transparent 35%
        ),
        var(--soft);

    color: var(--ink);

    font-family:
        Inter,
        ui-sans-serif,
        system-ui,
        -apple-system,
        BlinkMacSystemFont,
        "Segoe UI",
        sans-serif;

    line-height: 1.6;
}

main {
    width: min(1080px, calc(100% - 28px));
    margin: 0 auto;
    padding: 30px 0 70px;
}

.hero-card {
    background:
        linear-gradient(
            135deg,
            #111827,
            #27275f
        );

    color: white;
    border-radius: 30px;
    padding: 34px;
    margin-bottom: 22px;
    box-shadow: var(--shadow);
}

.hero-card h1 {
    margin: 8px 0;
    font-size: clamp(2rem, 7vw, 3.5rem);
    line-height: 1.05;
    letter-spacing: -.04em;
}

.hero-card p {
    color: rgba(255,255,255,.78);
}

.eyebrow {
    font-size: .72rem;
    letter-spacing: .12em;
    font-weight: 800;
    opacity: .75;
}

.content-card,
.upload-panel,
.score-card,
.parent-notice,
.error-state,
.empty-state {
    background: var(--surface);
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 25px;
    margin-bottom: 20px;
    box-shadow: var(--shadow);
}

.parent-notice {
    display: flex;
    gap: 16px;
    border-left: 5px solid var(--accent);
}

.notice-icon {
    font-size: 2rem;
}

.parent-notice p {
    margin-bottom: 0;
    color: var(--muted);
}

.assignment-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(250px, 1fr));
    gap: 16px;
}

.assignment-card,
.review-card {
    position: relative;
    display: block;
    text-decoration: none;
    color: inherit;
    background: white;
    border: 1px solid var(--line);
    border-radius: var(--radius);
    padding: 23px;
    transition:
        transform .18s ease,
        box-shadow .18s ease,
        border-color .18s ease;
}

.assignment-card:hover,
.review-card:hover {
    transform: translateY(-3px);
    box-shadow: var(--shadow);
    border-color: rgba(91,91,214,.35);
}

.assignment-card h3 {
    margin: 16px 0 7px;
}

.assignment-card p {
    color: var(--muted);
}

.card-arrow {
    position: absolute;
    right: 22px;
    bottom: 18px;
    font-size: 1.5rem;
}

.subject-pill,
.status-chip {
    display: inline-flex;
    align-items: center;
    border-radius: 999px;
    padding: 6px 11px;
    background: #eeeeff;
    color: var(--accent-dark);
    font-size: .75rem;
    font-weight: 800;
}

.status-chip {
    margin-top: 12px;
    background: #f2f4f7;
    color: #475467;
}

.preparation ul {
    list-style: none;
    padding: 0;
    margin: 0;
}

.preparation li {
    padding: 9px 0;
    border-bottom: 1px solid var(--line);
}

.instructions {
    margin-top: 25px;
    padding-top: 20px;
    border-top: 1px solid var(--line);
}

.requirement-grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
}

.requirement-grid > div {
    background: var(--soft);
    border-radius: 16px;
    padding: 15px;
}

.requirement-grid span {
    display: block;
    color: var(--muted);
    font-size: .8rem;
}

.requirement-grid strong {
    display: block;
    margin-top: 5px;
}

.upload-panel {
    display: grid;
    grid-template-columns: 70px 1fr;
    gap: 20px;
}

.upload-icon {
    font-size: 3rem;
}

.upload-panel input[type=file] {
    width: 100%;
    padding: 13px;
    border: 1px dashed #b9bfd0;
    border-radius: 15px;
    background: #fafbfc;
    margin: 15px 0 8px;
}

.photo-tips {
    background: #f8f8ff;
    border-radius: 16px;
    padding: 12px 17px;
    margin-top: 15px;
}

.photo-tips p {
    margin: 5px 0;
    font-size: .9rem;
}

.primary-button {
    appearance: none;
    border: 0;
    border-radius: 15px;
    background: var(--accent);
    color: white;
    padding: 14px 20px;
    font-weight: 800;
    cursor: pointer;
    margin-top: 14px;
}

.primary-button:hover {
    background: var(--accent-dark);
}

.score-card {
    text-align: center;
}

.score {
    font-size: clamp(3rem, 13vw, 6rem);
    font-weight: 900;
    letter-spacing: -.07em;
    color: var(--accent);
}

.feedback-columns {
    display: grid;
    grid-template-columns:
        repeat(auto-fit, minmax(230px, 1fr));
    gap: 15px;
}

.feedback-columns > div {
    background: var(--soft);
    padding: 17px;
    border-radius: 16px;
}

.marking-row,
.review-card {
    display: flex;
    justify-content: space-between;
    gap: 18px;
    align-items: center;
}

.marking-row {
    border-bottom: 1px solid var(--line);
    padding: 15px 0;
}

.review-list {
    display: grid;
    gap: 12px;
}

.review-card span {
    display: block;
    color: var(--muted);
    font-size: .8rem;
}

.review-image {
    border: 1px solid var(--line);
    border-radius: 16px;
    padding: 17px;
    margin-bottom: 10px;
}

.review-image small {
    color: var(--muted);
    overflow-wrap: anywhere;
}

.review-form {
    display: grid;
    gap: 17px;
}

.review-form label {
    display: grid;
    gap: 7px;
    font-weight: 700;
}

.review-form input,
.review-form textarea {
    width: 100%;
    padding: 13px;
    border: 1px solid var(--line);
    border-radius: 13px;
    font: inherit;
}

.review-form textarea {
    min-height: 110px;
}

.empty-state,
.error-state {
    text-align: center;
    padding: 55px 25px;
}

.empty-icon {
    font-size: 3rem;
}

.error-state {
    border-color: rgba(194,65,65,.2);
}

.muted-box {
    background: var(--soft);
    padding: 17px;
    border-radius: 15px;
    color: var(--muted);
}

.page-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.page-chip {
    background: var(--soft);
    padding: 9px 13px;
    border-radius: 999px;
}

@media (max-width: 650px) {

    main {
        width: min(100% - 18px, 1080px);
        padding-top: 15px;
    }

    .hero-card,
    .content-card,
    .upload-panel,
    .score-card,
    .parent-notice {
        border-radius: 19px;
        padding: 20px;
    }

    .upload-panel {
        grid-template-columns: 1fr;
    }

    .upload-icon {
        font-size: 2rem;
    }

    .review-card {
        align-items: flex-start;
    }
}

</style>
</head>

<body>

<main>
    {{ body|safe }}
</main>

</body>
</html>
"""


def register_assignment_system(app):

    # Avoid registering twice if the server is imported/reloaded.
    if "assignment_system" not in app.blueprints:
        app.register_blueprint(bp)

    return app


# ===== PHOTO UPLOAD WIDGET + AUTO-MARK (added) =====
from work_marking import check_upload, mark_answer

_UPLOAD_TEMPLATE = """
<div id="uploader" data-max="__MAX__" data-mb="__MB__">
<style>
#uploader .row{display:flex;gap:10px;flex-wrap:wrap;margin:12px 0}
#uploader .pick{flex:1 1 200px;padding:14px 16px;border-radius:14px;border:2px dashed #1f7a4d;background:#f2fbf6;font-weight:700;text-align:center;cursor:pointer;color:#14532d}
#uploader .pick input{display:none}
#uploader .pages{display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:10px;margin:10px 0}
#uploader .pg{position:relative;border-radius:12px;overflow:hidden;border:1px solid #d6e6dc;background:#fff}
#uploader .pg img{width:100%;height:120px;object-fit:cover;display:block}
#uploader .pg b{position:absolute;left:6px;top:6px;background:#14532d;color:#fff;border-radius:999px;font-size:12px;padding:2px 8px}
#uploader .pg button{width:100%;border:0;background:#fee2e2;color:#991b1b;padding:8px;font-weight:700;cursor:pointer}
#uploader .msg{color:#991b1b;font-weight:600;min-height:1.2em}
#uploader textarea{width:100%;min-height:110px;border-radius:12px;border:1px solid #cbd5d0;padding:10px;font:inherit;box-sizing:border-box}
</style>
<div class="row">
<label class="pick">📷 TAKE PHOTO<input id="up_cam" type="file" accept="image/*" capture="environment"></label>
<label class="pick">🖼️ UPLOAD FROM GALLERY<input id="up_gal" type="file" accept="image/jpeg,image/png,image/webp" multiple></label>
</div>
<div id="up_pages" class="pages"></div>
<div id="up_msg" class="msg"></div>
<input id="up_real" name="work_photo" type="file" multiple style="display:none">
<label for="up_typed"><b>Type your answers (recommended)</b><br>
<small>Start each answer with its number, like "1. x = 4", and include your working lines. If you skip this, a tutor will check your photos by hand.</small></label>
<textarea id="up_typed" name="typed_working" placeholder="1. 2x + 3 = 11&#10;2x = 8&#10;x = 4&#10;2. 12"></textarea>
<script>
(function(){
var box=document.getElementById('uploader');
var max=parseInt(box.dataset.max,10)||1, mb=parseInt(box.dataset.mb,10)||10;
var dt=new DataTransfer();
var real=document.getElementById('up_real'), pages=document.getElementById('up_pages'), msg=document.getElementById('up_msg');
var okTypes=['image/jpeg','image/png','image/webp'];
function render(){
  pages.innerHTML='';
  Array.prototype.forEach.call(dt.files,function(f,i){
    var d=document.createElement('div'); d.className='pg';
    var im=document.createElement('img'); im.src=URL.createObjectURL(f);
    var b=document.createElement('b'); b.textContent='Page '+(i+1);
    var x=document.createElement('button'); x.type='button'; x.textContent='Remove';
    x.onclick=function(){remove(i)};
    d.appendChild(im); d.appendChild(b); d.appendChild(x); pages.appendChild(d);
  });
  real.files=dt.files;
}
function remove(i){
  var n=new DataTransfer();
  Array.prototype.forEach.call(dt.files,function(f,j){ if(j!==i) n.items.add(f); });
  dt=n; msg.textContent=''; render();
}
function add(list){
  msg.textContent='';
  Array.prototype.forEach.call(list,function(f){
    if(okTypes.indexOf(f.type)<0){msg.textContent='Please use JPG, PNG or WEBP photos only.';return;}
    if(f.size>mb*1024*1024){msg.textContent='That photo is too large (limit '+mb+' MB). Lower your camera quality and try again.';return;}
    if(dt.files.length>=max){msg.textContent='This assignment allows up to '+max+' page(s).';return;}
    dt.items.add(f);
  });
  render();
}
document.getElementById('up_cam').onchange=function(e){add(e.target.files);e.target.value='';};
document.getElementById('up_gal').onchange=function(e){add(e.target.files);e.target.value='';};
box.closest('form').addEventListener('submit',function(e){
  if(dt.files.length===0){e.preventDefault();msg.textContent='Please add at least one photo of your work first.';}
});
})();
</script>
</div>
"""

def upload_widget(max_photos, max_mb):
    return (_UPLOAD_TEMPLATE.replace("__MAX__", str(max_photos))
                            .replace("__MB__", str(max_mb)))


def auto_mark_submission(submission_id, typed):
    """Mark typed answers against the answer key. Auto-finalise only when every
    question has a typed answer and nothing needs review; otherwise hold for tutor."""
    import re as _re
    typed = (typed or "")[:8000]
    conn = db()
    finalised = False
    try:
        try:
            conn.execute("ALTER TABLE assignment_submissions ADD COLUMN typed_working TEXT")
        except sqlite3.OperationalError:
            pass
        conn.execute("UPDATE assignment_submissions SET typed_working=? WHERE id=?",
                     (typed, submission_id))
        aid = conn.execute("SELECT assignment_id FROM assignment_submissions WHERE id=?",
                           (submission_id,)).fetchone()[0]
        qs = conn.execute(
            "SELECT question_number, question, correct_answer, marks, topic "
            "FROM assignment_questions WHERE assignment_id=? ORDER BY question_number",
            (aid,)).fetchall()
        ts = now()

        def hold(reason):
            conn.execute("UPDATE assignment_submissions SET manual_review_required=1, "
                         "manual_review_reason=?, updated_at=? WHERE id=?",
                         (reason, ts, submission_id))
            conn.commit()

        if not qs:
            return hold("No answer key on this assignment; tutor review needed.")
        if not typed.strip():
            return hold("Photos submitted without typed answers; tutor review needed.")

        parts = _re.split(r'(?im)^\s*(?:q(?:uestion)?\s*)?(\d+)[.)](?=\s)\s*', typed)
        answers = {parts[i]: parts[i + 1] for i in range(1, len(parts) - 1, 2)}

        conn.execute("DELETE FROM assignment_marking_results WHERE submission_id=?", (submission_id,))
        got_total = max_total = 0.0
        need_review = False
        weak, confs = [], []
        for q in qs:
            qn, key, marks, topic = q[0], q[2], (q[3] or 1), q[4]
            ans = answers.get(str(qn))
            if ans is None:
                r = {"marks_awarded": 0, "marks_total": marks, "result": "MISSING",
                     "feedback": "No typed answer found for this question; a tutor will check your photo.",
                     "confidence": 0.0, "manual_review_required": True}
            else:
                r = mark_answer(ans, key, marks)
            need_review = need_review or bool(r["manual_review_required"])
            got_total += r["marks_awarded"]; max_total += r["marks_total"]
            confs.append(r["confidence"])
            if r["marks_awarded"] < r["marks_total"] and topic:
                weak.append(topic)
            conn.execute(
                "INSERT INTO assignment_marking_results (submission_id, question_number, "
                "marks_awarded, marks_total, result, student_answer, expected_answer, "
                "feedback, confidence, manual_review_required) VALUES (?,?,?,?,?,?,?,?,?,?)",
                (submission_id, str(qn), r["marks_awarded"], r["marks_total"], r["result"],
                 (ans or "")[:1000], str(key or ""), r["feedback"], r["confidence"],
                 1 if r["manual_review_required"] else 0))

        pct = round(100 * got_total / max_total, 1) if max_total else 0
        conf = sum(confs) / len(confs) if confs else 0
        if need_review:
            conn.execute("UPDATE assignment_submissions SET score=?, total_marks=?, percentage=?, "
                         "confidence=?, manual_review_required=1, manual_review_reason=?, updated_at=? "
                         "WHERE id=?",
                         (got_total, max_total, pct, conf,
                          "Some answers were missing or could not be confirmed automatically.",
                          ts, submission_id))
            conn.commit()
            return
        recommended = ", ".join(sorted(set(weak)))
        from feedback_style import build_feedback
        _g = conn.execute("select st.grade_form from students st join assignment_submissions x on x.student_id=st.id where x.id=?", (submission_id,)).fetchone()
        feedback = build_feedback(_g[0] if _g else "", got_total, max_total, pct, weak)
        conn.execute("UPDATE assignment_submissions SET status='MARKED', marked_at=?, score=?, "
                     "total_marks=?, percentage=?, automatic_marked=1, confidence=?, feedback=?, "
                     "recommended_topics=?, manual_review_required=0, updated_at=? WHERE id=?",
                     (ts, got_total, max_total, pct, conf, feedback, recommended, ts, submission_id))
        conn.commit()
        finalised = True
    finally:
        conn.close()
    if finalised:
        try:
            integrate_assignment_result(submission_id)
        except Exception as e:
            print("integrate_assignment_result failed:", e)
