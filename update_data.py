import urllib.request
import csv
import json
import os
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

# Replace with your public Google Sheet CSV export URL
# To get this link: File > Share > Publish to web > Select Sheet and CSV format > Publish > Copy link.
DEFAULT_SHEET_ID = "YOUR_SPREADSHEET_ID_HERE"
DEFAULT_CSV_URL = f"https://docs.google.com/spreadsheets/d/{DEFAULT_SHEET_ID}/pub?output=csv"

def update_from_csv(csv_url_or_file):
    print(f"Updating data from: {csv_url_or_file}...")
    
    # Check if it's a URL or a local file
    if csv_url_or_file.startswith("http"):
        try:
            req = urllib.request.Request(
                csv_url_or_file, 
                headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, context=ctx, timeout=15) as response:
                content = response.read().decode('utf-8')
                lines = content.splitlines()
        except Exception as e:
            print(f"Error fetching CSV from URL: {e}")
            return False
    else:
        if not os.path.exists(csv_url_or_file):
            print(f"Local file {csv_url_or_file} not found.")
            return False
        with open(csv_url_or_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

    # Parse CSV lines
    reader = csv.DictReader(lines)
    shops = []
    
    for row in reader:
        # Convert images string back to array
        img_str = row.get("images", "")
        img_list = [img.strip() for img in img_str.split(",") if img.strip()]
        
        shop = {
            "id": row.get("id", "").strip(),
            "region": row.get("region", "").strip(),
            "province": row.get("province", "").strip(),
            "name": row.get("name", "").strip(),
            "address": row.get("address", "").strip(),
            "investment": row.get("investment", "").strip(),
            "model": row.get("model", "").strip(),
            "target_customers": row.get("target_customers", "").strip(),
            "images": img_list,
            "info_card_url": row.get("info_card_url", "").strip()
        }
        
        # Only add valid entries
        if shop["id"] and shop["province"]:
            shops.append(shop)

    # Save to src/data/shops.json
    output_path = "src/data/shops.json"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(shops, f, ensure_ascii=False, indent=2)

    print(f"SUCCESS: Synchronized {len(shops)} shops to {output_path}")
    return True

if __name__ == "__main__":
    import sys
    
    target = DEFAULT_CSV_URL
    if len(sys.argv) > 1:
        target = sys.argv[1]
    
    if "YOUR_SPREADSHEET_ID_HERE" in target:
        # If no custom sheet URL was passed, try using the local database we just created
        local_db = "/Users/hoangvan/.gemini/antigravity/brain/c68d7c20-27da-4738-bf75-cbe5f4dcd882/scratch/autoshop_setup_database.csv"
        if os.path.exists(local_db):
            print("No Google Sheet URL specified. Synchronizing from local CSV instead...")
            update_from_csv(local_db)
        else:
            print("Please specify a Google Sheet CSV URL or Spreadsheet ID.")
            print("Usage: python3 update_data.py <google_sheet_csv_url_or_id>")
    else:
        # If a short ID is passed, build the CSV url
        if not target.startswith("http") and "/" not in target and len(target) > 20:
            target = f"https://docs.google.com/spreadsheets/d/{target}/pub?output=csv"
        update_from_csv(target)
