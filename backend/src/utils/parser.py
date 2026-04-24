def parse_reddit_posts(raw_json: dict) -> list:
    posts_limpios = []
    
    # 1. Acceder a la lista de posts en el JSON original
    posts_crudos = raw_json.get("data", {}).get("children", [])
    
    for item in posts_crudos:
        post_data = item.get("data", {})
        
        # Ignorar posts que están pegados por los administradores (opcional pero recomendado)
        if post_data.get("stickied"):
            continue
            
        # 2. Extraer solo lo que nos importa
        post_limpio = {
            "reddit_id": post_data.get("id"),
            "subreddit": post_data.get("subreddit"),
            "title": post_data.get("title"),
            "body": post_data.get("selftext"),
            "score": post_data.get("score"),
            "num_comments": post_data.get("num_comments"),

            "url": f"https://www.reddit.com{post_data.get('permalink')}" 
        }
        posts_limpios.append(post_limpio)
        
    return posts_limpios
