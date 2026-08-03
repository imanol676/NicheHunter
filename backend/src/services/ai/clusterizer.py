import os
import json
import asyncio
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import cosine
from openai import AsyncOpenAI
from dotenv import load_dotenv

from sqlalchemy import select
from src.db.engine import AsyncSessionLocal
from src.models import PainPoint, PainPointCluster, RawPost

load_dotenv()

groq_client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

async def sintetizar_etiqueta_cluster(descripciones: list[str]) -> str:
    """
    Usa Groq Llama-3.1-8b para resumir un grupo de quejas similares en un título semántico y profesional (ej. 'Conciliación manual ineficiente de facturas').
    """
    if not descripciones:
        return "Problema General de Mercado"
        
    muestras = "\n".join([f"- {d}" for d in descripciones[:7]])
    
    try:
        response = await groq_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "system",
                    "content": "You are a B2B SaaS Product Strategist. Summarize the following list of customer complaints into ONE concise, professional problem title in English (3 to 6 words max). Do not use quotes or introductory text."
                },
                {
                    "role": "user",
                    "content": f"Customer Complaints:\n{muestras}"
                }
            ],
            max_tokens=25,
            temperature=0.2
        )
        titulo = response.choices[0].message.content.strip().replace('"', '')
        return titulo if titulo else descripciones[0][:50]
    except Exception as e:
        print(f"Error al sintetizar etiqueta con Groq: {e}")
        return descripciones[0][:50]

async def agrupar_pain_points(scan_job_id: str):
    print("Buscando Pain Points sin agrupar...")
    async with AsyncSessionLocal() as session:
        resultado = await session.execute(
            select(PainPoint)
            .join(RawPost, PainPoint.raw_post_id == RawPost.id)
            .filter(PainPoint.cluster_id == None)
            .filter(RawPost.scan_job_id == scan_job_id)
        )
        puntos = resultado.scalars().all()
        
        if not puntos:
            print("No hay puntos nuevos para agrupar.")
            return
            
        puntos_validos = [p for p in puntos if p.embedding is not None and hasattr(p.embedding, '__len__') and len(p.embedding) > 0]
        
        if not puntos_validos:
            print("No hay puntos con embeddings válidos para agrupar.")
            return
            
        print(f"Agrupando {len(puntos_validos)} Pain Points válidos...")
        
        vectores = [punto.embedding for punto in puntos_validos]
        matriz_vectores = np.array(vectores)
        
        if len(puntos_validos) == 1:
            etiquetas = [0]
        else:
            # Umbral adaptativo: Si hay muchos puntos, usamos un threshold más estricto
            threshold = 0.65 if len(puntos_validos) > 30 else 0.75
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=threshold, 
                metric='cosine',
                linkage='average'
            )
            etiquetas = clustering.fit_predict(matriz_vectores)

        grupos = {}
        for i, etiqueta_cluster in enumerate(etiquetas):
            if etiqueta_cluster not in grupos:
                grupos[etiqueta_cluster] = []
            grupos[etiqueta_cluster].append(puntos_validos[i])
            
        print(f"¡Se descubrieron {len(grupos)} problemas únicos (Clusters)!\n")
        
        # Guardamos cada cluster en la base de datos
        for id_grupo, puntos_del_grupo in grupos.items():
            print(f"Sintetizando Cluster #{id_grupo} ({len(puntos_del_grupo)} quejas)...")
            
            # Calculamos el Centroide (Vector promedio)
            vectores_del_grupo = [p.embedding for p in puntos_del_grupo]
            centroide = np.mean(vectores_del_grupo, axis=0).tolist()
            
            # Calculamos la Cohesión
            if len(puntos_del_grupo) <= 1:
                cohesion = 1.0
            else:
                similitudes = [1 - cosine(v, centroide) for v in vectores_del_grupo]
                cohesion = float(np.mean(similitudes))
                
            # Calcular severidad promedio
            severidades = []
            for p in puntos_del_grupo:
                try:
                    severidades.append(float(p.severity))
                except:
                    severidades.append(5.0)
            avg_severity = sum(severidades) / len(severidades)
            
            # Sintetizar etiqueta profesional usando IA con Groq
            descripciones_grupo = [p.description for p in puntos_del_grupo if p.description]
            etiqueta_semantica = await sintetizar_etiqueta_cluster(descripciones_grupo)
            
            # Resumen rápido del grupo
            resumen_rapido = f"Cluster of {len(puntos_del_grupo)} complaints regarding {etiqueta_semantica}. Primary friction: {descripciones_grupo[0] if descripciones_grupo else 'N/A'}"
            
            nuevo_cluster = PainPointCluster(
                scan_job_id=scan_job_id,
                size=len(puntos_del_grupo),
                centroid=centroide,
                cluster_cohesion=cohesion,
                label=etiqueta_semantica,
                avg_severity_score=avg_severity,
                summary=resumen_rapido
            )
            session.add(nuevo_cluster)
            await session.flush()
            
            for p in puntos_del_grupo:
                p.cluster_id = nuevo_cluster.id
                
        await session.commit()
        print("\n✅ ¡Agrupación (Clustering) semántica guardada exitosamente!")

if __name__ == "__main__":
    asyncio.run(agrupar_pain_points())