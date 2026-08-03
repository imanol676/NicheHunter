import asyncio
from duckduckgo_search import DDGS
from datetime import datetime, timezone

async def try_fetch_b2b_reviews(query: str, site: str) -> list[dict]:
    """
    Usa DuckDuckGo para buscar fragmentos (snippets) de reseñas en sitios específicos (g2, capterra, trustpilot, producthunt, linkedin).
    """
    results = []
    try:
        def sync_search():
            with DDGS() as ddgs:
                search_query = f"site:{site} {query}"
                return list(ddgs.text(search_query, max_results=20))
                
        raw_results = await asyncio.to_thread(sync_search)
        
        if not raw_results:
            return []
            
        for idx, res in enumerate(raw_results):
            body = res.get("body", "")
            title = res.get("title", "")
            url = res.get("href", "")
            
            if not body or len(body) < 15:
                continue
                
            source_id = f"b2b_{site.replace('.', '_').replace('/', '_')}_{abs(hash(url)) % 100000000}_{idx}"
            
            platform_name = "b2b_web"
            if "g2.com" in site:
                platform_name = "g2"
            elif "capterra.com" in site:
                platform_name = "capterra"
            elif "trustpilot.com" in site:
                platform_name = "trustpilot"
            elif "producthunt.com" in site:
                platform_name = "producthunt"
            elif "linkedin.com" in site:
                platform_name = "linkedin"
                
            post_dict = {
                "source_id": source_id,
                "title": title[:500],
                "body": body,
                "top_comments": "",
                "url": url,
                "source_platform": platform_name,
                "source_community": "b2b_review",
                "engagement_score": 1,
                "reply_count": 0,
                "source_created_at": datetime.now(timezone.utc).replace(tzinfo=None)
            }
            results.append(post_dict)
            
    except Exception as e:
        print(f"Error extrayendo datos B2B de {site} para '{query}': {e}")
        
    return results

async def fetch_all_b2b_channels(keyword: str) -> list[dict]:
    """
    Busca la keyword en los canales principales B2B (G2, Capterra, Trustpilot, ProductHunt, LinkedIn).
    """
    sites = ["g2.com", "capterra.com", "trustpilot.com", "producthunt.com", "linkedin.com/posts"]
    all_posts = []
    
    for site in sites:
        print(f"  -> Buscando en {site}...")
        posts = await try_fetch_b2b_reviews(keyword, site)
        all_posts.extend(posts)
        await asyncio.sleep(1.2)
        
    return all_posts

