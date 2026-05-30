import os
import json
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.db.engine import AsyncSessionLocal
from src.models import PainPointCluster, Opportunity, PainPoint, RawPost

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
    "proposed_solutions": "Descripción de la solución propuesta. Evita el 'SaaS Mágico con IA' si hay formas más simples de resolverlo.",
    "monetization_ideas": "El mejor modelo de negocio y estrategias de cómo cobrar por esto (suscripción, pago único, comisiones por venta, consultoría, etc)",
    "competitive_landscape": "Análisis rápido de la posible competencia o alternativas actuales",
    "opportunity_score": "Un número decimal del 1.0 al 10.0. SÉ DESPIADADO. Usa todo el rango (ej. 3.2, 5.5, 7.1). La mayoría de ideas son promedio (4.0 - 6.0). NO abuses del 8.0 o 8.5.",
    "difficulty": "Una palabra: Baja, Media, o Alta",
    "strategies": ["Estrategia 1", "MVP No-Code: Validar cobrando entrada a un grupo privado de WhatsApp o usando Airtable"],
    "sentiment": "Un resumen del sentimiento (ej. Frustración, Enojo, Desesperación)",
    "urgency": "Una palabra: Baja, Media, Alta, o Crítica. SÉ ESTRICTO: La mayoría son Baja/Media. Usa Alta/Crítica solo si hay pérdida de dinero o estrés severo.",
    "willingness_to_pay": "Una palabra: Baja, Media, o Alta. SÉ REALISTA: La mayoría de la gente no quiere pagar por soluciones triviales.",
    "temporal_trends": "Breve análisis de si es un problema en crecimiento, estacional o constante",
    "emerging_niches": "Subnichos específicos que sufren esto particularmente"
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

async def procesar_nuevas_oportunidades(scan_job_id: str):
    print("Buscando Clústeres sin Oportunidad de Negocio generada...")
    async with AsyncSessionLocal() as session:
        # Buscamos clusters que aún no tienen oportunidades asociadas
        # Usamos un LEFT OUTER JOIN implícito al buscar clusters donde no haya id en opportunities
        resultado = await session.execute(
            select(PainPointCluster)
            .outerjoin(Opportunity, PainPointCluster.id == Opportunity.cluster_id)
            .filter(Opportunity.id == None)
            .filter(PainPointCluster.scan_job_id == scan_job_id)
        )
        clusters_pendientes = resultado.scalars().all()
        
        if not clusters_pendientes:
            print("No hay clústeres nuevos para analizar.")
            return

        print(f"Se encontraron {len(clusters_pendientes)} clústeres listos para análisis.")
        
        for cluster in clusters_pendientes:
            print(f"\n Analizando Clúster de tamaño {cluster.size}: '{cluster.label}'...")
            
            prompt_sistema = """Eres un consultor de negocios senior evaluando ideas para emprendedores.
Tu objetivo es analizar un problema y proponer un negocio realista, evitando el síndrome del 'SaaS mágico que todo lo resuelve con IA'. 
CRÍTICO: En tu lista de 'strategies' (Estrategias de entrada), DEBES incluir siempre una estrategia de 'MVP No-Code / Low-Cost'. Por ejemplo: 'MVP: Grupo de WhatsApp de pago', 'MVP: Formulario de Airtable automatizado con Make', o 'MVP: Consultoría manual'. Esto es para que el usuario valide la idea antes de gastar meses programando.
"""
            # Recuperar las descripciones reales de las quejas para darle contexto a GPT-4o
            resultado_puntos = await session.execute(
                select(PainPoint.description)
                .filter(PainPoint.cluster_id == cluster.id)
            )
            descripciones = resultado_puntos.scalars().all()
            
            resumen_quejas = "\n".join([f"- {desc}" for desc in descripciones])
            resumen = f"Categoría general: {cluster.label}\nQuejas específicas:\n{resumen_quejas}"
            
            try:
                datos_ia = await generar_oportunidad_negocio(resumen, cluster.size)
                
                # Obtener los enlaces originales de Reddit
                resultado_urls = await session.execute(
                    select(RawPost.url)
                    .join(PainPoint, PainPoint.raw_post_id == RawPost.id)
                    .filter(PainPoint.cluster_id == cluster.id)
                )
                urls_unicas = list(set(resultado_urls.scalars().all()))
                
                # Obtener la suma total de upvotes
                resultado_upvotes = await session.execute(
                    select(func.sum(RawPost.score))
                    .join(PainPoint, PainPoint.raw_post_id == RawPost.id)
                    .filter(PainPoint.cluster_id == cluster.id)
                )
                total_upvotes = resultado_upvotes.scalar() or 0
                
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
                    strategies=datos_ia.get("strategies"),
                    post_count=cluster.size,
                    total_upvotes=total_upvotes,
                    sentiment=datos_ia.get("sentiment"),
                    urgency=datos_ia.get("urgency"),
                    willingness_to_pay=datos_ia.get("willingness_to_pay"),
                    temporal_trends=datos_ia.get("temporal_trends"),
                    emerging_niches=datos_ia.get("emerging_niches"),
                    reddit_links=urls_unicas
                )
                
                session.add(nueva_oportunidad)
                print(f" Oportunidad Generada: {nueva_oportunidad.title} (Score: {nueva_oportunidad.opportunity_score})")
            except Exception as e:
                print(f" Error al procesar cluster {cluster.id}: {e}")
            
        await session.commit()
        print("\n ¡Análisis de oportunidades guardado exitosamente!")

if __name__ == "__main__":
    asyncio.run(procesar_nuevas_oportunidades())
