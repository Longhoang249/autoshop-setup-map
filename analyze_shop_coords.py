import json
from collections import Counter

json_path = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/src/data/shops.json"
with open(json_path, 'r', encoding='utf-8') as f:
    shops = json.load(f)

coords = [(s['lat'], s['lng']) for s in shops if s.get('lat') and s.get('lng')]
coord_counts = Counter(coords)

print("Total shops:", len(shops))
print("Unique coordinates:", len(coord_counts))
print("\nMost common coordinates (potential province fallbacks):")
for coord, count in coord_counts.most_common(15):
    # Find some shops sharing this coordinate
    sharing = [s['name'] + " (" + s['province'] + ")" for s in shops if (s['lat'], s['lng']) == coord]
    print(f"Coord: {coord} -> Count: {count}")
    print(f"  Shops: {sharing[:4]}")
