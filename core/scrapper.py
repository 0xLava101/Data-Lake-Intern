# core/scrapper.py

import requests
from PIL import Image, UnidentifiedImageError
from io import BytesIO
from urllib.parse import urlparse


def load_blacklist(file_path="unallowed_domains.txt") -> set:
    try:
        with open(file_path, "r") as f:
            return set(line.strip().lower() for line in f if line.strip())
    except FileNotFoundError:
        return set()

BLACKLISTED_DOMAINS = load_blacklist()

def is_domain_allowed(url: str) -> bool:
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower().replace("www.", "")
        return domain not in BLACKLISTED_DOMAINS
    except Exception:
        return False


def download_image_in_memory(url, quality: int = 60) -> bytes | None:
    if not is_domain_allowed(url):
        return
    
    try:
        response = requests.get(
            url=url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36',
                'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            },
            timeout=10 
        )
    except requests.exceptions.RequestException:
        return None

    if response.status_code != 200:
        print(f"\n[-] Failed To Get Image : '{url}' \n")
        return None

    try:
        image = Image.open(BytesIO(response.content))
        image = image.convert("RGB")
    except UnidentifiedImageError:
        print(f"[-] Invalid image content at: '{url}' (Maybe text like 'Hello')")
        return None
    except Exception as e:
        print(f"[-] Error processing image from: '{url}'\n    Reason: {e}")
        return None

    buffer = BytesIO()
    image.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)
    image_bytes = buffer.getvalue()
    buffer.close()

    return image_bytes