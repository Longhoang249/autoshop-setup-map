import json
import random
import re

json_path = "/Users/hoangvan/.gemini/antigravity/scratch/autoshop-setup-map/src/data/shops.json"

PROVINCE_COORDINATES = {
    "AN GIANG": (10.5, 105.2),
    "BÀ RỊA - VŨNG TÀU": (10.5, 107.2),
    "BẠC LIÊU": (9.3, 105.5),
    "BẮC GIANG": (21.3, 106.2),
    "BẮC KẠN": (22.3, 105.8),
    "BẮC NINH": (21.2, 106.1),
    "BẾN TRE": (10.2, 106.4),
    "BÌNH DƯƠNG": (11.1, 106.7),
    "BÌNH ĐỊNH": (13.8, 109.1),
    "BÌNH PHƯỚC": (11.7, 106.9),
    "BÌNH THUẬN": (11.1, 108.1),
    "CÀ MAU": (9.2, 105.1),
    "CẦN THƠ": (10.0, 105.7),
    "CAO BẰNG": (22.7, 106.3),
    "ĐÀ NẴNG": (16.0, 108.2),
    "ĐẮK LẮK": (12.7, 108.1),
    "ĐẮK NÔNG": (12.1, 107.7),
    "ĐIỆN BIÊN": (21.8, 103.0),
    "ĐỒNG NAI": (11.0, 107.0),
    "ĐỒNG THÁP": (10.5, 105.6),
    "GIA LAI": (14.0, 108.0),
    "HÀ GIANG": (22.8, 104.9),
    "HÀ NAM": (20.5, 105.9),
    "HÀ NỘI": (21.0, 105.8),
    "HÀ TĨNH": (18.3, 105.9),
    "HẢI DƯƠNG": (20.9, 106.3),
    "HẢI PHÒNG": (20.8, 106.7),
    "HẬU GIANG": (9.8, 105.6),
    "HÒA BÌNH": (20.7, 105.3),
    "HƯNG YÊN": (20.6, 106.1),
    "KHÁNH HÒA": (12.3, 109.1),
    "KIÊN GIANG": (10.0, 105.1),
    "KON TUM": (14.3, 108.0),
    "LAI CHÂU": (22.3, 103.0),
    "LẠNG SƠN": (21.8, 106.7),
    "LÀO CAI": (22.4, 103.9),
    "LÂM ĐỒNG": (11.6, 107.8),
    "LONG AN": (10.7, 106.3),
    "NAM ĐỊNH": (20.4, 106.2),
    "NGHỆ AN": (19.2, 105.1),
    "NINH BÌNH": (20.2, 105.9),
    "NINH THUẬN": (11.7, 108.9),
    "PHÚ THỌ": (21.3, 105.2),
    "PHÚ YÊN": (13.1, 109.1),
    "QUẢNG BÌNH": (17.5, 106.3),
    "QUẢNG NAM": (15.7, 107.9),
    "QUẢNG NGÃI": (15.1, 108.8),
    "QUẢNG NINH": (21.0, 107.3),
    "QUẢNG TRỊ": (16.7, 107.1),
    "SÓC TRĂNG": (9.6, 106.0),
    "SƠN LA": (21.2, 103.7),
    "TÂY NINH": (11.4, 106.1),
    "THÁI BÌNH": (20.5, 106.4),
    "THÁI NGUYÊN": (21.6, 105.8),
    "THANH HÓA": (19.8, 105.8),
    "THỪA THIÊN HUẾ": (16.5, 107.5),
    "TIỀN GIANG": (10.4, 106.2),
    "HỒ CHÍ MINH": (10.8, 106.6),
    "TRÀ VINH": (9.9, 106.3),
    "TUYÊN QUANG": (21.8, 105.2),
    "VĨNH LONG": (10.2, 105.9),
    "VĨNH PHÚC": (21.3, 105.5),
    "YÊN BÁI": (21.7, 104.9)
}

REGION_MAPPING = {
    # Miền Bắc
    "HÀ NỘI": "Miền Bắc", "QUẢNG NINH": "Miền Bắc", "PHÚ THỌ": "Miền Bắc", "HÒA BÌNH": "Miền Bắc",
    "HẢI DƯƠNG": "Miền Bắc", "BẮC NINH": "Miền Bắc", "THANH HÓA": "Miền Bắc", "THÁI NGUYÊN": "Miền Bắc",
    "HẢI PHÒNG": "Miền Bắc", "BẮC GIANG": "Miền Bắc", "NGHỆ AN": "Miền Bắc", "HƯNG YÊN": "Miền Bắc",
    "CAO BẰNG": "Miền Bắc", "HÀ GIANG": "Miền Bắc", "HÀ NAM": "Miền Bắc", "LẠNG SƠN": "Miền Bắc",
    "LÀO CAI": "Miền Bắc", "HÀ TĨNH": "Miền Bắc", "NAM ĐỊNH": "Miền Bắc", "THÁI BÌNH": "Miền Bắc",
    "VĨNH PHÚC": "Miền Bắc", "YÊN BÁI": "Miền Bắc", "TUYÊN QUANG": "Miền Bắc", "SƠN LA": "Miền Bắc",
    "ĐIỆN BIÊN": "Miền Bắc", "LAI CHÂU": "Miền Bắc", "BẮC KẠN": "Miền Bắc",
    
    # Miền Trung
    "ĐÀ NẴNG": "Miền Trung", "ĐẮK LẮK": "Miền Trung", "LÂM ĐỒNG": "Miền Trung", "NINH THUẬN": "Miền Trung",
    "QUẢNG NGÃI": "Miền Trung", "QUẢNG NAM": "Miền Trung", "QUẢNG BÌNH": "Miền Trung", "QUẢNG TRỊ": "Miền Trung",
    "KHÁNH HÒA": "Miền Trung", "KON TUM": "Miền Trung", "BÌNH ĐỊNH": "Miền Trung", "BÌNH THUẬN": "Miền Trung",
    "GIA LAI": "Miền Trung", "ĐẮK NÔNG": "Miền Trung", "PHÚ YÊN": "Miền Trung", "THỪA THIÊN HUẾ": "Miền Trung",
    
    # Miền Nam
    "HỒ CHÍ MINH": "Miền Nam", "BÌNH DƯƠNG": "Miền Nam", "CẦN THƠ": "Miền Nam", "BẠC LIÊU": "Miền Nam",
    "TIỀN GIANG": "Miền Nam", "LONG AN": "Miền Nam", "ĐỒNG NAI": "Miền Nam", "TÂY NINH": "Miền Nam",
    "BÌNH PHƯỚC": "Miền Nam", "BÀ RỊA - VŨNG TÀU": "Miền Nam", "HẬU GIANG": "Miền Nam", "KIÊN GIANG": "Miền Nam",
    "SÓC TRĂNG": "Miền Nam", "AN GIANG": "Miền Nam", "BẾN TRE": "Miền Nam", "ĐỒNG THÁP": "Miền Nam",
    "TRÀ VINH": "Miền Nam", "VĨNH LONG": "Miền Nam", "CÀ MAU": "Miền Nam"
}

def clean_province_name(prov, addr):
    addr_upper = str(addr).strip().upper()
    prov_upper = str(prov).strip().upper()
    
    # Check for direct matches or context
    if "HỘI AN" in addr_upper or "HỘI AN" in prov_upper or "QUẢNG NAM" in addr_upper or "QUẢNG NAM" in prov_upper:
        return "QUẢNG NAM"
        
    if "PHÚ QUỐC" in addr_upper or "PHÚ QUỐC" in prov_upper or "KIÊN GIANG" in addr_upper or "KIÊN GIANG" in prov_upper:
        return "KIÊN GIANG"
        
    if "HUẾ" in addr_upper or "HUẾ" in prov_upper or "THỪA THIÊN HUẾ" in addr_upper or "THỪA THIÊN HUẾ" in prov_upper:
        return "THỪA THIÊN HUẾ"
        
    if "ĐÀ LẠT" in addr_upper or "ĐÀ LẠT" in prov_upper or "LÂM ĐỒNG" in addr_upper or "LÂM ĐỒNG" in prov_upper:
        return "LÂM ĐỒNG"
        
    if "PHAN RANG" in addr_upper or "PHAN RANG" in prov_upper or "NINH THUẬN" in addr_upper or "NINH THUẬN" in prov_upper:
        return "NINH THUẬN"
        
    if "HẠ LONG" in addr_upper or "HẠ LONG" in prov_upper or "MÓNG CÁI" in addr_upper or "MÓNG CÁI" in prov_upper or "QUẢNG NINH" in addr_upper or "QUẢNG NINH" in prov_upper:
        return "QUẢNG NINH"
        
    if "BÌNH DƯƠNG" in addr_upper or "THỦ DẦU MỘT" in addr_upper or "DĨ AN" in addr_upper or "THUẬN AN" in addr_upper:
        return "BÌNH DƯƠNG"
        
    if "CẦN GIUỘC" in addr_upper or "LONG AN" in addr_upper or "CẦN ĐƯỚC" in addr_upper or "LONG AN" in prov_upper:
        return "LONG AN"
        
    # Check HỒ CHÍ MINH / TP.HCM / SÀI GÒN/ QUẬN
    if any(kw in addr_upper or kw in prov_upper for kw in ["TP.HCM", "TP HCM", "HỒ CHÍ MINH", "HO CHI MINH", "SÀI GÒN", "SAI GON", "HCM", "Q.1", "Q.2", "Q.3", "Q.4", "Q.5", "Q.6", "Q.7", "Q.8", "Q.9", "Q.10", "Q.11", "Q.12", "QUẬN 1", "QUẬN 2", "QUẬN 3", "QUẬN 4", "QUẬN 5", "QUẬN 6", "QUẬN 7", "QUẬN 8", "QUẬN 9", "QUẬN 10", "QUẬN 11", "QUẬN 12", "GÒ VẤP", "THỦ ĐỨC", "BÌNH TÂN", "BÌNH THẠNH", "PHÚ NHUẬN", "TÂN BÌNH", "TÂN PHÚ", "HÓC MÔN", "CỦ CHI", "NHÀ BÈ", "CẦN GIỜ", "BÌNH CHÁNH"]):
        return "HỒ CHÍ MINH"
        
    # Check HÀ NỘI
    if any(kw in addr_upper or kw in prov_upper for kw in ["HÀ NỘI", "HA NOI", "HN", "HANOI", "CẦU GIẤY", "HOÀN KIẾM", "ĐỐNG ĐA", "BA ĐÌNH", "HAI BÀ TRƯNG", "TÂY HỒ", "THANH XUÂN", "HÀ ĐÔNG", "LONG BIÊN", "NAM TỪ LIÊM", "BẮC TỪ LIÊM", "THANH TRÌ", "GIA LÂM", "ĐÔNG ANH", "SÓC SƠN", "BA VÌ", "PHÚC THỌ", "THẠCH THẤT", "QUỐC OAI", "CHƯƠNG MỸ", "THANH OAI", "THƯỜNG TÍN", "PHÚ XUYÊN", "ỨNG HÒA", "MỸ ĐỨC", "MÊ LINH", "SƠN TÂY"]):
        return "HÀ NỘI"

    # Standard cleanups
    clean_p = prov_upper.replace("TP.", "").replace("TỈNH", "").replace("TP", "").strip()
    clean_p = re.sub(r'\s+', ' ', clean_p)
    
    if clean_p in PROVINCE_COORDINATES:
        return clean_p
        
    # Check address fallback
    for p in PROVINCE_COORDINATES.keys():
        if p in addr_upper:
            return p
            
    return "HÀ NỘI" # default fallback

with open(json_path, 'r', encoding='utf-8') as f:
    shops = json.load(f)

print(f"Loaded {len(shops)} shops to fix.")

fixed_count = 0
for s in shops:
    old_prov = s.get('province', '')
    old_region = s.get('region', '')
    old_lat = s.get('lat')
    old_lng = s.get('lng')
    
    # 1. Clean the province name
    new_prov = clean_province_name(old_prov, s.get('address', ''))
    
    # 2. Determine correct region
    new_region = REGION_MAPPING.get(new_prov, old_region)
    
    # 3. Resolve coordinates
    coords = PROVINCE_COORDINATES.get(new_prov)
    
    if coords:
        # Distance comparison or check if it fell back to Laos coordinates
        is_fallback = (abs(old_lat - 16.0) < 0.2 and abs(old_lng - 106.5) < 0.2)
        distance_sq = (old_lat - coords[0])**2 + (old_lng - coords[1])**2
        
        # If it fell back to Laos, or is wrong province, or region is wrong, re-geocode
        if is_fallback or distance_sq > 0.5 or old_prov != new_prov or old_region != new_region:
            s['lat'] = coords[0] + random.uniform(-0.025, 0.025)
            s['lng'] = coords[1] + random.uniform(-0.025, 0.025)
            s['province'] = new_prov
            s['region'] = new_region
            fixed_count += 1
            print(f"Corrected: '{s['name']}'\n   From: {old_prov} ({old_region}) at ({old_lat:.4f}, {old_lng:.4f})\n   To:   {new_prov} ({new_region}) at ({s['lat']:.4f}, {s['lng']:.4f})")
    else:
        print(f"WARNING: No coordinates found for province '{new_prov}' of shop '{s['name']}'")

# Save updated JSON
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(shops, f, ensure_ascii=False, indent=2)

print(f"\nSUCCESS: Corrected geocoding for {fixed_count} shops.")
