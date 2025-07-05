import requests
import urllib.parse
from duckduckgo_search import DDGS

'''def search_duckduckgo_image(celebrity_name: str) -> str:
    query = urllib.parse.quote(celebrity_name)
    url = f"https://duckduckgo.com/?q={query}&iax=images&ia=images"
    
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    script = soup.find("script", string=lambda t: t and "vqd=" in t)
    if not script:
        raise RuntimeError("Could not find vqd token for image search.")

    vqd = script.text.split("vqd='")[1].split("'")[0]

    # Fetch image results
    image_api = f"https://duckduckgo.com/i.js?l=us-en&o=json&q={query}&vqd={vqd}&f=,,,&p=1"
    headers = {"User-Agent": "Mozilla/5.0"}
    image_res = requests.get(image_api, headers=headers)
    image_data = image_res.json()

    for result in image_data.get("results", []):
        if result.get("image"):
            print(result["image"])
            return result["image"]

    raise ValueError("No image found.")

def search_duckduckgo_image(celebrity_name: str) -> str:
    with DDGS() as ddgs:
        results = ddgs.images(celebrity_name, max_results=5)
        for r in results:
            if r.get("image"):
                print(r["image"])
                return r["image"]
    raise ValueError("No suitable image found.")'''

def is_valid_image_url(url: str) -> bool:
    """Check if URL is reachable and points to an actual image."""
    try:
        r = requests.head(url, allow_redirects=True, timeout=5)
        content_type = r.headers.get("Content-Type", "")
        return (
            r.status_code == 200
            and content_type.startswith("image/")
            and not url.lower().endswith((".svg", ".gif"))  # optional: block SVGs/GIFs
        )
    except requests.RequestException:
        return False


def looks_bad(title: str) -> bool:
    """Filter out obviously bad images based on title/alt/keywords."""
    bad_keywords = [
        "statue",
        "drawing",
        "fan art",
        "sculpture",
        "figure",
        "cartoon",
        "poster",
        "logo",
        "shirt",
        "toy",
        "doll",
        "video",
    ]
    return any(word in title.lower() for word in bad_keywords)


def search_valid_celebrity_image(celebrity_name: str, max_attempts: int = 10) -> str:
    """Search and return a valid portrait image URL of the celebrity."""
    with DDGS() as ddgs:
        results = ddgs.images(celebrity_name, max_results=max_attempts)
        for result in results:
            title = result.get("title", "")
            image_url = result.get("image", "")
            if not image_url:
                continue
            if looks_bad(title):
                continue
            if is_valid_image_url(image_url):
                return image_url
    raise ValueError(f"No valid image found for {celebrity_name}")


'''def get_celebrity_image_url(celebrity_name, lang="en"):
    """
    Search Wikipedia for the celebrity and return a direct URL to their infobox thumbnail image.
    
    Parameters:
    - celebrity_name (str): Name of the celebrity (English or Persian).
    - lang (str): 'en' for English Wikipedia, 'fa' for Persian.

    Returns:
    - str or None: Image URL or None if not found.
    """
    try:
        # Wikipedia language-specific API
        base_url = f"https://{lang}.wikipedia.org/w/api.php"

        # Step 1: Search for the page title
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": celebrity_name,
        }
        response = requests.get(base_url, params=search_params)
        response.raise_for_status()
        results = response.json().get("query", {}).get("search", [])

        if not results:
            print(1)
            return None

        # Get best matching page title
        page_title = results[0]["title"]

        # Step 2: Get thumbnail image from that page
        image_params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "titles": page_title,
            "pithumbsize": 600
        }
        response = requests.get(base_url, params=image_params)
        response.raise_for_status()
        pages = response.json()["query"]["pages"]

        for page in pages.values():
            print(page)
            if "thumbnail" in page:
                print(page["thumbnail"]["source"])
                return page["thumbnail"]["source"]

        return None

    except Exception as e:
        print(f"[❌ Wikipedia Error] {e}")
        return None'''
    

def get_celebrity_image_url(celebrity_name, lang="en"):
    """
    Try to get the Wikipedia infobox image for a celebrity.
    Attempts exact match first, then fallback to search.
    """
    try:
        base_url = f"https://{lang}.wikipedia.org/w/api.php"

        # First try exact page match
        image_params = {
            "action": "query",
            "format": "json",
            "prop": "pageimages",
            "titles": celebrity_name,
            "pithumbsize": 600
        }
        response = requests.get(base_url, params=image_params)
        response.raise_for_status()
        pages = response.json().get("query", {}).get("pages", {})

        for page in pages.values():
            if "thumbnail" in page:
                return page["thumbnail"]["source"]

        # Fallback: Fuzzy search to find better title
        search_params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": celebrity_name,
        }
        response = requests.get(base_url, params=search_params)
        response.raise_for_status()
        results = response.json().get("query", {}).get("search", [])
        if not results:
            return None

        best_title = results[0]["title"]

        # Try again with best title
        image_params["titles"] = best_title
        response = requests.get(base_url, params=image_params)
        response.raise_for_status()
        pages = response.json()["query"]["pages"]
        for page in pages.values():
            if "thumbnail" in page:
                return page["thumbnail"]["source"]

        return None

    except Exception as e:
        print(f"[❌ Wikipedia Error] {e}")
        return None
