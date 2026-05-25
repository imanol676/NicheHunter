from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.deps import get_db
from src.models.cluster import PainPointCluster
from src.models.pain_point import PainPoint
from src.schemas.cluster import Cluster as ClusterSchema
from src.schemas.pain_point import PainPoint as PainPointSchema

router = APIRouter()

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
    query = select(PainPoint).where(PainPoint.cluster_id == id)
    result = await db.execute(query)
    pain_points = result.scalars().all()
    
    return pain_points
