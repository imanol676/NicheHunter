import asyncio
import random
from src.services.scraper.reddit_json_client import try_fetch_reddit
from src.db.engine import AsyncSessionLocal
from src.models import RawPost
from sqlalchemy.dialects.postgresql import insert


async def pausa_humana(min_segundos: float = 2.0, max_segundos: float = 5.0):
    random_number = random.uniform(min_segundos, max_segundos)
    tiempo_espera = round(random_number, 2)
    print(f"Esperando {tiempo_espera} segundos...")
    await asyncio.sleep(tiempo_espera)


from src.services.scraper.hn_json_client import try_fetch_hn
from src.services.scraper.youtube_api_client import try_fetch_youtube

async def run_scraper(extraction_plan: dict, scan_job_id: str):
    print("Iniciando escaneo multi-plataforma...")
    
    reddit_communities = extraction_plan.get("reddit_communities", [])
    hn_keywords = extraction_plan.get("hackernews_keywords", [])
    yt_queries = extraction_plan.get("youtube_search_queries", [])
    b2b_keywords = extraction_plan.get("b2b_search_keywords", [])
    
    # 1. Scraping B2B Software Reviews & LinkedIn (Alta Prioridad)
    from src.services.scraper.b2b_search_client import fetch_all_b2b_channels
    for kw in b2b_keywords:
        print(f"\n--- Extrayendo Web B2B (G2, Capterra, LinkedIn): '{kw}' ---")
        posts = await fetch_all_b2b_channels(kw)
        await guardar_posts_en_db(posts, scan_job_id)
        if kw != b2b_keywords[-1]:
            await pausa_humana(2.0, 4.0)

    # 2. Scraping Reddit
    for sub in reddit_communities:
        print(f"\n--- Extrayendo Reddit r/{sub} ---")
        posts = await try_fetch_reddit(sub)
        await guardar_posts_en_db(posts, scan_job_id)
        if sub != reddit_communities[-1]:
            await pausa_humana(2.5, 5.5)
            
    # 3. Scraping Hacker News
    for kw in hn_keywords:
        print(f"\n--- Extrayendo Hacker News: '{kw}' ---")
        posts = await try_fetch_hn(kw)
        await guardar_posts_en_db(posts, scan_job_id)
        if kw != hn_keywords[-1]:
            await pausa_humana(1.0, 3.0)
            
    # 4. Scraping YouTube
    for query in yt_queries:
        print(f"\n--- Extrayendo YouTube: '{query}' ---")
        posts = await try_fetch_youtube(query)
        await guardar_posts_en_db(posts, scan_job_id)
        if query != yt_queries[-1]:
            await pausa_humana(2.0, 4.0)

async def guardar_posts_en_db(posts_limpios: list[dict], scan_job_id: str):
    if not posts_limpios:
        return
        
    async with AsyncSessionLocal() as session:
        # Agregamos el scan_job_id a cada post
        for p in posts_limpios:
            p['scan_job_id'] = scan_job_id
        # Preparamos la orden de inserción masiva
        stmt = insert(RawPost).values(posts_limpios)
        
        # Magia de Postgres: "Si este source_id ya existe, simplemente ignóralo"
        stmt = stmt.on_conflict_do_nothing(index_elements=['source_id'])
        
        # Ejecutamos la orden y confirmamos los cambios
        await session.execute(stmt)
        await session.commit()
        print(f"Guardados en la Base de Datos exitosamente.")

if __name__ == "__main__":
    subreddits_de_prueba = ["freelance", "startups", "SaaS"]
    asyncio.run(run_scraper(subreddits_de_prueba))




