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
from src.services.ai.opportunity_generator import procesar_nuevas_oportunidades
from src.services.ai.niche_expander import expandir_nicho_a_subreddits

async def run_extraction_pipeline(niche: str, scan_job_id: str, task_self):
    """
    Coordina la ejecución de todos los scripts de IA y Scraping.
    """
    try:
        task_self.update_state(state='PROGRESS', meta={'status': f"Analizando nicho y mapeando subreddits con Llama-3..."})
        
        # Expandir la búsqueda dinámicamente usando IA
        subreddits_a_escanear = await expandir_nicho_a_subreddits(niche)
        lista_format = ", ".join([f"r/{sub}" for sub in subreddits_a_escanear])
        print(f"[{scan_job_id}] IA decidió escanear: {lista_format}")
        
        task_self.update_state(state='PROGRESS', meta={'status': f"Extrayendo publicaciones de {lista_format}..."})
        await run_scraper(subreddits_a_escanear, scan_job_id)
        
        task_self.update_state(state='PROGRESS', meta={'status': "Extrayendo quejas y dolores con GPT-4o..."})
        await procesar_lote_de_posts(scan_job_id)
        
        task_self.update_state(state='PROGRESS', meta={'status': "Calculando vectores multidimensionales..."})
        await procesar_embeddings_pendientes(scan_job_id)
        
        task_self.update_state(state='PROGRESS', meta={'status': "Agrupando problemas en Clústeres (HDBSCAN)..."})
        await agrupar_pain_points(scan_job_id)
        
        task_self.update_state(state='PROGRESS', meta={'status': "Diseñando Oportunidades de Negocio (SaaS)..."})
        await procesar_nuevas_oportunidades(scan_job_id)

        # Clústeres ya son vinculados dentro de clusterizer.py
        
        task_self.update_state(state='SUCCESS', meta={'status': "Completado"})
        return {"status": "SUCCESS", "niche": niche}
    except Exception as e:
        print("\n=== ERROR EN EL PIPELINE DE IA ===")
        traceback.print_exc()
        print("==================================\n")
        task_self.update_state(state='FAILURE', meta={'status': f"Error: {str(e)}"})
        raise Ignore()

@celery_app.task(bind=True, name="run_scraping_pipeline")
def run_scraping_pipeline(self, niche: str, scan_job_id: str):
    self.update_state(state='PROGRESS', meta={'status': 'Iniciando Pipeline...'})
    
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(run_extraction_pipeline(niche, scan_job_id, self))
    
    return result
