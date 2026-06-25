import httpx
import urllib.parse

async def try_fetch_hn(keyword: str) -> list:
    """
    Busca historias y comentarios en Hacker News relacionados con una keyword
    utilizando la API oficial de Algolia (sin auth).
    """
    # Buscamos 'story' y 'comment' que contengan la keyword, ordenados por relevancia
    encoded_keyword = urllib.parse.quote(keyword)
    url = f"http://hn.algolia.com/api/v1/search?query={encoded_keyword}&tags=(story,comment)&hitsPerPage=100"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            respuesta = await client.get(url)
            
            if respuesta.status_code != 200:
                print(f"Hacker News API Error: HTTP {respuesta.status_code}")
                return []
                
            data = respuesta.json()
            hits = data.get("hits", [])
            
            posts = []
            for hit in hits:
                # Extraer propiedades que varían si es historia o comentario
                title = hit.get("title") or hit.get("story_title") or ""
                body = hit.get("comment_text") or hit.get("story_text") or ""
                
                # Hacker News a veces devuelve posts vacíos de contenido
                if not title and not body:
                    continue
                    
                object_id = str(hit.get("objectID", ""))
                score = hit.get("points", 0) or 0
                num_comments = hit.get("num_comments", 0) or 0
                
                posts.append({
                    "source_id": f"hn_{object_id}",
                    "source_platform": "hackernews",
                    "source_community": keyword, # Usamos la keyword como "comunidad" para agrupar
                    "title": title,
                    "body": body,
                    "engagement_score": score,
                    "reply_count": num_comments,
                    "url": f"https://news.ycombinator.com/item?id={object_id}"
                })
                
            print(f"Hacker News: Encontrados {len(posts)} posts/comentarios para la keyword '{keyword}'.")
            return posts
            
    except Exception as e:
        print(f"Error al conectar con Hacker News API: {str(e)}")
        return []
