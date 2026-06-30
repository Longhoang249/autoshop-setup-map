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

new_shop = {
    "id": "MI-223",
    "name": "Pestanap Hoi An Sleep Pods and Coffee",
    "region": "Miền Trung",
    "province": "Quảng Nam",
    "address": "Lô số 13, Đường Lê Hồng Phong nối dài, Khu dân cư Lâm Sa - Tu Lễ - Xuân Hoà, Hội An, Quảng Nam",
    "lat": 15.8812,
    "lng": 108.3245,
    "investment": "1.5 Tỷ",
    "model": "cà phê, trà trái cây, trà sữa pha máy",
    "target_customers": "khách trẻ, khách du lịch",
    "images": []
}

def main():
    print("Loading current shops...")
    with open(json_path, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    # Check if MI-223 already exists
    existing_ids = {s['id'] for s in shops}
    if new_shop['id'] in existing_ids:
        print("MI-223 already exists. Exiting.")
        return
        
    print(f"Searching real photos for '{new_shop['name']}'...")
    # Search with the exact full name
    img_urls = get_bing_images("Pestanap Hoi An Sleep Pods and Coffee")
    
    if not img_urls:
        # Search with a simplified name
        img_urls = get_bing_images("Pestanap Hoi An")
        
    if img_urls:
        paths = download_shop_gallery(new_shop['id'], img_urls)
        if paths:
            new_shop['images'] = paths
            print(f"  -> Downloaded {len(paths)} real photos: {paths}")
        else:
            print("  -> Found no photos that passed filters.")
    else:
        print("  -> No whitelisted photo URLs found.")
        
    shops.append(new_shop)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)
        
    print("SUCCESS! Added Pestanap Hoi An Sleep Pods and Coffee to shops.json.")

if __name__ == "__main__":
    main()
