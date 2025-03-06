import json
import re
import os

# 獲取目前檔案所在的目錄路徑
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 前端資料目錄路徑 (使用絕對路徑)
WORKSPACE_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, '..', '..', '..', 'TravelFun'))
FRONTEND_DATA_DIR = os.path.join(WORKSPACE_ROOT, 'src', 'assets', 'theme_entertainment')

def print_debug_info():
    """
    輸出除錯資訊
    """
    # print(f"目前目錄: {CURRENT_DIR}")
    # print(f"工作區根目錄: {WORKSPACE_ROOT}")
    # print(f"前端靜態資料目錄: {FRONTEND_DATA_DIR}")
    print(f"taiwan_country_lat_lon.json 路徑: {os.path.join(CURRENT_DIR, 'taiwan_country_lat_lon.json')}")
    # print(f"events_data.json 路徑: {os.path.join(FRONTEND_DATA_DIR, 'events_data.json')}")

def load_taiwan_regions():
    """
    載入台灣行政區域資料
    """
    taiwan_regions_path = os.path.join(CURRENT_DIR, 'taiwan_country_lat_lon.json')
    # print(f"嘗試讀取台灣行政區資料: {taiwan_regions_path}")

    with open(taiwan_regions_path, 'r', encoding='utf-8-sig') as f:
        regions = json.load(f)

    # 建立郵遞區號對應表和行政區名對應表
    postal_map = {}
    district_map = {}
    for region in regions:
        # 移除 _x0033_ 前綴並儲存郵遞區號對應
        postal_code = region['_x0033_碼郵遞區號']
        postal_map[postal_code] = {
            'longitude': region['中心點經度'],
            'latitude': region['中心點緯度']
        }

        # 儲存行政區名對應
        district_name = region['行政區名']
        district_map[district_name] = {
            'longitude': region['中心點經度'],
            'latitude': region['中心點緯度']
        }

    return postal_map, district_map

def match_coordinates(address):
    """
    比對地址並返回對應的經緯度

    Args:
        address (str): 完整地址

    Returns:
        tuple: (經度, 緯度) 若無匹配則返回 (None, None)
    """
    if not address or address == "無資料":
        return None, None

    postal_map, district_map = load_taiwan_regions()

    # 嘗試匹配郵遞區號（前三碼）
    postal_match = re.match(r'^(\d{3})', address)
    if postal_match:
        postal_code = postal_match.group(1)
        if postal_code in postal_map:
            return (
                float(postal_map[postal_code]['longitude']),
                float(postal_map[postal_code]['latitude'])
            )

    # 處理「台」和「臺」的轉換
    address_variants = [
        address,
        address.replace('台', '臺'),
        address.replace('臺', '台')
    ]

    # 嘗試匹配行政區名（使用所有地址變體）
    for variant in address_variants:
        for district_name in district_map:
            # 檢查原始地址和轉換後的地址是否匹配
            if variant.startswith(district_name):
                return (
                    float(district_map[district_name]['longitude']),
                    float(district_map[district_name]['latitude'])
                )

            # 檢查行政區名的變體
            district_variants = [
                district_name,
                district_name.replace('台', '臺'),
                district_name.replace('臺', '台')
            ]

            for district_variant in district_variants:
                if variant.startswith(district_variant):
                    return (
                        float(district_map[district_name]['longitude']),
                        float(district_map[district_name]['latitude'])
                    )

    return None, None

def update_events_coordinates():
    """
    更新活動資料的經緯度
    """
    try:
        # 輸出除錯資訊
        print_debug_info()

        # 讀取活動資料
        events_data_path = os.path.join(FRONTEND_DATA_DIR, 'events_data.json')
        print(f"嘗試讀取活動資料: {events_data_path}")

        if not os.path.exists(events_data_path):
            return f"錯誤: 找不到檔案 {events_data_path}"

        with open(events_data_path, 'r', encoding='utf-8-sig') as f:
            events = json.load(f)

        # 更新經緯度
        updated_count = 0
        for event in events:
            # 檢查經緯度是否需要更新
            needs_update = (
                not event.get('latitude') or
                not event.get('longitude') or
                event['latitude'] in ["無資料", "", None, "0", 0] or
                event['longitude'] in ["無資料", "", None, "0", 0]
            )

            if needs_update and event.get('address') and event['address'] != "無資料":
                # print(f"處理地址: {event['address']}")
                longitude, latitude = match_coordinates(event['address'])
                if longitude is not None and latitude is not None:
                    event['longitude'] = float(longitude)  # 使用浮點數格式
                    event['latitude'] = float(latitude)    # 使用浮點數格式
                    # print(f"更新經緯度: 經度={longitude}, 緯度={latitude}")
                    updated_count += 1
                else:
                    # 如果無法匹配到經緯度，設置為"無資料"
                    event['longitude'] = "無資料"
                    event['latitude'] = "無資料"

        # 儲存更新後的資料
        with open(events_data_path, 'w', encoding='utf-8-sig') as f:
            json.dump(events, f, ensure_ascii=False, indent=2)

        return f"已更新 {updated_count} 筆資料的經緯度"

    except Exception as e:
        return f"更新過程發生錯誤: {str(e)}\n完整路徑: {events_data_path}"

if __name__ == "__main__":
    result = update_events_coordinates()
    print(result)