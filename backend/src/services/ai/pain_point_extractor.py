import os
import asyncio
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv
from sqlalchemy import select
from src.db.engine import AsyncSessionLocal
from src.models import RawPost, PainPoint


load_dotenv()


client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)


async def prueba_llm_gratuito(texto_del_post: str):
    response = await client.chat.completions.create(
        model="llama-3.1-8b-instant",
        response_format={"type": "json_object"}, 
        messages=[
            {
                "role": "system", 
                "content": """Eres un sistema backend automatizado de análisis de datos. 
                Lee la queja del usuario y extrae el dolor de mercado (pain point) principal.
                IMPORTANTE: DEBES responder ÚNICAMENTE con un objeto JSON válido con esta estructura exacta y sin texto adicional:
                {
                    "content": "resumen del problema principal en 1 sola oración",
                    "category": "una palabra clave (ej: finanzas, gestion, marketing, ventas)",
                    "severity_score": un numero del 1.0 al 10.0 evaluando qué tan grave es el dolor
                }"""
            },
            {"role": "user", "content": texto_del_post}
        ]
    )
    
    # Extraemos el texto de la IA y lo convertimos a un Diccionario Real de Python
    texto_crudo = response.choices[0].message.content
    diccionario_limpio = json.loads(texto_crudo) 
    
    return diccionario_limpio


#Procesamiento en lote de posts:

async def procesar_lote_de_posts():
    print("Conectando a la base de datos...")
    async with AsyncSessionLocal() as session:
        
        resultado = await session.execute(select(RawPost).limit(3))
        posts_reales = resultado.scalars().all()
        
        for post in posts_reales:
            print(f"\nAnalizando post: {post.title[:50]}...")
            
           
            texto_completo = f"Título: {post.title}\nCuerpo: {post.body}"
            
           
            datos_ia = await prueba_llm_gratuito(texto_completo)
            
         
            datos_ia['severity'] = float(datos_ia['severity_score'])
            datos_ia['confidence_score'] = float(datos_ia.get('confidence_score', 0.7))
            datos_ia['metadata'] = {}

           
            nuevo_pain_point = PainPoint(
                raw_post_id=post.id,
                description=datos_ia.get("content"),
                category=datos_ia.get("category"),
                severity=str(datos_ia.get("severity")) ,
                confidence_score=datos_ia.get("confidence_score"),
                metadata=datos_ia.get("metadata")
            )

            
            
            # Lo añadimos a la sesión
            session.add(nuevo_pain_point)
            print(f" Pain Point extraído: {datos_ia.get('category')}")
            
       
        await session.commit()
        print("\n ¡Lote de Pain Points guardado exitosamente!")

if __name__ == "__main__":
    asyncio.run(procesar_lote_de_posts())

