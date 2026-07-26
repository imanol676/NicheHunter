from fastapi import APIRouter, Depends
from pydantic import BaseModel
from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.models.scan_job import ScanJob
from src.workers.tasks import run_exploration_pipeline, run_deep_analysis_pipeline
from src.workers.celery_app import celery_app

router = APIRouter()

class ScanRequest(BaseModel):
    niche: str | None = None
    target_industry: str | None = None
    business_process: str | None = None
    competitors: str | None = None

@router.post("/")
async def create_scan(
    request: ScanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia un nuevo proceso de extracción de IA asociado al usuario.
    """
    # Combinar ambas entradas para el motor de scrapping
    if request.target_industry and request.business_process:
        combined_query = f"{request.target_industry} {request.business_process}"
    else:
        combined_query = request.niche or "General"
        
    comp_list = []
    if request.competitors:
        comp_list = [c.strip() for c in request.competitors.split(",") if c.strip()]
        
    scan_job = ScanJob(
        user_id=user.id, 
        niche_query=combined_query,
        target_industry=request.target_industry,
        business_process=request.business_process,
        competitors=comp_list
    )
    db.add(scan_job)
    await db.commit()
    await db.refresh(scan_job)

    # Enviamos el ID del scan_job a la tarea de fondo de EXPLORACION (Fase 1)
    task = run_exploration_pipeline.delay(combined_query, str(scan_job.id), comp_list)
    return {"task_id": task.id, "scan_job_id": str(scan_job.id), "message": f"Exploración para '{combined_query}' encolada."}

@router.get("/{scan_job_id}/preview")
async def get_scan_preview(
    scan_job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    from sqlalchemy import func
    from src.models import RawPost, PainPoint
    from fastapi import HTTPException
    
    scan = await db.get(ScanJob, scan_job_id)
    if not scan or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scan no encontrado")
        
    posts_count = await db.scalar(select(func.count(RawPost.id)).where(RawPost.scan_job_id == scan_job_id))
    pp_count = await db.scalar(
        select(func.count(PainPoint.id))
        .join(RawPost)
        .where(RawPost.scan_job_id == scan_job_id)
    )
    
    return {
        "scan_job_id": str(scan.id),
        "niche": scan.niche_query,
        "phase": scan.phase,
        "pain_points_extracted": pp_count or 0,
        "status": scan.status
    }

@router.get("/{scan_job_id}/clusters", response_model=list[dict])
async def get_scan_clusters(
    scan_job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from sqlalchemy.future import select
    from fastapi import HTTPException
    from src.models import PainPointCluster, ValidationReport
    
    scan = await db.get(ScanJob, scan_job_id)
    if not scan or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scan no encontrado")
        
    query = (
        select(PainPointCluster, ValidationReport.id.label("report_id"))
        .outerjoin(ValidationReport, PainPointCluster.id == ValidationReport.cluster_id)
        .where(PainPointCluster.scan_job_id == scan_job_id)
        .order_by(PainPointCluster.size.desc())
    )
    result = await db.execute(query)
    rows = result.all()
    
    clusters_data = []
    for cluster, report_id in rows:
        clusters_data.append({
            "id": str(cluster.id),
            "label": cluster.label,
            "summary": cluster.summary,
            "size": cluster.size,
            "avg_severity_score": cluster.avg_severity_score,
            "has_opportunity": bool(report_id)
        })
        
    return clusters_data

@router.post("/{scan_job_id}/analyze")
async def analyze_scan(
    scan_job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    from fastapi import HTTPException
    
    scan = await db.get(ScanJob, scan_job_id)
    if not scan or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scan no encontrado")
        
    if scan.phase != "pending_payment":
        raise HTTPException(status_code=400, detail=f"El scan no está listo para análisis. Fase actual: {scan.phase}")
        
    scan.phase = "deep_analysis"
    
    await db.commit()
    
    # Encolar Fase 2
    task = run_deep_analysis_pipeline.delay(scan.niche_query, str(scan.id))
    return {"task_id": task.id, "scan_job_id": str(scan.id), "message": "Análisis profundo encolado."}

@router.get("/{task_id}/status")
async def get_scan_status(task_id: str):
    """
    Endpoint para que el Frontend haga 'Polling' y actualice la Terminal en vivo.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    # Extraemos el mensaje personalizado del Worker o damos uno genérico
    status_msg = "Pendiente en cola de Redis..."
    phase = "exploration"
    if task_result.info and isinstance(task_result.info, dict):
        status_msg = task_result.info.get("status", status_msg)
        phase = task_result.info.get("phase", phase)
        
    return {
        "task_id": task_id,
        "status": task_result.status, # PENDING, PROGRESS, SUCCESS, FAILURE
        "info": status_msg,
        "phase": phase
    }

@router.delete("/{scan_job_id}")
async def delete_scan(
    scan_job_id: str,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Elimina por completo una búsqueda y todos los datos asociados.
    """
    from fastapi import HTTPException
    
    scan = await db.get(ScanJob, scan_job_id)
    if not scan or scan.user_id != user.id:
        raise HTTPException(status_code=404, detail="Scan no encontrado")
        
    await db.delete(scan)
    await db.commit()
    
    return {"message": "Búsqueda eliminada exitosamente"}
