from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.api.deps import get_db, get_current_user
from src.models.validation_report import ValidationReport
from src.models.user import User
from src.models.cluster import PainPointCluster
from src.models.scan_job import ScanJob
from src.schemas.validation_report import ValidationReport as ValidationReportSchema

router = APIRouter()

@router.get("/", response_model=List[ValidationReportSchema])
async def list_reports(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    query = (
        select(ValidationReport)
        .join(PainPointCluster, ValidationReport.cluster_id == PainPointCluster.id)
        .join(ScanJob, PainPointCluster.scan_job_id == ScanJob.id)
        .where(ScanJob.user_id == user.id)
        .options(joinedload(ValidationReport.cluster).joinedload(PainPointCluster.scan_job))
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(query)
    reports = result.scalars().all()
    return reports

@router.get("/{id}", response_model=ValidationReportSchema)
async def get_report(id: UUID, db: AsyncSession = Depends(get_db)):
    query = select(ValidationReport).where(ValidationReport.id == id)
    result = await db.execute(query)
    report = result.scalars().first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    return report

@router.delete("/{id}", status_code=204)
async def delete_report(
    id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = (
        select(ValidationReport)
        .join(PainPointCluster, ValidationReport.cluster_id == PainPointCluster.id)
        .join(ScanJob, PainPointCluster.scan_job_id == ScanJob.id)
        .where(ValidationReport.id == id, ScanJob.user_id == user.id)
    )
    result = await db.execute(query)
    report = result.scalars().first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    await db.delete(report)
    await db.commit()
    
    return None

@router.delete("/all", status_code=204)
async def delete_all_reports(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    query = (
        select(ValidationReport)
        .join(PainPointCluster, ValidationReport.cluster_id == PainPointCluster.id)
        .join(ScanJob, PainPointCluster.scan_job_id == ScanJob.id)
        .where(ScanJob.user_id == user.id)
    )
    result = await db.execute(query)
    reports = result.scalars().all()
    
    for r in reports:
        await db.delete(r)
        
    await db.commit()
    return None
