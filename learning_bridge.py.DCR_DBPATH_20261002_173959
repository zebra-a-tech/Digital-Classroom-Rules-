"""
learning_bridge.py — Digital Classroom Rules
--------------------------------------------

A thin, non-duplicating façade over the EXISTING tutoring + curriculum
machinery. It does not re-implement grade bands, curriculum lookup, or
tutor memory. It calls:

    student_learning.get_grade_aware_lesson(student_id, subject, topic)
    student_learning.get_grade_aware_question(student_id, subject, topic, idx)
    student_learning.get_student_grade_form(student_id)
    student_learning.get_student_learning_band(student_id)
    student_learning.SUBJECT_TOPICS
    subject_guard.apply_guard(sid, current, message)
    tutor.brain.tutor_reply(student_id, message, subject=None)

It writes progress ONLY to `learning_progress`. It never touches
curriculum, lessons, paid_sessions, student_sessions, or auth_users.

Public API:

    get_student(sid) -> dict
    get_active_subjects(sid) -> list[str]
    get_current_subject(sid) -> str
    set_current_subject(sid, subject) -> bool
    pick_topic(sid, subject) -> str          # topic with lowest mastery / fallback
    next_item(sid, subject=None, topic=None, question_index=None) -> dict
    submit_answer(sid, subject, topic, answer, correct=None, question_index=None) -> dict
    ask_tutor(sid, message, subject=None) -> dict

Every function that writes is explicit. Reads are read-only.
"""

import os
import sqlite3
import datetime

# ---- resolve DB relative to this file (cwd-independent) ----
_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, "digital_classroom.db")


# ============================================================
# low-level DB helpers (local, tiny — no circular import)
# ============================================================
def _connect(readonly=False):
    if readonly:
        con = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True, timeout=10)
    else:
        con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def _one(sql, params=(), readonly=True):
    con = _connect(readonly=readonly)
    try:
        return con.execute(sql, params).fetchone()
    finally:
        con.close()


def _all(sql, params=(), readonly=True):
    con = _connect(readonly=readonly)
    try:
        return list(con.execute(sql, params))
    finally:
        con.close()


def _write(sql, params=()):
    con = _connect(readonly=False)
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


# ============================================================
# lazy imports of the EXISTING modules (so import errors surface
# only when a bridge function is actually called)
# ============================================================
def _import_student_learning():
    import student_learning
    return student_learning


def _import_subject_guard():
    import subject_guard
    return subject_guard


def _import_tutor_brain():
    import importlib
    return importlib.import_module("tutor.brain")


# ============================================================
# student facts
# ============================================================
def get_student(sid):
    """Return {id, name, grade_form, current_subject, tutor, school, ...} or None."""
    row = _one("""
        SELECT id, name, age, school, location, grade_form, tutor,
               current_subject, exam_board, student_number, streak
        FROM students WHERE id = ?
    """, (sid,))
    return dict(row) if row else None


def get_active_subjects(sid):
    """Return list of active subject strings for the student."""
    rows = _all("""
        SELECT subject FROM student_subjects
        WHERE student_id = ? AND active = 1
        ORDER BY subject
    """, (sid,))
    return [r["subject"] for r in rows]


def get_current_subject(sid):
    """The student's current_subject, if it's an active subject. Else first active."""
    stu = get_student(sid)
    if not stu:
        return ""
    current = (stu.get("current_subject") or "").strip()
    active = get_active_subjects(sid)
    if current and current in active:
        return current
    return active[0] if active else ""


def set_current_subject(sid, subject):
    """Persist the student's current subject. Returns True on success."""
    active = get_active_subjects(sid)
    if subject not in active:
        return False
    _write("UPDATE students SET current_subject = ? WHERE id = ?", (subject, sid))
    return True


# ============================================================
# topic selection
# ============================================================
def pick_topic(sid, subject):
    """
    Choose the next topic for the student in `subject`.

    Order of preference:
      1) The topic in `subject` with the LOWEST mastery that has attempts > 0
         (so we revisit what they struggle with).
      2) Any topic in `subject` with NO progress row yet (fresh content).
      3) The first topic in SUBJECT_TOPICS[subject] as fallback.
    Returns "" if the subject has no topics defined.
    """
    sl = _import_student_learning()
    topics = list(sl.SUBJECT_TOPICS.get(subject, []))
    if not topics:
        return ""

    # 1) weakest studied topic
    rows = _all("""
        SELECT topic, mastery FROM learning_progress
        WHERE student_id = ? AND subject = ?
          AND topic IS NOT NULL AND topic != ''
    """, (sid, subject))
    studied = {r["topic"]: (r["mastery"] or 0) for r in rows}
    if studied:
        weakest = sorted(studied.items(), key=lambda kv: kv[1])
        # But only prefer the weakest if mastery < 90
        if weakest[0][1] < 90:
            return weakest[0][0]

    # 2) first unstudied topic
    for t in topics:
        if t not in studied:
            return t

    # 3) everything studied — go back to the weakest
    if studied:
        return sorted(studied.items(), key=lambda kv: kv[1])[0][0]

    return topics[0]


# ============================================================
# next item (lesson + question)
# ============================================================
def next_item(sid, subject=None, topic=None, question_index=None):
    """
    Return the next teaching item for the student.

    Shape:
      {
        "student_id": int,
        "subject": str,
        "topic": str,
        "grade_form": str,
        "learning_band": str,
        "lesson": dict,          # from get_grade_aware_lesson
        "question": dict,        # question dict (fields vary — pass through)
        "question_index": int,
        "source": "curriculum" | "fallback",
      }

    Raises ValueError if the student is missing, or the subject is empty.
    """
    sl = _import_student_learning()

    stu = get_student(sid)
    if not stu:
        raise ValueError(f"No such student: {sid}")

    if not subject:
        subject = get_current_subject(sid)
    if not subject:
        raise ValueError(f"Student {sid} has no active subject.")

    active = get_active_subjects(sid)
    if subject not in active:
        raise ValueError(f"Subject {subject!r} is not active for student {sid}.")

    if not topic:
        topic = pick_topic(sid, subject)
    if not topic:
        raise ValueError(f"No topics defined for subject {subject!r}.")

    grade_form = sl.get_student_grade_form(sid) or stu.get("grade_form") or ""
    band = sl.get_student_learning_band(sid) or ""

    # Lesson: dict
    lesson = sl.get_grade_aware_lesson(sid, subject, topic) or {}

    # Question: (lesson_dict, index)
    q_lesson, q_index = sl.get_grade_aware_question(sid, subject, topic, question_index)

    # q_lesson is a superset of lesson + question fields. Prefer it.
    merged = dict(lesson)
    merged.update(q_lesson or {})

    # Question-specific fields
    question_text = (
        merged.get("question")
        or merged.get("prompt")
        or merged.get("text")
        or merged.get("question_text")
        or ""
    )
    # Real curriculum uses `answers` (list of accepted forms).
    correct = (
        merged.get("answers")
        or merged.get("answer")
        or merged.get("correct_answer")
        or merged.get("correct")
        or []
    )

    source = "curriculum" if merged.get("_curriculum") else "fallback"

    return {
        "student_id": sid,
        "subject": subject,
        "topic": topic,
        "grade_form": grade_form,
        "learning_band": band,
        "lesson": lesson,
        "question": merged,
        "question_text": question_text,
        "correct_answer": correct,
        "question_index": q_index,
        "source": source,
    }


# ============================================================
# answer submission + progress write
# ============================================================
def _norm(s):
    return " ".join(str(s or "").strip().lower().split())


def _check_answer(student_answer, correct_answer):
    """
    Deterministic grader.

    `correct_answer` may be:
      - a single string, or
      - a list/tuple of acceptable strings (the real curriculum uses `answers`).

    Returns True if the student's answer matches ANY accepted form.
    """
    a = _norm(student_answer)
    if not a:
        return False

    # Normalise correct_answer into a list of candidates
    if isinstance(correct_answer, (list, tuple, set)):
        candidates = [_norm(x) for x in correct_answer if _norm(x)]
    else:
        candidates = [_norm(correct_answer)] if _norm(correct_answer) else []

    if not candidates:
        return False

    for b in candidates:
        if a == b:
            return True
        # numeric compare
        try:
            if float(a) == float(b):
                return True
        except Exception:
            pass
        # substring compare (guards against minor wording differences)
        if len(b) >= 4 and (b in a or a in b):
            return True
    return False


def submit_answer(sid, subject, topic, answer, correct=None, question_index=None):
    """
    Grade the student's answer, write to learning_progress, return a result dict.

    If `correct` is None, the bridge will look up the expected answer using
    get_grade_aware_question(sid, subject, topic, question_index).
    Otherwise the caller may pass a pre-known correct answer string.

    Shape:
      {
        "student_id", "subject", "topic",
        "answer", "expected",
        "is_correct": bool,
        "attempts": int, "correct_total": int, "mastery": int,
        "band": str, "grade_form": str,
      }
    """
    sl = _import_student_learning()

    stu = get_student(sid)
    if not stu:
        raise ValueError(f"No such student: {sid}")

    active = get_active_subjects(sid)
    if subject not in active:
        raise ValueError(f"Subject {subject!r} is not active for student {sid}.")

    # Resolve expected answer if not supplied — single curriculum call.
    expected = correct
    if expected is None:
        try:
            q_lesson, _ = sl.get_grade_aware_question(
                sid, subject, topic, question_index
            )
        except Exception:
            q_lesson = {}
        merged = dict(q_lesson or {})
        expected = (
            merged.get("answers")
            or merged.get("answer")
            or merged.get("correct_answer")
            or merged.get("correct")
            or []
        )

    is_correct = _check_answer(answer, expected)

    # Upsert into learning_progress
    row = _one("""
        SELECT id, attempts, correct, mastery FROM learning_progress
        WHERE student_id=? AND subject=? AND topic=?
    """, (sid, subject, topic))

    now = datetime.datetime.now().isoformat(timespec="seconds")

    if row:
        attempts = (row["attempts"] or 0) + 1
        correct_total = (row["correct"] or 0) + (1 if is_correct else 0)
        mastery = int(round(100.0 * correct_total / attempts)) if attempts else 0
        _write("""
            UPDATE learning_progress
               SET attempts=?, correct=?, mastery=?, last_activity=?
             WHERE id=?
        """, (attempts, correct_total, mastery, now, row["id"]))
    else:
        attempts = 1
        correct_total = 1 if is_correct else 0
        mastery = 100 if is_correct else 0
        _write("""
            INSERT INTO learning_progress
                (student_id, subject, topic, attempts, correct, mastery, last_activity)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (sid, subject, topic, attempts, correct_total, mastery, now))

    return {
        "student_id": sid,
        "subject": subject,
        "topic": topic,
        "answer": answer,
        "expected": expected,
        "is_correct": is_correct,
        "attempts": attempts,
        "correct_total": correct_total,
        "mastery": mastery,
        "band": sl.get_student_learning_band(sid),
        "grade_form": sl.get_student_grade_form(sid),
    }


# ============================================================
# tutor interaction (subject-safe)
# ============================================================
def ask_tutor(sid, message, subject=None):
    """
    Send a message to the tutor for the student, subject-aware.

    Steps:
      1) Determine the student's current subject (or `subject` if given).
      2) Run subject_guard.apply_guard to see if the message implies a switch
         to another *active* subject.
      3) Call tutor.brain.tutor_reply with the resolved subject.

    Shape:
      {
        "student_id", "subject_used", "note", "response", "switched": bool
      }
    """
    guard = _import_subject_guard()
    brain = _import_tutor_brain()

    current = subject or get_current_subject(sid)
    if not current:
        raise ValueError(f"Student {sid} has no active subject.")

    # apply_guard writes to students.current_subject if it switches.
    used, note = guard.apply_guard(sid, current, message)
    switched = bool(used and used != current)

    response = brain.tutor_reply(sid, message, subject=used)

    return {
        "student_id": sid,
        "subject_used": used,
        "note": note,
        "response": response,
        "switched": switched,
    }


# ============================================================
# quick self-test (read-only against real DB)
# ============================================================
if __name__ == "__main__":
    print("DB_PATH:", DB_PATH)
    print("students:")
    for r in _all("SELECT id, name, student_number, grade_form, current_subject FROM students ORDER BY id"):
        print("  ", dict(r))

    for sid in [1, 2, 3]:
        stu = get_student(sid)
        if not stu:
            continue
        subs = get_active_subjects(sid)
        cur = get_current_subject(sid)
        print(f"\nstudent {sid} ({stu['name']}): subjects={subs} current={cur!r}")
        if cur:
            topic = pick_topic(sid, cur)
            print(f"  pick_topic({cur}) -> {topic!r}")
            try:
                item = next_item(sid, subject=cur, topic=topic)
                print(f"  next_item: band={item['learning_band']} "
                      f"topic={item['topic']} q_index={item['question_index']} "
                      f"source={item['source']}")
                qt = (item.get("question_text") or "")[:70]
                print(f"  question[:70] = {qt!r}")
            except Exception as e:
                print(f"  next_item FAILED: {type(e).__name__}: {e}")
