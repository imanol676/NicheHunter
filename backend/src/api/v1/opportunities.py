from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.api.deps import get_db
from src.models.opportunity import Opportunity
from src.schemas.opportunity import Opportunity as OpportunitySchema

router = APIRouter()

@router.get("/", response_model=List[OpportunitySchema])
async def list_opportunities(
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 50
):
    """
    Lista las mejores oportunidades de negocio generadas, ordenadas por score de mayor a menor.
    """
    query = select(Opportunity).order_by(Opportunity.opportunity_score.desc()).offset(skip).limit(limit)
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
