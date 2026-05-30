from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.api.deps import get_db, get_current_user
from src.models.opportunity import Opportunity
from src.models.user import User
from src.models.cluster import PainPointCluster
from src.models.scan_job import ScanJob
from src.schemas.opportunity import Opportunity as OpportunitySchema

router = APIRouter()

@router.get("/", response_model=List[OpportunitySchema])
async def list_opportunities(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    """
    Lista las mejores oportunidades de negocio generadas, ordenadas por score de mayor a menor, filtradas por usuario.
    """
    query = (
        select(Opportunity)
        .join(PainPointCluster, Opportunity.cluster_id == PainPointCluster.id)
        .join(ScanJob, PainPointCluster.scan_job_id == ScanJob.id)
        .where(ScanJob.user_id == user.id)
        .options(joinedload(Opportunity.cluster).joinedload(PainPointCluster.scan_job))
        .order_by(Opportunity.opportunity_score.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    opportunities = result.scalars().all()
    return opportunities

@router.get("/{id}", response_model=OpportunitySchema)
async def get_opportunity(id: UUID, db: AsyncSession = Depends(get_db)):
    """
    Obtiene los detalles completos de una oportunidad de negocio específica.
    """
    query = select(Opportunity).where(Opportunity.id == id)
    result = await db.execute(query)
    opportunity = result.scalars().first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada")
        
    return opportunity

@router.delete("/{id}", status_code=204)
async def delete_opportunity(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """
    Elimina una oportunidad si pertenece al usuario activo.
    """
    query = (
        select(Opportunity)
        .join(PainPointCluster, Opportunity.cluster_id == PainPointCluster.id)
        .join(ScanJob, PainPointCluster.scan_job_id == ScanJob.id)
        .where(Opportunity.id == id, ScanJob.user_id == user.id)
    )
    result = await db.execute(query)
    opportunity = result.scalars().first()
    
    if not opportunity:
        raise HTTPException(status_code=404, detail="Oportunidad no encontrada o no autorizada")
        
    await db.delete(opportunity)
    await db.commit()
    
    return None
