import urllib.request
import urllib.parse
import re
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def search_google(query):
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.google.com/search?q={query_encoded}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8')
            # Extract links containing google.com/maps/place or /maps/dir or similar
            links = re.findall(r'https?://(?:www\.)?google\.(?:com|com\.vn)/maps/(?:place|dir|search)/[^\s"\'&>]+', html)
            
            # Also search for googleusercontent to see if there is maps info
            cid_matches = re.findall(r'https?://maps\.google\.com/[^\s"\'&>]+', html)
            links.extend(cid_matches)
            
            # Check for closed signs
            is_closed = "đã đóng cửa" in html.lower() or "permanently closed" in html.lower() or "đóng cửa vĩnh viễn" in html.lower()
            return list(set(links)), is_closed
    except Exception as e:
        print(f"Error: {e}")
        return [], False

links, closed = search_google("NHÀ SÁCH HOÀNG YẾN Mê Linh google maps")
print("Links:", links)
print("Closed:", closed)
