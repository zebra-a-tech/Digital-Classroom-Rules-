import os, gzip, json, sqlite3, base64
_SEED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_content.json.gz")

def _dec(v):
    if isinstance(v, str) and v.startswith("__b64__"):
        return base64.b64decode(v[7:])
    return v

def restore(path=None):
    try:
        if not os.path.exists(_SEED):
            return
        if not (isinstance(path, str) and path):
            path = os.environ.get("DB_PATH", "").strip() or "digital_classroom.db"
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
        seed = json.load(gzip.open(_SEED, "rt", encoding="utf-8"))
        con = sqlite3.connect(path, timeout=30)
        for t, spec in seed.items():
            try:
                exists = con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name=?", (t,)).fetchone()
                if not exists:
                    con.execute(spec["sql"])
                have = con.execute('SELECT COUNT(*) FROM "%s"' % t).fetchone()[0]
                if have >= len(spec["rows"]):
                    continue
                tcols = [r[1] for r in con.execute('PRAGMA table_info("%s")' % t)]
                idx = [i for i, c in enumerate(spec["cols"]) if c in tcols]
                names = ",".join('"%s"' % spec["cols"][i] for i in idx)
                q = 'INSERT OR REPLACE INTO "%s" (%s) VALUES (%s)' % (t, names, ",".join("?" * len(idx)))
                con.execute('DELETE FROM "%s"' % t)
                con.executemany(q, [[_dec(r[i]) for i in idx] for r in spec["rows"]])
                con.commit()
                print("SEED RESTORE: %s %d -> %d rows" % (t, have, len(spec["rows"])))
            except Exception as e:
                con.rollback()
                print("SEED RESTORE skipped %s: %s" % (t, e))
        con.close()
    except Exception as e:
        print("SEED RESTORE failed:", e)
