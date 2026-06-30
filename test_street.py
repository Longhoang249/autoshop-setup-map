import urllib.request
import urllib.parse
import json
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'AutoshopSetupNewShopVerifier/2.0 (long2492000@gmail.com)'
}

def get_coords(query):
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data:
                return float(data[0]['lat']), float(data[0]['lon']), data[0]['display_name']
    except Exception as e:
        print(f"Error geocoding '{query}': {e}")
    return None

queries = [
    "Đường Hồ Tùng Mậu, Liên Chiểu, Đà Nẵng",
    "Phan Thái Ất, Nghĩa Lộ, Quảng Ngãi",
    "Đường Lê Trọng Tấn, Cẩm Lệ, Đà Nẵng",
    "Đường Trung Lập 2, Liên Chiểu, Đà Nẵng"
]

for q in queries:
    res = get_coords(q)
    if res:
        print(f"{q} -> Lat: {res[0]}, Lng: {res[1]}, Display: {res[2]}")
    else:
        print(f"{q} -> FAILED")
