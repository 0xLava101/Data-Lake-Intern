# core/scrap_duckduck_go.py

from ddgs import DDGS

def duckduck_search(key_word,max_r):
    with DDGS() as ddgs:
        results = ddgs.images(key_word , max_results=max_r)
        images_urls = []

        for res in results:
            if res.get('image'):
                images_urls.append(res.get('image'))
    
    return images_urls