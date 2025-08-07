# core/wikimedia.py

import requests

def get_images(keyword: str, limit: int = 10) -> list[str]:
    url = "https://commons.wikimedia.org/w/api.php"
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": keyword,
        "gsrlimit": limit,
        "gsrnamespace":6 ,
        "prop": "imageinfo",
        "iiprop": "url",
        "format": "json"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        res.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching from Wikimedia: {e}")
        return []

    pages = res.json().get("query", {}).get("pages", {})
    urls = [info["imageinfo"][0]["url"] for info in pages.values() if "imageinfo" in info]

    return urls