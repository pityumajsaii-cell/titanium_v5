from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ONLINE", "system": "Titanium V44"}

@app.get("/health")
def health():
    return {"status": "ok"}
