import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def search_ddg(query):
    query_encoded = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={query_encoded}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8')
            # Extract links containing google.com/maps
            links = re.findall(r'https?://(?:www\.)?google\.(?:com|com\.vn)/maps/[^\s"\'&>]+', html)
            # Find any raw maps links or search queries
            cleaned_links = []
            for l in links:
                # Clean URL decoding
                l_decoded = urllib.parse.unquote(l)
                if 'place' in l_decoded or 'cid=' in l_decoded:
                    cleaned_links.append(l_decoded)
            return list(set(cleaned_links)), "đóng cửa" in html.lower() or "closed" in html.lower()
    except Exception as e:
        print(f"Error: {e}")
        return [], False

links, closed = search_ddg("NHÀ SÁCH HOÀNG YẾN Mê Linh Hà Nội google maps")
print("Links:", links)
print("Closed:", closed)
