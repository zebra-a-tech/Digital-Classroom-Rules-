import sqlite3
from datetime import datetime, timedelta
from flask import request, redirect, url_for, render_template_string

import os as _os_for_db


def _ensure_parent(path):
    """Create the parent directory of `path` if it doesn't exist.
    Safe to call repeatedly. Silently ignores permission errors on
    non-writable parents (sqlite3.connect will surface the real error)."""
    import os as _os
    try:
        p = path
        d = _os.path.dirname(p)
        if d and not _os.path.isdir(d):
            _os.makedirs(d, exist_ok=True)
    except Exception:
        pass

DB = _os_for_db.environ.get("DB_PATH", "digital_classroom.db")
PRICE = 1.00

ECOCASH_NAME = "Lucky Munyanyiwa"
ECOCASH_NUMBER = "0790 026 436"

MUKURU_NAME = "Lucky Munyanyiwa"
MUKURU_NUMBER = "+263 719 809 683"


# ============================================================
# DATABASE
# ============================================================

def db():
    _ensure_parent(DB)
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_tables():
    conn = db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS payment_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            subject TEXT,
            amount REAL DEFAULT 1.00,
            status TEXT DEFAULT 'PENDING',
            requested_at TEXT DEFAULT CURRENT_TIMESTAMP,
            verified_at TEXT,
            session_started TEXT,
            session_expires TEXT
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS paid_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            payment_request_id INTEGER,
            started_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            active INTEGER DEFAULT 1
        )
    """)

    conn.commit()
    conn.close()


ensure_tables()


# ============================================================
# TIME
# ============================================================

def now():
    return datetime.now()


# ============================================================
# STUDENT CHECK
# ============================================================

def student_exists(student_id):

    conn = db()

    row = conn.execute(
        "SELECT id FROM students WHERE id=?",
        (student_id,)
    ).fetchone()

    conn.close()

    return row is not None


# ============================================================
# LATEST PAYMENT
# ============================================================

def get_latest_payment(student_id):

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM payment_requests
        WHERE student_id=?
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,)).fetchone()

    conn.close()

    return row


# ============================================================
# ACTIVE PAID SESSION
# ============================================================

def active_paid_session(student_id):

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM paid_sessions
        WHERE student_id=?
        AND active=1
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,)).fetchone()

    if not row:
        conn.close()
        return None

    try:
        expires = datetime.fromisoformat(
            row["expires_at"]
        )
    except Exception:
        conn.execute("""
            UPDATE paid_sessions
            SET active=0
            WHERE id=?
        """, (row["id"],))

        conn.commit()
        conn.close()

        return None

    # --------------------------------------------------------
    # PAUSED SESSION PROTECTION
    # --------------------------------------------------------
    # While paused, the lesson must NOT expire.
    # The remaining learning time is preserved until resume.
    # --------------------------------------------------------

    if row["paused"]:
        conn.close()
        return row

    # --------------------------------------------------------
    # SESSION EXPIRED
    # --------------------------------------------------------

    if now() >= expires:

        conn.execute("""
            UPDATE paid_sessions
            SET active=0
            WHERE id=?
        """, (row["id"],))

        if row["payment_request_id"]:

            conn.execute("""
                UPDATE payment_requests
                SET session_expires=?
                WHERE id=?
            """, (
                row["expires_at"],
                row["payment_request_id"]
            ))

        conn.commit()
        conn.close()

        return None

    conn.close()

    return row



# ============================================================
# PAUSE / RESUME MASTER PAID SESSION
# ============================================================

def pause_paid_session(student_id):
    """
    Pause the master paid session.

    The remaining learning time is preserved because the original
    expiry time is moved forward when the session is resumed.
    """

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM paid_sessions
        WHERE student_id=?
        AND active=1
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,)).fetchone()

    if not row:
        conn.close()
        return False, "NO_ACTIVE_SESSION"

    if row["paused"]:
        conn.close()
        return True, "ALREADY_PAUSED"

    now_time = datetime.now().isoformat()

    conn.execute("""
        UPDATE paid_sessions
        SET paused=1,
            paused_at=?
        WHERE id=?
    """, (now_time, row["id"]))

    conn.commit()
    conn.close()

    return True, "PAUSED"


def resume_paid_session(student_id):
    """
    Resume the master paid session.

    The amount of time spent paused is added to expires_at,
    preserving the student's remaining learning time.
    """

    conn = db()

    row = conn.execute("""
        SELECT *
        FROM paid_sessions
        WHERE student_id=?
        AND active=1
        ORDER BY id DESC
        LIMIT 1
    """, (student_id,)).fetchone()

    if not row:
        conn.close()
        return False, "NO_ACTIVE_SESSION"

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
        UPDATE paid_sessions
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

def paid_access(student_id):

    return active_paid_session(student_id) is not None


# ============================================================
# PAYMENT PAGE
# ============================================================

PAYMENT_PAGE = """
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
      content="width=device-width, initial-scale=1">

<title>Unlock Your Lesson</title>

<style>

body {
    font-family: Arial, sans-serif;
    background: #f3f6fb;
    margin: 0;
    padding: 15px;
    color: #172033;
}

.container {
    max-width: 650px;
    margin: auto;
}

.card {
    background: white;
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
}

.price {
    font-size: 42px;
    font-weight: bold;
    text-align: center;
    margin: 15px;
}

.message {
    background: #fff7d6;
    padding: 18px;
    border-radius: 14px;
    line-height: 1.6;
    font-size: 17px;
}

.payment-box {
    border: 2px solid #e5e9f2;
    border-radius: 14px;
    padding: 18px;
    margin-top: 15px;
}

.number {
    font-size: 23px;
    font-weight: bold;
    margin: 8px 0;
}

input {
    width: 100%;
    box-sizing: border-box;
    padding: 14px;
    border: 1px solid #ccd3df;
    border-radius: 10px;
    font-size: 16px;
    margin-top: 8px;
    margin-bottom: 15px;
}

button {
    width: 100%;
    padding: 15px;
    border: none;
    border-radius: 12px;
    font-size: 17px;
    font-weight: bold;
    background: #1677ff;
    color: white;
}

.pending {
    background: #fff3cd;
    padding: 17px;
    border-radius: 12px;
}

.verified {
    background: #e4f7e8;
    padding: 17px;
    border-radius: 12px;
}

a {
    text-decoration: none;
}

</style>

</head>

<body>

<div class="container">


<div class="card">

<h1>📚 Unlock Your 1-Hour Lesson</h1>

<div class="price">$1</div>

<div class="message">

<strong>What's $1 compared to the knowledge you'll gain?</strong>

<br><br>

For just <strong>$1</strong>, you can unlock a focused
one-hour learning session designed to help you understand
your subject, practise and prepare with confidence.

<br><br>

<strong>
One dollar is small — but the knowledge you gain can stay
with you for years. 📚✨
</strong>

<br><br>

Your payment unlocks your <strong>60-minute paid learning
session</strong>, including the protected learning resources
available on the platform.

</div>

</div>


<div class="card">

<h2>💳 Step 1 — Pay $1</h2>

<p>
Choose either EcoCash or Mukuru.
</p>


<div class="payment-box">

<h3>📱 EcoCash</h3>

<p>
<strong>Name:</strong>
{{ ecocash_name }}
</p>

<div class="number">
{{ ecocash_number }}
</div>

<p>
Send <strong>$1</strong>.
</p>

</div>


<div class="payment-box">

<h3>💰 Mukuru</h3>

<p>
<strong>Name:</strong>
{{ mukuru_name }}
</p>

<div class="number">
{{ mukuru_number }}
</div>

<p>
Send/transfer <strong>$1</strong>.
</p>

</div>

</div>


<div class="card">

<h2>🧾 Step 2 — Submit Payment</h2>

<p>
After making your $1 payment, your Student ID will be used
automatically to identify your payment request.
</p>

<form method="POST"
action="{{ url_for(
'request_verified_paid',
student_id=student_id
) }}">

<div style="padding:14px;border-radius:10px;background:#f1f5f9;margin-bottom:15px;">
<strong>Student ID</strong><br>
<span style="font-size:24px;font-weight:bold;">
{{ student_id }}
</span>
<br>
<small>Your Student ID is automatically attached to this payment request.</small>
</div>

<p style="margin-bottom:15px;">
Once you have made your $1 payment, simply click the button below.
Your Student ID is already attached automatically.
</p>

<button type="submit">
✅ SUBMIT $1 PAYMENT FOR VERIFICATION
</button>

</form>

</div>


{% if payment %}

<div class="card">

{% if payment["status"] == "PENDING" %}

<div class="pending">

<h2>⏳ Payment Pending</h2>

<p>
Your payment request has been received.
</p>

<p>
<strong>Reference:</strong>
{{ payment["payment_note"] if "payment_note" in payment.keys()
else "Submitted" }}
</p>

<p>
Your full learning resources remain locked until the
Agent approves the payment.
</p>

</div>


{% elif payment["status"] == "VERIFIED" %}

<div class="verified">

<h2>✅ PAYMENT VERIFIED!</h2>

<p>
Your $1 payment has been verified.
</p>

<p>
You can now start your one-hour paid lesson.
</p>

<a href="{{ url_for(
'start_verified_paid',
student_id=student_id
) }}">

<button>
🚀 START MY 1-HOUR LESSON
</button>

</a>

</div>


{% elif payment["status"] == "REJECTED" %}

<div class="pending">

<h2>⚠️ Payment Not Verified</h2>

<p>
Please check your payment reference and submit the
correct transaction details.
</p>

</div>

{% endif %}

</div>

{% endif %}


<div class="card">

<p>
🔒 <strong>Important:</strong>
Playbooks, full lessons, homework, tests, exams,
tutor tools and progress resources require an active
paid session.
</p>

<p>
⏱️ Your paid access lasts exactly <strong>60 minutes</strong>
from the moment you start the lesson.
</p>

</div>


</div>

</body>
</html>
"""


# ============================================================
# PAID SESSION PAGE
# ============================================================

SESSION_PAGE = """
<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Active Paid Lesson</title>

<style>

body {
    font-family: Arial;
    background: #f3f6fb;
    padding: 15px;
}

.card {
    max-width: 650px;
    margin: auto;
    background: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 5px 20px rgba(0,0,0,.08);
}

.timer {
    font-size: 48px;
    font-weight: bold;
    text-align: center;
    margin: 25px;
}

a {
    display: block;
    padding: 14px;
    margin-top: 12px;
    background: #1677ff;
    color: white;
    text-align: center;
    text-decoration: none;
    border-radius: 10px;
}

</style>

</head>

<body>

<div class="card">

<h1>🎓 Paid Lesson Active</h1>

<p>
Your one-hour learning session is now active.
</p>

<div class="timer" id="timer">
60:00
</div>

<p>
While your session is active, your paid learning resources
are unlocked.
</p>

<a href="/student/{{ student_id }}/home">
🏠 Student Home
</a>

<a href="/student/{{ student_id }}/playbook">
📖 Open Playbook
</a>

<a href="/student/{{ student_id }}/learning">
📚 Learning Centre
</a>

</div>


<script>

const expiry =
new Date("{{ expires_at }}").getTime();

function updateTimer() {

    const current =
    new Date().getTime();

    let remaining =
    expiry - current;

    if (remaining <= 0) {

        document.getElementById("timer")
        .innerHTML = "00:00";

        alert(
        "Your 1-hour paid lesson has ended. Your paid learning resources are now locked."
        );

        window.location.href =
        "/student/{{ student_id }}/home";

        return;
    }

    let seconds =
    Math.floor(remaining / 1000);

    let minutes =
    Math.floor(seconds / 60);

    seconds =
    seconds % 60;

    document.getElementById("timer")
    .innerHTML =
    String(minutes).padStart(2,"0")
    + ":" +
    String(seconds).padStart(2,"0");
}

updateTimer();

setInterval(updateTimer,1000);

</script>

</body>

</html>
"""




# ============================================================
# REGISTER EVERYTHING
# ============================================================

def register_paid_access(app):

    ensure_tables()


    # ========================================================
    # PAYMENT PAGE
    # ========================================================

    @app.route(
        "/student/<int:student_id>/payment"
    )
    def student_payment_page(student_id):

        if not student_exists(student_id):
            return "Student not found", 404

        session = active_paid_session(student_id)

        if session:

            return redirect(
                url_for(
                    "paid_session_page",
                    student_id=student_id
                )
            )

        payment = get_latest_payment(student_id)

        return render_template_string(
            PAYMENT_PAGE,
            student_id=student_id,
            payment=payment,
            ecocash_name=ECOCASH_NAME,
            ecocash_number=ECOCASH_NUMBER,
            mukuru_name=MUKURU_NAME,
            mukuru_number=MUKURU_NUMBER
        )


    # ========================================================
    # REQUEST PAYMENT VERIFICATION
    # ========================================================

    @app.route(
        "/student/<int:student_id>/request-verified-paid",
        methods=["POST"]
    )
    def request_verified_paid(student_id):

        if not student_exists(student_id):
            return "Student not found", 404

        # The Student ID is the automatic payment identifier.
        # A transaction/reference number is no longer required
        # from the student at this stage.

        conn = db()

        # Remove previous PENDING request for this student
        conn.execute("""
            UPDATE payment_requests
            SET status='REJECTED'
            WHERE student_id=?
            AND status='PENDING'
        """, (student_id,))

        conn.execute("""
            INSERT INTO payment_requests
            (
                student_id,
                subject,
                amount,
                status
            )
            VALUES (?, ?, ?, 'PENDING')
        """, (
            student_id,
            "STUDENT_ID: " + str(student_id),
            PRICE
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "student_payment_page",
                student_id=student_id
            )
        )


    # ========================================================
    # START VERIFIED SESSION
    # ========================================================

    @app.route(
        "/student/<int:student_id>/start-verified-paid"
    )
    def start_verified_paid(student_id):

        if not student_exists(student_id):
            return "Student not found", 404

        existing = active_paid_session(student_id)

        if existing:

            return redirect(
                url_for(
                    "paid_session_page",
                    student_id=student_id
                )
            )

        payment = get_latest_payment(student_id)

        if not payment:
            return redirect(
                url_for(
                    "student_payment_page",
                    student_id=student_id
                )
            )

        if payment["status"] != "VERIFIED":

            return redirect(
                url_for(
                    "student_payment_page",
                    student_id=student_id
                )
            )

        started = now()

        expires = (
            started +
            timedelta(minutes=60)
        )

        conn = db()

        # ========================================================
        # MASTER SESSION PROTECTION
        # ========================================================
        # If this student already has an active paid session,
        # NEVER create another one and NEVER reset the timer.
        # ========================================================

        existing = conn.execute("""
            SELECT *
            FROM paid_sessions
            WHERE student_id=?
            AND active=1
            ORDER BY id DESC
            LIMIT 1
        """, (student_id,)).fetchone()

        if existing:
            try:
                existing_expires = datetime.fromisoformat(
                    existing["expires_at"]
                )

                if datetime.now() < existing_expires:
                    conn.close()

                    return redirect(
                        url_for(
                            "paid_session_page",
                            student_id=student_id
                        )
                    )

                # Existing session has expired.
                conn.execute("""
                    UPDATE paid_sessions
                    SET active=0
                    WHERE id=?
                """, (existing["id"],))

            except Exception:
                conn.execute("""
                    UPDATE paid_sessions
                    SET active=0
                    WHERE id=?
                """, (existing["id"],))

        conn.execute("""
            INSERT INTO paid_sessions
            (
                student_id,
                payment_request_id,
                started_at,
                expires_at,
                active
            )
            VALUES (?, ?, ?, ?, 1)
        """, (
            student_id,
            payment["id"],
            started.isoformat(),
            expires.isoformat()
        ))

        conn.execute("""
            UPDATE payment_requests
            SET
                session_started=?,
                session_expires=?
            WHERE id=?
        """, (
            started.isoformat(),
            expires.isoformat(),
            payment["id"]
        ))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "paid_session_page",
                student_id=student_id
            )
        )


    # ========================================================
    # ACTIVE SESSION PAGE
    # ========================================================

    @app.route(
        "/student/<int:student_id>/paid-session"
    )
    def paid_session_page(student_id):

        session = active_paid_session(student_id)

        if not session:

            return redirect(
                url_for(
                    "student_payment_page",
                    student_id=student_id
                )
            )

        return render_template_string(
            SESSION_PAGE,
            student_id=student_id,
            expires_at=session["expires_at"]
        )


    # ========================================================
    # STRICT STUDENT ACCESS CONTROL
    # ========================================================

    @app.before_request
    def paid_content_gate():

        path = request.path

        if not path.startswith("/student/"):
            return None

        parts = path.strip("/").split("/")

        if len(parts) < 2:
            return None

        if parts[0] != "student":
            return None

        try:
            student_id = int(parts[1])
        except Exception:
            return None

        # ----------------------------------------------------
        # HOME + PAYMENT ARE FREE
        # ----------------------------------------------------

        if len(parts) == 2:
            return None

        route = parts[2].lower()

        free_routes = {
            "home",
            "payment",
            "request-verified-paid",
            "start-verified-paid",
            "paid-session"
        }

        if route in free_routes:
            return None

        # ----------------------------------------------------
        # FREE 30-MINUTE TRIAL ENTRY
        # Allow ONLY /start-session/trial through.
        # /start-session/paid remains protected.
        # ----------------------------------------------------
        if (
            len(parts) >= 4
            and route == "start-session"
            and parts[3].lower() == "trial"
        ):
            return None

        # ----------------------------------------------------
        # ACTIVE FREE TRIAL SESSION
        # Allow /student/<id>/session/<session_id> ONLY when
        # that session belongs to this student and is a trial.
        # Paid sessions remain protected by the master
        # paid-session system.
        # ----------------------------------------------------
        if (
            len(parts) >= 4
            and route == "session"
        ):
            try:
                trial_session_id = int(parts[3])

                conn = db()
                trial_row = conn.execute("""
                    SELECT id, student_id, session_type, expires_at, paused
                    FROM student_sessions
                    WHERE id=?
                      AND student_id=?
                    LIMIT 1
                """, (trial_session_id, student_id)).fetchone()
                conn.close()

                print(f"GATE SESSION CHECK: session_id={trial_session_id}, student={student_id}, found={bool(trial_row)}", flush=True)

                if trial_row:
                    from datetime import datetime

                    # Paused = allow access
                    if trial_row["paused"]:
                        print(f"GATE: allowing paused session", flush=True)
                        return None

                    # Check expiry
                    try:
                        expires = datetime.fromisoformat(trial_row["expires_at"])
                        if datetime.now() < expires:
                            print(f"GATE: allowing unexpired session (expires {expires})", flush=True)
                            return None
                        else:
                            print(f"GATE: session EXPIRED (was {expires})", flush=True)
                    except Exception as ex:
                        print(f"GATE: expiry parse error: {ex}", flush=True)
                        return None  # Allow if we can't parse

            except Exception as ex:
                print(f"GATE: session lookup error: {ex}", flush=True)
                pass

        # ----------------------------------------------------
        # REAL FREE-TRIAL LEARNING ACCESS
        # ----------------------------------------------------
        # During an unfinished free trial the learner may:
        #
        #   /learn
        #   /tutor
        #   /check-answer
        #
        # Everything else remains protected.
        #
        # A paused trial is also allowed to access learning.
        # ----------------------------------------------------

        trial_learning_routes = {
            "learn",
            "tutor",
            "check-answer",
            "trial-lesson",
            "playbook",
            "playbook-answer",
            "centre"
        }

        if route in trial_learning_routes:

            try:
                conn = db()

                trial_row = conn.execute("""
                    SELECT id, paused, expires_at
                    FROM student_sessions
                    WHERE student_id=?
                      -- session_type filter removed
                      AND completed=0
                    ORDER BY id DESC
                    LIMIT 1
                """, (student_id,)).fetchone()

                conn.close()

                if trial_row:

                    if trial_row["paused"]:
                        return None

                    from datetime import datetime

                    try:
                        trial_expires = datetime.fromisoformat(
                            trial_row["expires_at"]
                        )
                    except Exception:
                        trial_expires = None

                    if (
                        trial_expires is not None
                        and datetime.now() < trial_expires
                    ):
                        return None

            except Exception:
                pass

        # ----------------------------------------------------
        # EVERY OTHER STUDENT FEATURE IS PAID
        # ----------------------------------------------------

        protected = (
            "playbook",
            "lesson",
            "learning",
            "learn",
            "homework",
            "test",
            "exam",
            "tutor",
            "smart",
            "progress",
            "report",
            "recovery",
            "academy",
            "session",
            "check-answer"
        )

        is_protected = any(
            word in route
            for word in protected
        )

        if not is_protected:
            return None

        # ----------------------------------------------------
        # CHECK 60-MINUTE PAID SESSION
        # ----------------------------------------------------

        if paid_access(student_id):
            return None

        # ----------------------------------------------------
        # LOCK
        # ----------------------------------------------------

        return redirect(
            url_for(
                "student_payment_page",
                student_id=student_id
            )
        )


    # ========================================================
    # FOUNDER PAYMENT DASHBOARD
    # ========================================================

    @app.route(
        "/founder/payments"
    )
    def founder_payment_dashboard():

        conn = db()

        rows = conn.execute("""
            SELECT
                p.*,
                s.name AS student_name,
                s.grade_form,
                s.subject AS student_subject
            FROM payment_requests p
            LEFT JOIN students s
                ON s.id=p.student_id
            ORDER BY p.id DESC
        """).fetchall()

        conn.close()

        html = """

<!DOCTYPE html>
<html>

<head>

<meta name="viewport"
content="width=device-width, initial-scale=1">

<title>Payment Verification</title>

<style>

body {
    font-family: Arial;
    background: #f3f6fb;
    padding: 15px;
}

.card {
    background: white;
    padding: 20px;
    margin-bottom: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 15px rgba(0,0,0,.08);
}

button {
    padding: 13px;
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: bold;
}

.verify {
    background: #159447;
}

.reject {
    background: #d9534f;
}

</style>

</head>

<body>

<h1>💳 Payment Verification</h1>

<p>
Check the payment before granting the 60-minute lesson.
</p>

{% for p in rows %}

<div class="card">

<h2>
{{ p['student_name'] or 'Student' }}
</h2>

<p>
<strong>Student ID:</strong>
{{ p['student_id'] }}
</p>

<p>
<strong>Grade/Form:</strong>
{{ p['grade_form'] or '' }}
</p>

<p>
<strong>Subject:</strong>
{{ p['student_subject'] or '' }}
</p>

<p>
<strong>Amount:</strong>
${{ "%.2f"|format(p['amount']) }}
</p>

<p>
<strong>Student Payment Identifier:</strong><br>
{{ p['subject'] or 'Not supplied' }}
</p>

<p>
<strong>Status:</strong>
{{ p['status'] }}
</p>

{% if p['status'] == 'PENDING' %}

<a href="{{ url_for(
'founder_verify_payment',
request_id=p['id']
) }}">

<button class="verify">
✅ VERIFY PAYMENT
</button>

</a>

<a href="{{ url_for(
'founder_reject_payment',
request_id=p['id']
) }}">

<button class="reject">
❌ REJECT
</button>

</a>

{% endif %}

</div>

{% else %}

<div class="card">
No payment requests yet.
</div>

{% endfor %}

</body>

</html>

"""

        return render_template_string(
            html,
            rows=rows
        )


    # ========================================================
    # REJECT PAYMENT
    # ========================================================

    @app.route(
        "/founder/payments/<int:request_id>/reject"
    )
    def founder_reject_payment(request_id):

        conn = db()

        conn.execute("""
            UPDATE payment_requests
            SET status='REJECTED'
            WHERE id=?
        """, (request_id,))

        conn.commit()
        conn.close()

        return redirect(
            url_for(
                "founder_payment_dashboard"
            )
        )


    print(
        "✅ PAID ACCESS LOADED — DATABASE COMPATIBLE"
    )
