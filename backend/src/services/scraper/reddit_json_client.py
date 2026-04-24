import httpx
import asyncio 
from src.utils.parser import parse_reddit_posts
from src.services.scraper.user_agents import get_random_headers




async def try_fetch_reddit(subreddit: str) -> dict:
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=20"
    
    async with httpx.AsyncClient(headers=get_random_headers(), timeout=5.0) as client:
        respuesta = await client.get(url)
        return parse_reddit_posts(respuesta.json())
    


