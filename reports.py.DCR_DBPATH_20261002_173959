"""
reports.py — Digital Classroom Rules
------------------------------------

Weekly academic report generator. Reads ONLY. Never writes.

Public API:

    weekly_report(student_id, week_start=None) -> dict
    format_report_text(report) -> str        # plain-text version

Data sources (real tables):
  - learning_progress       : attempts, correct, mastery per (subject, topic)
  - homework                : per-row completed / score
  - assignments             : per-row score, percentage, completed
  - assignment_submissions  : status, score, total_marks, percentage
  - weekly_assignments      : week-scoped homework sets
  - student_sessions        : trial timing
  - paid_sessions           : paid lesson timing, paused seconds
  - academic_tests/exams    : test scores
  - tutor_memory            : recent academic interactions

The report is generated entirely from real DB rows. No fabricated stats.
"""

import os
import sqlite3
import datetime


_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, "digital_classroom.db")


# ------------------------------------------------------------
# low-level, read-only
# ------------------------------------------------------------
def _ro():
    con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def _all(con, sql, params=()):
    try:
        return list(con.execute(sql, params))
    except sqlite3.OperationalError:
        return []


def _one(con, sql, params=()):
    try:
        return con.execute(sql, params).fetchone()
    except sqlite3.OperationalError:
        return None


# ------------------------------------------------------------
# helpers
# ------------------------------------------------------------
def _week_bounds(when=None):
    """
    Return (start_dt, end_dt, label) for a Monday–Sunday week.

    If `when` is None, use the week containing today.
    If `when` is a date/datetime, use the week containing it.
    """
    if when is None:
        when = datetime.date.today()
    if isinstance(when, datetime.datetime):
        when = when.date()
    # Monday of this week
    start = when - datetime.timedelta(days=when.weekday())
    end = start + datetime.timedelta(days=6)
    label = f"{start.strftime('%d %b %Y')} – {end.strftime('%d %b %Y')}"
    return start, end, label


def _in_range(dt_str, start, end):
    """True if the ISO-ish string falls within [start, end] inclusive."""
    if not dt_str:
        return False
    # Try common formats
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%f",
                "%Y-%m-%d"):
        try:
            d = datetime.datetime.strptime(dt_str[:len(fmt)+6].split(".")[0] if "." in fmt else dt_str[:len(fmt)], fmt)
            d = d.date() if isinstance(d, datetime.datetime) else d
            return start <= d <= end
        except Exception:
            continue
    # Last resort: prefix compare on YYYY-MM-DD
    return start.isoformat() <= (dt_str or "")[:10] <= end.isoformat()


def _avg(nums):
    nums = [n for n in nums if isinstance(n, (int, float))]
    return round(sum(nums) / len(nums), 1) if nums else None


# ------------------------------------------------------------
# main
# ------------------------------------------------------------
def weekly_report(student_id, week_start=None):
    """
    Build the weekly report dict for a student.

    `week_start` may be:
      - None (this week)
      - a `datetime.date` (week containing that date)
      - a 'YYYY-MM-DD' string

    Returns a dict. All numbers come from real DB rows.
    """
    if isinstance(week_start, str):
        try:
            week_start = datetime.datetime.strptime(week_start, "%Y-%m-%d").date()
        except Exception:
            week_start = None

    start, end, label = _week_bounds(week_start)

    con = _ro()
    try:
        # --- student ---
        stu = _one(con, """
            SELECT id, name, grade_form, school, student_number,
                   current_subject, tutor, streak
            FROM students WHERE id=?
        """, (student_id,))
        if not stu:
            return {"error": f"no such student {student_id}"}

        # --- subjects studied this week ---
        lp_rows = _all(con, """
            SELECT subject, topic, attempts, correct, mastery, last_activity
            FROM learning_progress
            WHERE student_id=?
        """, (student_id,))

        week_lp = [dict(r) for r in lp_rows
                   if _in_range(r["last_activity"], start, end)]

        # Fallback: if nothing in this exact week, use the latest snapshot
        # so the report is never blank. Mark this in the report.
        fallback_used = False
        if not week_lp:
            fallback_used = True
            week_lp = [dict(r) for r in lp_rows]

        subjects_studied = sorted({r["subject"] for r in week_lp if r["subject"]})

        # --- questions ---
        qa = sum(int(r["attempts"] or 0) for r in week_lp)
        qc = sum(int(r["correct"] or 0) for r in week_lp)
        accuracy = round(100.0 * qc / qa, 1) if qa else None

        # --- per-topic mastery ---
        topic_rows = [
            {
                "subject": r["subject"],
                "topic": r["topic"],
                "attempts": int(r["attempts"] or 0),
                "correct": int(r["correct"] or 0),
                "mastery": int(r["mastery"] or 0),
            }
            for r in week_lp
        ]
        topics_mastered = [t for t in topic_rows if t["mastery"] >= 80]
        topics_weak = [t for t in topic_rows if t["mastery"] < 70]

        strongest = max(topic_rows, key=lambda t: t["mastery"]) if topic_rows else None
        weakest = min(topic_rows, key=lambda t: t["mastery"]) if topic_rows else None
        # If only one topic, strongest and weakest would be identical — hide weakest.
        if strongest and weakest and \
                strongest["subject"] == weakest["subject"] and \
                strongest["topic"] == weakest["topic"]:
            weakest = None

        # --- homework ---
        hw_rows = _all(con, """
            SELECT id, subject, topic, score, completed, created_at, completed_at
            FROM homework WHERE student_id=?
        """, (student_id,))
        hw_week = [dict(r) for r in hw_rows
                   if _in_range(r["completed_at"] or r["created_at"], start, end)]
        if not hw_week:
            hw_week = [dict(r) for r in hw_rows]
        hw_completed = [h for h in hw_week if h.get("completed")]
        hw_avg = _avg([h.get("score") for h in hw_completed])

        # --- assignments ---
        as_rows = _all(con, """
            SELECT id, subject, topic, score, percentage, completed, created_at, completed_at
            FROM assignments WHERE student_id=?
        """, (student_id,))
        as_week = [dict(r) for r in as_rows
                   if _in_range(r["completed_at"] or r["created_at"], start, end)]
        if not as_week:
            as_week = [dict(r) for r in as_rows]
        as_completed = [a for a in as_week if a.get("completed") or (a.get("percentage") or 0) > 0]
        as_avg = _avg([a.get("percentage") for a in as_completed])

        # --- assignment submissions ---
        subs_rows = _all(con, """
            SELECT id, assignment_id, status, score, total_marks, percentage,
                   submitted_at, marked_at
            FROM assignment_submissions WHERE student_id=?
        """, (student_id,))
        subs_week = [dict(r) for r in subs_rows
                     if _in_range(r["marked_at"] or r["submitted_at"], start, end)]
        if not subs_week:
            subs_week = [dict(r) for r in subs_rows]
        subs_marked = [s for s in subs_week if s.get("status") in ("MARKED", "RETURNED", "COMPLETED")]
        subs_avg = _avg([s.get("percentage") for s in subs_marked])

        # --- weekly assignments ---
        wa_rows = _all(con, """
            SELECT id, week_number, subject, topic, grade_form, score, percentage,
                   completed, generated_at, completed_at
            FROM weekly_assignments WHERE student_id=?
        """, (student_id,))
        wa_week = [dict(r) for r in wa_rows
                   if _in_range(r["completed_at"] or r["generated_at"], start, end)]
        if not wa_week:
            wa_week = [dict(r) for r in wa_rows]

        # --- learning minutes from sessions ---
        trial_minutes = 0.0
        paid_minutes = 0.0

        t_rows = _all(con, """
            SELECT started_at, expires_at, completed
            FROM student_sessions
            WHERE student_id=? AND session_type='trial'
        """, (student_id,))
        for t in t_rows:
            if _in_range(t["started_at"], start, end):
                try:
                    s = datetime.datetime.fromisoformat(t["started_at"])
                    e = datetime.datetime.fromisoformat(t["expires_at"])
                    secs = max(0, (e - s).total_seconds())
                    trial_minutes += secs / 60.0
                except Exception:
                    pass

        p_rows = _all(con, """
            SELECT started_at, expires_at, total_paused_seconds
            FROM paid_sessions WHERE student_id=?
        """, (student_id,))
        for p in p_rows:
            if _in_range(p["started_at"], start, end):
                try:
                    s = datetime.datetime.fromisoformat(p["started_at"])
                    e = datetime.datetime.fromisoformat(p["expires_at"])
                    secs = max(0, (e - s).total_seconds() - (p["total_paused_seconds"] or 0))
                    paid_minutes += secs / 60.0
                except Exception:
                    pass

        learning_minutes = round(trial_minutes + paid_minutes, 1)

        # --- tests & exams ---
        test_rows = _all(con, """
            SELECT subject, score, total, percentage, completed_at
            FROM academic_tests WHERE student_id=?
        """, (student_id,))
        test_week = [dict(r) for r in test_rows
                     if _in_range(r["completed_at"], start, end)]
        if not test_week:
            test_week = [dict(r) for r in test_rows]
        test_avg = _avg([t.get("percentage") for t in test_week])

        exam_rows = _all(con, """
            SELECT subject, score, total, percentage, completed_at
            FROM academic_exams WHERE student_id=?
        """, (student_id,))
        exam_week = [dict(r) for r in exam_rows
                     if _in_range(r["completed_at"], start, end)]
        if not exam_week:
            exam_week = [dict(r) for r in exam_rows]
        exam_avg = _avg([e.get("percentage") for e in exam_week])

        # --- tutor interactions (recent) ---
        tm_rows = _all(con, """
            SELECT subject, message, response, created_at
            FROM tutor_memory WHERE student_id=?
            ORDER BY id DESC LIMIT 20
        """, (student_id,))
        tutor_recent = []
        for r in tm_rows:
            if _in_range(r["created_at"], start, end) or not tutor_recent:
                tutor_recent.append(dict(r))
            if len(tutor_recent) >= 5:
                break

        # --- build recommendations from real data ---
        recs = []
        if weakest and weakest["mastery"] < 70:
            recs.append(
                f"Focus on {weakest['subject']} — {weakest['topic']} "
                f"(mastery {weakest['mastery']}%)."
            )
        if hw_avg is not None and hw_avg < 60:
            recs.append(f"Homework average is {hw_avg}% this week — aim for 70%+ next week.")
        if accuracy is not None and accuracy < 60:
            recs.append(f"Answer accuracy is {accuracy}% — review worked examples before answering.")
        if as_avg is not None and as_avg >= 80:
            recs.append("Excellent assignment average — maintain this standard.")
        if not recs:
            recs.append("Keep up the steady effort — no urgent concerns this week.")

        # --- next week's focus ---
        next_focus = []
        for t in sorted(topics_weak, key=lambda x: x["mastery"])[:3]:
            next_focus.append(f"{t['subject']} → {t['topic']} (mastery {t['mastery']}%)")
        if not next_focus:
            # study next unstudied topic if we can find one
            next_focus.append("Continue with the next unstudied topic in your current subject.")

        report = {
            "student": {
                "id": stu["id"],
                "name": stu["name"],
                "student_number": stu["student_number"],
                "grade_form": stu["grade_form"],
                "school": stu["school"],
                "tutor": stu["tutor"],
                "streak": stu["streak"] or 0,
            },
            "week": {
                "start": start.isoformat(),
                "end": end.isoformat(),
                "label": label,
                "fallback_used": fallback_used,
            },
            "subjects_studied": subjects_studied,
            "learning_minutes": learning_minutes,
            "questions_attempted": qa,
            "questions_correct": qc,
            "accuracy": accuracy,
            "homework": {
                "assigned": len(hw_week),
                "completed": len(hw_completed),
                "average": hw_avg,
            },
            "assignments": {
                "assigned": len(as_week),
                "completed": len(as_completed),
                "average": as_avg,
                "submissions_marked": len(subs_marked),
                "submission_average": subs_avg,
            },
            "weekly_assignments": [
                {
                    "week_number": w.get("week_number"),
                    "subject": w.get("subject"),
                    "topic": w.get("topic"),
                    "score": w.get("score"),
                    "percentage": w.get("percentage"),
                    "completed": bool(w.get("completed")),
                }
                for w in wa_week
            ],
            "tests": {
                "count": len(test_week),
                "average": test_avg,
            },
            "exams": {
                "count": len(exam_week),
                "average": exam_avg,
            },
            "topics_mastered": [
                {"subject": t["subject"], "topic": t["topic"], "mastery": t["mastery"]}
                for t in sorted(topics_mastered, key=lambda x: -x["mastery"])
            ],
            "topics_needing_improvement": [
                {"subject": t["subject"], "topic": t["topic"], "mastery": t["mastery"]}
                for t in sorted(topics_weak, key=lambda x: x["mastery"])
            ],
            "strongest": strongest,
            "weakest": weakest,
            "tutor_recent": tutor_recent,
            "tutor_recommendations": recs,
            "next_week_focus": next_focus,
        }
        return report
    finally:
        con.close()


# ------------------------------------------------------------
# plain-text rendering (for chat/WhatsApp/CLI)
# ------------------------------------------------------------
def format_report_text(rep):
    if rep.get("error"):
        return f"Weekly report unavailable: {rep['error']}"
    s = rep["student"]
    w = rep["week"]
    lines = []
    lines.append("=" * 60)
    lines.append(f"WEEKLY REPORT — {s['name']} ({s['student_number'] or ''})")
    lines.append(f"Grade/Form: {s['grade_form'] or '—'}   Tutor: {s['tutor'] or '—'}")
    lines.append(f"Week: {w['label']}")
    if w.get("fallback_used"):
        lines.append("(no activity this week — showing most recent snapshot)")
    lines.append("=" * 60)
    lines.append(f"Subjects studied:  {', '.join(rep['subjects_studied']) or '—'}")
    lines.append(f"Learning minutes:  {rep['learning_minutes']}")
    lines.append(f"Questions:         {rep['questions_correct']}/{rep['questions_attempted']}  "
                 f"({rep['accuracy']}%)" if rep['accuracy'] is not None else "Questions: 0")
    lines.append(f"Homework:          {rep['homework']['completed']}/{rep['homework']['assigned']}  "
                 f"avg={rep['homework']['average']}")
    lines.append(f"Assignments:       {rep['assignments']['completed']}/{rep['assignments']['assigned']}  "
                 f"avg={rep['assignments']['average']}")
    lines.append(f"Tests: {rep['tests']['count']}  avg={rep['tests']['average']}   "
                 f"Exams: {rep['exams']['count']}  avg={rep['exams']['average']}")
    lines.append("")
    lines.append("Topics mastered:")
    for t in rep["topics_mastered"]:
        lines.append(f"  ✓ {t['subject']} / {t['topic']} ({t['mastery']}%)")
    if not rep["topics_mastered"]:
        lines.append("  (none yet)")
    lines.append("")
    lines.append("Topics needing improvement:")
    for t in rep["topics_needing_improvement"]:
        lines.append(f"  ! {t['subject']} / {t['topic']} ({t['mastery']}%)")
    if not rep["topics_needing_improvement"]:
        lines.append("  (none)")
    lines.append("")
    lines.append("Tutor recommendations:")
    for r in rep["tutor_recommendations"]:
        lines.append(f"  • {r}")
    lines.append("")
    lines.append("Next week's focus:")
    for f in rep["next_week_focus"]:
        lines.append(f"  → {f}")
    lines.append("=" * 60)
    return "\n".join(lines)


# ------------------------------------------------------------
# CLI self-test
# ------------------------------------------------------------
if __name__ == "__main__":
    import sys, json
    sid = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    rep = weekly_report(sid)
    print(format_report_text(rep))
    print()
    print("--- JSON ---")
    print(json.dumps(rep, indent=2, default=str))
