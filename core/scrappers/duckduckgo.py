# core/scrap_duckduck_go.py

from ddgs import DDGS
from core.scrappers.scrapper import Scrapper 


class DuckDuckGoScrapper(Scrapper):
    def get_images_urls(self,keyword: str, limit: int = 10) -> str :
        with DDGS() as ddgs:
            results = ddgs.images(keyword , max_results=limit)
            images_urls = []

            for res in results:
                if res.get('image'):
                    images_urls.append(res.get('image'))
        
        return images_urls