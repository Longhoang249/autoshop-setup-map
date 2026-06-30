import json
import os
import urllib.request
import urllib.parse
import re
import ssl
import time
import sys

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
            return images[:10] # Fetch more candidates to filter
    except Exception as e:
        print(f"Search error for query '{query}': {e}")
        return []

def download_image(url, filepath):
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, context=ctx, timeout=10) as response:
            # Check content size (must be between 40KB and 1.2MB)
            info = response.info()
            content_length = info.get('Content-Length')
            if content_length:
                size_bytes = int(content_length)
                if size_bytes < 35000: # Too small, probably a thumbnail or icon/logo
                    print(f"  -> Skipping (too small: {size_bytes/1000} KB)")
                    return False
                if size_bytes > 1200000: # Too large, slow to load
                    print(f"  -> Skipping (too large: {size_bytes/1000} KB)")
                    return False
                
            data = response.read()
            # Double check raw data length if Content-Length header was missing
            if not content_length:
                size_bytes = len(data)
                if size_bytes < 35000 or size_bytes > 1200000:
                    print(f"  -> Skipping raw size check failed: {size_bytes/1000} KB")
                    return False
                    
            with open(filepath, 'wb') as f:
                f.write(data)
            return True
    except Exception as e:
        return False

def main():
    print("Creating public/images directory...")
    os.makedirs(output_dir, exist_ok=True)
    
    print("Loading shops database...")
    with open(json_path, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    # Process only shops that don't have images
    # We clear any previously failed downloads in the same run
    shops_to_process = [s for s in shops if not s.get('images')]
    total = len(shops_to_process)
    
    print(f"Found {total} shops without images. Starting beautiful image downloader...")
    
    success_count = 0
    for count, shop in enumerate(shops_to_process, 1):
        name = shop.get('name', '')
        province = shop.get('province', '')
        address = shop.get('address', '')
        shop_id = shop.get('id', '')
        
        clean_name = name
        for word in ["setup", "menu", "đã đóng cửa", "cửa hàng", "quán", "ats"]:
            clean_name = clean_name.replace(word, "").replace(word.upper(), "")
            
        # Refined query focusing on space/interior or drinks
        query_space = f"{clean_name.strip()} {province} không gian quán cafe"
        print(f"\n[{count}/{total}] Searching space for '{name}' ({province})...")
        
        img_urls = get_bing_images(query_space)
        
        if not img_urls:
            # Fallback 1: drinks/food
            query_drinks = f"{clean_name.strip()} {province} đồ uống cafe"
            print(f"  -> No space results. Searching drinks: {query_drinks}")
            img_urls = get_bing_images(query_drinks)
            
        if not img_urls:
            # Fallback 2: general shop info
            query_general = f"{clean_name.strip()} {province} cafe"
            print(f"  -> Trying general query: {query_general}")
            img_urls = get_bing_images(query_general)

        downloaded = False
        for idx, url in enumerate(img_urls):
            ext = ".jpg"
            if ".png" in url.lower():
                ext = ".png"
            elif ".webp" in url.lower():
                ext = ".webp"
                
            filename = f"{shop_id}{ext}"
            filepath = os.path.join(output_dir, filename)
            
            print(f"  -> Attempting download {idx+1}/{len(img_urls)}: {url[:60]}...")
            if download_image(url, filepath):
                shop['images'] = [f"/images/{filename}"]
                success_count += 1
                downloaded = True
                print(f"  -> SUCCESS! Saved space/drink photo: {filename}")
                break
                
        if not downloaded:
            print("  -> FAILED to download a high-quality space/drink photo.")
            
        # Rate limit protection
        time.sleep(1.8)
        
        # Periodic database save
        if count % 5 == 0:
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(shops, f, ensure_ascii=False, indent=2)
                
    # Final database save
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)
        
    print(f"\nCOMPLETED! Successfully downloaded beautiful photos for {success_count} / {total} shops.")

if __name__ == "__main__":
    main()
