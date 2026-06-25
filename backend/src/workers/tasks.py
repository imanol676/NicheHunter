import asyncio
from src.workers.celery_app import celery_app
from sqlalchemy import update
from src.db.engine import AsyncSessionLocal
from src.models import PainPointCluster
from celery.exceptions import Ignore
import traceback

from src.services.scraper.scraper_serviece import run_scraper
from src.services.ai.pain_point_extractor import procesar_lote_de_posts
from src.services.ai.embedder import procesar_embeddings_pendientes
from src.services.ai.clusterizer import agrupar_pain_points
from src.services.ai.niche_expander import expand_niche_to_sources

async def run_exploration_task(niche: str, scan_job_id: str, task_self):
    try:
        task_self.update_state(state='PROGRESS', meta={'status': f"Analizando nicho y mapeando fuentes con Llama-3..."})
        extraction_plan = await expand_niche_to_sources(niche)
        
        reddit_str = ", ".join(extraction_plan.get("reddit_communities", []))
        hn_str = ", ".join(extraction_plan.get("hackernews_keywords", []))
        yt_str = ", ".join(extraction_plan.get("youtube_search_queries", []))
        
        print(f"[{scan_job_id}] IA decidió escanear Reddit: [{reddit_str}], HN: [{hn_str}], YT: [{yt_str}]")
        
        task_self.update_state(state='PROGRESS', meta={'status': f"Extrayendo publicaciones multi-plataforma..."})
        await run_scraper(extraction_plan, scan_job_id)
        
        task_self.update_state(state='PROGRESS', meta={'status': "Extrayendo quejas y dolores con IA..."})
        await procesar_lote_de_posts(scan_job_id)
        
        async with AsyncSessionLocal() as session:
            from sqlalchemy.future import select
            from sqlalchemy import func
            from src.models import ScanJob, PainPoint, RawPost
            
            result = await session.execute(
                select(func.count(PainPoint.id))
                .join(RawPost)
                .where(RawPost.scan_job_id == scan_job_id)
            )
            pp_count = result.scalar() or 0
            
            scan = await session.get(ScanJob, scan_job_id)
            if pp_count < 3:
                scan.phase = "failed_no_data"
            else:
                scan.phase = "pending_payment"
                
            await session.commit()
        
        task_self.update_state(state='SUCCESS', meta={'status': "Exploración completada. Esperando pago.", 'phase': scan.phase})
        return {"status": "SUCCESS", "phase": scan.phase}
    except Exception as e:
        print("\n=== ERROR EN LA EXPLORACIÓN ===")
        traceback.print_exc()
        task_self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'status': f"Error: {str(e)}"})
        raise Ignore()

async def run_deep_analysis_task(niche: str, scan_job_id: str, task_self):
    try:
        task_self.update_state(state='PROGRESS', meta={'status': "Calculando vectores multidimensionales..."})
        await procesar_embeddings_pendientes(scan_job_id)
        
        task_self.update_state(state='PROGRESS', meta={'status': "Agrupando problemas en Clústeres (HDBSCAN)..."})
        await agrupar_pain_points(scan_job_id)
        
        async with AsyncSessionLocal() as session:
            from sqlalchemy.future import select
            from sqlalchemy import func
            from src.models import ScanJob, PainPointCluster, User
            import datetime
            
            result = await session.execute(
                select(func.count(PainPointCluster.id))
                .where(PainPointCluster.scan_job_id == scan_job_id)
            )
            cluster_count = result.scalar() or 0
            
            scan = await session.get(ScanJob, scan_job_id)
            if cluster_count == 0 and scan.cost_coins > 0:
                scan.phase = "completed_no_reports"
                user = await session.get(User, scan.user_id)
                user.credits_remaining += scan.cost_coins
                scan.cost_coins = 0
                print(f"[{scan_job_id}] 0 clusters. Reembolsando 1 moneda.")
            else:
                scan.phase = "completed"
                
            scan.completed_at = datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)
            await session.commit()
            
        task_self.update_state(state='SUCCESS', meta={'status': "Analítica completada.", 'phase': scan.phase})
        return {"status": "SUCCESS", "niche": niche, "phase": scan.phase}
    except Exception as e:
        print("\n=== ERROR EN ANÁLISIS PROFUNDO ===")
        traceback.print_exc()
        task_self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'status': f"Error: {str(e)}"})
        raise Ignore()

async def run_ideation_task(cluster_id: str, niche: str, task_self):
    try:
        task_self.update_state(state='PROGRESS', meta={'status': "Diseñando Oportunidad de Negocio (SaaS)..."})
        
        from src.services.ai.validation_generator import procesar_oportunidad_individual
        await procesar_oportunidad_individual(cluster_id, niche)
        
        task_self.update_state(state='SUCCESS', meta={'status': "Oportunidad Generada Exitosamente"})
        return {"status": "SUCCESS", "niche": niche}
    except Exception as e:
        print("\n=== ERROR EN IDEACION ===")
        traceback.print_exc()
        task_self.update_state(state='FAILURE', meta={'exc_type': type(e).__name__, 'exc_message': str(e), 'status': f"Error: {str(e)}"})
        raise Ignore()

@celery_app.task(bind=True, name="run_exploration_pipeline")
def run_exploration_pipeline(self, niche: str, scan_job_id: str):
    self.update_state(state='PROGRESS', meta={'status': 'Iniciando Exploración...'})
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_exploration_task(niche, scan_job_id, self))

@celery_app.task(bind=True, name="run_deep_analysis_pipeline")
def run_deep_analysis_pipeline(self, niche: str, scan_job_id: str):
    self.update_state(state='PROGRESS', meta={'status': 'Iniciando Análisis Estadístico...'})
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_deep_analysis_task(niche, scan_job_id, self))

@celery_app.task(bind=True, name="run_ideation_pipeline")
def run_ideation_pipeline(self, cluster_id: str, niche: str):
    self.update_state(state='PROGRESS', meta={'status': 'Generando Solución...'})
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(run_ideation_task(cluster_id, niche, self))
