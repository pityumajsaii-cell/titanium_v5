from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "LIVE", "system": "Titanium FIXED CORE"}

@app.get("/health")
def health():
    return {"status": "ok"}
