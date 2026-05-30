from fastapi import APIRouter, Depends
from pydantic import BaseModel
from celery.result import AsyncResult
from sqlalchemy.ext.asyncio import AsyncSession
from src.api.deps import get_current_user, get_db
from src.models.user import User
from src.models.scan_job import ScanJob
from src.workers.tasks import run_scraping_pipeline
from src.workers.celery_app import celery_app

router = APIRouter()

class ScanRequest(BaseModel):
    niche: str

@router.post("/")
async def create_scan(
    request: ScanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Inicia un nuevo proceso de extracción de IA asociado al usuario.
    """
    scan_job = ScanJob(user_id=user.id, niche_query=request.niche)
    db.add(scan_job)
    await db.commit()
    await db.refresh(scan_job)

    # Enviamos el ID del scan_job a la tarea de fondo
    task = run_scraping_pipeline.delay(request.niche, str(scan_job.id))
    return {"task_id": task.id, "scan_job_id": str(scan_job.id), "message": f"Escaneo para '{request.niche}' encolado."}

@router.get("/{task_id}/status")
async def get_scan_status(task_id: str):
    """
    Endpoint para que el Frontend haga 'Polling' y actualice la Terminal en vivo.
    """
    task_result = AsyncResult(task_id, app=celery_app)
    
    # Extraemos el mensaje personalizado del Worker o damos uno genérico
    status_msg = "Pendiente en cola de Redis..."
    if task_result.info and isinstance(task_result.info, dict):
        status_msg = task_result.info.get("status", status_msg)
        
    return {
        "task_id": task_id,
        "status": task_result.status, # PENDING, PROGRESS, SUCCESS, FAILURE
        "info": status_msg
    }
