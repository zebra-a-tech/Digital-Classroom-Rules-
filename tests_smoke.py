"""
tests_smoke.py — Digital Classroom Rules smoke suite.

Runs read-only checks against the real database and the HTTP server.
Never modifies production data. Writes only to a temp audit file.

Usage:
    python tests_smoke.py              # DB-only checks
    python tests_smoke.py --http       # also exercise HTTP endpoints
                                         (requires student_server.py running)
"""

import sys, os, sqlite3, json, datetime, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
BASE = "http://127.0.0.1:5001"

DO_HTTP = "--http" in sys.argv

results = []

def check(name, ok, detail=""):
    results.append((name, bool(ok), detail))
    mark = "PASS" if ok else "FAIL"
    line = f"[{mark}] {name}"
    if detail and not ok:
        line += f"  — {detail}"
    print(line)


def db():
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True, timeout=10)
    con.row_factory = sqlite3.Row
    return con


def http_get(path, timeout=4):
    try:
        with urllib.request.urlopen(BASE + path, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""
    except Exception as e:
        return 0, str(e).encode()


# ============================================================
# Section 1 — Database integrity
# ============================================================
print("\n=== Section 1: Database ===")
con = db()
cur = con.cursor()

# 1. DB opens
try:
    cur.execute("SELECT 1").fetchone()
    check("1. Database opens", True)
except Exception as e:
    check("1. Database opens", False, str(e))

# 2. Tables exist
required_tables = [
    "students", "auth_users", "curriculum", "student_subjects",
    "learning_progress", "homework", "assignments", "assignment_questions",
    "assignment_submissions", "student_sessions", "paid_sessions",
    "payment_requests", "tutor_memory", "learning_sessions",
    "weekly_assignments", "weekly_assignment_questions",
]
missing = []
for t in required_tables:
    row = cur.execute(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)
    ).fetchone()
    if not row:
        missing.append(t)
check("2. All required tables exist", not missing, f"missing: {missing}")

# 3. Existing curriculum is accessible (expected count > 800)
cur_n = cur.execute("SELECT COUNT(*) FROM curriculum").fetchone()[0]
check("3. Curriculum has >800 lessons", cur_n > 800, f"got {cur_n}")

# 4. Existing students preserved
student_count = cur.execute("SELECT COUNT(*) FROM students").fetchone()[0]
check("4. Students table has >=3 rows", student_count >= 3, f"got {student_count}")

# 5. No DCR duplicates (unique index working)
dupes = list(cur.execute("""
    SELECT student_number, COUNT(*) c FROM students
    WHERE student_number IS NOT NULL AND student_number != ''
    GROUP BY student_number HAVING c > 1
"""))
check("5. No duplicate student numbers", not dupes, f"dupes: {[dict(d) for d in dupes]}")

# 6. No stuck paid_sessions
stuck = list(cur.execute("""
    SELECT id FROM paid_sessions
    WHERE active=1 AND (total_paused_seconds > 7200 OR subject IS NULL)
"""))
check("6. No stuck paid sessions", not stuck, f"stuck: {[dict(s) for s in stuck]}")

# 7. auth_users aligned with students
auth = {r["student_id"]: r["student_number"]
        for r in cur.execute("SELECT student_id, student_number FROM auth_users")}
students = {r["id"]: r["student_number"]
            for r in cur.execute("SELECT id, student_number FROM students")}
mismatch = [(sid, students.get(sid), auth[sid])
            for sid in auth if students.get(sid) != auth[sid]]
check("7. auth_users aligned with students", not mismatch, f"mismatch: {mismatch}")

# 8. All students have a grade_form (per spec)
no_grade = list(cur.execute(
    "SELECT id, name FROM students WHERE grade_form IS NULL OR grade_form=''"
))
check("8. All students have grade_form", not no_grade,
      f"missing: {[dict(g) for g in no_grade]}")

con.close()


# ============================================================
# Section 2 — Learning engine
# ============================================================
print("\n=== Section 2: Learning Engine ===")
try:
    import learning_bridge as lb
    check("9. learning_bridge imports", True)
except Exception as e:
    check("9. learning_bridge imports", False, str(e))
    lb = None

if lb:
    # 10. get_student works
    s = lb.get_student(3)
    check("10. get_student(3) returns Mike", s and s["name"] == "Mike zebra",
          f"got: {s}")

    # 11. get_active_subjects works
    subs = lb.get_active_subjects(3)
    check("11. get_active_subjects(3) returns list", isinstance(subs, list),
          f"got: {subs}")

    # 12. get_current_subject works
    cur_subj = lb.get_current_subject(3)
    check("12. get_current_subject(3) non-empty", bool(cur_subj),
          f"got: {cur_subj!r}")

    # 13. pick_topic works
    topic = lb.pick_topic(3, cur_subj) if cur_subj else ""
    check("13. pick_topic returns a topic", bool(topic), f"got: {topic!r}")

    # 14. next_item returns lesson + question
    try:
        item = lb.next_item(3, subject=cur_subj, topic=topic)
        ok = bool(item.get("question_text")) and bool(item.get("learning_band"))
        check("14. next_item returns question + band", ok,
              f"q={item.get('question_text')!r} band={item.get('learning_band')!r}")
    except Exception as e:
        check("14. next_item returns question + band", False, str(e))

    # 15. Grade band correctness for Grade 5 student
    try:
        item = lb.next_item(3, subject=cur_subj)
        band = item.get("learning_band")
        check("15. Grade 5 student -> G4_G5 band", band == "G4_G5",
              f"got {band}")
    except Exception as e:
        check("15. Grade 5 student -> G4_G5 band", False, str(e))

    # 16. Grade band for Form 6 student (Tinashe id=1)
    try:
        item = lb.next_item(1, subject="English", topic="Tenses")
        band = item.get("learning_band")
        check("16. Form 6 student -> F5_F6 band", band == "F5_F6",
              f"got {band}")
    except Exception as e:
        check("16. Form 6 student -> F5_F6 band", False, str(e))

    # 17. Subject guard prevents wrong subject
    try:
        r = lb.ask_tutor(3, "What is a noun?")  # Mike only does Accounting
        # Wait — Mike's subject is now Accounting.
        # A Maths/English question should stay on Accounting (not switch to English)
        ok = (r["subject_used"] == "Accounting")
        check("17. ask_tutor keeps subject when not in list", ok,
              f"used: {r['subject_used']}")
    except Exception as e:
        check("17. ask_tutor keeps subject when not in list", False, str(e))


# ============================================================
# Section 3 — Reports
# ============================================================
print("\n=== Section 3: Weekly Reports ===")
try:
    import reports as rp
    rep = rp.weekly_report(1)
    check("18. reports imports + runs", bool(rep and "student" in rep))
    check("19. Report has real student name",
          rep.get("student", {}).get("name") == "Tinashe")
    check("20. Report has week.label",
          bool(rep.get("week", {}).get("label")))
    check("21. Report has next_week_focus",
          isinstance(rep.get("next_week_focus"), list))
    txt = rp.format_report_text(rep)
    check("22. format_report_text returns text", "WEEKLY REPORT" in txt)
except Exception as e:
    check("18. reports imports + runs", False, str(e))


# ============================================================
# Section 4 — Msasa design system files
# ============================================================
print("\n=== Section 4: Msasa design files ===")
for path in ["static/msasa.css", "static/msasa.js",
             "templates/base.html", "templates/msasa_dashboard.html",
             "templates/msasa_report.html",
             "templates/_partials/ring.html",
             "templates/_partials/empty.html",
             "templates/_partials/timer.html"]:
    full = os.path.join(HERE, path)
    check(f"file exists: {path}", os.path.exists(full) and os.path.getsize(full) > 0)


# ============================================================
# Section 5 — HTTP endpoints (optional)
# ============================================================
if DO_HTTP:
    print("\n=== Section 5: HTTP endpoints ===")
    endpoints = [
        "/student/1/v2",
        "/student/3/v2",
        "/student/3/v2/report",
    ]
    for path in endpoints:
        code, body = http_get(path)
        ok = (code == 200 and len(body) > 200)
        check(f"HTTP 200 {path}", ok, f"code={code} size={len(body)}")

    # Msasa classes present in dashboard HTML
    code, body = http_get("/student/3/v2")
    html = body.decode("utf-8", errors="replace")
    for cls in ["ms-card", "ms-chip", "ms-subject"]:
        check(f"dashboard has class .{cls}", cls in html)


# ============================================================
# Summary
# ============================================================
print("\n" + "=" * 60)
passed = sum(1 for _, ok, _ in results if ok)
failed = sum(1 for _, ok, _ in results if not ok)
print(f"TOTAL: {len(results)} checks | PASS: {passed} | FAIL: {failed}")
print("=" * 60)
if failed:
    print("\nFailing checks:")
    for name, ok, detail in results:
        if not ok:
            print(f"  ✗ {name}  {detail}")
    sys.exit(1)
else:
    print("\nAll checks passed.")
    sys.exit(0)
