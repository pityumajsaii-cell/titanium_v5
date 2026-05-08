from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "LIVE", "system": "Titanium CORE OK"}

@app.get("/health")
def health():
    return {"status": "ok"}
