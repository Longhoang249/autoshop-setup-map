import urllib.request
import urllib.parse
import re
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

WHITELIST_DOMAINS = [
    "fbcdn.net", "fbsbx.com", "googleusercontent.com", "foody.vn", "shopeefood.vn", "lozi.vn", "riviu.vn"
]

def is_whitelisted(url):
    url_lower = url.lower()
    for domain in WHITELIST_DOMAINS:
        if domain in url_lower:
            return True
    return False

def get_bing_images(query):
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.bing.com/images/search?q={query_encoded}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8')
            matches = re.findall(r'm="([^"]+)"', html)
            images = []
            for m in matches:
                m_clean = m.replace('&quot;', '"').replace('&amp;', '&')
                try:
                    data = json.loads(m_clean)
                    img_url = data.get('murl')
                    if img_url and img_url.startswith('http'):
                        images.append(img_url)
                except Exception:
                    img_match = re.search(r'"murl":"(.*?)"', m_clean)
                    if img_match and img_match.group(1).startswith('http'):
                        images.append(img_match.group(1))
            return images
    except Exception as e:
        print("Error:", e)
        return []

query = "Read Station Coffee & Tea Chùa Láng Hà Nội"
print(f"Searching for: {query}")
urls = get_bing_images(query)
print(f"Found {len(urls)} total URLs.")
whitelisted = [u for u in urls if is_whitelisted(u)]
print(f"Found {len(whitelisted)} whitelisted URLs:")
for u in whitelisted[:5]:
    print(" -", u)
