import httpx
import random
import asyncio
from bs4 import BeautifulSoup

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36"
]

async def try_fetch_reddit(subreddit: str) -> list:
    # Usamos old.reddit.com porque su HTML es increíblemente ligero y fácil de parsear
    # Obtenemos el "Top de Todos los Tiempos" para encontrar los dolores más grandes de la historia del sub
    url = f"https://old.reddit.com/r/{subreddit}/top/?sort=top&t=all&limit=150"
    
    headers = {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            respuesta = await client.get(url, headers=headers)
            
            if respuesta.status_code == 429:
                print(f"Reddit Rate Limit (429) en r/{subreddit}. Esperando 10 segundos antes de reintentar...")
                await asyncio.sleep(10)
                respuesta = await client.get(url, headers=headers)

            if respuesta.status_code != 200:
                print(f"Reddit API Error: HTTP {respuesta.status_code} - {respuesta.text[:100]}")
                return []
            
            html_content = respuesta.text
            soup = BeautifulSoup(html_content, "html.parser")
            posts = []
            
            # Buscar todos los contenedores de posts
            for thing in soup.select("div.thing"):
                # Ignorar anuncios
                if "promoted" in thing.get("class", []):
                    continue
                
                # Extraer Título
                title_elem = thing.select_one("a.title")
                if not title_elem:
                    continue
                title = title_elem.text.strip()
                
                # Extraer Puntuación (Upvotes)
                score_elem = thing.select_one("div.score.unvoted")
                score = 0
                if score_elem:
                    title_attr = score_elem.get("title", "")
                    if title_attr and title_attr.isdigit():
                        score = int(title_attr)
                    elif score_elem.text.strip().isdigit():
                        score = int(score_elem.text.strip())
                        
                # Extraer Número de Comentarios
                comments_elem = thing.select_one("a.bylink.comments")
                num_comments = 0
                if comments_elem:
                    comments_text = comments_elem.text.strip().split(" ")[0]
                    if comments_text.isdigit():
                        num_comments = int(comments_text)
                        
                # Extraer Metadata
                permalink = thing.get("data-permalink", "")
                reddit_id = thing.get("data-fullname", "")
                
                # Para un MVP, el Título + Metadata suele ser suficiente si no podemos acceder al JSON.
                posts.append({
                    "source_id": reddit_id,
                    "source_platform": "reddit",
                    "source_community": subreddit,
                    "title": title,
                    "body": "", # El body no está disponible en la vista de lista
                    "engagement_score": score,
                    "reply_count": num_comments,
                    "url": f"https://www.reddit.com{permalink}"
                })
            
            print(f"Artesanal HTML Parsing: Encontrados {len(posts)} posts limpios en r/{subreddit} usando User-Agent rotativo.")
            return posts
    except Exception as e:
        print(f"Error de red o proxy al conectar con Reddit HTML: {str(e)}")
        return []
