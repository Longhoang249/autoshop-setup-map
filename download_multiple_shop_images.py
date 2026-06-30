import json
import os
import urllib.request
import urllib.parse
import re
import ssl
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

json_path = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/src/data/shops.json"
output_dir = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/public/images"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
}

BLACKLIST_WORDS = [
    "logo", "avatar", "map", "marker", "icon", "pin", "banner", "flag", 
    "profile", "card", "ad", "quangcao", "quang-cao", "advertisement",
    "facebook-logo", "youtube-logo", "instagram-logo", "signpost", "placeholder"
]

def is_blacklisted(url):
    url_lower = url.lower()
    for word in BLACKLIST_WORDS:
        if word in url_lower:
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
                    if img_url and img_url.startswith('http') and not is_blacklisted(img_url):
                        images.append(img_url)
                except Exception:
                    img_match = re.search(r'"murl":"(.*?)"', m_clean)
                    if img_match and img_match.group(1).startswith('http'):
                        u = img_match.group(1)
                        if not is_blacklisted(u):
                            images.append(u)
            return images[:15] # Get 15 candidates to extract 5 good photos
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
        return []

def download_single_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            # Size check: 40KB - 1.2MB
            info = response.info()
            content_length = info.get('Content-Length')
            if content_length:
                size_bytes = int(content_length)
                if size_bytes < 35000 or size_bytes > 1200000:
                    return None
                    
            data = response.read()
            if not content_length:
                size_bytes = len(data)
                if size_bytes < 35000 or size_bytes > 1200000:
                    return None
                    
            with open(filepath, 'wb') as f:
                f.write(data)
            return filepath
    except Exception:
        return None

def download_shop_gallery(shop_id, urls):
    # Downloads up to 5 images in parallel threads
    saved_paths = []
    
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = {}
        for idx, url in enumerate(urls[:10]): # Try first 10 candidate URLs
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
                if len(saved_paths) >= 5: # Limit to max 5 images
                    break
                    
    # Sort paths by index to keep order
    saved_paths.sort()
    return saved_paths

def main():
    print("Creating public/images directory...")
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading shops database...")
    with open(json_path, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    # We will enrich all new shops (IDs MI-083 to MI-218) with multiple photos
    shops_to_process = []
    for s in shops:
        sid = s.get('id', '')
        match = re.search(r'MI-(\d+)', sid)
        if match:
            num = int(match.group(1))
            # Process new shops, especially those with 0 or 1 image
            if num >= 83 and len(s.get('images', [])) <= 1:
                shops_to_process.append(s)
                
    total = len(shops_to_process)
    print(f"Found {total} shops to enrich with multi-photo galleries. Starting parallel download...")
    
    success_count = 0
    for count, shop in enumerate(shops_to_process, 1):
        name = shop.get('name', '')
        province = shop.get('province', '')
        shop_id = shop.get('id', '')
        
        clean_name = name
        for word in ["setup", "menu", "đã đóng cửa", "cửa hàng", "quán", "ats"]:
            clean_name = clean_name.replace(word, "").replace(word.upper(), "")
            
        query = f"{clean_name.strip()} {province} không gian quán cafe"
        print(f"\n[{count}/{total}] Fetching gallery for '{name}' ({province})...")
        
        img_urls = get_bing_images(query)
        if not img_urls:
            # Fallback
            query_general = f"{clean_name.strip()} {province} cafe đồ uống"
            img_urls = get_bing_images(query_general)
            
        if img_urls:
            paths = download_shop_gallery(shop_id, img_urls)
            if paths:
                shop['images'] = paths
                success_count += 1
                print(f"  -> SUCCESS! Saved {len(paths)} photos: {paths}")
            else:
                print("  -> FAILED to download any images.")
        else:
            print("  -> No image URLs found.")
            
        # Rate limit protection between Bing searches
        time.sleep(1.8)
        
        # Save progress periodic
        if count % 5 == 0:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(shops, f, ensure_ascii=False, indent=2)
                
    # Final database save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)
        
    print(f"\nCOMPLETED! Successfully updated multi-photo galleries for {success_count} / {total} shops.")

if __name__ == "__main__":
    main()
