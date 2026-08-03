import os
import json
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

async def expand_niche_to_sources(niche: str, competitors: list[str] = None) -> dict:
    if competitors is None:
        competitors = []
        
    """
    Toma un nicho y devuelve un plan de extracción multiplataforma.
    """
    prompt_sistema = """You are an expert in market intelligence.
Your objective is to take a keyword or niche provided by the user and determine the best online sources to find pain points, complaints, and technical questions.

STRICT RULES:
1. Return EXACTLY a valid JSON object. Nothing else.
2. The JSON must have the following lists of strings: "reddit_communities", "hackernews_keywords", "youtube_search_queries", "b2b_search_keywords".
3. Each list MUST NOT HAVE MORE THAN 5 items.
4. For Reddit, return ONLY the subreddit name (no "r/").
5. For Hacker News, return specific search keywords (e.g., "freelance clients", "upwork alternative").
6. For YouTube, return specific video search queries where tutorials or reviews for this niche exist (e.g., "how to use quickbooks", "real estate agent day in life").
7. B2B FOCUS: Always target professionals, owners, and founders, not consumers.
8. For "b2b_search_keywords", generate highly targeted queries for finding bad software reviews by including the software category and keywords like "cons" or "complaints" (e.g., "real estate CRM cons", "payroll software complaints").

Output example:
{
    "reddit_communities": ["realestate", "realtors", "RealEstateInvesting"],
    "hackernews_keywords": ["real estate software", "proptech", "realtor CRM"],
    "youtube_search_queries": ["how to start real estate agency", "best CRM for realtors"],
    "b2b_search_keywords": ["real estate CRM cons", "property management software complaints"]
}
"""

    prompt_usuario = f"The user wants to analyze the following niche or market: '{niche}'. Return the top extraction sources."

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
        
        # Clean up and expand limits to 10 per source
        reddit = [str(sub).strip().lower().replace("r/", "") for sub in diccionario.get("reddit_communities", [])][:10]
        hn = [str(k).strip().lower() for k in diccionario.get("hackernews_keywords", [])][:10]
        youtube = [str(q).strip().lower() for q in diccionario.get("youtube_search_queries", [])][:10]
        b2b = [str(b).strip().lower() for b in diccionario.get("b2b_search_keywords", [])][:10]
        
        # Inject competitor queries if provided
        for comp in competitors:
            b2b.append(f"{comp} reviews cons")
            b2b.append(f"{comp} alternatives complaints")
            
        b2b = b2b[:12]
        
        if not reddit and not hn and not youtube and not b2b:
            return {"reddit_communities": [niche.replace(" ", "").lower()], "hackernews_keywords": [niche], "youtube_search_queries": [niche], "b2b_search_keywords": [niche + " cons"]}
            
        return {
            "reddit_communities": reddit,
            "hackernews_keywords": hn,
            "youtube_search_queries": youtube,
            "b2b_search_keywords": b2b
        }
        
    except Exception as e:
        print(f"Error al expandir nicho con Groq: {e}")
        return {"reddit_communities": [niche.replace(" ", "").lower()], "hackernews_keywords": [niche], "youtube_search_queries": [niche]}


