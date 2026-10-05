"""Tiny Turso-over-HTTPS client (stdlib only). Falls back to local SQLite if no Turso env vars."""
import os, json, sqlite3, urllib.request

URL = (os.environ.get("TURSO_DATABASE_URL") or os.environ.get("TURSO_URL") or "").replace("libsql://", "https://")
TOKEN = os.environ.get("TURSO_AUTH_TOKEN") or os.environ.get("TURSO_TOKEN") or ""
LOCAL = os.environ.get("DCR_LOCAL_DB", "dcr_local.db")


def mode():
    return "turso" if (URL and TOKEN) else "local-sqlite"


def _arg(v):
    if v is None:
        return {"type": "null"}
    if isinstance(v, bool):
        v = int(v)
    if isinstance(v, int):
        return {"type": "integer", "value": str(v)}
    if isinstance(v, float):
        return {"type": "float", "value": v}
    return {"type": "text", "value": str(v)}


def _cell(c):
    t, v = c.get("type"), c.get("value")
    if t == "null":
        return None
    if t == "integer":
        return int(v)
    if t == "float":
        return float(v)
    return v


def run(sql, args=()):
    """Execute one statement, return a list of dict rows."""
    if mode() == "turso":
        body = json.dumps({"requests": [
            {"type": "execute", "stmt": {"sql": sql, "args": [_arg(a) for a in args]}},
            {"type": "close"}]}).encode()
        req = urllib.request.Request(
            URL.rstrip("/") + "/v2/pipeline", data=body,
            headers={"Authorization": "Bearer " + TOKEN, "Content-Type": "application/json",
                     "User-Agent": "dcr-app/1.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            res = json.load(r)["results"][0]
        if res.get("type") == "error":
            raise RuntimeError(res["error"]["message"])
        out = res["response"]["result"]
        cols = [c["name"] for c in out["cols"]]
        return [dict(zip(cols, [_cell(c) for c in row])) for row in out["rows"]]
    con = sqlite3.connect(LOCAL)
    con.row_factory = sqlite3.Row
    try:
        rows = [dict(r) for r in con.execute(sql, tuple(args)).fetchall()]
        con.commit()
        return rows
    finally:
        con.close()


SCHEMA = [
    "CREATE TABLE IF NOT EXISTS dcr_users (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT UNIQUE, "
    "pw TEXT, grade INTEGER DEFAULT 1, ecocash TEXT, ref_code TEXT UNIQUE, referred_by INTEGER, "
    "credit_cents INTEGER DEFAULT 0, created TEXT)",
    "CREATE TABLE IF NOT EXISTS dcr_referrals (id INTEGER PRIMARY KEY AUTOINCREMENT, referrer_id INTEGER, "
    "new_user_id INTEGER, cents INTEGER, ts TEXT)",
    "CREATE TABLE IF NOT EXISTS dcr_payouts (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, cents INTEGER, ts TEXT)",
    "CREATE TABLE IF NOT EXISTS dcr_progress (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, book INTEGER, "
    "chapter INTEGER, score INTEGER, ts TEXT)",
]


def init():
    for s in SCHEMA:
        run(s)
