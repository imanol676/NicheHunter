from fastapi import APIRouter
from src.api.v1 import opportunities, clusters

api_router = APIRouter()

api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(clusters.router, prefix="/clusters", tags=["clusters"])
