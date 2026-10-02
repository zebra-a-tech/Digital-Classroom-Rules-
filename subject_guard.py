import re, sqlite3, os
DB = __import__("os").environ.get("DB_PATH", "digital_classroom.db")
KW = {
 "Maths": r"\bsolve\b|equation|fraction|multipl|divid|algebra|\barea\b|perimeter|\bsum of\b|\bfactor|percent|decimal|geometry|\bangle|\bplus\b|\bminus\b|\btimes\b|add|subtract|number",
 "English": r"grammar|\bnoun\b|\bverb\b|adjective|adverb|comprehension|synonym|antonym|\bessay\b|spelling|punctuation|\btense\b|\bsentence\b|\bparagraph\b|\bwriting\b",
 "Science": r"photosynthesis|\bcell\b|\batom\b|\benergy\b|\bforce\b|\bplant|\banimal|habitat|\bmatter\b|\bant\b|insect|\bbug\b|\bleg\b|\bbody\b|\bheart\b|\blung\b|\bblood\b|\bwater\b|weather|season|\bsoil\b|\brock\b|mineral|\bmagnet\b|electric|circuit|light|sound|heat|gas|solid|liquid",
 "Geography": r"\briver|climate|\bmap\b|\bcontinent|\bmountain|rainfall|\bsoil\b|settlement|country|capital|population|weather|ocean|desert",
 "History": r"\bwar\b|colonial|independence|\bking\b|\bempire|ancient|\bchimurenga|\bheritage\b|liberation|ancestor|tribe",
 "Biology": r"\bcell\b|organism|ecosystem|digestion|respiration|\bgenetic|\bdna\b|blood|bone|muscle|organ|disease|bacteria|virus",
 "Chemistry": r"\bacid|\bbase\b|\bmolecule|reaction|periodic table|\bion\b|\belement|compound|mixture|solution|gas|metal",
 "Physics": r"\bvelocity|acceleration|\bcircuit|\bvoltage|\bnewton|\bmoment\b|\bwave|gravity|force|energy|motion|friction|magnet",
 "Economics": r"\bdemand\b|\bsupply\b|inflation|\bgdp\b|opportunity cost|\bmarket\b|money|trade|business|profit|loss",
 "Accounting": r"\bledger|debit|credit|balance sheet|trial balance|\bprofit\b|journal entry|asset|liability|capital|invoice",
 "Social Studies": r"\bcitizen|\bculture\b|\bgovernment\b|\bcommunity\b|\bhuman rights|family|tradition|society",
 "Shona": r"shona|chiShona|tsika|unhu|\bnhetembo|nyaya|\bmadimikira",
 "Ndebele": r"ndebele|isNdebele|ubuntu|izaga|izithakazelo|\bindaba",
 "Agriculture": r"\bcrop|\bsoil\b|\bplant|\bfertil|\birrigat|\blivestock|\bcattle|harvest|\bfarm|pest|weed",
 "Commerce": r"\btrade\b|\bbusiness\b|\bbuyer|\bseller|\bmarket\b|profit|money|bank|insurance",
 "Computer Studies": r"\bcomputer|\bprogram|\bsoftware|\bhardware|\bdata\b|network|internet|keyboard|mouse",
 "Heritage Studies": r"\bheritage\b|\bculture\b|\btradition|monument|\bstone\b|great zimbabwe",
 "Religious Studies": r"\breligion|\bgod\b|\bchurch\b|\bbible\b|\bquran\b|prayer|faith",
}
MATH_EXPR = re.compile(r"\d\s*[+\-*/x×÷=]\s*\d|\d+\s*[a-z]\s*[+\-=]|\bx\s*=")

def detect_subject(message):
    m = (message or "").lower()
    if MATH_EXPR.search(m): return "Maths"
    hits = {s: len(re.findall(p, m)) for s, p in KW.items()}
    best = max(hits, key=hits.get)
    return best if hits[best] >= 1 and list(hits.values()).count(hits[best]) == 1 else None

def _art(w):
    return "an" if w[:1].upper() in "AEIOU" else "a"

def apply_guard(sid, current, message):
    """Return (subject_to_use, note_or_empty). Only switches to a subject the pupil studies."""
    found = detect_subject(message)
    if not found or found == current:
        return current, ""
    c = sqlite3.connect(DB)
    try:
        subs = [r[0] for r in c.execute("select subject from student_subjects where student_id=? and active=1", (sid,))]
        if found in subs:
            c.execute("update students set current_subject=? where id=?", (found, sid)); c.commit()
            return found, f"That looks like {_art(found)} {found} question, so I switched you to {found}."
        return current, f"That looks like {_art(found)} {found} question. You haven't added {found} yet. Add it on your home page if you want help with it."
    finally:
        c.close()
