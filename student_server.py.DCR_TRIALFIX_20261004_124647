from paid_access import register_paid_access
from flask import Flask, request, redirect, url_for
import sqlite3
import html
from datetime import datetime, timedelta

app = Flask(__name__)

# ------------------------------------------------------------
# DB bootstrap — creates the schema and seeds curriculum if the
# database file is missing (fresh Railway container, etc).
# Reads DB_PATH from environment if set.
# ------------------------------------------------------------
try:
    import db_bootstrap
    DB_PATH_RESOLVED = db_bootstrap.ensure_db()
except Exception as _bs_err:
    print('BOOTSTRAP: skipped due to error:', _bs_err)
    DB_PATH_RESOLVED = None



# Digital Classroom Rules assignment system
from assignment_system import register_assignment_system
register_assignment_system(app)
app.secret_key = 'dcr-secret-key-2026-change-this-later'
app.permanent_session_lifetime = __import__('datetime').timedelta(days=7)


# RAILWAY_DB_INIT — ensure database exists on startup
import os as _db_os
if not _db_os.path.exists("digital_classroom.db"):
    print("⚠️ Database not found — will be created by app")


# === Digital Classroom module imports ===
from parent_assist import register_parent_assist
from marking_flow import register_marking_flow
from whatsapp_webhook import register_whatsapp_webhook
from student_learning import register_student_learning
from auth import register_auth_routes, login_required, current_user

# === Register all routes ===
register_parent_assist(app)
register_marking_flow(app)
register_whatsapp_webhook(app)
register_student_learning(app)






DB = _db_os.environ.get("DB_PATH", "digital_classroom.db")
_db_parent = _db_os.path.dirname(DB)
if _db_parent:
    _db_os.makedirs(_db_parent, exist_ok=True)


def student(sid):
    """Fetch a student record by ID."""
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT * FROM students WHERE id = ?", (sid,)).fetchone()
    conn.close()
    return row


# Subject list is derived from the curriculum table at startup.
# Every subject with at least one curriculum row becomes selectable.
# Falls back to a safe default if the DB is unavailable.
_SUBJECTS_FALLBACK = [
    "Maths", "English", "Science", "Social Studies", "Geography",
    "History", "Biology", "Chemistry", "Physics", "Economics", "Accounting",
    "Shona", "Ndebele",
]

def _load_subjects():
    try:
        import sqlite3 as _sq
        _c = _sq.connect(DB)
        rows = _c.execute(
            "SELECT DISTINCT subject FROM curriculum "
            "WHERE subject IS NOT NULL AND subject != '' "
            "ORDER BY subject"
        ).fetchall()
        _c.close()
        found = [r[0] for r in rows]
        if found:
            return found
    except Exception as _e:
        print("SUBJECTS: falling back to default list:", _e)
    return list(_SUBJECTS_FALLBACK)

SUBJECTS = _load_subjects()
print(f"SUBJECTS loaded: {len(SUBJECTS)} subjects")

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def setup():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            active INTEGER DEFAULT 1,
            added_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS student_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER,
            subject TEXT,
            session_type TEXT,
            started_at TEXT,
            expires_at TEXT,
            completed INTEGER DEFAULT 0
        )
    """)

    try:
        conn.execute("ALTER TABLE students ADD COLUMN current_subject TEXT")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    conn.close()

setup()


def get_student(sid):
    conn = db()
    s = conn.execute(
        "SELECT * FROM students WHERE id=?",
        (sid,)
    ).fetchone()
    conn.close()
    return s


def get_subjects(sid):
    conn = db()
    rows = conn.execute("""
        SELECT subject
        FROM student_subjects
        WHERE student_id=? AND active=1
        ORDER BY id
    """, (sid,)).fetchall()
    conn.close()

    return [r["subject"] for r in rows]


def get_current_subject(sid):
    conn = db()
    row = conn.execute(
        "SELECT current_subject FROM students WHERE id=?",
        (sid,)
    ).fetchone()
    conn.close()

    if row and row["current_subject"]:
        return row["current_subject"]

    subjects = get_subjects(sid)
    return subjects[0] if subjects else None


def esc(value):
    return html.escape(str(value or ""))


def layout(title, sid, content):
    return f"""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only">
<meta name="theme-color" content="#172554">
<title>{esc(title)}</title>

<style>
/* Force light rendering — stops Android/WebView auto-inversion
   which was washing out pale-yellow cards on paid/trial pages. */
html {{ color-scheme: light only; }}
* {{
    box-sizing:border-box;
}}

body {{
    margin:0;
    font-family:Arial,sans-serif;
    background:#f1f5f9;
    color:#172033;
}}

.container {{
    max-width:850px;
    margin:auto;
    padding:15px;
}}

.nav {{
    display:flex;
    flex-wrap:wrap;
    gap:8px;
    margin-bottom:15px;
}}

.nav a {{
    background:white;
    color:#1d4ed8;
    text-decoration:none;
    padding:10px 13px;
    border-radius:10px;
    font-weight:bold;
}}

.hero {{
    background:linear-gradient(135deg,#172554,#2563eb);
    color:white;
    padding:25px;
    border-radius:20px;
    margin-bottom:15px;
}}

.card {{
    background:white;
    padding:20px;
    border-radius:18px;
    margin:15px 0;
    box-shadow:0 5px 18px rgba(0,0,0,.07);
}}

.btn {{
    display:block;
    width:100%;
    padding:15px;
    margin:10px 0;
    border-radius:12px;
    background:#2563eb;
    color:white;
    text-decoration:none;
    text-align:center;
    font-weight:bold;
    border:0;
    font-size:16px;
}}

.green {{background:#15803d;}}
.orange {{background:#ea580c;}}
.purple {{background:#7c3aed;}}
.gray {{background:#475569;}}
.red {{background:#dc2626;}}

.subject {{
    background:white;
    border:2px solid #e2e8f0;
    border-radius:15px;
    padding:15px;
    margin:10px 0;
}}

.current {{
    border-color:#2563eb;
    background:#eff6ff;
}}

textarea,input {{
    width:100%;
    padding:14px;
    border:1px solid #cbd5e1;
    border-radius:10px;
    font-size:16px;
    margin:7px 0;
}}

.question {{
    background:#f8fafc;
    padding:17px;
    border-radius:14px;
    margin:15px 0;
}}

.success {{
    background:#dcfce7;
    padding:15px;
    border-radius:12px;
}}

.warning {{
    background:#fef3c7;
    padding:15px;
    border-radius:12px;
}}
</style>
</head>

<body>

<div class="container">

<div class="nav">
    <a href="/student/{sid}/home">🏠 Home</a>
    <a href="/student/{sid}/centre">📚 Learning Centre</a>
    <a href="/student/{sid}/profile">👤 Profile</a>
</div>

{content}

</div>
</body>
</html>
"""




# ============================================================
# PAUSE / RESUME MASTER PAID SESSION
# ============================================================

@app.route("/student/<int:student_id>/pause-paid")
def pause_paid_route(student_id):

    try:
        from paid_access import pause_paid_session

        success, status = pause_paid_session(student_id)

    except Exception as e:
        return f"Pause error: {e}", 500

    if not success:
        return redirect(url_for("paid", sid=student_id))

    next_url = request.args.get("next")

    if next_url and next_url.startswith("/student/"):
        return redirect(next_url)

    return redirect(url_for("home", sid=student_id))


@app.route("/student/<int:student_id>/resume-paid")
def resume_paid_route(student_id):

    try:
        from paid_access import resume_paid_session

        success, status = resume_paid_session(student_id)

    except Exception as e:
        return f"Resume error: {e}", 500

    if not success:
        return redirect(url_for("paid", sid=student_id))

    next_url = request.args.get("next")

    if next_url and next_url.startswith("/student/"):
        return redirect(next_url)

    return redirect(url_for("home", sid=student_id))


# Old root route disabled

@app.route("/student/<int:sid>/home")
def home(sid):

    s = get_student(sid)

    if not s:
        return "Student not found",404

    subjects = get_subjects(sid)
    current = get_current_subject(sid)

    selected = ", ".join(subjects) if subjects else "None selected"

    # MASTER PAID SESSION
    # Home only reads the existing master session.
    # It NEVER creates or resets a timer.
    try:
        from paid_access import active_paid_session
        paid_home = active_paid_session(sid)
    except Exception:
        paid_home = None

    # Conditional copy for trial vs. used state
    if s["free_trial_used"]:
        trial_line = "✅ Your free trial has been used. Unlock a full 1-hour paid lesson below."
    else:
        trial_line = "Try your first lesson free, or unlock a full 1-hour paid lesson."

    content = f"""
<div class="hero">
    <h1>Welcome, {esc(s['name'])} 👋</h1>
    <h2>Digital Classroom Rules</h2>
    <p>Your personal learning centre</p>
    <p>🧑‍🏫 Tutor: <b>{esc(s['tutor'])}</b></p>
</div>

<div class="card">
    <h2>🎓 Start Learning</h2>

    <a class="btn green"
       href="/student/{sid}/trial">
       🆓 FREE 30-Minute Trial
    </a>

    <a class="btn orange"
       href="/student/{sid}/paid">
       💵 $1 — 1-Hour Lesson
    </a>

    <p style="margin-top:12px;">
        {trial_line}
    </p>
</div>

<div class="card">
    <h2>📊 Your Learning Profile</h2>
    <p><b>Grade/Form:</b> {esc(s['grade_form'])}</p>
    <p><b>🔥 Streak:</b> {s['streak'] or 0}</p>
    <p><b>📚 Lessons:</b> {s['paid_lessons'] or 0}</p>
</div>

<div class="card">
    <h2>📚 What do you want to study?</h2>
    <p>You can choose <b>one or multiple subjects</b>.</p>
    <p><b>Selected:</b> {esc(selected)}</p>
    <p><b>Current subject:</b> {esc(current or 'None')}</p>
</div>

<div class="card">
<h2>📖 Select Your Subjects</h2>
"""

    for subject in SUBJECTS:

        if subject in subjects:
            content += f"""
<div class="subject current">
    <h3>✓ {esc(subject)}</h3>
    <p>Currently selected</p>

    <a class="btn green"
       href="/student/{sid}/select/{subject}">
       📚 Study {esc(subject)}
    </a>

    <a class="btn gray"
       href="/student/{sid}/toggle/{subject}">
       Remove Subject
    </a>
</div>
"""
        else:
            content += f"""
<div class="subject">
    <h3>{esc(subject)}</h3>

    <a class="btn"
       href="/student/{sid}/select/{subject}">
       ➕ Choose {esc(subject)}
    </a>
</div>
"""

    content += f"""
</div>



<div class="card">
    <h2>🚀 Learning Centre</h2>
    <p>
        Current subject:
        <b>{esc(current or 'Choose a subject first')}</b>
    </p>
"""

    if current:
        content += f"""
<a class="btn purple"
   href="/student/{sid}/centre">
   📚 Open {esc(current)} Learning Centre
</a>
"""
    else:
        content += """
<p class="warning">Choose a subject above to enter your Learning Centre.</p>
"""

    content += "</div>"

    # ========================================================
    # MASTER PAID SESSION TIMER + PAUSE / RESUME
    # ========================================================
    if paid_home:
        pause_button = ""

        if paid_home["paused"]:
            pause_button = f"""
<a class="btn green"
   href="/student/{sid}/resume-paid?next=/student/{sid}/home">
   ▶️ RESUME LESSON
</a>
"""
        else:
            pause_button = f"""
<a class="btn orange"
   href="/student/{sid}/pause-paid?next=/student/{sid}/home">
   ⏸️ PAUSE LESSON
</a>
"""

        content += f"""
<div class="card">
    <h2 id="home_timer">⏱️ Loading timer...</h2>
    <p><b>🔐 Paid lesson active</b></p>
    <p>
        This is your master lesson timer.
        Changing subjects or topics will not reset it.
    </p>
    {pause_button}
</div>

<script>
let homeEnd = new Date("{paid_home['expires_at']}").getTime();
let homePaused = {str(bool(paid_home["paused"])).lower()};

function updateHomeTimer() {{
    let timer = document.getElementById("home_timer");

    if (!timer) return;

    if (homePaused) {{
        timer.innerHTML = "⏸️ Lesson PAUSED";
        return;
    }}

    let distance = homeEnd - new Date().getTime();

    if (distance <= 0) {{
        timer.innerHTML = "⏰ Lesson time finished";

        setTimeout(function() {{
            window.location.href = "/student/{sid}/pay";
        }}, 1000);

        return;
    }}

    let minutes = Math.floor(distance / 60000);
    let seconds = Math.floor((distance % 60000) / 1000);

    timer.innerHTML =
        "⏱️ Paid lesson time remaining: " +
        minutes + "m " + seconds + "s";
}}

updateHomeTimer();
setInterval(updateHomeTimer, 1000);
</script>
"""

    return layout("Student Home",sid,content)


@app.route("/student/<int:sid>/select/<path:subject>")
def select_subject(sid,subject):

    if subject not in SUBJECTS:
        return redirect(url_for("home",sid=sid))

    conn = db()

    existing = conn.execute("""
        SELECT id,active
        FROM student_subjects
        WHERE student_id=? AND subject=?
    """,(sid,subject)).fetchone()

    if existing:
        conn.execute("""
            UPDATE student_subjects
            SET active=1
            WHERE id=?
        """,(existing["id"],))
    else:
        conn.execute("""
            INSERT INTO student_subjects
            (student_id,subject,active)
            VALUES (?,?,1)
        """,(sid,subject))

    conn.execute("""
        UPDATE students
        SET current_subject=?
        WHERE id=?
    """,(subject,sid))

    conn.commit()
    conn.close()

    # --------------------------------------------------------
    # Auto-grant the 30-minute free trial the first time a
    # student selects a subject — as long as they haven't
    # used it yet.
    # --------------------------------------------------------
    print(f"[DBG select_subject] sid={sid} subject={subject!r} free_trial_used={get_student(sid)["free_trial_used"]}")
    try:
        s = get_student(sid)
        if s and not s["free_trial_used"]:
            existing_trial = active_trial_session(sid)
            if existing_trial:
                return redirect(
                    url_for(
                        "active_session",
                        sid=sid,
                        session_id=existing_trial["id"]
                    )
                )
            # No active trial yet → start one now and enter it.
            return redirect(
                url_for(
                    "start_session",
                    sid=sid,
                    session_type="trial"
                )
            )
    except Exception as _e:
        print("select_subject auto-trial failed:", _e)

    # Fall back to the Learning Centre.
    return redirect(url_for("centre",sid=sid))


@app.route("/student/<int:sid>/toggle/<path:subject>")
def toggle_subject(sid,subject):

    conn = db()

    conn.execute("""
        UPDATE student_subjects
        SET active=0
        WHERE student_id=? AND subject=?
    """,(sid,subject))

    conn.commit()
    conn.close()

    return redirect(url_for("home",sid=sid))


@app.route("/student/<int:sid>/centre")
def centre(sid):

    s = get_student(sid)
    subject = get_current_subject(sid)

    if not s:
        return "Student not found",404

    if not subject:
        content = f"""
<div class="card">
  <h1>📚 Choose a subject first</h1>
  <p>To open your Learning Centre, pick at least one subject to study.</p>
  <a class="btn green" href="/student/{sid}/home">
    Choose my subjects
  </a>
</div>
"""
        return layout("Choose a subject", sid, content)

    # ========================================================
    # TRIAL FIRST, THEN PAID
    # ========================================================
    # If the student has an active (unfinished) trial session,
    # send them straight into that trial instead of the paid gate.
    try:
        trial = active_trial_session(sid)
    except Exception:
        trial = None

    if trial:
        return redirect(
            url_for(
                "active_session",
                sid=sid,
                session_id=trial["id"]
            )
        )

    # No active trial — check for a paid session
    try:
        from paid_access import active_paid_session
        paid = active_paid_session(sid)
    except Exception:
        paid = None

    # No active paid session either: if trial not used yet, offer it;
    # otherwise offer paid.
    if not paid:
        if not (s and s["free_trial_used"]):
            # Still has a free trial available → start it
            return redirect(url_for("start_session", sid=sid, session_type="trial"))
        return redirect(url_for("paid", sid=sid))

    content = f"""
<div class="hero">
    <h1>📚 {esc(subject)} Learning Centre</h1>
    <p>Welcome {esc(s['name'])}.</p>
    <p>🧑‍🏫 Tutor: <b>{esc(s['tutor'])}</b></p>
</div>

<div class="card">
    <h2 id="centre_timer">⏱️ Loading timer...</h2>
    <p><b>🔐 Paid lesson active</b></p>
    <p>Your Lessons, Playbook, Tutor and Learning Centre share this same timer.</p>

    {"<a class='btn green' href='/student/" + str(sid) + "/resume-paid?next=/student/" + str(sid) + "/centre'>▶️ RESUME LESSON</a>" if paid["paused"] else "<a class='btn orange' href='/student/" + str(sid) + "/pause-paid?next=/student/" + str(sid) + "/centre'>⏸️ PAUSE LESSON</a>"}
</div>

<div class="card">

<h2>🎓 What would you like to do?</h2>

<a class="btn green"
   href="/student/{sid}/trial">
   🆓 FREE 30-Minute Trial
</a>

<a class="btn orange"
   href="/student/{sid}/paid">
   💵 $1 — 1-Hour Lesson
</a>

<a class="btn"
   href="/student/{sid}/homework">
   📝 {esc(subject)} Homework
</a>

<a class="btn purple"
   href="/student/{sid}/tutor">
   🧑‍🏫 {esc(subject)} Tutor
</a>

<a class="btn gray"
   href="/student/{sid}/progress">
   📊 {esc(subject)} Progress
</a>

</div>

<div class="card">

<h3>🔄 Change Subject</h3>
"""

    for sub in get_subjects(sid):
        content += f"""
<a class="btn gray"
   href="/student/{sid}/select/{sub}">
   Study {esc(sub)}
</a>
"""

    content += "</div>"

    content += f"""
<script>
let centreEnd = new Date("{paid['expires_at']}").getTime();
let centrePaused = {str(bool(paid["paused"])).lower()};

function updateCentreTimer() {{
    let timer = document.getElementById("centre_timer");

    if (!timer) return;

    if (centrePaused) {{
        timer.innerHTML = "⏸️ Lesson PAUSED";
        return;
    }}

    let distance = centreEnd - new Date().getTime();

    if (distance <= 0) {{
        timer.innerHTML = "⏰ Lesson time finished";

        setTimeout(function() {{
            window.location.href = "/student/{sid}/pay";
        }}, 1000);

        return;
    }}

    let minutes = Math.floor(distance / 60000);
    let seconds = Math.floor((distance % 60000) / 1000);

    timer.innerHTML =
        "⏱️ Paid lesson time remaining: " +
        minutes + "m " + seconds + "s";
}}

updateCentreTimer();
setInterval(updateCentreTimer, 1000);
</script>
"""

    return layout(f"{subject} Learning Centre",sid,content)



# ============================================================
# FREE TRIAL SESSION HELPERS
# ============================================================

def active_trial_session(student_id):
    """
    Return the student's current unfinished free trial.

    A trial remains active while it is not completed.
    Paused trials are also considered active.
    If the trial has expired while running, it is completed here.
    """

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM student_sessions
        WHERE student_id=?
          AND session_type='trial'
          AND completed=0
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,)).fetchone()

    if not row:
        conn.close()
        return None

    try:
        expires = datetime.fromisoformat(row["expires_at"])
    except Exception:
        conn.close()
        return None

    # --------------------------------------------------------
    # PAUSED TRIAL
    # --------------------------------------------------------
    # A paused trial must remain active even if its original
    # expiry timestamp has passed.
    # Resume will extend the expiry by the paused duration.
    # --------------------------------------------------------

    if row["paused"]:
        conn.close()
        return row

    # --------------------------------------------------------
    # RUNNING TRIAL EXPIRED
    # --------------------------------------------------------

    if datetime.now() >= expires:

        conn.execute("""
            UPDATE student_sessions
            SET completed=1,
                paused=0,
                paused_at=NULL
            WHERE id=?
        """, (row["id"],))

        conn.execute("""
            UPDATE students
            SET free_trial_used=1
            WHERE id=?
        """, (student_id,))

        conn.commit()
        conn.close()

        return None

    conn.close()
    return row


def pause_trial_session(student_id):
    """
    Pause the student's free trial.
    """

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM student_sessions
        WHERE student_id=?
          AND session_type='trial'
          AND completed=0
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,)).fetchone()

    if not row:
        conn.close()
        return False, "NO_ACTIVE_TRIAL"

    if row["paused"]:
        conn.close()
        return True, "ALREADY_PAUSED"

    try:
        expires = datetime.fromisoformat(row["expires_at"])
    except Exception:
        conn.close()
        return False, "INVALID_TRIAL"

    # Do not allow an already-expired running trial to be paused.
    if datetime.now() >= expires:

        conn.execute("""
            UPDATE student_sessions
            SET completed=1
            WHERE id=?
        """, (row["id"],))

        conn.execute("""
            UPDATE students
            SET free_trial_used=1
            WHERE id=?
        """, (student_id,))

        conn.commit()
        conn.close()

        return False, "TRIAL_FINISHED"

    now_time = datetime.now().isoformat()

    conn.execute("""
        UPDATE student_sessions
        SET paused=1,
            paused_at=?
        WHERE id=?
    """, (now_time, row["id"]))

    conn.commit()
    conn.close()

    return True, "PAUSED"


def resume_trial_session(student_id):
    """
    Resume the free trial.

    The time spent paused is added to expires_at so the student
    receives the full 30 minutes of actual learning time.
    """

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM student_sessions
        WHERE student_id=?
          AND session_type='trial'
          AND completed=0
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,)).fetchone()

    if not row:
        conn.close()
        return False, "NO_ACTIVE_TRIAL"

    if not row["paused"]:
        conn.close()
        return True, "ALREADY_RUNNING"

    try:
        paused_at = datetime.fromisoformat(row["paused_at"])
    except Exception:
        paused_at = datetime.now()

    now_time = datetime.now()

    paused_seconds = max(
        0,
        int((now_time - paused_at).total_seconds())
    )

    try:
        old_expires = datetime.fromisoformat(row["expires_at"])
    except Exception:
        old_expires = now_time

    new_expires = old_expires + timedelta(
        seconds=paused_seconds
    )

    total_paused = (
        row["total_paused_seconds"] or 0
    ) + paused_seconds

    conn.execute("""
        UPDATE student_sessions
        SET paused=0,
            paused_at=NULL,
            expires_at=?,
            total_paused_seconds=?
        WHERE id=?
    """, (
        new_expires.isoformat(),
        total_paused,
        row["id"]
    ))

    conn.commit()
    conn.close()

    return True, "RESUMED"



# ============================================================
# PAUSE FREE TRIAL
# ============================================================

@app.route("/student/<int:sid>/pause-trial")
def pause_trial(sid):

    try:
        from urllib.parse import urlparse

        ok, status = pause_trial_session(sid)

    except Exception:
        ok, status = False, "ERROR"

    next_url = request.args.get("next")

    if next_url and urlparse(next_url).path.startswith(
        f"/student/{sid}/"
    ):
        return redirect(next_url)

    return redirect(
        url_for(
            "trial",
            sid=sid
        )
    )


# ============================================================
# RESUME FREE TRIAL
# ============================================================

@app.route("/student/<int:sid>/resume-trial")
def resume_trial(sid):

    try:
        from urllib.parse import urlparse

        ok, status = resume_trial_session(sid)

    except Exception:
        ok, status = False, "ERROR"

    next_url = request.args.get("next")

    if next_url and urlparse(next_url).path.startswith(
        f"/student/{sid}/"
    ):
        return redirect(next_url)

    existing = active_trial_session(sid)

    if existing:
        return redirect(
            url_for(
                "active_session",
                sid=sid,
                session_id=existing["id"]
            )
        )

    return redirect(
        url_for(
            "trial",
            sid=sid
        )
    )


@app.route("/student/<int:sid>/trial")
def trial(sid):

    subject = get_current_subject(sid)
    s = get_student(sid)

    if not subject:
        content = f"""
<div class="card">
  <h1>📚 Choose a subject first</h1>
  <p>Before you can start your free 30-minute trial, you need to pick at least one subject to study.</p>
  <p>Your trial has <b>not</b> been used up — you still have your full 30 minutes waiting.</p>
  <a class="btn green" href="/student/{sid}/home">
    Choose my subjects
  </a>
</div>
"""
        return layout("Choose a subject", sid, content)

    # --------------------------------------------------------
    # CHECK FOR EXISTING TRIAL
    # --------------------------------------------------------

    existing = active_trial_session(sid)

    if existing:

        paused = bool(existing["paused"])

        if paused:
            button_text = "▶️ RESUME FREE TRIAL"
            button_class = "green"
        else:
            button_text = "▶️ CONTINUE FREE TRIAL"
            button_class = "green"

        content = f"""
<div class="hero">
<h1>🆓 FREE 30-Minute Trial</h1>
<p>{esc(existing["subject"] or subject)}</p>
</div>

<div class="card">

<h2>
{"⏸️ Your trial is paused" if paused else "🎓 Your trial is still active"}
</h2>

<p>
Your original free trial has <b>not</b> been completed.
</p>

<p>
You still have your remaining free learning time.
Leaving the page does not use up your trial.
</p>

<a class="btn {button_class}"
href="/student/{sid}/session/{existing["id"]}">
{button_text}
</a>

<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>

</div>
"""

        return layout("Free Trial",sid,content)

    # --------------------------------------------------------
    # TRIAL ALREADY COMPLETED
    # --------------------------------------------------------

    if s["free_trial_used"]:

        content = f"""
<div class="card">

<h1>🆓 Free Trial Completed</h1>

<p>
Your 30-minute free trial has been completed.
</p>

<p>
You can now unlock a full 1-hour lesson for just <b>$1</b>.
</p>

<a class="btn orange"
href="/student/{sid}/paid">
💵 $1 — 1-HOUR LESSON
</a>

<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>

</div>
"""

        return layout("Trial Completed",sid,content)

    # --------------------------------------------------------
    # NEW FREE TRIAL
    # --------------------------------------------------------

    content = f"""
<div class="hero">
<h1>🆓 FREE 30-Minute Trial</h1>
<p>{esc(subject)}</p>
</div>

<div class="card">

<h2>Try your first lesson FREE</h2>

<p>
⏱️ Lesson length: <b>30 minutes of actual learning time</b>
</p>

<p>
You can pause your lesson, leave the page and return later.
Your trial will continue until all 30 minutes have been used.
</p>

<p>
Your tutor will guide you through the lesson and help you
understand the subject.
</p>

<a class="btn green"
href="/student/{sid}/start-session/trial">
▶️ START FREE 30-MINUTE TRIAL
</a>

<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>

</div>
"""

    return layout("Free Trial",sid,content)

@app.route("/student/<int:sid>/paid")
def paid(sid):

    subject = get_current_subject(sid)

    content = f"""
<div class="hero">
<h1>💵 $1 — 1-Hour Lesson</h1>
<p>{esc(subject)}</p>
</div>

<div class="card">

<h2>One-hour lesson</h2>

<p><b>Price: $1 USD</b></p>

<p>📱 EcoCash: Lucky Munyanyiwa — 0790 026 436</p>
<p>💰 Mukuru: Lucky Munyanyiwa — +263 719 809 683</p>

<a class="btn orange"
href="/student/{sid}/start-session/paid">
▶ START 1-HOUR LESSON
</a>



<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>

</div>
"""

    return layout("Paid Lesson",sid,content)



# ============================================================
# ACTIVE STUDENT SESSION
# ============================================================
# Handles the 30-minute FREE TRIAL session.
#
# Paid sessions use the separate master paid-session system
# and therefore use session_id=0 through the existing flow.
# ============================================================

@app.route("/student/<int:sid>/session/<int:session_id>")
def active_session(sid,session_id):
    print(f"[DBG active_session] sid={sid} session_id={session_id}")
    # --------------------------------------------------------
    # PAID MASTER SESSION
    # --------------------------------------------------------

    if session_id == 0:

        try:
            from paid_access import active_paid_session

            paid = active_paid_session(sid)

        except Exception:
            paid = None

        if not paid:
            pass
            return redirect(
                url_for(
                    "paid",
                    sid=sid
                )
            )

        subject = get_current_subject(sid) or "Lesson"

        try:
            expires = datetime.fromisoformat(
                paid["expires_at"]
            )
        except Exception:
            return redirect(
                url_for(
                    "paid",
                    sid=sid
                )
            )

        now = datetime.now()

        paused = bool(paid["paused"])

        if paused:
            timer_text = "⏸️ PAID LESSON PAUSED"
        else:
            remaining = expires - now

            total_seconds = max(
                0,
                int(remaining.total_seconds())
            )

            mins = total_seconds // 60
            secs = total_seconds % 60

            if total_seconds <= 0:
                return redirect(
                    url_for(
                        "paid",
                        sid=sid
                    )
                )

            timer_text = (
                f"⏱️ Time remaining: "
                f"{mins}m {secs:02d}s"
            )

        if paused:
            paid_button = f"""
<a class="btn green"
href="/student/{sid}/resume-paid">
▶️ RESUME LESSON
</a>
"""
        else:
            paid_button = f"""
<a class="btn orange"
href="/student/{sid}/pause-paid">
⏸️ PAUSE LESSON
</a>
"""

        content = f"""
<div class="hero">

<h1>🎓 {esc(subject)} Lesson</h1>

<p>
Your paid 1-hour lesson is
{"paused." if paused else "active."}
</p>

</div>

<div class="card">

<h2 id="paid_timer">
{timer_text}
</h2>

{paid_button}

<a class="btn green"
href="/student/{sid}/paid-lessons">
📚 START REAL PAID LESSON
</a>

<a class="btn gray"
href="/student/{sid}/home">
🏠 BACK TO HOME
</a>

<h3>🎯 Lesson Goal</h3>

<p>
Understand the topic, practise your skills and build
exam confidence.
</p>

<a class="btn purple"
href="/student/{sid}/centre">
📚 OPEN LEARNING CENTRE
</a>

</div>

<script>

let paidPaused = {"true" if paused else "false"};

let paidEnd =
new Date("{paid['expires_at']}").getTime();

function updatePaidTimer() {{

    const timer =
        document.getElementById("paid_timer");

    if (paidPaused) {{
        timer.innerHTML =
            "⏸️ PAID LESSON PAUSED";
        return;
    }}

    let now =
        new Date().getTime();

    let distance =
        paidEnd - now;

    if (distance <= 0) {{

        timer.innerHTML =
            "⏰ Lesson time finished";

        window.location.href =
            "/student/{sid}/paid";

        return;
    }}

    let mins =
        Math.floor(distance / 60000);

    let secs =
        Math.floor(
            (distance % 60000) / 1000
        );

    timer.innerHTML =
        "⏱️ Time remaining: " +
        mins + "m " +
        String(secs).padStart(2,"0") +
        "s";
}}

updatePaidTimer();

setInterval(
    updatePaidTimer,
    1000
);

</script>
"""

        return layout(
            "Active Paid Lesson",
            sid,
            content
        )


    # ========================================================
    # FREE TRIAL SESSION
    # ========================================================

    conn = db()

    session = conn.execute("""
        SELECT *
        FROM student_sessions
        WHERE id=?
          AND student_id=?
          AND session_type='trial'
        LIMIT 1
    """,(session_id,sid)).fetchone()

    conn.close()

    if not session:
        return redirect(
            url_for(
                "trial",
                sid=sid
            )
        )

    # --------------------------------------------------------
    # COMPLETED TRIAL
    # --------------------------------------------------------

    if session["completed"]:

        return redirect(
            url_for(
                "paid",
                sid=sid
            )
        )

    subject = (
        session["subject"]
        or get_current_subject(sid)
        or "Lesson"
    )

    try:
        expires = datetime.fromisoformat(
            session["expires_at"]
        )
    except Exception:
        return redirect(
            url_for(
                "paid",
                sid=sid
            )
        )

    now = datetime.now()

    paused = bool(session["paused"])

    # --------------------------------------------------------
    # RUNNING TRIAL HAS EXPIRED
    # --------------------------------------------------------

    if not paused and now >= expires:

        conn = db()

        conn.execute("""
            UPDATE student_sessions
            SET completed=1,
                paused=0,
                paused_at=NULL
            WHERE id=?
              AND student_id=?
        """,(session_id,sid))

        conn.execute("""
            UPDATE students
            SET free_trial_used=1
            WHERE id=?
        """,(sid,))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "paid",
                sid=sid
            )
        )

    # --------------------------------------------------------
    # TIMER DISPLAY
    # --------------------------------------------------------

    if paused:

        timer_text = "⏸️ TRIAL PAUSED"

    else:

        remaining = expires - now

        total_seconds = max(
            0,
            int(remaining.total_seconds())
        )

        mins = total_seconds // 60
        secs = total_seconds % 60

        timer_text = (
            f"⏱️ Time remaining: "
            f"{mins}m {secs:02d}s"
        )

    # --------------------------------------------------------
    # PAUSE / RESUME BUTTON
    # --------------------------------------------------------

    if paused:

        trial_button = f"""
<a class="btn green"
href="/student/{sid}/resume-trial?next=/student/{sid}/session/{session_id}">
▶️ RESUME TRIAL
</a>
"""

    else:

        trial_button = f"""
<a class="btn orange"
href="/student/{sid}/pause-trial?next=/student/{sid}/session/{session_id}">
⏸️ PAUSE TRIAL
</a>
"""

    content = f"""
<div class="hero">

<h1>🆓 {esc(subject)} Free Trial</h1>

<p>
Your 30-minute free trial is
{"paused." if paused else "active."}
</p>

</div>

<div class="card">

<h2 id="trial_timer">
{timer_text}
</h2>

<p>
🎓 <b>FREE 30-MINUTE TRIAL LESSON</b>
</p>

<p>
You receive 30 minutes of actual learning time.
Pausing the lesson does not consume your remaining time.
</p>

{trial_button}

<a class="btn gray"
href="/student/{sid}/home">
🏠 BACK TO HOME
</a>

<h3>🎯 Lesson Goal</h3>

<p>
Understand the topic, ask questions and build confidence.
</p>

<h3>✏️ Your Mission</h3>

<p>
Work with your tutor and complete the lesson activity.
</p>

{f'<a class="btn green" href="/student/{sid}/trial-lesson">📚 START FREE LESSON</a>' if not paused else ""}
<a class="btn purple"
href="/student/{sid}/tutor">
🧑‍🏫 ASK MY TUTOR
</a>

</div>

<script>

let trialPaused =
{"true" if paused else "false"};

let trialEnd =
new Date("{session['expires_at']}").getTime();

function updateTrialTimer() {{

    const timer =
        document.getElementById("trial_timer");

    if (trialPaused) {{

        timer.innerHTML =
            "⏸️ TRIAL PAUSED";

        return;
    }}

    let now =
        new Date().getTime();

    let distance =
        trialEnd - now;

    if (distance <= 0) {{

        timer.innerHTML =
            "⏰ Free trial finished";

        window.location.href =
            "/student/{sid}/session/{session_id}";

        return;
    }}

    let mins =
        Math.floor(distance / 60000);

    let secs =
        Math.floor(
            (distance % 60000) / 1000
        );

    timer.innerHTML =
        "⏱️ Time remaining: " +
        mins + "m " +
        String(secs).padStart(2,"0") +
        "s";
}}

updateTrialTimer();

setInterval(
    updateTrialTimer,
    1000
);

</script>
"""

    return layout(
        "Free Trial Lesson",
        sid,
        content
    )


@app.route("/student/<int:sid>/trial-lesson")
def trial_lesson(sid):

    # Get the student's active free-trial session.
    try:
        trial = active_trial_session(sid)
    except Exception:
        trial = None

    # No active trial.
    # The student must start from the FREE TRIAL page.
    if not trial:
        return redirect(url_for("trial", sid=sid))

    # A paused trial must NEVER enter the actual lesson.
    # The student must press RESUME first.
    if bool(trial["paused"]):
        return redirect(
            url_for(
                "active_session",
                sid=sid,
                session_id=trial["id"]
            )
        )

    # The trial is actively running.
    # Now it is safe to open the actual learning lesson.
    subject = trial["subject"] or get_current_subject(sid)

    if not subject:
        return redirect(url_for("home", sid=sid))


    topics = SUBJECT_TOPICS.get(subject, [])

    if not topics:
        return redirect(url_for("tutor", sid=sid))

    topic = topics[0]

    return redirect(
        url_for(
            "student_learn",
            sid=sid,
            subject=subject,
            topic=topic
        )
    )


@app.route("/student/<int:sid>/paid-lessons")
def paid_lessons(sid):

    # A real paid lesson requires the master paid session.
    try:
        from paid_access import active_paid_session
        paid = active_paid_session(sid)
    except Exception:
        paid = None

    if not paid:
        return redirect(url_for("paid", sid=sid))

    # Current subject selected by the student.
    subject = get_current_subject(sid)

    if not subject:
        return redirect(url_for("home", sid=sid))

    # Real lesson topics already supported by the learning engine.

    topics = SUBJECT_TOPICS.get(subject, [])

    if not topics:
        topics = ["Whole Numbers"] if subject == "Maths" else []

    timer_expiry = paid["expires_at"]

    content = f"""
    <!doctype html>
    <html>
    <head>
    <meta name="viewport"
          content="width=device-width,initial-scale=1">
    <title>Paid Learning Centre</title>

    <style>
    body {{
        font-family:Arial,sans-serif;
        background:#f4f7fb;
        margin:0;
        padding:20px;
    }}

    .box {{
        max-width:800px;
        margin:auto;
    }}

    .hero {{
        background:#111827;
        color:white;
        padding:24px;
        border-radius:20px;
        margin-bottom:18px;
    }}

    .timer {{
        background:#fff3cd;
        color:#664d03;
        padding:18px;
        border-radius:16px;
        margin-bottom:18px;
        text-align:center;
        font-size:20px;
        font-weight:bold;
    }}

    .card {{
        background:white;
        padding:20px;
        border-radius:18px;
        margin-bottom:14px;
        box-shadow:0 2px 10px #ddd;
    }}

    .topic {{
        display:block;
        background:#111827;
        color:white;
        padding:16px;
        margin-top:10px;
        border-radius:12px;
        text-decoration:none;
        font-weight:bold;
    }}

    .green {{
        background:#198754;
    }}

    .purple {{
        background:#6f42c1;
    }}

    .gray {{
        background:#6c757d;
    }}
    </style>
    </head>

    <body>
    <div class="box">

        <div class="hero">
            <h1>📚 Paid Learning Centre</h1>
            <p>
                This is your full paid learning session.
            </p>
            <p>
                Subject: <b>{subject}</b>
            </p>
            <p>
                Your full lesson, practice and progress tools
                are unlocked while your 60-minute session is active.
            </p>
        </div>

        <div class="timer">
            ⏱️ PAID SESSION ACTIVE
            <div id="paidTimer">Loading...</div>
        </div>

        <div class="card">
            <h2>🎯 Choose Your Lesson</h2>
            <p>
                Select a topic below to begin your real lesson.
            </p>

    """

    for topic in topics:
        safe_topic = str(topic).replace('"', '&quot;')

        content += f"""
            <a class="topic"
               href="/student/{sid}/learn?subject={subject}&topic={safe_topic}">
               📖 {safe_topic}
            </a>
        """

    content += f"""
        </div>

        <div class="card">
            <h2>🧑‍🏫 Need Help?</h2>

            <a class="topic purple"
               href="/student/{sid}/tutor">
               🧑‍🏫 ASK MY TUTOR
            </a>

            <a class="topic green"
               href="/student/{sid}/home">
               🏠 STUDENT HOME
            </a>
        </div>

    </div>

    <script>
    const expiry = new Date(
        "{timer_expiry}".replace(" ", "T")
    );

    function updatePaidTimer() {{
        const now = new Date();
        let seconds = Math.floor(
            (expiry.getTime() - now.getTime()) / 1000
        );

        if (seconds <= 0) {{
            document.getElementById("paidTimer").innerText =
                "SESSION EXPIRED";

            setTimeout(function() {{
                window.location.href =
                    "/student/{sid}/payment";
            }}, 1200);

            return;
        }}

        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;

        document.getElementById("paidTimer").innerText =
            mins + "m " +
            String(secs).padStart(2, "0") +
            "s remaining";
    }}

    updatePaidTimer();
    setInterval(updatePaidTimer, 1000);
    </script>

    </body>
    </html>
    """

    return content


# =========================================================
# PAID LESSON LAUNCHER
# =========================================================

@app.route("/student/<int:sid>/start-paid-learning")
def start_paid_learning(sid):

    try:
        from paid_access import active_paid_session
        paid = active_paid_session(sid)
    except Exception:
        paid = None

    if not paid:
        return redirect(url_for("paid", sid=sid))

    return redirect(
        url_for(
            "paid_lessons",
            sid=sid
        )
    )


@app.route("/student/<int:sid>/start-session/<session_type>")
def start_session(sid,session_type):

    # --------------------------------------------------------
    # ONLY TRIAL IS STARTED FROM THIS ROUTE.
    # PAID SESSIONS USE THE MASTER PAID-ACCESS SYSTEM.
    # --------------------------------------------------------

    if session_type not in ["trial","paid"]:
        return redirect(url_for("centre",sid=sid))

    subject = get_current_subject(sid)
    s = get_student(sid)

    if not subject:
        return redirect(url_for("home",sid=sid))

    # --------------------------------------------------------
    # FREE TRIAL
    # --------------------------------------------------------

    if session_type == "trial":

        # Never create a second unfinished trial.
        existing_trial = active_trial_session(sid)

        if existing_trial:
            return redirect(
                url_for(
                    "active_session",
                    sid=sid,
                    session_id=existing_trial["id"]
                )
            )

        # If the student has already completed their trial,
        # send them to the paid lesson page.
        if s["free_trial_used"]:
            return redirect(
                url_for(
                    "paid",
                    sid=sid
                )
            )

        # Create exactly one 30-minute trial.
        #
        # IMPORTANT:
        # The trial starts PAUSED.
        # The student's 30 minutes must not begin counting
        # until the student explicitly presses PLAY/RESUME.
        minutes = 30

        created = datetime.now()

        conn = db()

        cur = conn.execute("""
            INSERT INTO student_sessions
            (
                student_id,
                subject,
                session_type,
                started_at,
                expires_at,
                completed,
                paused,
                paused_at,
                total_paused_seconds
            )
            VALUES (?,?,?,?,?,0,1,?,0)
        """,(
            sid,
            subject,
            "trial",
            created.isoformat(),
            (created + timedelta(minutes=minutes)).isoformat(),
            created.isoformat()
        ))

        session_id = cur.lastrowid

        # IMPORTANT:
        # Do NOT set free_trial_used=1 here.
        # The flag is set only after the full 30 minutes
        # of actual learning time have been used.

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "active_session",
                sid=sid,
                session_id=session_id
            )
        )

    # --------------------------------------------------------
    # PAID SESSION
    # --------------------------------------------------------
    # Paid sessions are controlled by paid_access.py.
    # Never create a second timer here.
    # --------------------------------------------------------

    if session_type == "paid":

        try:
            from paid_access import active_paid_session

            paid = active_paid_session(sid)

        except Exception:
            paid = None

        if paid:
            return redirect(
                url_for(
                    "active_session",
                    sid=sid,
                    session_id=0
                )
            )

        return redirect(
            url_for(
                "paid",
                sid=sid
            )
        )


@app.route("/student/<int:sid>/finish-session/<int:session_id>")
def finish_session(sid,session_id):

    conn = db()

    conn.execute("""
        UPDATE student_sessions
        SET completed=1
        WHERE id=? AND student_id=?
    """,(session_id,sid))

    conn.execute("""
        UPDATE students
        SET paid_lessons=paid_lessons+1
        WHERE id=?
    """,(sid,))

    conn.commit()
    conn.close()

    content = f"""
<div class="card">

<h1>🎉 Lesson Complete!</h1>

<p>Excellent work!</p>

<p>
Keep learning, keep practising and keep building your streak.
</p>

<a class="btn purple"
href="/student/{sid}/centre">
📚 Back to Learning Centre
</a>

</div>
"""

    return layout("Lesson Complete",sid,content)


@app.route("/student/<int:sid>/tutor")
def tutor(sid):

    subject = get_current_subject(sid)

    content = f"""
<div class="hero">
<h1>🧑‍🏫 {esc(subject)} Tutor</h1>
<p>Ask your tutor a question.</p>
</div>

<div class="card">

<form method="POST"
action="/student/{sid}/tutor/ask">

<textarea
name="message"
rows="6"
placeholder="Ask your tutor a question about {{ subject }}..."
required></textarea>

<button class="btn purple" type="submit">
🧑‍🏫 Ask My Tutor
</button>

</form>

</div>

<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>
"""

    return layout(f"{subject} Tutor",sid,content)


@app.route("/student/<int:sid>/tutor/ask",methods=["POST"])
def tutor_ask(sid):

    subject = get_current_subject(sid)
    message = request.form.get("message","").strip()

    from subject_guard import apply_guard
    subject, _guard_note = apply_guard(sid, subject, message)
    _guard_html = ('<p><i>' + esc(_guard_note) + '</i></p>') if _guard_note else ''
    # Use the full tutoring chain via learning_bridge.
    # Order: brain → intelligence → bridge.ask_tutor → plain fallback.
    response = ""
    try:
        from tutor.brain import tutor_reply
        response = tutor_reply(sid, message, subject=subject)
    except Exception as _e1:
        print("tutor_ask: brain failed:", _e1)

    if not response:
        try:
            from learning_bridge import ask_tutor as _bridge_ask
            r = _bridge_ask(sid, message, subject=subject)
            response = r.get("response") or ""
            note = r.get("note") or ""
            if note:
                response = note + "<br><br>" + response
        except Exception as _e2:
            print("tutor_ask: bridge failed:", _e2)

    if not response:
        try:
            from tutor.intelligence import teach
            response = teach(sid, subject, message) or ""
        except Exception as _e3:
            print("tutor_ask: intelligence failed:", _e3)

    if not response:
        response = (
            f"<b>Your Tutor:</b><br><br>"
            f"I couldn't find a specific answer for that just now. "
            f"Try rephrasing, or ask about a topic from your {esc(subject)} curriculum."
        )

    content = f"""
<div class="hero">
<h1>🧑‍🏫 {esc(subject)} Tutor</h1>
</div>

<div class="card">

<h3>❓ You asked:</h3>

<p>{esc(message)}</p>

</div>

<div class="card">

<h3>🧑‍🏫 Tutor:</h3>

<div>
{_guard_html}{response}
</div>

</div>

<a class="btn purple"
href="/student/{sid}/tutor">
💬 Ask Another Question
</a>

<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>
"""

    return layout(f"{subject} Tutor",sid,content)


def homework_questions(subject):

    banks = {

        "Maths": [
            ("What is 25 + 37?","62"),
            ("What is 8 × 7?","56"),
            ("What is 100 ÷ 4?","25"),
            ("What is 15% of 200?","30"),
            ("Solve: 2x = 10. What is x?","5")
        ],

        "English": [
            ("Complete: The boy _____ to school every day.","goes"),
            ("Give the plural of child.","children"),
            ("What is the opposite of difficult?","easy"),
            ("Identify the verb: Sarah writes neatly.","writes"),
            ("Give the past tense of go.","went")
        ],

        "Science": [
            ("What organ pumps blood around the body?","heart"),
            ("What gas do humans breathe in?","oxygen"),
            ("What is H2O commonly called?","water"),
            ("What force pulls objects towards Earth?","gravity"),
            ("What do plants use to make food?","sunlight")
        ],

        "Biology": [
            ("What is the basic unit of life?","cell"),
            ("Which organ pumps blood?","heart"),
            ("What process do plants use to make food?","photosynthesis"),
            ("Which gas is used in photosynthesis?","carbon dioxide"),
            ("Where is genetic material found in a cell?","nucleus")
        ],

        "Chemistry": [
            ("What is the chemical symbol for oxygen?","O"),
            ("What is the chemical symbol for hydrogen?","H"),
            ("What is the pH of a neutral substance?","7"),
            ("What is the smallest unit of an element?","atom"),
            ("What is H2O?","water")
        ],

        "Physics": [
            ("What force pulls objects towards Earth?","gravity"),
            ("What is the SI unit of force?","newton"),
            ("What is the SI unit of energy?","joule"),
            ("What instrument measures temperature?","thermometer"),
            ("Speed is distance divided by what?","time")
        ],

        "Geography": [
            ("What is the largest continent?","asia"),
            ("What is the capital of Zimbabwe?","harare"),
            ("What imaginary line divides Earth into Northern and Southern Hemispheres?","equator"),
            ("What is a large body of salt water called?","ocean"),
            ("What is the study of weather called?","meteorology")
        ],

        "History": [
            ("In which year did Zimbabwe gain independence?","1980"),
            ("What was Zimbabwe called before independence?","rhodesia"),
            ("What is the study of past events called?","history"),
            ("Which ancient civilization built pyramids at Giza?","egyptian"),
            ("What event happened in 1980 in Zimbabwe?","independence")
        ],

        "Economics": [
            ("What is the study of production, distribution and consumption called?","economics"),
            ("What is the desire and ability to buy a product called?","demand"),
            ("What do producers offer for sale?","supply"),
            ("What is money paid for work called?","wages"),
            ("What is the opposite of scarcity?","abundance")
        ],

        "Accounting": [
            ("What is money owed by a business called?","liability"),
            ("What the owner invests in a business is called what?","capital"),
            ("What is money received by a business called?","income"),
            ("What is money spent by a business called?","expense"),
            ("What is the accounting equation?","assets = capital + liabilities")
        ],

        "Social Studies": [
            ("What is a group of people living together called?","community"),
            ("What is the highest law of a country called?","constitution"),
            ("What do we call people who make laws?","legislators"),
            ("What is the capital city of Zimbabwe?","harare"),
            ("What is respect for one's country called?","patriotism")
        ]
    }

    return banks.get(subject,banks["Science"])



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


@app.route("/student/<int:sid>/homework/start")
def homework_start(sid):

    subject = get_current_subject(sid)
    questions = homework_questions(subject)

    content = f"""
<div class="hero">
<h1>📝 {esc(subject)} Homework</h1>
<p>Answer all five questions.</p>
</div>

<form method="POST"
action="/student/{sid}/homework/submit">
"""

    for i,(question,correct) in enumerate(questions,1):

        content += f"""
<div class="question">

<h3>Question {i}</h3>

<p>{esc(question)}</p>

<input
type="text"
name="q{i}"
placeholder="Your answer"
required>

</div>
"""

    content += """
<button class="btn green" type="submit">
✅ SUBMIT HOMEWORK
</button>

</form>
"""

    return layout(f"{subject} Homework",sid,content)


@app.route("/student/<int:sid>/homework/submit",methods=["POST"])
def homework_submit(sid):

    subject = get_current_subject(sid)
    questions = homework_questions(subject)

    score = 0
    results = []

    for i,(question,correct) in enumerate(questions,1):

        answer = request.form.get(f"q{i}","").strip()

        good = answer.lower().strip() == correct.lower().strip()

        if good:
            score += 1

        results.append(
            (question,answer,correct,good)
        )

    percentage = int(score / len(questions) * 100)

    if percentage >= 80:
        message = "Excellent work! 🎉"
        css = "success"
    elif percentage >= 50:
        message = "Good effort! Review the questions you missed. 💪"
        css = "warning"
    else:
        message = "Don't give up. Let's learn these topics together. ❤️"
        css = "warning"

    content = f"""
<div class="hero">
<h1>📊 Homework Result</h1>
<p>{esc(subject)}</p>
</div>

<div class="card">

<h2>Score: {score}/{len(questions)}</h2>
<h2>{percentage}%</h2>

<div class="{css}">
{message}
</div>

</div>
"""

    for i,(question,answer,correct,good) in enumerate(results,1):

        content += f"""
<div class="question">

<h3>Question {i}</h3>

<p>{esc(question)}</p>

<p><b>Your answer:</b> {esc(answer)}</p>

<p><b>Correct answer:</b> {esc(correct)}</p>

<p>
{'✅ Correct' if good else '❌ Needs correction'}
</p>

</div>
"""

    content += f"""
<a class="btn purple"
href="/student/{sid}/tutor">
🧑‍🏫 Ask Tutor
</a>

<a class="btn"
href="/student/{sid}/homework">
📝 Try Again
</a>

<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>
"""

    return layout("Homework Result",sid,content)


@app.route("/student/<int:sid>/progress")
def progress(sid):

    subject = get_current_subject(sid)

    conn = db()

    try:
        rows = conn.execute("""
            SELECT topic,mastery,attempts,correct
            FROM learning_topics
            WHERE student_id=? AND subject=?
            ORDER BY mastery ASC
        """,(sid,subject)).fetchall()
    except:
        rows = []

    conn.close()

    content = f"""
<div class="hero">
<h1>📊 {esc(subject)} Progress</h1>
<p>Your learning journey.</p>
</div>

<div class="card">
"""

    if rows:

        for row in rows:

            content += f"""
<div class="question">

<h3>{esc(row['topic'])}</h3>

<p>
<b>Mastery:</b> {row['mastery']}%
</p>

<p>
Attempts: {row['attempts']} |
Correct: {row['correct']}
</p>

</div>
"""

    else:

        content += """
<p>
Your progress will appear here as you complete lessons and homework.
</p>
"""

    content += f"""
</div>

<a class="btn purple"
href="/student/{sid}/tutor">
🧑‍🏫 Study With Tutor
</a>

<a class="btn gray"
href="/student/{sid}/home">
← Back to Home
</a>
"""

    return layout(f"{subject} Progress",sid,content)


@app.route("/student/<int:sid>/profile")
def profile(sid):

    s = get_student(sid)

    if not s:
        return "Student not found",404

    content = f"""
<div class="hero">
<h1>👤 My Profile</h1>
<p>Digital Classroom Rules</p>
</div>

<div class="card">

<h2>{esc(s['name'])}</h2>

<p><b>Age:</b> {esc(s['age'])}</p>
<p><b>School:</b> {esc(s['school'])}</p>
<p><b>Location:</b> {esc(s['location'])}</p>
<p><b>Grade/Form:</b> {esc(s['grade_form'])}</p>
<p><b>Tutor:</b> {esc(s['tutor'])}</p>
<p><b>🔥 Streak:</b> {s['streak'] or 0}</p>
<p><b>📚 Paid lessons:</b> {s['paid_lessons'] or 0}</p>

</div>

<a class="btn purple"
href="/student/{sid}/centre">
📚 My Learning Centre
</a>

<a class="btn gray"
href="/student/{sid}/home">
🏠 Student Home
</a>
"""

    return layout("My Profile",sid,content)



# ==============================
# SMART LEARNING SYSTEM
# ==============================
try:
    # (moved) from student_learning import register_student_learning
    # (moved) register_student_learning(app)
    print("SMART LEARNING SYSTEM: READY")
except Exception as e:
    print("SMART LEARNING SYSTEM ERROR:", e)



# ==============================
# STUDENT ACADEMY SYSTEM
# ==============================
from student_academy import register_student_academy
register_student_academy(app)


from student_playbook import register_student_playbook
register_student_playbook(app)




from connect_playbook import register_playbook_connection
register_playbook_connection(app)

# ============================================================
# PAID ACCESS MUST LOAD BEFORE FLASK STARTS
# ============================================================
register_paid_access(app)

from student_learning import SUBJECT_TOPICS
from founder_guard import register_founder_guard
register_founder_guard(app)
from design import register_design
register_design(app)
from notices import register_notices
register_notices(app)
register_auth_routes(app)

# ============================================================
# MSASA DESIGN SYSTEM — additive /v2 routes
# ============================================================
try:
    from msasa_pages import register_msasa_pages
    register_msasa_pages(app)
    print('Msasa pages registered: /student/<sid>/v2')
except Exception as _msasa_err:
    print('msasa registration FAILED:', _msasa_err)



# ============================================================
# FOUNDER DASHBOARD / PAYMENT APPROVAL
# ============================================================
try:
    from founder_payments import register_founder_payments
    register_founder_payments(app)
    print('Founder dashboard registered: /founder/dashboard')
except Exception as _fp_err:
    print('founder_payments registration FAILED:', _fp_err)

# ============================================================
# TEMPORARY: one-shot DB upload endpoint for Railway seeding
# ============================================================
# Disabled unless SEED_UPLOAD_TOKEN is set in the environment.
# Accepts POST /admin/seed-db with the raw .db file as the body.
# After seeding, remove this block and redeploy.
# ============================================================
@app.route("/admin/seed-db", methods=["POST"])
def _admin_seed_db():
    import os as _os
    expected = _os.environ.get("SEED_UPLOAD_TOKEN", "").strip()
    if not expected:
        return "endpoint disabled (SEED_UPLOAD_TOKEN not set)", 404

    # Token can be passed as ?token=... or X-Seed-Token header
    from flask import request as _rq
    provided = (_rq.args.get("token") or
                _rq.headers.get("X-Seed-Token") or "").strip()
    if provided != expected:
        return "forbidden", 403

    # Where should we write?
    try:
        target = _os.environ.get("DB_PATH", "").strip() or "digital_classroom.db"
        # Ensure parent dir
        parent = _os.path.dirname(target)
        if parent:
            _os.makedirs(parent, exist_ok=True)

        data = _rq.get_data(cache=False, as_text=False)
        if not data or len(data) < 1024:
            return f"payload too small ({len(data)} bytes)", 400

        # Sanity: does it look like a SQLite file?
        if not data.startswith(b"SQLite format 3\x00"):
            return "not a sqlite database", 400

        # Write to a temp file first, then atomically swap in place
        tmp = target + ".seed-tmp"
        with open(tmp, "wb") as fh:
            fh.write(data)
        _os.replace(tmp, target)

        return f"seeded {len(data):,} bytes to {target}", 200
    except Exception as e:
        return f"seed failed: {type(e).__name__}: {e}", 500


if __name__ == "__main__":
    import os as _railway_os
    _port = int(_railway_os.environ.get("PORT", 5001))
    _host = "0.0.0.0" if _railway_os.environ.get("RAILWAY_ENVIRONMENT") else "127.0.0.1"
    print("")
    print("==========================================")
    print(" DIGITAL CLASSROOM - STUDENT SERVER")
    print("==========================================")
    print("Student portal:")
    print(f"http://{_host}:{_port}/student/1/home")
    print("")
    app.run(host=_host, port=_port, debug=False)


# ============================================================
# PAID ACCESS / PAYMENT VERIFICATION
# ============================================================
