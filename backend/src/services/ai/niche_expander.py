import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

async def expandir_nicho_a_subreddits(niche: str) -> list[str]:
    """
    Toma un nicho (ej. 'inmobiliarias', 'startups') y devuelve una lista de 
    hasta 3 subreddits de Reddit altamente relevantes en inglés.
    """
    prompt_sistema = """Eres un experto en inteligencia de mercado y conocedor profundo de Reddit.
Tu objetivo es tomar una palabra clave o nicho proporcionado por el usuario y determinar los mejores foros (subreddits) en inglés donde este público objetivo se reúne a quejarse, hacer preguntas técnicas o hablar de sus problemas diarios.

REGLAS ESTRICTAS:
1. Debes devolver EXACTAMENTE un objeto JSON. Nada más.
2. El JSON debe tener una propiedad llamada "subreddits" que sea una lista de strings.
3. La lista NO DEBE TENER MÁS DE 3 subreddits. Escoge solo los 3 más relevantes.
4. Devuelve SOLO el nombre del subreddit, sin el prefijo "r/" (ej. "realtors", no "r/realtors").
5. Asegúrate de que los subreddits existan y sean activos.
6. ENFOQUE B2B (IMPORTANTE): Si el nicho es una industria o negocio (ej. "restaurantes", "inmobiliarias"), asegúrate de devolver foros de DUEÑOS, FUNDADORES o PROFESIONALES de la industria (ej. "restaurateur", "restaurantowners") y NUNCA foros de consumidores (ej. NO uses "Cooking" ni "food").

Ejemplo de salida:
{
    "subreddits": ["realestate", "realtors", "RealEstateInvesting"]
}
"""

    prompt_usuario = f"El usuario quiere analizar el siguiente nicho o mercado: '{niche}'. Devuélveme los 3 subreddits en inglés más importantes."

    try:
        response = await client.chat.completions.create(
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"}, 
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.1
        )
        
        texto_crudo = response.choices[0].message.content
        diccionario = json.loads(texto_crudo)
        
        subreddits = diccionario.get("subreddits", [])
        
        # Validación de seguridad: Asegurarnos de que no pasen de 3 y sean strings
        subreddits_limpios = [str(sub).strip().lower().replace("r/", "") for sub in subreddits][:3]
        
        if not subreddits_limpios:
            # Fallback en caso de que la IA se rompa
            return [niche.replace(" ", "").lower()]
            
        return subreddits_limpios
        
    except Exception as e:
        print(f"Error al expandir nicho con Groq: {e}")
        # Fallback de seguridad al comportamiento original MVP
        return [niche.replace(" ", "").lower()]
