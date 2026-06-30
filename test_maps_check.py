import urllib.request
import urllib.parse
import re
import ssl
import json
import time

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

def check_google_maps_status(name, address):
    query = f"{name} {address}"
    query_encoded = urllib.parse.quote(query)
    # Search Bing for the Google Maps link
    url = f"https://www.bing.com/search?q={query_encoded}+google+maps"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            html = response.read().decode('utf-8')
            
            # Look for Google Maps links in the HTML
            maps_links = re.findall(r'https?://(?:www\.)?google\.(?:com|com\.vn)/maps/(?:place|search)/[^\s"\'<>]+', html)
            
            # Check for indications of being closed (sập / đóng cửa)
            closed_indicators = ["đã đóng cửa", "permanently closed", "đóng cửa vĩnh viễn", "tạm thời đóng cửa"]
            is_closed = False
            for ind in closed_indicators:
                if ind in html.lower():
                    is_closed = True
                    break
                    
            return {
                "query": query,
                "maps_links": list(set(maps_links))[:3],
                "is_closed": is_closed
            }
    except Exception as e:
        return {"error": str(e)}

test_shops = [
    ("NHÀ SÁCH HOÀNG YẾN", "thị trấn Chi Đông, Mê Linh, Hà Nội"),
    ("HÒA CA CAFE", "31 ngõ 279 P. Giảng Võ, Chợ Dừa, Đống Đa, Hà Nội"),
    ("LEE CHLOE COFFEE", "Số D34-14, Khu đô thị Geleximco D, Lê Trọng Tấn, Hà Đông, Hà Nội")
]

for name, addr in test_shops:
    res = check_google_maps_status(name, addr)
    print(f"\nShop: {name}")
    print(json.dumps(res, indent=2, ensure_ascii=False))
    time.sleep(2)
