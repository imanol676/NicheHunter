import os
import json
import asyncio
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from src.db.engine import AsyncSessionLocal
from src.models import PainPointCluster, ValidationReport, PainPoint, RawPost

load_dotenv()

client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("GPT4O_ENDPOINT")
)

async def generar_reporte_validacion(resumen_cluster: str, tamaño_cluster: int, niche: str, total_upvotes: int, total_comments: int, cohesion: float) -> dict:
    prompt_sistema = f"""You are a skeptical B2B Market Analyst evaluating user complaints in the industry: '{niche}'.
Your job is to critically analyze these complaints and generate a Market Validation Report.

YOU MUST respond ONLY with a valid JSON object using this exact structure and without any additional text. Write all output content in English:
{{
    "report_title": "Concise name of the problem space (e.g. Dental Clinic Payroll Bottleneck)",
    "friction_summary": "Executive summary of the real bottleneck",
    "cost_of_inaction": "What does the company lose if they don't fix it? (Money, hours, churn)",
    "audience_profile": "Exact profile of the decision maker (e.g. CFO, HR Manager)",
    "existing_alternatives": "How are they solving it now? (e.g. Excel, manual integrations)",
    "competitor_gaps": "Why existing solutions are failing",
    "trend_velocity": "Is it a growing problem or stagnant?",
    "risk_profile": "Distribution, technical or adoption risks",
    "willingness_to_pay": "Low, Medium, or High. Briefly justify.",
    "validation_verdict": "Strong Buy, Hold, or Pass. Final recommendation on market entry."
}}"""

    prompt_usuario = f"I have found a cluster of {tamaño_cluster} similar complaints. In total they sum {total_upvotes} upvotes and {total_comments} comments. Cluster cohesion: {cohesion:.2f}. Problem summary:\n{resumen_cluster}"

    response = await client.chat.completions.create(
        model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"),
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt_sistema},
            {"role": "user", "content": prompt_usuario}
        ]
    )
    
    return json.loads(response.choices[0].message.content)

async def procesar_oportunidad_individual(cluster_id: str, niche: str):
    print(f"Generando reporte para el Clúster {cluster_id}...")
    async with AsyncSessionLocal() as session:
        cluster = await session.get(PainPointCluster, cluster_id)
        if not cluster:
            print("Cluster no encontrado.")
            return None

        resultado = await session.execute(
            select(ValidationReport).where(ValidationReport.cluster_id == cluster.id)
        )
        existing_opp = resultado.scalars().first()
        if existing_opp:
            print("El cluster ya tiene un reporte generado.")
            return existing_opp

        resultado_puntos = await session.execute(
            select(PainPoint.description).filter(PainPoint.cluster_id == cluster.id)
        )
        descripciones = resultado_puntos.scalars().all()
        
        resumen_quejas = "\n".join([f"- {desc}" for desc in descripciones])
        resumen = f"General category: {cluster.label}\nSpecific complaints:\n{resumen_quejas}"
        
        try:
            resultado_upvotes = await session.execute(
                select(func.sum(RawPost.engagement_score))
                .join(PainPoint, PainPoint.raw_post_id == RawPost.id)
                .filter(PainPoint.cluster_id == cluster.id)
            )
            total_upvotes = resultado_upvotes.scalar() or 0
            
            resultado_comments = await session.execute(
                select(func.sum(RawPost.reply_count))
                .join(PainPoint, PainPoint.raw_post_id == RawPost.id)
                .filter(PainPoint.cluster_id == cluster.id)
            )
            total_comments = resultado_comments.scalar() or 0
            
            datos_ia = await generar_reporte_validacion(resumen, cluster.size, niche, total_upvotes, total_comments, getattr(cluster, 'cluster_cohesion', 1.0))
            
            resultado_urls = await session.execute(
                select(RawPost.url)
                .join(PainPoint, PainPoint.raw_post_id == RawPost.id)
                .filter(PainPoint.cluster_id == cluster.id)
            )
            urls_unicas = list(set(resultado_urls.scalars().all()))
            
            nuevo_reporte = ValidationReport(
                cluster_id=cluster.id,
                report_title=datos_ia.get("report_title"),
                friction_summary=datos_ia.get("friction_summary"),
                cost_of_inaction=datos_ia.get("cost_of_inaction"),
                audience_profile=datos_ia.get("audience_profile"),
                existing_alternatives=datos_ia.get("existing_alternatives"),
                competitor_gaps=datos_ia.get("competitor_gaps"),
                trend_velocity=datos_ia.get("trend_velocity"),
                risk_profile=datos_ia.get("risk_profile"),
                willingness_to_pay=datos_ia.get("willingness_to_pay"),
                validation_verdict=datos_ia.get("validation_verdict"),
                post_count=cluster.size,
                total_upvotes=total_upvotes,
                total_comments=total_comments,
                source_links=urls_unicas
            )
            
            session.add(nuevo_reporte)
            await session.commit()
            print(f"Reporte Generado: {nuevo_reporte.report_title}")
            return nuevo_reporte
        except Exception as e:
            print(f"Error al procesar cluster {cluster.id}: {e}")
            return None
