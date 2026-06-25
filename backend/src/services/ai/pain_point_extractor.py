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
                "content": """You are a highly strict B2B Market Research Data Analyst. 
                Read the user's post and extract the main market pain point.
                CRITICAL RULES FOR EXTRACTION:
                1. Only extract REAL frictions, workflow bottlenecks, money leaks, or tedious manual tasks.
                2. REJECT (is_valid_pain_point: false) any aspirational desires or vague goals (e.g. "I want to make $100M", "I want more customers").
                3. REJECT general questions, news, self-promotion, or spam.
                4. REJECT personal anecdotes or one-off complaints that do NOT represent a systemic B2B market problem. We only want structural flaws.
                5. The severity score MUST be objective. Do NOT give an 8.0 to vague complaints. An 8.0+ means "If this is not solved, the business loses money or hours of time daily."
                
                IMPORTANT: YOU MUST respond ONLY with a valid JSON object using this exact structure and without any additional text. Write everything in English:
                {
                    "is_valid_pain_point": true or false,
                    "content": "summary of the specific actionable friction in 1 single sentence",
                    "category": "a keyword (e.g., finance, management, marketing, sales)",
                    "severity_score": a float from 1.0 to 10.0 evaluating how severe the actionable pain is,
                    "justification": "Brief 10-word reason why this severity score was given"
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

async def procesar_lote_de_posts(scan_job_id: str):
    print("Buscando posts sin analizar...")
    async with AsyncSessionLocal() as session:
        # Buscamos RawPosts que aún no tengan un PainPoint asociado (limitamos a 15 para evitar Rate Limits)
        resultado = await session.execute(
            select(RawPost)
            .outerjoin(PainPoint, RawPost.id == PainPoint.raw_post_id)
            .filter(PainPoint.id == None)
            .filter(RawPost.scan_job_id == scan_job_id)
            .limit(100)
        )
        posts_reales = resultado.scalars().all()
        
        for post in posts_reales:
            print(f"\nAnalizando post: {post.title[:50]}...")
            
            texto_completo = f"Título: {post.title}\nCuerpo: {post.body}"
            
            try:
                datos_ia = await prueba_llm_gratuito(texto_completo)
            except Exception as e:
                print(f" Error al extraer pain point: {e}")
                continue
            
            # Si el modelo determina que no hay dolor real (ej. es una pregunta genérica), descartamos el post
            if not datos_ia.get("is_valid_pain_point", True):
                print(f" Post descartado por la IA (No contiene un dolor real).")
                await session.delete(post)
                continue
                
         
            datos_ia['severity'] = float(datos_ia.get('severity_score', 5.0))
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

