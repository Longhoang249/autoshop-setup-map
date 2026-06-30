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

def debug_bing(query):
    query_encoded = urllib.parse.quote(query)
    url = f"https://www.bing.com/search?q={query_encoded}"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8')
            print("HTML Length:", len(html))
            
            # Find all links starting with http/https
            links = re.findall(r'href="([^"]+)"', html)
            print("Total href links:", len(links))
            
            # Search for any link that contains 'google' or 'map'
            matches = [l for l in links if 'google' in l or 'map' in l]
            print("Matches containing 'google' or 'map':", matches[:15])
    except Exception as e:
        print("Error:", e)

debug_bing("NHÀ SÁCH HOÀNG YẾN Mê Linh google maps")
