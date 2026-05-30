from fastapi import APIRouter
from src.api.v1 import opportunities, clusters, scans

api_router = APIRouter()

api_router.include_router(opportunities.router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(clusters.router, prefix="/clusters", tags=["clusters"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
