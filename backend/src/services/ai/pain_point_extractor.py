import os
import asyncio
import json
from openai import AsyncOpenAI, RateLimitError
from dotenv import load_dotenv
from sqlalchemy import select
from src.db.engine import AsyncSessionLocal
from src.models import RawPost, PainPoint


load_dotenv()


client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
    max_retries=5
)


async def prueba_llm_gratuito(texto_del_post: str, max_intentos: int = 4):
    # Truncar el texto del post para mantener el consumo de tokens bajo control (~250-300 tokens por llamada)
    texto_recortado = texto_del_post[:1200]
    
    for intento in range(max_intentos):
        try:
            response = await client.chat.completions.create(
                model="llama-3.1-8b-instant",
                response_format={"type": "json_object"}, 
                messages=[
                    {
                        "role": "system", 
                        "content": """You are a highly strict, ruthless B2B Market Research Data Analyst. 
                        Read the user's post and extract the main market pain point.
                        CRITICAL RULES FOR EXTRACTION:
                        1. Only extract REAL frictions, software limitations, workflow bottlenecks, money leaks, or tedious manual tasks.
                        2. REJECT (is_valid_pain_point: false) any inspirational quotes, "thought leadership", general life advice, or motivational posts (e.g., "People leave managers, not jobs").
                        3. REJECT aspirational desires or vague goals (e.g. "I want to make $100M", "I want more customers").
                        4. REJECT general questions, news, self-promotion, or spam.
                        5. REJECT personal anecdotes or complaints that do NOT represent a systemic B2B market problem. We only want structural, software, or process flaws.
                        6. The severity score MUST be objective. Do NOT give an 8.0 to vague complaints. An 8.0+ means "If this software/process is not fixed, the business loses money or hours of time daily."
                        
                        If the post does not complain about a specific tool, workflow, or business process, it is NOT a valid pain point. Set "is_valid_pain_point" to false.

                        IMPORTANT: YOU MUST respond ONLY with a valid JSON object using this exact structure and without any additional text. Write everything in English:
                        {
                            "is_valid_pain_point": true or false,
                            "content": "summary of the specific actionable friction in 1 single sentence",
                            "category": "a keyword (e.g., finance, management, marketing, sales)",
                            "severity_score": a float from 1.0 to 10.0 evaluating how severe the actionable pain is,
                            "confidence_score": a float from 0.0 to 1.0 representing how confident you are that this is a real B2B software/process problem,
                            "justification": "Brief 10-word reason why this severity score was given"
                        }"""
                    },
                    {"role": "user", "content": texto_recortado}
                ],
                temperature=0.1
            )
            
            texto_crudo = response.choices[0].message.content
            return json.loads(texto_crudo)
            
        except RateLimitError as rle:
            print(f"  [429 Rate Limit Groq] Esperando 6 segundos para reiniciar ventana de TPM (Intento {intento+1}/{max_intentos})...")
            await asyncio.sleep(6.0)
        except Exception as e:
            if "429" in str(e) or "rate_limit" in str(e).lower():
                print(f"  [429 Rate Limit Groq] Esperando 6 segundos (Intento {intento+1}/{max_intentos})...")
                await asyncio.sleep(6.0)
            else:
                raise e
                
    # Si después de los reintentos falla por Rate Limit, devolvemos respuesta vacía en vez de crash
    return {"is_valid_pain_point": False}


# Procesamiento en lote de posts:

async def procesar_lote_de_posts(scan_job_id: str, status_callback=None):
    print(f"Iniciando procesamiento iterativo de todas las publicaciones para el escaneo {scan_job_id}...")
    total_procesados = 0
    chunk_size = 25
    
    while True:
        async with AsyncSessionLocal() as session:
            resultado = await session.execute(
                select(RawPost)
                .outerjoin(PainPoint, RawPost.id == PainPoint.raw_post_id)
                .filter(PainPoint.id == None)
                .filter(RawPost.scan_job_id == scan_job_id)
                .limit(chunk_size)
            )
            posts_lote = resultado.scalars().all()
            
            if not posts_lote:
                print(f"✅ Procesamiento completado. Total de posts analizados: {total_procesados}")
                break
                
            print(f"\n--- Procesando lote de {len(posts_lote)} posts (Total hasta ahora: {total_procesados}) ---")
            if status_callback:
                status_callback(f"Extrayendo quejas con IA (Procesados {total_procesados} posts)...")
            
            for post in posts_lote:
                texto_completo = f"Título: {post.title}\nCuerpo: {post.body}"
                
                try:
                    datos_ia = await prueba_llm_gratuito(texto_completo)
                except Exception as e:
                    print(f" Error al extraer pain point: {e}")
                    await asyncio.sleep(2.0)
                    continue
                
                # Pausa estratégica entre llamadas para no saturar 6000 TPM de Groq
                await asyncio.sleep(2.0)
                
                # Si el modelo determina que no hay dolor real, descartamos el post
                if not datos_ia.get("is_valid_pain_point", True):
                    await session.delete(post)
                    continue
                    
                datos_ia['severity'] = float(datos_ia.get('severity_score', 5.0))
                datos_ia['confidence_score'] = float(datos_ia.get('confidence_score', 0.7))
                datos_ia['metadata'] = {}

                nuevo_pain_point = PainPoint(
                    raw_post_id=post.id,
                    description=datos_ia.get("content"),
                    category=datos_ia.get("category"),
                    severity=str(datos_ia.get("severity")),
                    confidence_score=datos_ia.get("confidence_score"),
                    metadata=datos_ia.get("metadata")
                )
                session.add(nuevo_pain_point)
                total_procesados += 1
                
            await session.commit()
            print(f"Lote de {len(posts_lote)} guardado exitosamente. Pausa de cortesía para la API de Groq...")
            await asyncio.sleep(2.0)


if __name__ == "__main__":
    asyncio.run(procesar_lote_de_posts())


