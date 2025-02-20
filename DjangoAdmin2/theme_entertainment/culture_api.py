import requests
import json
from datetime import datetime
import os
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time


def convert_date_format(date_str: str) -> str:
    """將日期字串轉換為 MySQL 可接受的格式 (YYYY-MM-DD HH:MM:SS)"""
    if not date_str:
        return None

    # 定義可能的日期格式
    date_formats = [
        '%Y/%m/%d %H:%M:%S',  # YYYY/MM/DD HH:MM:SS
        '%Y-%m-%d %H:%M:%S',  # YYYY-MM-DD HH:MM:SS
        '%d/%m/%Y %H:%M:%S',  # DD/MM/YYYY HH:MM:SS
        '%m/%d/%Y %H:%M:%S',  # MM/DD/YYYY HH:MM:SS
        '%b %d, %Y %I:%M:%S %p',  # Jan 18, 2025 12:00:00 AM
        '%Y/%m/%d',           # YYYY/MM/DD
        '%Y-%m-%d',           # YYYY-MM-DD
        '%d/%m/%Y',           # DD/MM/YYYY
        '%m/%d/%Y',           # MM/DD/YYYY
        '%b %d, %Y',          # Jan 18, 2025
    ]

    # 預處理日期字串
    date_str = date_str.strip()

    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_str, date_format)
            # 如果原始格式沒有時間部分，加上 00:00:00
            if len(date_format) <= 10:  # 只有日期部分
                return date_obj.strftime('%Y-%m-%d 00:00:00')
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

    print(f"無法解析日期格式: {date_str}")
    return None


def validate_coordinate(value: float, is_latitude: bool = True) -> Optional[float]:
    """驗證並處理經緯度值"""
    if value is None:
        return None
    try:
        value = float(value)
        # 檢查是否在有效範圍內
        if is_latitude and -90 <= value <= 90:
            return round(value, 8)
        elif not is_latitude and -180 <= value <= 180:
            return round(value, 8)
        return None
    except (ValueError, TypeError):
        return None


class CultureAPI:
    def __init__(self):
        self.base_url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do"
        self.params = {
            "method": "doFindTypeJ",
            "category": "all"
        }

        # 設定重試策略
        retry_strategy = Retry(
            total=3,  # 最多重試3次
            backoff_factor=1,  # 重試間隔時間
            status_forcelist=[500, 502, 503, 504]  # 需要重試的HTTP狀態碼
        )

        # 創建帶有重試機制的 session
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def make_request(self, url, params=None):
        """發送請求並處理可能的錯誤"""
        max_retries = 3
        retry_delay = 5  # 秒
        timeout = 30  # 秒

        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=timeout,
                    verify=True  # SSL 驗證
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    print(f"請求超時，{retry_delay}秒後進行第{attempt + 2}次嘗試...")
                    time.sleep(retry_delay)
                    continue
                raise

            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"請求失敗，{retry_delay}秒後進行第{
                          attempt + 2}次嘗試... 錯誤: {e}")
                    time.sleep(retry_delay)
                    continue
                raise

    def filter_event_data(self, event):
        # 提取 showInfo 中的資料
        show_info_list = []
        if 'showInfo' in event:
            for show in event['showInfo']:
                # 檢查並安全地獲取時間資訊
                start_date = show.get('time', {})
                end_date = show.get('endTime', {})

                show_info = {
                    '活動起始日期': convert_date_format(start_date),
                    '活動結束日期': convert_date_format(end_date),
                    '地址': show.get('location', ''),
                    '場地名稱': show.get('locationName', ''),
                    '是否售票': show.get('onSales', ''),
                    '緯度': show.get('latitude', ''),
                    '經度': show.get('longitude', ''),
                    '票價': show.get('price', '')
                }
                show_info_list.append(show_info)

        # 取得圖片連結並加上基礎網址
        image_url = event.get('imageURL', '')
        if image_url and not image_url.startswith('http'):
            image_url = f"https://cloud.culture.tw{image_url}"

        # 建立過濾後的資料結構
        filtered_data = {
            'UID': event.get('UID', ''),
            '活動名稱': event.get('title', ''),
            '演出單位': event.get('showUnit', ''),
            '簡介說明': event.get('descriptionFilterHtml', ''),
            '圖片連結': image_url,
            '主辦單位': event.get('masterUnit', ''),
            '相關資訊': show_info_list
        }
        return filtered_data

    def filter_festival_data(self, festival):
        """過濾節慶活動資料"""
        # 取得圖片連結並加上基礎網址
        image_url = festival.get('imageUrl', '')
        if image_url and not image_url.startswith('http'):
            image_url = f"https://cloud.culture.tw{image_url}"

        filtered_data = {
            'id': festival.get('actId', ''),
            '活動名稱': festival.get('actName', ''),
            '簡介說明': festival.get('description', ''),
            '活動地點': festival.get('address', ''),
            '電話': festival.get('tel', ''),
            '主辦單位': festival.get('org', ''),
            '活動起始時間': convert_date_format(festival.get('startTime', '')),
            '活動結束時間': convert_date_format(festival.get('endTime', '')),
            '網址': festival.get('website', ''),
            '緯度': festival.get('longitude', ''),
            '經度': festival.get('latitude', ''),
            '交通資訊': festival.get('travellinginfo', ''),
            '停車資訊': festival.get('parkinginfo', ''),
            '費用': festival.get('charge', ''),
            '備註': festival.get('remarks', ''),
            '所在區域': festival.get('cityName', ''),
            '圖片連結': image_url
        }
        return filtered_data

    def get_events(self, category="all"):
        try:
            self.params["category"] = category
            raw_data = self.make_request(self.base_url, self.params)
            filtered_data = [self.filter_event_data(
                event) for event in raw_data]

            # 建立結果資料夾（如果不存在）
            os.makedirs("culture_api", exist_ok=True)

            # 使用當前時間戳記建立檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if category == "all":
                category_name = "所有"
            elif category == "11":
                category_name = "文化部整合綜藝活動"
            else:
                category_name = f"類別{category}"
            filename = f"culture_api/{category_name}藝文活動_{timestamp}.json"

            # 將資料儲存為 JSON 檔案
            with open(filename, "w", encoding="utf-8-sig") as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)

            print(f"成功獲取{category_name}展演資訊，共 {
                  len(filtered_data)} 筆！資料已儲存至：{filename}")

            # 將資料轉換為標準格式
            formatted_data = {
                "result": [],
                "queryTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(filtered_data),
                "limit": len(filtered_data),
                "offset": 0
            }

            for event in filtered_data:
                # 使用第一個 showInfo 的資訊（如果有的話）
                show_info = event['相關資訊'][0] if event['相關資訊'] else {}

                # 處理經緯度
                latitude = validate_coordinate(show_info.get('緯度'), True)
                longitude = validate_coordinate(show_info.get('經度'), False)

                formatted_event = {
                    "uid": str(event['UID']),  # 確保是字串
                    "title": str(event['活動名稱']),
                    "description": str(event['簡介說明']),
                    "organizer": str(event['主辦單位']),
                    "address": str(show_info.get('地址', '')),
                    "startDate": show_info.get('活動起始日期'),
                    "endDate": show_info.get('活動結束日期'),
                    "location": str(show_info.get('場地名稱', '')),
                    "latitude": latitude,
                    "longitude": longitude,
                    "price": str(show_info.get('票價', '')),
                    "url": "",  # 文化部的資料沒有直接的 URL
                    "imageUrl": str(event['圖片連結'])
                }
                formatted_data["result"].append(formatted_event)

            return formatted_data

        except requests.exceptions.RequestException as e:
            print(f"獲取資料時發生錯誤：{str(e)}")
            return {"result": [], "error": str(e)}

    def get_integrated_events(self):
        """獲取文化部整合綜藝活動資料（包含表演、美食、講座、旅遊等綜合類型之整合活動）"""
        return self.get_events(category="11")

    def get_festival_events(self):
        """以本部整合之公民營單位的藝文活動資訊為範圍，推薦節慶相關的活動"""
        try:
            params = {
                "method": "doFindFestivalTypeJ"
            }
            raw_data = self.make_request(self.base_url, params)
            filtered_data = [self.filter_festival_data(
                festival) for festival in raw_data]

            # 建立結果資料夾（如果不存在）
            os.makedirs("culture_api", exist_ok=True)

            # 使用當前時間戳記建立檔案名稱
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"culture_api/文化部節慶活動_{timestamp}.json"

            # 將資料儲存為 JSON 檔案
            with open(filename, "w", encoding="utf-8-sig") as f:
                json.dump(filtered_data, f, ensure_ascii=False, indent=2)

            print(f"成功獲取文化部節慶活動資訊，共 {len(filtered_data)} 筆！資料已儲存至：{filename}")

            # 將資料轉換為標準格式
            formatted_data = {
                "result": [],
                "queryTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(filtered_data),
                "limit": len(filtered_data),
                "offset": 0
            }

            for festival in filtered_data:
                # 處理經緯度
                latitude = validate_coordinate(festival['緯度'], True)
                longitude = validate_coordinate(festival['經度'], False)

                formatted_event = {
                    "uid": str(festival['id']),
                    "title": str(festival['活動名稱']),
                    "description": str(festival['簡介說明']),
                    "organizer": str(festival['主辦單位']),
                    "address": str(festival['活動地點']),
                    "startDate": festival['活動起始時間'],
                    "endDate": festival['活動結束時間'],
                    "location": str(festival['活動地點']),
                    "latitude": latitude,
                    "longitude": longitude,
                    "price": str(festival['費用']),
                    "url": str(festival['網址']),
                    "imageUrl": str(festival['圖片連結'])
                }
                formatted_data["result"].append(formatted_event)

            return formatted_data

        except requests.exceptions.RequestException as e:
            print(f"獲取資料時發生錯誤：{str(e)}")
            return {"result": [], "error": str(e)}


if __name__ == "__main__":
    api = CultureAPI()

    # 獲取所有藝文活動
    all_events = api.get_events()

    # 獲取文化部整合綜藝活動
    integrated_events = api.get_integrated_events()

    # 獲取文化部節慶活動
    festival_events = api.get_festival_events()
