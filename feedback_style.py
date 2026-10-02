def band(grade):
    g = (grade or "").lower()
    n = "".join(ch for ch in g if ch.isdigit())
    n = int(n) if n else 0
    if g.startswith("grade") and n <= 3: return "young"
    if g.startswith("grade"): return "middle"
    return "senior"

def build_feedback(grade, got, total, pct, weak):
    weak = sorted(set(w for w in weak if w))
    b = band(grade)
    if b == "young":
        stars = "⭐" * max(1, round(pct / 20))
        t = f"Well done! You got {got:g} out of {total:g}. {stars}"
        if weak: t += " Let's practise " + " and ".join(weak) + " again with your grown-up."
        return t
    if b == "middle":
        t = f"Score: {got:g}/{total:g} ({pct:g}%). " + ("Great work!" if pct >= 70 else "Good effort, keep practising.")
        if weak: t += " Revise: " + ", ".join(weak) + "."
        return t
    t = f"Score: {got:g}/{total:g} ({pct:g}%)."
    t += " Strong performance." if pct >= 70 else " Several areas need consolidation."
    if weak: t += " Recommended revision: " + ", ".join(weak) + "."
    return t
