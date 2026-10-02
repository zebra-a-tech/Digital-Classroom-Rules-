"""
Digital Classroom Rules — single SQLite access layer.
All new modules import from here. Existing modules are untouched.

Design rules:
- Never opens a connection at import time.
- Every public function opens and closes its own connection.
- Read-only helpers never write (no PRAGMA that requires a write).
- WAL is enabled only on writable connections, and failure is non-fatal.
- Path is resolved relative to this file, so cwd does not matter.
"""
import os
import sqlite3
import datetime


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


_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(_HERE, "digital_classroom.db")


# ---------- connection ----------
def connect(readonly=False):
    if readonly:
        uri = f"file:{DB_PATH}?mode=ro"
        con = sqlite3.connect(uri, uri=True, timeout=10)
    else:
        con = sqlite3.connect(DB_PATH, timeout=10)
    con.row_factory = sqlite3.Row
    # Foreign keys check is read-safe on both modes.
    try:
        con.execute("PRAGMA foreign_keys = ON")
    except sqlite3.OperationalError:
        pass
    # WAL requires write access — only attempt on writable connections,
    # and treat failure as non-fatal (some Android filesystems disallow it).
    if not readonly:
        try:
            con.execute("PRAGMA journal_mode = WAL")
        except sqlite3.OperationalError:
            pass
    return con


# ---------- query helpers ----------
def query(sql, params=(), readonly=True):
    """Run a SELECT and return a list of sqlite3.Row."""
    con = connect(readonly=readonly)
    try:
        return list(con.execute(sql, params))
    finally:
        con.close()


def query_one(sql, params=(), readonly=True):
    """Run a SELECT and return the first row or None."""
    con = connect(readonly=readonly)
    try:
        return con.execute(sql, params).fetchone()
    finally:
        con.close()


def exec_(sql, params=()):
    """Run a write statement. Returns lastrowid."""
    con = connect(readonly=False)
    try:
        cur = con.execute(sql, params)
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def exec_many(sql, seq_of_params):
    """Run a write statement many times in one transaction."""
    con = connect(readonly=False)
    try:
        cur = con.executemany(sql, seq_of_params)
        con.commit()
        return cur.rowcount
    finally:
        con.close()


# ---------- schema introspection (safe) ----------
def table_exists(name):
    row = query_one(
        "SELECT 1 FROM sqlite_master WHERE type='table' AND name=?",
        (name,),
    )
    return row is not None


def table_columns(name):
    """Return list of column names for a table, or [] if missing."""
    if not table_exists(name):
        return []
    rows = query(f'PRAGMA table_info("{name}")')
    return [r["name"] for r in rows]


def column_exists(table, column):
    return column in table_columns(table)


# ---------- time helpers ----------
def now_iso():
    return datetime.datetime.now().isoformat(timespec="seconds")


def now_dt():
    return datetime.datetime.now()


def parse_iso(s):
    if not s:
        return None
    try:
        return datetime.datetime.fromisoformat(s)
    except Exception:
        return None


def seconds_between(a_iso, b_iso):
    a = parse_iso(a_iso)
    b = parse_iso(b_iso)
    if not a or not b:
        return None
    return (b - a).total_seconds()


# ---------- self-test ----------
if __name__ == "__main__":
    print("DB_PATH:", DB_PATH)
    print("exists:", os.path.exists(DB_PATH))
    tables = query("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    print("tables:", len(tables))
    print("students cols:", table_columns("students"))
    print("curriculum rows:", query_one("SELECT COUNT(*) c FROM curriculum")["c"])
