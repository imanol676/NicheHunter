from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List

from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.models.scan_job import ScanJob
from src.models.pain_point import PainPoint
from src.models.raw_post import RawPost

router = APIRouter()

@router.get("/")
async def get_pain_points(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Obtiene todos los pain points extraídos de los scan jobs del usuario actual.
    Incluye información de la publicación original (url, plataforma) y del scan_job (niche).
    """
    # 1. Obtener todos los scan_jobs del usuario
    scans_result = await db.execute(select(ScanJob.id).where(ScanJob.user_id == user.id))
    scan_ids = scans_result.scalars().all()
    
    if not scan_ids:
        return []
        
    # 2. Obtener los pain points que pertenezcan a los RawPosts de esos scan_jobs
    # Haciendo un JOIN con RawPost y ScanJob
    query = (
        select(PainPoint)
        .join(RawPost, PainPoint.raw_post_id == RawPost.id)
        .join(ScanJob, RawPost.scan_job_id == ScanJob.id)
        .where(ScanJob.user_id == user.id)
        .options(selectinload(PainPoint.raw_post).selectinload(RawPost.scan_job))
        .order_by(PainPoint.created_at.desc())
    )
    
    result = await db.execute(query)
    pain_points = result.scalars().all()
    
    # Formatear la respuesta
    response_data = []
    for pp in pain_points:
        response_data.append({
            "id": str(pp.id),
            "description": pp.description,
            "category": pp.category,
            "severity": pp.severity,
            "confidence_score": pp.confidence_score,
            "created_at": pp.created_at,
            "source_platform": pp.raw_post.source_platform if pp.raw_post else "unknown",
            "source_url": pp.raw_post.url if pp.raw_post else None,
            "niche": pp.raw_post.scan_job.niche_query if pp.raw_post and pp.raw_post.scan_job else "Unknown"
        })
        
    return response_data

@router.delete("/all")
async def delete_all_pain_points(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina de forma masiva todos los pain points asociados al usuario.
    Al eliminar los Pain Points, por regla general deberíamos eliminar los Raw Posts también o dejarlos.
    Para mayor limpieza, eliminaremos todos los ScanJobs del usuario, lo que borra TODO en cascada
    relacionado a los pain points.
    """
    from sqlalchemy.future import select
    from src.models.scan_job import ScanJob
    
    # Obtenemos todos los scans del usuario
    result = await db.execute(select(ScanJob).where(ScanJob.user_id == user.id))
    scans = result.scalars().all()
    
    # Eliminamos uno por uno para que el ORM active el cascade="all, delete-orphan"
    for scan in scans:
        await db.delete(scan)
        
    await db.commit()
    
    return {"message": "Todos los datos (Scans, Clusters, Pain Points, Oportunidades) han sido eliminados."}
