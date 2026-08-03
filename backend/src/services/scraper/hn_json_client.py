import httpx
import urllib.parse
import asyncio

async def try_fetch_hn(keyword: str, max_pages: int = 3) -> list:
    """
    Busca historias y comentarios en Hacker News relacionados con una keyword
    utilizando la API oficial de Algolia (100% Gratuita) con paginación de hasta max_pages.
    """
    encoded_keyword = urllib.parse.quote(keyword)
    all_posts = []
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            for page in range(max_pages):
                url = f"http://hn.algolia.com/api/v1/search?query={encoded_keyword}&tags=(story,comment)&page={page}&hitsPerPage=50"
                respuesta = await client.get(url)
                
                if respuesta.status_code != 200:
                    print(f"Hacker News API Error (página {page}): HTTP {respuesta.status_code}")
                    break
                    
                data = respuesta.json()
                hits = data.get("hits", [])
                
                if not hits:
                    break
                    
                for hit in hits:
                    title = hit.get("title") or hit.get("story_title") or ""
                    body = hit.get("comment_text") or hit.get("story_text") or ""
                    
                    if not title and not body:
                        continue
                        
                    object_id = str(hit.get("objectID", ""))
                    score = hit.get("points", 0) or 0
                    num_comments = hit.get("num_comments", 0) or 0
                    
                    all_posts.append({
                        "source_id": f"hn_{object_id}",
                        "source_platform": "hackernews",
                        "source_community": keyword,
                        "title": title,
                        "body": body,
                        "engagement_score": score,
                        "reply_count": num_comments,
                        "url": f"https://news.ycombinator.com/item?id={object_id}"
                    })
                    
                if page < max_pages - 1:
                    await asyncio.sleep(0.5)
                    
            print(f"Hacker News: Encontrados {len(all_posts)} posts/comentarios en {max_pages} páginas para la keyword '{keyword}'.")
            return all_posts
            
    except Exception as e:
        print(f"Error al conectar con Hacker News API: {str(e)}")
        return all_posts

