from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {
        "status": "ONLINE",
        "system": "Titanium CLEAN REBOOT",
        "hf": "recovered"
    }

@app.get("/health")
def health():
    return {"status": "ok"}
