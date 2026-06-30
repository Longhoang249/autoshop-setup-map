import urllib.request
import urllib.parse
import json
import ssl
import time

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
    ("177 Hồ Tùng Mậu, Hòa Minh, Liên Chiểu, Đà Nẵng", "T&K coffee"),
    ("Đường Phan Thái Ất, Nghĩa Lộ, Quảng Ngãi", "Trạm Kí Ức"),
    ("104 Lê Trọng Tấn, Hòa Phát, Cẩm Lệ, Đà Nẵng", "Mickey Trà Sữa"),
    ("Đường Trung Lập 2, Liên Chiểu, Đà Nẵng", "Cafe SOUL 1422")
]

for q, name in queries:
    res = get_coords(q)
    if res:
        print(f"{name} -> Lat: {res[0]}, Lng: {res[1]}, Address: {res[2]}")
    else:
        print(f"{name} -> FAILED to geocode")
    time.sleep(1.5)
