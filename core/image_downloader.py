# core/scrapper.py

import requests
from urllib.parse import urlparse

from PIL import Image, UnidentifiedImageError
from io import BytesIO

from configs import Allowed_Image_Formates
from utils.logger import Logger

logger = Logger().set_logger()


def load_blacklist(file_path="blacklist_domains.txt") -> set:
    try:
        with open(file_path, "r") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        logger.warning("Faild To Find File 'blacklist_domains.txt'")
        return set()

BLACKLISTED_DOMAINS = load_blacklist()


class ImageDownloader:
    @staticmethod
    def is_domain_allowed(url: str) -> bool:
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower().replace("www.", "")
            return domain not in BLACKLISTED_DOMAINS
        except Exception:
            return False
    
    @staticmethod
    def check_response_content_type(response):
        return response.headers.get("Content-Type", "").startswith("image/")

    def download_image_in_memory(self, url , quality: int = 60) -> bytes | None:
        if not ImageDownloader.is_domain_allowed(url):
            logger.info(f"Unallowed Domain In Url : '{url}'")
            return None

        try:
            response = requests.get(
                url=url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                },
                timeout=10 
            )

            if response.status_code != 200:
                logger.error(f"\nFailed To Get Image : '{url}' | Request Status Code : {response.status_code}\n")
                return None
        
        except requests.exceptions.RequestException:
            return None
        
        if not ImageDownloader.check_response_content_type(response):
            logger.warning(f"Unsupported Content-Type : '{url}'")
            return None
        
        try:

            image = Image.open(BytesIO(response.content))

            if image.format.lower() not in Allowed_Image_Formates : 
                logger.warning(f"Unsupported Image Format : '{url}' | '{image.format.lower()}'")
                return None
            
            image = image.convert("RGB")

        except UnidentifiedImageError:
            logger.error(f"Invalid image content at : '{url}' (Maybe text like 'Hello')")
            return None
        except Exception as e:
            logger.error(f"Error processing image from: '{url}'\n    Reason: {e}")
            return None
        
        buffer = BytesIO()

        image.save(buffer, format='JPEG', quality=quality, optimize=True)
        buffer.seek(0)
        image_bytes = buffer.getvalue()
        buffer.close()

        return image_bytes
    
    @staticmethod
    def very_simple_test(url):
        if not ImageDownloader.is_domain_allowed(url):
            return None
        
        try : 
            response = requests.get(
                url=url,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                    'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
                },
                timeout=10 
            )

            if response.status_code != 200:
                return None
        
        except requests.exceptions.RequestException:
            return None
        
        if not ImageDownloader.check_response_content_type(response):
            return None
        
        return True