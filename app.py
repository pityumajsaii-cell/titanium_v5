from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
def root():
    return {"status": "RUNNING"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/admin", response_class=HTMLResponse)
def admin():
    return "<h1>Titanium V44 FIXED OK</h1>"
