import urllib.request
import urllib.parse
import re
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def ddg_image_search(query):
    # Use DuckDuckGo HTML search or a public API if possible
    # We can fetch DuckDuckGo's main page or use their instant answer API
    query_encoded = urllib.parse.quote(query)
    # DuckDuckGo's vqd token is needed for their image API.
    # Let's try retrieving it from the main search page
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8')
            # For images, let's search Google Images instead because it has cleaner public HTML or use a public free proxy
            return html[:500]
    except Exception as e:
        return str(e)

print(ddg_image_search("MM CF & TEA 1A6 Khu tập thể ĐHNN"))
