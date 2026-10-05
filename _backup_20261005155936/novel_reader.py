import random
from datetime import datetime, timedelta
from functools import wraps
from flask import Blueprint, request, session, redirect, url_for, abort
import dcr_db as db
from ui import page

novel_bp = Blueprint("novels", __name__)

# STARTER CONTENT: 4 graded books x 10 chapters. Replace/extend the beats with your full chapter text.
_RAW = [
    (1, "Tendai and the Talking Baobab", "1-2", 2,
     "Tendai finds a huge baobab tree near her school.|The baobab says hello in a deep, kind voice.|"
     "Tendai promises to keep the tree's secret.|A hungry goat nibbles the baobab's low leaves.|"
     "Tendai shares her lunch with the goat.|The baobab shows her a hidden nest of eggs.|"
     "Dark clouds gather and the dry fields finally get rain.|Tendai tells her class to protect old trees.|"
     "The class plants ten small trees together.|Tendai waves goodbye as the baobab whispers thank you."),
    (2, "The Little Weaver of Mutare", "2-3", 3,
     "Farai watches his gogo weave a basket on the veranda.|He asks to learn, and Gogo hands him a bundle of reeds.|"
     "His first basket falls apart in his hands.|Farai feels sad but Gogo tells him to try again.|"
     "He practises every afternoon after school.|A neighbour orders a small basket for her market stall.|"
     "Farai finishes it just before the market opens.|The basket sells for two dollars, his first earnings.|"
     "He saves one dollar and gives one to Gogo for reeds.|Farai learns that patience turns practice into skill."),
    (3, "Rudo's River Journey", "3-4", 4,
     "Rudo's village well dries up during a long drought.|She decides to follow the river to find clean water.|"
     "Her brother Tafara insists on coming along.|They cross a rocky gorge by balancing on stones.|"
     "A kind fisherman shares his map with the children.|Night falls and they shelter in a cave and count stars.|"
     "Tafara twists his ankle and Rudo carries his bag.|At sunrise they find a spring flowing from a hill.|"
     "They lead the village elders back to the spring.|The village digs a new borehole and Rudo is thanked."),
    (4, "The Great Zimbabwe Mystery", "4-5", 5,
     "Chipo joins a school trip to the ancient stone ruins.|Her guide mentions that a carved bird has gone missing.|"
     "Chipo notices fresh footprints near the Hill Complex.|She sketches the prints and compares them with her classmates' shoes.|"
     "A torn blue cloth is snagged on a stone wall.|Chipo interviews the caretaker and spots a nervous habit.|"
     "The clues point to a hidden storeroom behind the walls.|She asks the guide to open it while a teacher watches.|"
     "They find the bird safe, moved for cleaning, with the paperwork lost.|Chipo learns that careful questions solve more than guesses."),
]
BOOKS = {b[0]: {"id": b[0], "title": b[1], "grades": b[2], "maxg": b[3], "beats": b[4].split("|")} for b in _RAW}


def login_required(f):
    @wraps(f)
    def w(*a, **k):
        if not session.get("uid"):
            return redirect(url_for("auth.login"))
        return f(*a, **k)
    return w


LIB = """
<div class="card"><h1>Novel Library</h1>
{% for b in books %}<p><strong>{{ b.title }}</strong> <span class="muted">(Grades {{ b.grades }}, 10 chapters)</span><br>
<a class="btn" href="/novels/{{ b.id }}">Open</a></p>{% endfor %}
<a class="btn alt" href="/novels/report">Weekly reading report</a></div>
"""

TOC = """
<div class="card"><h1>{{ b.title }}</h1>
{% for i in range(1, 11) %}<a class="btn alt" href="/novels/{{ b.id }}/{{ i }}">Chapter {{ i }}</a>{% endfor %}</div>
"""

READ = """
<div class="card"><h2>{{ b.title }}: Chapter {{ n }}</h2>
<p class="story" id="story">{{ text }}</p>
<button class="btn" type="button" onclick="dcrPlay()">&#9654; Play</button>
<button class="btn alt" type="button" onclick="dcrPause()">&#10074;&#10074; Pause</button>
<button class="btn warn" type="button" onclick="dcrStop()">&#9632; Stop</button>
{% if b.maxg <= 5 %}<p><button class="btn alt" type="button" onclick="document.getElementById('assist').style.display='block'">Parent assist mode</button></p>
<div id="assist" class="warnbox" style="display:none;border-color:#006400;background:#f1fbf1">
<strong>For parents:</strong> 1) Read the sentence aloud slowly. 2) Ask your child to read it back.
3) Ask: "Who is in this chapter and what happened?" 4) Ask: "What do you think happens next?" Then take the quiz together.</div>{% endif %}
</div>
<div class="card"><h2>Chapter quiz</h2><p>Which sentence happened in this chapter?</p>
<form method="post">{% for o in opts %}<label class="opt"><input type="radio" name="choice" value="{{ o }}" required>{{ beats[o] }}</label>{% endfor %}
<button class="btn" type="submit">Check answer</button></form></div>
<script>
var synth = window.speechSynthesis;
function dcrPlay(){ if(!synth){alert('Audio is not supported on this browser.');return;}
  if(synth.paused){synth.resume();return;} synth.cancel();
  var u=new SpeechSynthesisUtterance(document.getElementById('story').innerText); u.rate=0.85; synth.speak(u); }
function dcrPause(){ if(synth){synth.pause();} }
function dcrStop(){ if(synth){synth.cancel();} }
</script>
"""

RESULT = """
<div class="card"><h2>{% if ok %}<span class="ok">Correct! Well done.</span>{% else %}<span class="err">Not quite.</span>{% endif %}</h2>
<p>This chapter: <em>{{ truth }}</em></p>
{% if n < 10 %}<a class="btn" href="/novels/{{ b.id }}/{{ n + 1 }}">Next chapter</a>{% endif %}
<a class="btn alt" href="/novels/{{ b.id }}">Chapter list</a></div>
"""

REPORT = """
<div class="card"><h1>Weekly reading report</h1><p class="muted">Last 7 days for {{ name }}</p>
{% if rows %}<table><tr><th>Book</th><th>Chapters</th><th>Avg quiz</th></tr>
{% for r in rows %}<tr><td>{{ r.title }}</td><td>{{ r.chapters }}</td><td>{{ r.avg }}%</td></tr>{% endfor %}</table>
{% else %}<p>No reading yet this week. Start a chapter today!</p>{% endif %}</div>
"""


def _book(bid):
    b = BOOKS.get(bid)
    if not b:
        abort(404)
    return b


@novel_bp.route("/novels")
@login_required
def library():
    return page("Novels", LIB, books=list(BOOKS.values()))


@novel_bp.route("/novels/report")
@login_required
def report():
    since = (datetime.utcnow() - timedelta(days=7)).isoformat()
    data = db.run("SELECT book,chapter,score FROM dcr_progress WHERE user_id=? AND ts>=?", (session["uid"], since))
    agg = {}
    for d in data:
        a = agg.setdefault(d["book"], {"ch": set(), "sc": []})
        a["ch"].add(d["chapter"])
        a["sc"].append(d["score"])
    rows = [{"title": BOOKS[k]["title"], "chapters": len(v["ch"]), "avg": round(sum(v["sc"]) / len(v["sc"]))}
            for k, v in agg.items() if k in BOOKS]
    return page("Report", REPORT, rows=rows, name=session.get("name"))


@novel_bp.route("/novels/<int:bid>")
@login_required
def toc(bid):
    return page(_book(bid)["title"], TOC, b=_book(bid))


@novel_bp.route("/novels/<int:bid>/<int:n>", methods=["GET", "POST"])
@login_required
def chapter(bid, n):
    b = _book(bid)
    if not 1 <= n <= 10:
        abort(404)
    i = n - 1
    beats = b["beats"]
    if request.method == "POST":
        try:
            ok = int(request.form.get("choice", "-1")) == i
        except ValueError:
            ok = False
        db.run("INSERT INTO dcr_progress(user_id,book,chapter,score,ts) VALUES(?,?,?,?,?)",
               (session["uid"], bid, n, 100 if ok else 0, datetime.utcnow().isoformat()))
        return page("Result", RESULT, ok=ok, truth=beats[i], b=b, n=n)
    rnd = random.Random(bid * 100 + n)
    opts = rnd.sample([x for x in range(10) if x != i], 2) + [i]
    rnd.shuffle(opts)
    return page("Chapter " + str(n), READ, b=b, n=n, text=beats[i], beats=beats, opts=opts)
