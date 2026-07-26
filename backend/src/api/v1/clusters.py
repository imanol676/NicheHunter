from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.deps import get_db, get_current_user
from src.models.cluster import PainPointCluster
from src.models.pain_point import PainPoint
from src.models.user import User
from src.schemas.cluster import Cluster as ClusterSchema
from src.schemas.pain_point import PainPoint as PainPointSchema

router = APIRouter()

@router.get("/", response_model=list[dict])
async def list_clusters(
    db: AsyncSession = Depends(get_db),
    user = Depends(get_current_user),
    skip: int = 0,
    limit: int = 50
):
    """
    Lista todos los clústeres estadísticos del usuario, ordenados por tamaño.
    """
    from src.models import ScanJob, ValidationReport
    
    query = (
        select(PainPointCluster, ScanJob.niche_query, ValidationReport.id.label("report_id"))
        .join(ScanJob, PainPointCluster.scan_job_id == ScanJob.id)
        .outerjoin(ValidationReport, PainPointCluster.id == ValidationReport.cluster_id)
        .where(ScanJob.user_id == user.id)
        .order_by(PainPointCluster.size.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    rows = result.all()
    
    clusters_data = []
    for cluster, niche, report_id in rows:
        clusters_data.append({
            "id": str(cluster.id),
            "label": cluster.label,
            "summary": cluster.summary,
            "size": cluster.size,
            "avg_severity_score": cluster.avg_severity_score,
            "niche": niche,
            "has_opportunity": bool(report_id)
        })
        
    return clusters_data

@router.get("/{id}", response_model=ClusterSchema)
async def get_cluster(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Obtiene la información general de un clúster específico.
    """
    query = select(PainPointCluster).where(PainPointCluster.id == id)
    result = await db.execute(query)
    cluster = result.scalars().first()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Clúster no encontrado")
        
    return cluster

@router.get("/{id}/pain_points", response_model=List[PainPointSchema])
async def get_cluster_pain_points(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Lista todas las quejas o problemas individuales (Pain Points) que pertenecen a un clúster.
    Útil para investigar el contexto real de la oportunidad generada.
    """
    # Verificamos si el cluster existe
    cluster_query = select(PainPointCluster).where(PainPointCluster.id == id)
    cluster_result = await db.execute(cluster_query)
    if not cluster_result.scalars().first():
        raise HTTPException(status_code=404, detail="Clúster no encontrado")

    # Obtenemos los pain points
    from src.models.raw_post import RawPost
    query = select(PainPoint, RawPost.url).join(RawPost, PainPoint.raw_post_id == RawPost.id).where(PainPoint.cluster_id == id)
    result = await db.execute(query)
    rows = result.all()
    
    response_data = []
    for pp, url in rows:
        pp_dict = {
            "id": pp.id,
            "description": pp.description,
            "category": pp.category,
            "severity": pp.severity,
            "confidence_score": pp.confidence_score,
            "frequency_count": pp.frequency_count,
            "metadata": pp.metadata_,
            "raw_post_id": pp.raw_post_id,
            "cluster_id": pp.cluster_id,
            "url": url,
            "created_at": pp.created_at
        }
        response_data.append(pp_dict)
    
    return response_data

@router.post("/{cluster_id}/generate-report")
async def generate_report_for_cluster(
    cluster_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Desencadena la generación de un reporte de validación B2B para un clúster específico.
    """
    from fastapi import HTTPException
    from src.models import User, ScanJob
    from src.workers.tasks import run_ideation_pipeline
    
    cluster_query = select(PainPointCluster).where(PainPointCluster.id == cluster_id)
    cluster_result = await db.execute(cluster_query)
    cluster = cluster_result.scalars().first()
    
    if not cluster:
        raise HTTPException(status_code=404, detail="Clúster no encontrado")
        
    scan = await db.get(ScanJob, cluster.scan_job_id)
    if not scan or scan.user_id != user.id:
        raise HTTPException(status_code=403, detail="No tienes acceso a este clúster")
        
    # Lanzar tarea
    task = run_ideation_pipeline.delay(str(cluster.id), scan.niche_query)
    
    return {
        "task_id": task.id, 
        "cluster_id": str(cluster.id), 
        "message": "Generación de solución encolada."
    }
