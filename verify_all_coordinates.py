import json

json_path = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/src/data/shops.json"
with open(json_path, 'r', encoding='utf-8') as f:
    shops = json.load(f)

invalid_shops = []
for s in shops:
    lat = s.get('lat')
    lng = s.get('lng')
    
    if lat is None or lng is None:
        invalid_shops.append((s['id'], s['name'], "Missing lat/lng"))
        continue
        
    try:
        lat_f = float(lat)
        lng_f = float(lng)
        
        # Check range for Vietnam bounds (lat: 8 to 24, lng: 102 to 110)
        if not (8.0 <= lat_f <= 24.0) or not (102.0 <= lng_f <= 110.0):
            invalid_shops.append((s['id'], s['name'], f"Out of bounds: ({lat_f}, {lng_f})"))
    except ValueError:
        invalid_shops.append((s['id'], s['name'], f"Non-numeric values: ({lat}, {lng})"))

print(f"Total shops: {len(shops)}")
print(f"Invalid shops count: {len(invalid_shops)}")
if invalid_shops:
    print("\nInvalid shops list:")
    for item in invalid_shops:
        print(item)
else:
    print("\nAll shops have valid coordinates!")
