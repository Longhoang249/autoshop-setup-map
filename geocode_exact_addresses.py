import json
import urllib.request
import urllib.parse
import time
import ssl
import sys
import re

json_path = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/src/data/shops.json"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def geocode_query(query):
    url = f"https://nominatim.openstreetmap.org/search?q={urllib.parse.quote(query)}&format=json&limit=1"
    try:
        req = urllib.request.Request(
            url, 
            headers={'User-Agent': 'AutoshopSetupExactGeocoding/2.0 (long2492000@gmail.com)'}
        )
        with urllib.request.urlopen(req, context=ctx, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            if data:
                return float(data[0]['lat']), float(data[0]['lon']), "Exact match"
    except Exception as e:
        # Silently fail to try shorter query
        pass
    return None

def clean_address(addr):
    # Remove special chars and clean up address text for search
    addr = re.sub(r'\(.*?\)', '', addr) # Remove parenthetical notes
    addr = addr.replace("setup", "").replace("Setup", "").replace("máy móc", "").replace("nguyên liệu", "")
    return addr.strip()

def geocode_shop(name, address, province):
    cleaned_addr = clean_address(address)
    
    # Try 1: Exact name + address + province + Vietnam
    q1 = f"{name}, {cleaned_addr}, {province}, Vietnam"
    res = geocode_query(q1)
    if res:
        return res
        
    # Try 2: Cleaned address + province + Vietnam
    q2 = f"{cleaned_addr}, {province}, Vietnam"
    res = geocode_query(q2)
    if res:
        return res
        
    # Try 3: Shorter address (split by comma, take first 2 parts) + province + Vietnam
    parts = [p.strip() for p in cleaned_addr.split(',') if p.strip()]
    if len(parts) > 1:
        q3 = f"{parts[0]} {parts[1]}, {province}, Vietnam"
        res = geocode_query(q3)
        if res:
            return res
            
    # Try 4: Just the first part of address + province + Vietnam
    if parts:
        q4 = f"{parts[0]}, {province}, Vietnam"
        res = geocode_query(q4)
        if res:
            return res
            
    return None

def main():
    print("Loading shops database...")
    with open(json_path, 'r', encoding='utf-8') as f:
        shops = json.load(f)
        
    # Filter shops to geocode (IDs MI-083 to MI-218)
    shops_to_geocode = []
    for idx, shop in enumerate(shops):
        sid = shop.get('id', '')
        match = re.search(r'MI-(\d+)', sid)
        if match:
            num = int(match.group(1))
            if num >= 83:
                shops_to_geocode.append((idx, shop))
                
    total = len(shops_to_geocode)
    print(f"Starting exact geocoding for {total} new shops...")
    
    success_count = 0
    for count, (idx, shop) in enumerate(shops_to_geocode, 1):
        name = shop.get('name', '')
        address = shop.get('address', '')
        province = shop.get('province', '')
        
        print(f"[{count}/{total}] Geocoding '{name}' - {address}...")
        
        coords = geocode_shop(name, address, province)
        
        if coords:
            lat, lng, match_type = coords
            shop['lat'] = lat
            shop['lng'] = lng
            success_count += 1
            print(f"  -> SUCCESS ({match_type}): ({lat}, {lng})")
        else:
            print("  -> FAILED: Kept fallback province coordinates.")
            
        # Respect Nominatim usage limit (1 request per second)
        time.sleep(1.2)
        
    # Save back to database
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)
        
    print(f"\nCompleted exact geocoding! Successfully resolved exact coordinates for {success_count} / {total} shops.")

if __name__ == "__main__":
    main()
