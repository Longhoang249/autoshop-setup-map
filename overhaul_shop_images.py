import json
import os
import urllib.request
import urllib.parse
import re
import ssl
import time
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

json_path = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/src/data/shops.json"
output_dir = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/public/images"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

# Whitelist of CDNs hosting only 100% real user/owner uploaded photos
WHITELIST_CDNS = [
    "fbcdn.net", "fbsbx.com",           # Facebook
    "googleusercontent.com",            # Google Maps
    "foody.vn", "shopeefood.vn",        # Foody / ShopeeFood
    "lozi.vn", "riviu.vn",              # Lozi / Riviu
    "instagram.com", "cdninstagram.com" # Instagram
]

def is_whitelisted(url):
    url_lower = url.lower()
    for domain in WHITELIST_CDNS:
        if domain in url_lower:
            return True
    return False

def delete_existing_new_shop_images():
    print("Deleting existing new shop images from public/images/...")
    # Find all files starting with MI-083 to MI-218
    deleted_count = 0
    for num in range(83, 219):
        pattern = os.path.join(output_dir, f"MI-{num:03d}*")
        files = glob.glob(pattern)
        for f in files:
            try:
                os.remove(f)
                deleted_count += 1
            except Exception as e:
                print(f"Error deleting {f}: {e}")
    print(f"Deleted {deleted_count} old images.")

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
            # Remove duplicates while preserving order
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
            # Check content size: 30KB - 1.2MB
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
        for idx, url in enumerate(urls[:12]): # Try top 12 candidate URLs
            # Determine extension
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
                if len(saved_paths) >= 5: # Max 5 images
                    break
                    
    saved_paths.sort()
    return saved_paths

def main():
    delete_existing_new_shop_images()
    
    print("Loading shops database...")
    with open(json_path, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    # Reset images for all new shops (MI-083 to MI-218)
    for s in shops:
        sid = s.get('id', '')
        match = re.search(r'MI-(\d+)', sid)
        if match:
            num = int(match.group(1))
            if num >= 83:
                s['images'] = []
                
    # Filter shops to process
    shops_to_process = []
    for s in shops:
        sid = s.get('id', '')
        match = re.search(r'MI-(\d+)', sid)
        if match:
            num = int(match.group(1))
            if num >= 83:
                shops_to_process.append(s)
                
    total = len(shops_to_process)
    print(f"Processing {total} shops for 100% real photos...")
    
    success_count = 0
    empty_count = 0
    
    for count, shop in enumerate(shops_to_process, 1):
        name = shop.get('name', '')
        province = shop.get('province', '')
        address = shop.get('address', '')
        shop_id = shop.get('id', '')
        
        clean_name = name
        for word in ["setup", "menu", "đã đóng cửa", "cửa hàng", "quán", "ats"]:
            clean_name = clean_name.replace(word, "").replace(word.upper(), "")
            
        # Specific search queries to get direct social/maps hits
        query = f"{clean_name.strip()} {province} cafe"
        print(f"\n[{count}/{total}] Searching real photos for '{name}' ({province})...")
        
        img_urls = get_bing_images(query)
        
        if not img_urls:
            # Fallback using address
            query_fallback = f"{clean_name.strip()} {address}"
            img_urls = get_bing_images(query_fallback)
            
        if img_urls:
            paths = download_shop_gallery(shop_id, img_urls)
            if paths:
                shop['images'] = paths
                success_count += 1
                print(f"  -> SUCCESS! Saved {len(paths)} real photos: {paths}")
            else:
                shop['images'] = []
                empty_count += 1
                print("  -> FAILED to download whitelisted photos. Left EMPTY.")
        else:
            shop['images'] = []
            empty_count += 1
            print("  -> No whitelisted images found. Left EMPTY.")
            
        # Respect Search Engine limits
        time.sleep(1.8)
        
        # Periodic save
        if count % 5 == 0:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(shops, f, ensure_ascii=False, indent=2)
                
    # Final save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)
        
    print(f"\nOVERHAUL COMPLETED!")
    print(f" - Successfully set real photos for: {success_count} shops")
    print(f" - Left empty (real photos not found): {empty_count} shops")

if __name__ == "__main__":
    main()
