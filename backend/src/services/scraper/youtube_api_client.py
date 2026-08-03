import httpx
import urllib.parse
import os
import re
from dotenv import load_dotenv
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound

load_dotenv()

def extract_video_id(url_or_id: str) -> str:
    if len(url_or_id) == 11 and not " " in url_or_id:
        return url_or_id
    match = re.search(r"(?:v=|\/)([0-9A-Za-z_-]{11})", url_or_id)
    return match.group(1) if match else ""

async def try_fetch_youtube_transcripts(video_ids_with_titles: list[dict]) -> list[dict]:
    """
    Extrae la transcripción hablada de videos de YouTube usando youtube-transcript-api (100% Gratis, sin API Key).
    """
    posts = []
    yt_api = YouTubeTranscriptApi()
    
    for item in video_ids_with_titles:
        v_id = item.get("video_id")
        v_title = item.get("title", "YouTube Video")
        if not v_id:
            continue
            
        try:
            # Obtener transcripción en inglés o español
            fetched = yt_api.fetch(v_id, languages=['en', 'es'])
            full_text = " ".join([snippet.text for snippet in fetched])
            
            if len(full_text) > 100:
                posts.append({
                    "source_id": f"yt_transcript_{v_id}",
                    "source_platform": "youtube_transcript",
                    "source_community": item.get("query", "youtube"),
                    "title": f"Transcripción de Video: {v_title[:80]}",
                    "body": full_text[:4000], # Limitar tamaño para el LLM
                    "engagement_score": 10,
                    "reply_count": 0,
                    "url": f"https://www.youtube.com/watch?v={v_id}"
                })
                print(f"  └─ Transcripción obtenida exitosamente para: {v_title[:40]}...")
        except (TranscriptsDisabled, NoTranscriptFound):
            pass
        except Exception as e:
            print(f"  └─ No se pudo obtener transcripción para {v_id}: {e}")
            
    return posts

async def try_fetch_youtube(query: str) -> list:
    """
    Busca videos de YouTube y extrae comentarios + transcripciones habladas.
    Funciona con o sin YOUTUBE_API_KEY.
    """
    api_key = os.getenv("YOUTUBE_API_KEY")
    posts = []
    
    if not api_key:
        print("YouTube API Key no configurada. Usando búsqueda web abierta para transcripciones...")
        # Búsqueda abierta por DuckDuckGo para encontrar IDs de videos de YouTube relevantes
        try:
            from duckduckgo_search import DDGS
            import asyncio
            
            def search_yt_videos():
                with DDGS() as ddgs:
                    results = list(ddgs.text(f"site:youtube.com {query} review cons complaints", max_results=5))
                    return results

                    
            raw_results = await asyncio.to_thread(search_yt_videos)
            video_items = []
            for r in raw_results:
                v_id = extract_video_id(r.get("href", ""))
                if v_id:
                    video_items.append({"video_id": v_id, "title": r.get("title", ""), "query": query})
                    
            transcript_posts = await try_fetch_youtube_transcripts(video_items)
            return transcript_posts
        except Exception as e:
            print(f"Error en fallback abierto de YouTube: {e}")
            return []

    # Si hay API Key oficial
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.googleapis.com/youtube/v3/search?part=id,snippet&q={encoded_query}&type=video&maxResults=5&key={api_key}"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            search_response = await client.get(search_url)
            if search_response.status_code != 200:
                print(f"YouTube Search API Error: HTTP {search_response.status_code}")
                return []
                
            search_data = search_response.json()
            videos = search_data.get("items", [])
            video_items = []
            
            for video in videos:
                v_id = video.get("id", {}).get("videoId")
                v_title = video.get("snippet", {}).get("title", "")
                if v_id:
                    video_items.append({"video_id": v_id, "title": v_title, "query": query})
                    
                # Extraer comentarios vía API key
                comments_url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={v_id}&maxResults=15&order=relevance&key={api_key}"
                comments_response = await client.get(comments_url)
                if comments_response.status_code == 200:
                    comments_data = comments_response.json()
                    for thread in comments_data.get("items", []):
                        comment_snippet = thread.get("snippet", {}).get("topLevelComment", {}).get("snippet", {})
                        comment_id = thread.get("id")
                        body = comment_snippet.get("textDisplay", "")
                        score = comment_snippet.get("likeCount", 0)
                        
                        posts.append({
                            "source_id": f"yt_{comment_id}",
                            "source_platform": "youtube",
                            "source_community": query,
                            "title": f"Comentario en: {v_title[:50]}...",
                            "body": body,
                            "engagement_score": score,
                            "reply_count": thread.get("snippet", {}).get("totalReplyCount", 0),
                            "url": f"https://www.youtube.com/watch?v={v_id}&lc={comment_id}"
                        })
            
            # Obtener transcripciones habladas para estos videos
            transcript_posts = await try_fetch_youtube_transcripts(video_items)
            posts.extend(transcript_posts)
            
            print(f"YouTube: Encontrados {len(posts)} comentarios y transcripciones para '{query}'.")
            return posts
            
    except Exception as e:
        print(f"Error al conectar con YouTube API: {str(e)}")
        return posts

