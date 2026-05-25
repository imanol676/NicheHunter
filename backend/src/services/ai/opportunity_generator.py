import os
import json
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from src.db.engine import AsyncSessionLocal
from src.models import PainPointCluster, Opportunity

load_dotenv()

# Cliente de Azure OpenAI
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01", # Versión más reciente de la API de Chat
    azure_endpoint=os.getenv("GPT4O_ENDPOINT")
)

async def generar_oportunidad_negocio(resumen_cluster: str, tamaño_cluster: int) -> dict:
    prompt_sistema = """Eres un estratega de negocios y Analista de Startups de primer nivel.
Tu trabajo es leer resúmenes de quejas de usuarios (Pain Points) y diseñar la oportunidad de negocio más adecuada y rentable para resolver ese problema específico (puede ser un SaaS, una agencia de servicios, un producto físico, una plataforma de intermediación, info-producto, etc).

IMPORTANTE: DEBES responder ÚNICAMENTE con un objeto JSON válido con esta estructura exacta y sin texto adicional:
{
    "title": "Nombre atractivo de la idea de negocio",
    "problem_statement": "Explicación clara del problema que sufren los usuarios (2-3 oraciones)",
    "market_analysis": "Análisis de por qué este es un buen mercado para entrar",
    "proposed_solutions": "Descripción de la solución propuesta (software, servicio, producto, etc.)",
    "monetization_ideas": "El mejor modelo de negocio y estrategias de cómo cobrar por esto (suscripción, pago único, comisiones por venta, consultoría, etc)",
    "competitive_landscape": "Análisis rápido de la posible competencia o alternativas actuales",
    "opportunity_score": un numero del 1.0 al 10.0 evaluando el potencial financiero del proyecto,
    "difficulty": "Una palabra: Baja, Media, o Alta",
    "strategies": ["Estrategia de entrada 1", "Estrategia 2"]
}"""

    prompt_usuario = f"He encontrado un clúster de {tamaño_cluster} quejas similares. Aquí tienes un resumen del problema principal que están teniendo:\n{resumen_cluster}"

    response = await client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"), # Nombre de tu deployment en Azure
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

async def procesar_nuevas_oportunidades():
    print("Buscando Clústeres sin Oportunidad de Negocio generada...")
    async with AsyncSessionLocal() as session:
        # Buscamos clusters que aún no tienen oportunidades asociadas
        # Usamos un LEFT OUTER JOIN implícito al buscar clusters donde no haya id en opportunities
        resultado = await session.execute(
            select(PainPointCluster)
            .outerjoin(Opportunity, PainPointCluster.id == Opportunity.cluster_id)
            .filter(Opportunity.id == None)
        )
        clusters_pendientes = resultado.scalars().all()
        
        if not clusters_pendientes:
            print("No hay clústeres nuevos para analizar.")
            return

        print(f"Se encontraron {len(clusters_pendientes)} clústeres listos para análisis.")
        
        for cluster in clusters_pendientes:
            print(f"\n Analizando Clúster de tamaño {cluster.size}: '{cluster.label}'...")
            
            # Usamos el label como resumen base. Si tuviéramos más datos, los sumaríamos aquí.
            resumen = cluster.label 
            
            try:
                datos_ia = await generar_oportunidad_negocio(resumen, cluster.size)
                
                nueva_oportunidad = Opportunity(
                    cluster_id=cluster.id,
                    title=datos_ia.get("title"),
                    problem_statement=datos_ia.get("problem_statement"),
                    market_analysis=datos_ia.get("market_analysis"),
                    proposed_solutions=datos_ia.get("proposed_solutions"),
                    monetization_ideas=datos_ia.get("monetization_ideas"),
                    competitive_landscape=datos_ia.get("competitive_landscape"),
                    opportunity_score=float(datos_ia.get("opportunity_score", 5.0)),
                    difficulty=datos_ia.get("difficulty"),
                    strategies=datos_ia.get("strategies")
                )
                
                session.add(nueva_oportunidad)
                print(f" Oportunidad Generada: {nueva_oportunidad.title} (Score: {nueva_oportunidad.opportunity_score})")
            except Exception as e:
                print(f" Error al procesar cluster {cluster.id}: {e}")
            
        await session.commit()
        print("\n ¡Análisis de oportunidades guardado exitosamente!")

if __name__ == "__main__":
    asyncio.run(procesar_nuevas_oportunidades())
