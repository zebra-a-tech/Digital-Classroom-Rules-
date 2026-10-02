"""Upload validation + working checker. Standalone, no third-party deps required."""
import re
from fractions import Fraction as F

ALLOWED = {"jpg": "jpeg", "jpeg": "jpeg", "png": "png", "webp": "webp"}

def _sniff(b):
    if b[:3] == b"\xff\xd8\xff": return "jpeg"
    if b[:8] == b"\x89PNG\r\n\x1a\n": return "png"
    if b[:4] == b"RIFF" and b[8:12] == b"WEBP": return "webp"
    return None

def check_upload(filename, content, max_mb=10):
    """Return (ok, message). Message is student-friendly."""
    ext = (filename or "").rsplit(".", 1)[-1].lower() if "." in (filename or "") else ""
    if ext not in ALLOWED:
        return False, "Please upload a JPG, PNG or WEBP photo only."
    if not content:
        return False, "That file is empty. Please take the photo again."
    if len(content) > max_mb * 1024 * 1024:
        return False, f"That photo is too large (limit {max_mb} MB). Try again with a lower camera quality."
    kind = _sniff(content)
    if kind is None or kind != ALLOWED[ext]:
        return False, "That file is not a real photo. Please take the picture again."
    try:
        from PIL import Image
        import io
        im = Image.open(io.BytesIO(content)); im.verify()
        im = Image.open(io.BytesIO(content))
        if min(im.size) < 400:
            return False, "I couldn't clearly read part of your uploaded work. Please upload a clearer photograph."
    except ImportError:
        pass  # Pillow not installed: signature check only
    except Exception:
        return False, "I couldn't open that photo. Please upload a clearer photograph."
    return True, "OK"

# ---------- linear equation working checker ----------
_OK = re.compile(r"^[0-9xX+\-*/().=\s^]+$")

def _expr(side):
    s = side.replace("X", "x").replace("^", "**").replace(" ", "")
    s = re.sub(r"(\d|\))(x|\()", r"\1*\2", s)
    s = re.sub(r"(x)(\d|\(|x)", r"\1*\2", s)
    s = re.sub(r"(\d+(?:\.\d+)?)", r'F("\1")', s)
    return s

def _val(side, x):
    return eval(_expr(side), {"__builtins__": {}}, {"F": F, "x": x})

def solve_line(line):
    """Return solution of a linear equation in x as Fraction, or None."""
    line = line.strip().replace("−", "-").replace("×", "*").replace("÷", "/")
    if line.count("=") != 1 or not _OK.match(line): return None
    l, r = line.split("=")
    if not l.strip() or not r.strip(): return None
    try:
        f0 = _val(l, F(0)) - _val(r, F(0))
        f1 = _val(l, F(1)) - _val(r, F(1))
        f2 = _val(l, F(2)) - _val(r, F(2))
        if f2 - f1 != f1 - f0: return None      # not linear
        if f1 == f0: return None                # no unique solution
        return -f0 / (f1 - f0)
    except Exception:
        return None

def mark_linear_working(working_text, expected, marks=2):
    """working_text: student's lines. expected: e.g. '4'. Returns dict."""
    lines = [l for l in re.split(r"[\n;]+", working_text or "") if l.strip()]
    try: exp = F(str(expected).strip().replace("x=", "").replace("x =", ""))
    except Exception:
        return _r(0, marks, "REVIEW", "Answer key is not numeric; needs tutor review.", 0.0, True)
    if not lines:
        return _r(0, marks, "MISSING", "No working or answer was found for this question.", 1.0, False)
    sols = [solve_line(l) for l in lines]
    if any(s is None for s in sols):
        bad = next(i for i, s in enumerate(sols) if s is None) + 1
        return _r(0, marks, "REVIEW",
                  f"I couldn't clearly read line {bad} of your working. Please upload a clearer photograph or retype it.",
                  0.3, True)
    if sols[-1] == exp and all(s == exp for s in sols):
        return _r(marks, marks, "CORRECT", "Correct. Your working is clear and every step is valid.", 0.95, False)
    first = sols[0]
    for i in range(1, len(sols)):
        if sols[i] != sols[i - 1]:
            part = marks / 2 if (first == exp and i >= 2) else 0
            fb = f"Your working goes wrong at line {i + 1}: '{lines[i].strip()}' does not follow from the line before."
            if part: fb += " Good start, you earn method marks for the earlier steps."
            return _r(part, marks, "PARTIAL" if part else "INCORRECT", fb, 0.9, False)
    if sols[-1] != exp:
        return _r(0, marks, "INCORRECT", f"Your steps are consistent but the answer to the question is not x = {exp}. Re-read the question.", 0.8, False)
    return _r(marks, marks, "CORRECT", "Correct.", 0.9, False)

def _r(got, total, result, fb, conf, review):
    return {"marks_awarded": got, "marks_total": total, "result": result,
            "feedback": fb, "confidence": conf, "manual_review_required": review}


def _num(t):
    try:
        return F(str(t).strip().replace(",", ""))
    except Exception:
        return None

def _norm(t):
    t = re.sub(r"^\s*(answer|ans)\s*[:=]\s*", "", str(t or "").strip(), flags=re.I)
    return re.sub(r"\s+", " ", t).strip().rstrip(".").lower()

def mark_answer(text, expected, marks=1):
    """Mark one typed answer. Equations get step checking; anything else is
    final-answer only, and a non-match is held for tutor review (never auto-failed)."""
    lines = [l for l in re.split(r"[\n;]+", text or "") if l.strip()]
    exp = str(expected or "").strip()
    if not lines:
        return _r(0, marks, "MISSING", "No answer found for this question.", 1.0, True)
    if not exp:
        return _r(0, marks, "REVIEW", "No answer key; tutor review needed.", 0.0, True)
    exp_n = _num(exp.lower().replace("x =", "").replace("x=", ""))
    if exp_n is not None and any(solve_line(l) is not None for l in lines):
        return mark_linear_working(text, exp, marks)
    final = lines[-1].split("=")[-1]
    a, b = _num(final), _num(exp)
    same = (a is not None and b is not None and a == b) or _norm(final) == _norm(exp)
    if same:
        return _r(marks, marks, "CORRECT", "Your final answer is correct.", 0.7, False)
    return _r(0, marks, "INCORRECT",
              "Your final answer does not match the expected answer. A tutor will check it before it counts.",
              0.5, True)
