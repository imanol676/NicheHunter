import httpx
import urllib.parse
import os
from dotenv import load_dotenv

load_dotenv()

async def try_fetch_youtube(query: str) -> list:
    """
    Busca videos de YouTube por una keyword, y luego extrae los top comentarios de esos videos.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    if not api_key:
        print("YouTube API Key no configurada en .env")
        return []
        
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=id,snippet&q={encoded_query}&type=video&maxResults=5&key={api_key}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # 1. Buscar los top 5 videos para la consulta
            search_response = await client.get(search_url)
            if search_response.status_code != 200:
                print(f"YouTube Search API Error: HTTP {search_response.status_code}")
                return []
                
            search_data = search_response.json()
            videos = search_data.get("items", [])
            
            posts = []
            
            # 2. Para cada video, obtener el top 20 de comentarios
            for video in videos:
                video_id = video.get("id", {}).get("videoId")
                video_title = video.get("snippet", {}).get("title", "")
                
                if not video_id:
                    continue
                    
                comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults=20&order=relevance&key={api_key}"
                
                comments_response = await client.get(comments_url)
                if comments_response.status_code != 200:
                    # Es posible que los comentarios estén desactivados para este video (403 Forbidden)
                    continue
                    
                comments_data = comments_response.json()
                threads = comments_data.get("items", [])
                
                for thread in threads:
                    comment_snippet = thread.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                    
                    comment_id = thread.get("id")
                    body = comment_snippet.get("textDisplay", "")
                    score = comment_snippet.get("likeCount", 0)
                    
                    # YouTube comments HTML sometimes needs mild stripping, but raw is okay for MVP
                    posts.append({
                        "source_id": f"yt_{comment_id}",
                        "source_platform": "youtube",
                        "source_community": query, # Usamos la query de búsqueda
                        "title": f"Comment on: {video_title[:50]}...", # El comentario no tiene título, usamos el del video
                        "body": body,
                        "engagement_score": score,
                        "reply_count": thread.get("snippet", {}).get("totalReplyCount", 0),
                        "url": f"https://www.youtube.com/watch?v={video_id}&lc={comment_id}"
                    })
                    
            print(f"YouTube: Encontrados {len(posts)} comentarios en top videos para '{query}'.")
            return posts
            
    except Exception as e:
        print(f"Error al conectar con YouTube API: {str(e)}")
        return []
