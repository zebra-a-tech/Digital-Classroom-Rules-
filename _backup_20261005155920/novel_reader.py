import os, json, sqlite3
from flask import request, redirect, url_for, render_template_string, jsonify

def db():
    if os.environ.get("TURSO_DATABASE_URL") and os.environ.get("TURSO_AUTH_TOKEN"):
        try:
            import turso_db
            return turso_db.connect()
        except: pass
    return sqlite3.connect("digital_classroom.db")

def init_tables():
    c = db()
    for q in [
        "CREATE TABLE IF NOT EXISTS novels (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, grade TEXT, genre TEXT, descr TEXT, parent_req INT DEFAULT 0, emoji TEXT DEFAULT '📖')",
        "CREATE TABLE IF NOT EXISTS novel_chapters (id INTEGER PRIMARY KEY AUTOINCREMENT, novel_id INT, chapter_num INT, title TEXT, content TEXT, quiz_json TEXT)",
        "CREATE TABLE IF NOT EXISTS novel_reading_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, student_id INT, novel_id INT, chapter_num INT, score INT, max_score INT, parent_ok INT DEFAULT 0, completed_at TEXT DEFAULT CURRENT_TIMESTAMP)"
    ]:
        try: c.execute(q); c.commit()
        except: pass
    c.close()

def seed_data():
    init_tables()
    c = db()
    try:
        if c.execute("SELECT COUNT(*) FROM novels").fetchone()[0] > 0:
            c.close(); return
    except: pass
    
    books = [
        ("The Giggle Giraffe of Hwange", "Grade 1-3", "Comedy", "Gogo the giraffe giggles when birds tickle his long neck!", 1, "🦒"),
        ("The Mystery of the Flying Sadza", "Grade 4-5", "School Adventure", "Farai and Chipo launch an accidental porridge rocket on sports day!", 1, "🍲"),
        ("The Missing Vintage Bicycle", "Grade 6-7 / Form 1-2", "Mystery & Comedy", "Eagle Eye Detectives investigate the Headmaster's missing green bike.", 0, "🚲"),
        ("The Great Harare Debate", "Form 3-4", "Satire & Wit", "Simba and Tariro clash in an unforgettable battle of rhetoric and humor.", 0, "🎭")
    ]
    for title, grade, genre, desc, parent, emoji in books:
        try:
            cur = c.execute("INSERT INTO novels (title, grade, genre, descr, parent_req, emoji) VALUES (?,?,?,?,?,?)", (title, grade, genre, desc, parent, emoji))
            nid = cur.lastrowid
            for ch_num in range(1, 11):
                c_title = f"Chapter {ch_num} Adventure"
                c_text = f"This is Chapter {ch_num} of {title}. The adventure continues across Zimbabwe with exciting twists, funny moments, and deep lessons!"
                quiz = [{"q": f"What is the main theme of Chapter {ch_num}?", "options": ["Adventure & Learning", "Sleeping", "Traffic"], "a": 0}]
                c.execute("INSERT INTO novel_chapters (novel_id, chapter_num, title, content, quiz_json) VALUES (?,?,?,?,?)", (nid, ch_num, c_title, c_text, json.dumps(quiz)))
        except: pass
    try: c.commit(); c.close()
    except: pass

def register_novel_reader(app):
    seed_data()
    
    @app.route("/student/<int:sid>/library")
    def student_library(sid):
        c = db()
        novels = c.execute("SELECT id, title, grade, genre, descr, parent_req, emoji FROM novels").fetchall()
        c.close()
        h = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Library</title>
        <style>body{font-family:sans-serif;background:#f8fafc;padding:16px;max-width:700px;margin:auto}.c{background:white;padding:16px;border-radius:12px;margin:12px 0;box-shadow:0 2px 6px #ddd;display:flex;gap:12px;align-items:center}.btn{background:#0f766e;color:white;padding:8px 14px;border-radius:6px;text-decoration:none;font-weight:bold;display:inline-block;margin-top:6px}</style></head><body>
        <div style="background:#0f766e;color:white;padding:18px;border-radius:12px"><h2>📚 Graded Novel Library</h2><p>10-Chapter comedy stories with Voice Read-Aloud & Quizzes</p><a href="/student/{{sid}}/home" style="color:#ccfbf1">🏠 Home</a> | <a href="/student/{{sid}}/novel-report" style="color:#ccfbf1">📊 Reading Report</a></div>
        {% for b in novels %}
        <div class="c"><div style="font-size:2.5rem">{{b[6]}}</div><div style="flex:1"><b>{{b[1]}}</b> <span style="background:#e0f2fe;color:#0284c7;font-size:0.75rem;padding:2px 6px;border-radius:8px">{{b[2]}}</span><div>{{b[4]}}</div><a class="btn" href="/student/{{sid}}/novel/{{b[0]}}/chapter/1">▶️ Read Book (10 Ch.)</a></div></div>
        {% endfor %}</body></html>"""
        return render_template_string(h, sid=sid, novels=novels)

    @app.route("/student/<int:sid>/novel/<int:nid>/chapter/<int:chn>")
    def read_chapter(sid, nid, chn):
        c = db()
        n = c.execute("SELECT title, parent_req FROM novels WHERE id=?", (nid,)).fetchone()
        ch = c.execute("SELECT title, content, quiz_json FROM novel_chapters WHERE novel_id=? AND chapter_num=?", (nid, chn)).fetchone()
        c.close()
        if not ch: return redirect(url_for("student_library", sid=sid))
        quiz = json.loads(ch[2])
        h = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>{{ch[0]}}</title>
        <style>body{font-family:Georgia,serif;background:#f8fafc;padding:16px;max-width:680px;margin:auto}.b{background:white;padding:20px;border-radius:14px;box-shadow:0 2px 8px #ddd}.btn{background:#0f766e;color:white;border:none;padding:8px 14px;border-radius:6px;cursor:pointer}</style></head><body><div class="b">
        <a href="/student/{{sid}}/library" style="color:#0f766e;font-family:sans-serif">← Back to Library</a>
        <div style="background:#f0fdfa;padding:10px;border-radius:8px;margin:12px 0;display:flex;gap:8px;font-family:sans-serif">
          <button class="btn" onclick="pVoice()">▶️ Play</button><button class="btn" style="background:#d97706" onclick="sVoice()">⏸️ Pause</button>
        </div>
        <h2>{{ch[0]}}</h2><div id="tx" style="font-size:1.15rem;line-height:1.8;margin:16px 0">{{ch[1]}}</div>
        <div style="background:#f8fafc;padding:14px;border-radius:10px;border:1px solid #ccc;font-family:sans-serif">
          <h3>📝 Comprehension Check</h3>
          <form onsubmit="subQ(event)">
            {% for q in quiz %}
            <p><b>{{q.q}}</b></p>
            {% for opt in q.options %}<label style="display:block;margin:4px 0"><input type="radio" name="q" value="{{loop.index0}}" required> {{opt}}</label>{% endfor %}
            {% endfor %}
            <button class="btn" style="margin-top:10px;width:100%" type="submit">Submit Chapter →</button>
          </form>
          <div id="res" style="display:none;margin-top:10px;font-weight:bold"></div>
        </div></div>
        <script>
        let s=window.speechSynthesis, u=null;
        function pVoice(){ if(s.paused){s.resume();return;} s.cancel(); u=new SpeechSynthesisUtterance(document.getElementById("tx").innerText); s.speak(u); }
        function sVoice(){ if(s.speaking) s.pause(); }
        async function subQ(e){
          e.preventDefault();
          let r = await fetch("/student/{{sid}}/novel/{{nid}}/chapter/{{chn}}/submit", {method:"POST"});
          let d = await r.json();
          document.getElementById("res").style.display="block";
          document.getElementById("res").innerHTML = "🎉 Passed! <a href='"+d.next+"'>Next Chapter →</a>";
        }
        </script></body></html>"""
        return render_template_string(h, sid=sid, nid=nid, chn=chn, n=n, ch=ch, quiz=quiz)

    @app.route("/student/<int:sid>/novel/<int:nid>/chapter/<int:chn>/submit", methods=["POST"])
    def submit_chapter(sid, nid, chn):
        c = db()
        try:
            c.execute("INSERT OR REPLACE INTO novel_reading_progress (student_id, novel_id, chapter_num, score, max_score, completed_at) VALUES (?,?,?,3,3,datetime('now'))", (sid, nid, chn))
            c.commit()
        except: pass
        c.close()
        nxt = url_for("read_chapter", sid=sid, nid=nid, chn=chn+1) if chn < 10 else url_for("student_library", sid=sid)
        return jsonify({"passed": True, "next": nxt})

    @app.route("/student/<int:sid>/novel-report")
    def novel_report(sid):
        c = db()
        rows = c.execute("SELECT n.title, p.chapter_num, p.completed_at FROM novel_reading_progress p JOIN novels n ON p.novel_id=n.id WHERE p.student_id=? ORDER BY p.completed_at DESC", (sid,)).fetchall()
        c.close()
        h = """<!doctype html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Report</title>
        <style>body{font-family:sans-serif;background:#f8fafc;padding:16px;max-width:600px;margin:auto}.c{background:white;padding:20px;border-radius:12px;box-shadow:0 2px 6px #ddd}</style></head><body><div class="c">
        <h2>📊 Weekly Reading Report</h2><a href="/student/{{sid}}/library" style="color:#0f766e">← Back to Library</a>
        <p>Total Chapters Completed: <b>{{rows|length}}</b></p>
        <table style="width:100%;border-collapse:collapse;margin-top:12px">
        <tr style="background:#f1f5f9"><th style="padding:6px;text-align:left">Book</th><th style="padding:6px">Chapter</th><th style="padding:6px">Date</th></tr>
        {% for r in rows %}<tr><td style="padding:6px">{{r[0]}}</td><td style="padding:6px;text-align:center">Ch. {{r[1]}}</td><td style="padding:6px;color:#64748b">{{r[2][:10]}}</td></tr>{% endfor %}
        </table></div></body></html>"""
        return render_template_string(h, sid=sid, rows=rows)
