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


async def run_scraper(subreddits: list[str]):
    print(f"Iniciando escaneo de {len(subreddits)} subreddits...")
    
    for sub in subreddits:
        print(f"\n--- Extrayendo r/{sub} ---")
        
        # 1. Llamar a try_fetch_reddit
        posts = await try_fetch_reddit(sub)
        print(f"Se encontraron {len(posts)} posts limpios.")
        await guardar_posts_en_db(posts)
        # 2. Hacer la pausa humana ANTES de pasar al siguiente subreddit
        if sub != subreddits[-1]:
            await pausa_humana(2.5, 5.5)

async def guardar_posts_en_db(posts_limpios: list[dict]):
    if not posts_limpios:
        return
        
    async with AsyncSessionLocal() as session:
        # Preparamos la orden de inserción masiva
        stmt = insert(RawPost).values(posts_limpios)
        
        # Magia de Postgres: "Si este reddit_id ya existe, simplemente ignóralo"
        stmt = stmt.on_conflict_do_nothing(index_elements=['reddit_id'])
        
        # Ejecutamos la orden y confirmamos los cambios
        await session.execute(stmt)
        await session.commit()
        print(f"Guardados en la Base de Datos exitosamente.")

if __name__ == "__main__":
    subreddits_de_prueba = ["freelance", "startups", "SaaS"]
    asyncio.run(run_scraper(subreddits_de_prueba))




