import asyncio
import os
import json
from ddgs import DDGS
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("GPT4O_ENDPOINT")
)

async def estimate_market_size(niche: str, problem_title: str) -> dict:
    """
    Busca reportes de tamaño de mercado (TAM) y CAGR en DuckDuckGo.
    Luego usa GPT-4o para extraer y formatear los números exactos.
    """
    try:
        # 1. Buscar snippets web sobre el mercado
        def sync_search():
            with DDGS() as ddgs:
                # Usamos términos clave de investigación B2B
                queries = [
                    f"{niche} market size report USD",
                    f"{problem_title} total addressable market CAGR"
                ]
                results = []
                for q in queries:
                    results.extend(list(ddgs.text(q, max_results=5)))
                return results
                
        raw_results = await asyncio.to_thread(sync_search)
        snippets = "\n".join([f"- {r.get('title')}: {r.get('body')} (Source: {r.get('href')})" for r in raw_results if r.get('body')])
    except Exception as e:
        print(f"Error con DuckDuckGo (probablemente rate limit): {e}")
        snippets = ""
    
    try:
        if not snippets:
            snippets = "[SYSTEM: No real-time search data available due to rate limits. YOU MUST estimate the TAM and CAGR based on your training data for this niche. ALWAYS output a realistic estimate with an asterisk *]."

        # 2. Usar LLM para extraer el TAM y CAGR
        prompt_sistema = """You are a Financial Analyst. You will receive search engine snippets regarding a specific market.
Your job is to extract the estimated Total Addressable Market (TAM) in USD and the Compound Annual Growth Rate (CAGR).

STRICT RULES:
1. Return EXACTLY a valid JSON object.
2. Provide short, concise formatting (e.g. "$4.5B" or "$120M").
3. For CAGR, provide the percentage (e.g. "12.5%").
4. If the data is completely absent in the snippets, estimate a realistic B2B market size based on the niche (but label it with an asterisk * to indicate it's an AI estimate).
5. Extract the source URLs provided in the snippets and return them in a list under the key "sources". If it's an AI estimate without sources, return an empty list.

Output format:
{
    "market_size_tam": "$4.5B",
    "market_growth_cagr": "12.5%",
    "sources": ["https://example.com/report1"]
}"""

        prompt_usuario = f"Market: {niche}\nProblem: {problem_title}\n\nSearch Snippets:\n{snippets}"

        response = await client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "gpt-4o"),
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": prompt_sistema},
                {"role": "user", "content": prompt_usuario}
            ],
            temperature=0.1
        )
        
        datos = json.loads(response.choices[0].message.content)
        return {
            "market_size_tam": datos.get("market_size_tam", "Unknown"),
            "market_growth_cagr": datos.get("market_growth_cagr", "Unknown"),
            "sources": datos.get("sources", [])
        }
        
    except Exception as e:
        print(f"Error estimando tamaño de mercado para {niche}: {e}")
        return {"market_size_tam": "Data Unavailable", "market_growth_cagr": "N/A", "sources": []}
