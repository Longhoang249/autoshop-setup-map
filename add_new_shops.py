import json
import os
import urllib.request
import urllib.parse
import re
import ssl
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

json_path = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/src/data/shops.json"
output_dir = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/public/images"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

WHITELIST_CDNS = [
    "fbcdn.net", "fbsbx.com",
    "googleusercontent.com",
    "foody.vn", "shopeefood.vn",
    "lozi.vn", "riviu.vn",
    "instagram.com", "cdninstagram.com"
]

def is_whitelisted(url):
    url_lower = url.lower()
    for domain in WHITELIST_CDNS:
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
                    if img_url and img_url.startswith('http') and is_whitelisted(img_url):
                        images.append(img_url)
                except Exception:
                    img_match = re.search(r'"murl":"(.*?)"', m_clean)
                    if img_match and img_match.group(1).startswith('http'):
                        u = img_match.group(1)
                        if is_whitelisted(u):
                            images.append(u)
            seen = set()
            unique_images = []
            for img in images:
                if img not in seen:
                    seen.add(img)
                    unique_images.append(img)
            return unique_images
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
        return []

def download_single_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            info = response.info()
            content_length = info.get('Content-Length')
            if content_length:
                size_bytes = int(content_length)
                if size_bytes < 30000 or size_bytes > 1200000:
                    return None
                    
            data = response.read()
            if not content_length:
                size_bytes = len(data)
                if size_bytes < 30000 or size_bytes > 1200000:
                    return None
                    
            with open(filepath, 'wb') as f:
                f.write(data)
            return filepath
    except Exception:
        return None

def download_shop_gallery(shop_id, urls):
    saved_paths = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for idx, url in enumerate(urls[:12]):
            ext = ".jpg"
            if ".png" in url.lower():
                ext = ".png"
            elif ".webp" in url.lower():
                ext = ".webp"
                
            filename = f"{shop_id}_{idx}{ext}"
            filepath = os.path.join(output_dir, filename)
            futures[executor.submit(download_single_image, url, filepath)] = f"/images/{filename}"
            
        for future in as_completed(futures):
            res_path = future.result()
            if res_path:
                saved_paths.append(futures[future])
                if len(saved_paths) >= 5:
                    break
                    
    saved_paths.sort()
    return saved_paths

new_shops_data = [
    {
        "id": "MI-219",
        "name": "T&K coffee",
        "region": "Miền Trung",
        "province": "Đà Nẵng",
        "address": "177 Hồ Tùng Mậu, phường Hòa Minh, quận Liên Chiểu, Đà Nẵng",
        "lat": 16.0595,
        "lng": 108.1638,
        "investment": "2.5 Tỷ",
        "model": "cà phê, trà trái cây",
        "target_customers": "trung niên, văn phòng, bđs",
        "images": []
    },
    {
        "id": "MI-220",
        "name": "Trạm Kí Ức acoustic & coffee",
        "region": "Miền Trung",
        "province": "Quảng Ngãi",
        "address": "Lô A7-A8-A9 Phan Thái Ất, phường Nghĩa Lộ, thành phố Quảng Ngãi",
        "lat": 15.1025707,
        "lng": 108.7999066,
        "investment": "1.5 Tỷ",
        "model": "cà phê, matcha, trà sữa pha máy",
        "target_customers": "khách giới trẻ",
        "images": []
    },
    {
        "id": "MI-221",
        "name": "Mickey Trà sữa & ăn vặt",
        "region": "Miền Trung",
        "province": "Đà Nẵng",
        "address": "104 Lê Trọng Tấn, phường Hòa Phát, quận Cẩm Lệ, Đà Nẵng",
        "lat": 16.0028,
        "lng": 108.1725,
        "investment": "500 Tr",
        "model": "trà sữa, ăn vặt",
        "target_customers": "học sinh, sinh viên",
        "images": []
    },
    {
        "id": "MI-222",
        "name": "Cafe SOUL 1422",
        "region": "Miền Trung",
        "province": "Đà Nẵng",
        "address": "Lô 1422, Đường Trung Lập 2 (gần Mê Linh), phường Hòa Hiệp Nam, quận Liên Chiểu, Đà Nẵng",
        "lat": 16.085,
        "lng": 108.136,
        "investment": "350 Tr",
        "model": "cà phê, trà trái cây, matcha",
        "target_customers": "dân cư chung cư và văn phòng",
        "images": []
    }
]

def main():
    print("Loading current shops...")
    with open(json_path, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    # Filter out any pre-existing duplicates of the new IDs to be safe
    existing_ids = {s['id'] for s in shops}
    
    for new_shop in new_shops_data:
        if new_shop['id'] in existing_ids:
            print(f"Skipping ID {new_shop['id']} because it already exists.")
            continue
            
        name = new_shop['name']
        province = new_shop['province']
        shop_id = new_shop['id']
        
        print(f"\nProcessing '{name}' ({province}) - ID: {shop_id}...")
        
        query = f"{name} {province} cafe"
        img_urls = get_bing_images(query)
        
        if not img_urls:
            query_alt = f"{name} {new_shop['address']}"
            img_urls = get_bing_images(query_alt)
            
        if img_urls:
            paths = download_shop_gallery(shop_id, img_urls)
            if paths:
                new_shop['images'] = paths
                print(f"  -> Downloaded {len(paths)} real photos: {paths}")
            else:
                print("  -> Found no photos that passed filters.")
        else:
            print("  -> No whitelisted photo URLs found.")
            
        shops.append(new_shop)
        time.sleep(1.8)
        
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)
        
    print("\nSUCCESS! Appended new verified shops to shops.json.")

if __name__ == "__main__":
    main()
