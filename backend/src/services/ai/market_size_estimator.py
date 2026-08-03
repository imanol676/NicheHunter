import asyncio
import os
import json
from duckduckgo_search import DDGS
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
    Busca reportes reales de tamaño de mercado (TAM) y CAGR en DuckDuckGo.
    Extrae únicamente datos cuantitativos verificables sin alucinaciones.
    """
    try:
        def sync_search():
            with DDGS() as ddgs:
                queries = [
                    f"{niche} market size report USD",
                    f"{problem_title} addressable market size CAGR"
                ]
                results = []
                for q in queries:
                    results.extend(list(ddgs.text(q, max_results=5)))
                return results
                
        raw_results = await asyncio.to_thread(sync_search)
        snippets = "\n".join([f"- {r.get('title')}: {r.get('body')} (Fuente: {r.get('href')})" for r in raw_results if r.get('body')])
    except Exception as e:
        print(f"Búsqueda de mercado no disponible: {e}")
        snippets = ""
    
    try:
        if not snippets:
            return {"market_size_tam": "Unverified in open sources", "market_growth_cagr": "N/A", "sources": []}

        prompt_sistema = """You are a Ruthless Financial Analyst. You will receive search engine snippets regarding a specific market.
Your job is to extract ONLY VERIFIED metrics: Total Addressable Market (TAM) in USD and Compound Annual Growth Rate (CAGR).

STRICT RULES:
1. Return EXACTLY a valid JSON object.
2. Provide short, concise formatting (e.g. "$4.5B" or "$120M").
3. For CAGR, provide the percentage (e.g. "12.5%").
4. CRITICAL: If the snippets DO NOT contain real market reports or quantitative figures, DO NOT invent numbers. Set "market_size_tam" to "Unverified in open sources" and "market_growth_cagr" to "N/A".
5. Extract the source URLs provided in the snippets and return them in a list under the key "sources".

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
            temperature=0.0
        )
        
        datos = json.loads(response.choices[0].message.content)
        return {
            "market_size_tam": datos.get("market_size_tam", "Unverified in open sources"),
            "market_growth_cagr": datos.get("market_growth_cagr", "N/A"),
            "sources": datos.get("sources", [])
        }
        
    except Exception as e:
        print(f"Error estimando tamaño de mercado para {niche}: {e}")
        return {"market_size_tam": "Unverified in open sources", "market_growth_cagr": "N/A", "sources": []}

