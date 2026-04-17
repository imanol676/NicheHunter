from fastapi import FastAPI

app = FastAPI(title="NicheHunter AI API", version="1.0.0")

@app.get("/api/health")
async def health_check():
    return {"status": "ok"}
