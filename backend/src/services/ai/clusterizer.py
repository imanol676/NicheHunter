import asyncio
import numpy as np
from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import cosine

from sqlalchemy import select
from src.db.engine import AsyncSessionLocal
from src.models import PainPoint, PainPointCluster, RawPost

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
            clustering = AgglomerativeClustering(
                n_clusters=None,
                distance_threshold=0.75, 
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
            print(f"Cluster #{id_grupo} contiene {len(puntos_del_grupo)} quejas.")
            
            # Calculamos el "Centroide" (El vector promedio de todo el grupo)
            vectores_del_grupo = [p.embedding for p in puntos_del_grupo]
            centroide = np.mean(vectores_del_grupo, axis=0).tolist()
            
            # Calculamos la "Cohesión" (Similitud promedio al centroide)
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
            
            # Generar un resumen rápido con el primer pain point
            resumen_rapido = puntos_del_grupo[0].description
            
            # Creamos el cluster
            nuevo_cluster = PainPointCluster(
                scan_job_id=scan_job_id,
                size=len(puntos_del_grupo),
                centroid=centroide,
                cluster_cohesion=cohesion,
                label=puntos_del_grupo[0].category, # Por ahora le ponemos la categoría del primero
                avg_severity_score=avg_severity,
                summary=resumen_rapido
            )
            session.add(nuevo_cluster)
            await session.flush() # Para obtener el ID generado sin hacer commit aún
            
            # Actualizamos cada Pain Point para enlazarlo a su nuevo "padre" (el Cluster)
            for p in puntos_del_grupo:
                p.cluster_id = nuevo_cluster.id
                
        # Confirmamos los cambios en Postgres
        await session.commit()
        print("\n✅ ¡Agrupación (Clustering) guardada exitosamente!")

if __name__ == "__main__":
    asyncio.run(agrupar_pain_points())