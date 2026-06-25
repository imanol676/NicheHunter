from fastapi import APIRouter
from src.api.v1 import validation_reports, clusters, scans, users, pain_points

api_router = APIRouter()

api_router.include_router(validation_reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(clusters.router, prefix="/clusters", tags=["clusters"])
api_router.include_router(scans.router, prefix="/scans", tags=["scans"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(pain_points.router, prefix="/pain-points", tags=["pain points"])
