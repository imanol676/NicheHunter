import asyncio
import numpy as np
from sklearn.cluster import AgglomerativeClustering

from sqlalchemy import select
from src.db.engine import AsyncSessionLocal
from src.models import PainPoint, PainPointCluster

async def agrupar_pain_points():
    print("Buscando Pain Points sin agrupar...")
    async with AsyncSessionLocal() as session:
        resultado = await session.execute(select(PainPoint).filter(PainPoint.cluster_id == None))
        puntos = resultado.scalars().all()
        
        if not puntos:
            print("No hay puntos nuevos para agrupar.")
            return
            
        print(f"Agrupando {len(puntos)} Pain Points...")
        
        
        vectores = [punto.embedding for punto in puntos]
        matriz_vectores = np.array(vectores)
        

        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=0.3, 
            metric='cosine',
            linkage='average'
        )
        
      
        etiquetas = clustering.fit_predict(matriz_vectores)
        

        grupos = {}
        for i, etiqueta_cluster in enumerate(etiquetas):
            if etiqueta_cluster not in grupos:
                grupos[etiqueta_cluster] = []
            grupos[etiqueta_cluster].append(puntos[i])
            
        print(f"¡Se descubrieron {len(grupos)} problemas únicos (Clusters)!\n")
        
        # Guardamos cada cluster en la base de datos
        for id_grupo, puntos_del_grupo in grupos.items():
            print(f"Cluster #{id_grupo} contiene {len(puntos_del_grupo)} quejas.")
            
            # Calculamos el "Centroide" (El vector promedio de todo el grupo)
            vectores_del_grupo = [p.embedding for p in puntos_del_grupo]
            centroide = np.mean(vectores_del_grupo, axis=0).tolist()
            
            # Creamos el cluster
            nuevo_cluster = PainPointCluster(
                size=len(puntos_del_grupo),
                centroid=centroide,
                label=puntos_del_grupo[0].category # Por ahora le ponemos la categoría del primero
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