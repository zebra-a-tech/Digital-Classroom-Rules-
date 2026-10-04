import os, sys, requests, base64, sqlite3

TURSO_URL = os.environ.get("TURSO_DATABASE_URL", "").strip()
TURSO_TOKEN = os.environ.get("TURSO_AUTH_TOKEN", "").strip()

if TURSO_URL.startswith("libsql://"):
    TURSO_URL = TURSO_URL.replace("libsql://", "https://")
if TURSO_URL and not TURSO_URL.startswith("http"):
    TURSO_URL = "https://" + TURSO_URL
API_URL = TURSO_URL.rstrip("/") + "/v2/pipeline"

HEADERS = {
    "Authorization": f"Bearer {TURSO_TOKEN}",
    "Content-Type": "application/json"
}

class TursoRow(dict):
    def __init__(self, items):
        self._list = [v for _, v in items]
        super().__init__(items)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._list[key]
        return super().__getitem__(key)

class TursoCursor:
    def __init__(self, conn):
        self.conn = conn
        self.description = None
        self.lastrowid = None
        self.rowcount = 0
        self._results = []

    def execute(self, sql, params=None):
        stmt = {"sql": sql}
        if params:
            stmt["args"] = []
            for val in params:
                if val is None:
                    stmt["args"].append({"type": "null"})
                elif isinstance(val, int):
                    stmt["args"].append({"type": "integer", "value": str(val)})
                elif isinstance(val, float):
                    stmt["args"].append({"type": "float", "value": val})
                elif isinstance(val, (bytes, bytearray)):
                    stmt["args"].append({"type": "blob", "base64": base64.b64encode(val).decode()})
                else:
                    stmt["args"].append({"type": "text", "value": str(val)})
        
        payload = {"requests": [{"type": "execute", "stmt": stmt}, {"type": "close"}]}
        r = requests.post(API_URL, headers=HEADERS, json=payload, timeout=25)
        if r.status_code != 200:
            raise Exception(f"Turso error {r.status_code}: {r.text}")
        
        data = r.json()
        res = data.get("results", [{}])[0]
        if res.get("type") == "error":
            raise Exception(res.get("error", {}).get("message", "Turso error"))
        
        result = res.get("response", {}).get("result", {})
        cols = [c["name"] for c in result.get("cols", [])]
        self.description = [(c, None, None, None, None, None, None) for c in cols]
        self.lastrowid = result.get("last_insert_rowid")
        self.rowcount = result.get("affected_row_count", 0)
        
        self._results = []
        for row in result.get("rows", []):
            parsed = []
            for cell in row:
                if cell.get("type") == "null":
                    parsed.append(None)
                elif cell.get("type") == "integer":
                    parsed.append(int(cell.get("value")))
                elif cell.get("type") == "float":
                    parsed.append(float(cell.get("value")))
                elif cell.get("type") == "blob":
                    parsed.append(base64.b64decode(cell.get("base64", "")))
                else:
                    parsed.append(cell.get("value"))
            self._results.append(TursoRow(list(zip(cols, parsed))))
        return self

    def executemany(self, sql, seq_of_params):
        for p in seq_of_params:
            self.execute(sql, p)
        return self

    def fetchone(self):
        return self._results.pop(0) if self._results else None

    def fetchall(self):
        res = list(self._results)
        self._results = []
        return res

class TursoConnection:
    def __init__(self):
        self.row_factory = None

    def cursor(self):
        return TursoCursor(self)

    def execute(self, sql, params=None):
        c = self.cursor()
        return c.execute(sql, params)

    def executemany(self, sql, params):
        c = self.cursor()
        return c.executemany(sql, params)

    def commit(self):
        pass

    def rollback(self):
        pass

    def close(self):
        pass

def connect(*args, **kwargs):
    return TursoConnection()

# Auto-patch sqlite3 globally when Turso env vars exist
if TURSO_URL and TURSO_TOKEN:
    sqlite3.connect = connect
    print("🌍 Global SQLite connection successfully hooked to Turso Cloud!")
