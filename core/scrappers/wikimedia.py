# core/wikimedia.py

import requests

from core.scrappers.scrapper import Scrapper
from utils.logger import Logger 


logger = Logger().set_logger()


class WikimediaScrapper(Scrapper):
    @staticmethod
    def get_urls_from_response(res):
        pages = res.json().get("query", {}).get("pages", {})
        urls = [info["imageinfo"][0]["url"] for info in pages.values() if "imageinfo" in info]

        return urls
    
    def get_images_urls(self,keyword: str, limit: int = 10) -> list[str]:
        url = "https://commons.wikimedia.org/w/api.php"
        urls = []
        batch_size = 500
        
        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": keyword,
            "gsrlimit": min(limit,batch_size),
            "gsrnamespace":6 ,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }
        
        while True: 
            try:
                res = requests.get(url, params=params, timeout=10,headers={
                    "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
                })
                res.raise_for_status()
                res_json = res.json()
            except Exception as e:
                logger.error(f"Error To Fatch Data From Wikimedia : '{e}'")
                return []
            
            urls.extend(WikimediaScrapper.get_urls_from_response(res))

            if len(urls) >= limit:
                urls = urls[:limit]
                break

            if "continue" in res_json:
                for key, value in res_json["continue"].items():
                    if key != "continue":
                        params[key] = value
            else : 
                break
            
        return urls