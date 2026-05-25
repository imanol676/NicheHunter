from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.v1.api import api_router

app = FastAPI(
    title="NicheHunter AI API", 
    version="1.0.0",
    description="API REST para consultar oportunidades de negocio generadas por IA."
)

# Configuración de CORS para permitir que el Frontend (React/Next.js) consuma la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"], # Origen del frontend en desarrollo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registramos todos los endpoints de la API bajo el prefijo /api/v1
app.include_router(api_router, prefix="/api/v1")

@app.get("/api/health", tags=["health"])
async def health_check():
    return {"status": "ok", "message": "NicheHunter AI Backend is running!"}
