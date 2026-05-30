import httpx
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")

async def try_fetch_reddit(subreddit: str) -> list:
    # Usamos old.reddit.com porque su HTML es increíblemente ligero y fácil de parsear
    # Obtenemos el "Top del Año" para encontrar dolores altamente frecuentes
    target_url = f"https://old.reddit.com/r/{subreddit}/top/?sort=top&t=year"
    url = f"http://api.scraperapi.com?api_key={SCRAPER_API_KEY}&url={target_url}&premium=true"
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            respuesta = await client.get(url)
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
                    "reddit_id": reddit_id,
                    "subreddit": subreddit,
                    "title": title,
                    "body": "", # El body no está disponible en la vista de lista
                    "score": score,
                    "num_comments": num_comments,
                    "url": f"https://www.reddit.com{permalink}"
                })
            
            print(f"ScraperAPI HTML Parsing: Encontrados {len(posts)} posts limpios en old.reddit.com")
            return posts
    except Exception as e:
        print(f"Error de red o proxy al conectar con Reddit HTML: {str(e)}")
        return []
