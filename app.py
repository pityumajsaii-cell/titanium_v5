from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "OK", "system": "Titanium V44 LIVE"}

@app.get("/health")
def health():
    return {"status": "ok"}
