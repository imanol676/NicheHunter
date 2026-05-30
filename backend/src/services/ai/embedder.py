import os
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from sqlalchemy import select
from src.db.engine import AsyncSessionLocal
from src.models import PainPoint, RawPost

load_dotenv()


client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2023-05-15",
    azure_endpoint="https://nhunter.cognitiveservices.azure.com/"
)

async def generar_vector_azure(texto: str) -> list[float]:
    response = await client.embeddings.create(
        input=texto,
        model="text-embedding-3-large" 
    )
    return response.data[0].embedding

async def procesar_embeddings_pendientes(scan_job_id: str):
    print("Buscando Pain Points sin vector...")
    async with AsyncSessionLocal() as session:
        resultado = await session.execute(
            select(PainPoint)
            .join(RawPost, PainPoint.raw_post_id == RawPost.id)
            .filter(PainPoint.embedding == None)
            .filter(RawPost.scan_job_id == scan_job_id)
        )
        puntos_pendientes = resultado.scalars().all()
        
        print(f"Se encontraron {len(puntos_pendientes)} registros pendientes.")
        
        for punto in puntos_pendientes:
            print(f"Calculando matemáticas (3072 dimensiones) para el problema: '{punto.category}'...")
            vector = await generar_vector_azure(punto.description)
            punto.embedding = vector
            
        await session.commit()
        print("¡Vectores guardados exitosamente con Azure!")

if __name__ == "__main__":
    asyncio.run(procesar_embeddings_pendientes())
