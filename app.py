from fastapi import FastAPI
import requests
import time

app = FastAPI(title="Titanium Multi-Space Orchestrator v2 SaaS")

SPACES = [
    "https://space-a.hf.space",
    "https://space-b.hf.space",
    "https://space-c.hf.space"
]

_cache = {"node": None, "t": 0}

def check(url):
    try:
        r = requests.get(url + "/health", timeout=3)
        return 2 if r.status_code == 200 else 0
    except:
        return 0

def select():
    best = None
    best_score = -1

    for s in SPACES:
        score = check(s)
        if score > best_score:
            best_score = score
            best = s

    return best, best_score

def get_node():
    global _cache

    now = time.time()
    if _cache["node"] and now - _cache["t"] < 10:
        return _cache["node"]

    node, score = select()

    if score <= 0:
        return None

    _cache["node"] = node
    _cache["t"] = now
    return node


@app.get("/")
def root():
    return {"system": "Titanium SaaS v2", "status": "online"}


@app.get("/route")
def route():
    node = get_node()
    if not node:
        return {"status": "NO_NODE"}
    return {"active": node}


@app.get("/proxy")
def proxy():
    node = get_node()
    if not node:
        return {"error": "no node"}

    try:
        r = requests.get(node + "/", timeout=5)
        return {"node": node, "response": r.text}
    except Exception as e:
        return {"error": str(e)}
