import requests
import json
from datetime import datetime
import os
from typing import Optional
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import time


def convert_date_format(date_str: str) -> str:
    # 將日期字串轉換為標準格式 (YYYY-MM-DD HH:MM:SS)
    if not date_str:
        return None

    # 定義可能的日期格式清單
    date_formats = [
        '%Y/%m/%d %H:%M:%S',  # 西元年/月/日 時:分:秒
        '%Y-%m-%d %H:%M:%S',  # 西元年-月-日 時:分:秒
        '%d/%m/%Y %H:%M:%S',  # 日/月/西元年 時:分:秒
        '%m/%d/%Y %H:%M:%S',  # 月/日/西元年 時:分:秒
        '%b %d, %Y %I:%M:%S %p',  # 英文月份 日, 西元年 12小時制時:分:秒 AM/PM
        '%Y/%m/%d',           # 西元年/月/日
        '%Y-%m-%d',           # 西元年-月-日
        '%d/%m/%Y',           # 日/月/西元年
        '%m/%d/%Y',           # 月/日/西元年
        '%b %d, %Y',          # 英文月份 日, 西元年
    ]

    # 預處理日期字串（移除前後空白）
    date_str = date_str.strip()

    # 嘗試各種日期格式進行轉換
    for date_format in date_formats:
        try:
            date_obj = datetime.strptime(date_str, date_format)
            # 若原始格式沒有時間部分，則加上 00:00:00
            if len(date_format) <= 10:  # 只有日期部分
                return date_obj.strftime('%Y-%m-%d 00:00:00')
            return date_obj.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

    print(f"無法解析日期格式: {date_str}")
    return None


def validate_coordinate(value: float, is_latitude: bool = True) -> Optional[float]:
    # 驗證並處理經緯度值
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
        # 設定 API 基本網址和參數
        self.base_url = "https://cloud.culture.tw/frontsite/trans/SearchShowAction.do"
        self.params = {
            "method": "doFindTypeJ",
            "category": "all"
        }

        # 設定重試策略
        retry_strategy = Retry(
            total=3,  # 最多重試 3 次
            backoff_factor=1,  # 重試間隔時間
            status_forcelist=[500, 502, 503, 504]  # 需要重試的 HTTP 狀態碼
        )

        # 建立帶有重試機制的 session
        self.session = requests.Session()
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def make_request(self, url, params=None):
        # 發送請求並處理可能的錯誤
        max_retries = 3  # 最大重試次數
        retry_delay = 5  # 重試間隔 5 秒
        timeout = 30  # 請求超時 30 秒

        for attempt in range(max_retries):
            try:
                # 發送 API 請求
                response = self.session.get(
                    url,
                    params=params,
                    timeout=timeout,
                    verify=True  # 啟用 SSL 驗證
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
        # 提取並處理活動資訊
        show_info_list = []
        if 'showInfo' in event:
            for show in event['showInfo']:
                # 檢查並安全地獲取時間資訊
                start_date = show.get('time', {})
                end_date = show.get('endTime', {})

                # 格式化展演資訊
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

        # 處理圖片網址
        image_url = event.get('imageURL', '')
        if image_url and not image_url.startswith('http'):
            image_url = f"https://cloud.culture.tw{image_url}"

        # 處理主辦單位：從串列中提取第一個元素
        master_unit = event.get('masterUnit', [])
        if isinstance(master_unit, list) and master_unit:
            master_unit = master_unit[0]  # 取得第一個元素
        elif isinstance(master_unit, str):
            master_unit = master_unit
        else:
            master_unit = ''  # 若為空串列或其他類型，設為空字串

        # 建立過濾後的資料結構
        filtered_data = {
            'UID': event.get('UID', ''),
            '活動名稱': event.get('title', ''),
            '演出單位': event.get('showUnit', ''),
            '簡介說明': event.get('descriptionFilterHtml', ''),
            '圖片連結': image_url,
            '主辦單位': master_unit,
            '網址': event.get('webSales', '') if event.get('webSales', '').strip() else event.get('sourceWebPromote', ''),
            '相關資訊': show_info_list
        }
        return filtered_data

    def filter_festival_data(self, festival):
        # 過濾節慶活動資料
        # 處理圖片網址
        image_url = festival.get('imageUrl', '')
        if image_url and not image_url.startswith('http'):
            image_url = f"https://cloud.culture.tw{image_url}"

        # 格式化節慶活動資料
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
            # 設定查詢參數
            self.params["category"] = category
            raw_data = self.make_request(self.base_url, self.params)
            filtered_data = [self.filter_event_data(event) for event in raw_data]

            # 建立輸出目錄
            os.makedirs("culture_api", exist_ok=True)

            # 產生檔案名稱（包含時間戳記）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            if category == "all":
                category_name = "所有"
            elif category == "11":
                category_name = "文化部整合綜藝活動"
            else:
                category_name = f"類別{category}"
            filename = f"culture_api/{category_name}藝文活動_{timestamp}.json"

            # 儲存資料為 JSON 檔案
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

            # 處理每筆活動資料
            for event in filtered_data:
                # 使用第一個展演資訊（如果有的話）
                show_info = event['相關資訊'][0] if event['相關資訊'] else {}

                # 處理經緯度
                latitude = validate_coordinate(show_info.get('緯度'), True)
                longitude = validate_coordinate(show_info.get('經度'), False)

                # 處理網址：優先使用售票網址，若為空則使用活動網址
                source_url = event.get('網址', '').strip()
                if not source_url:
                    source_url = event.get('sourceWebPromote', '').strip()

                # 格式化單筆活動資料
                formatted_event = {
                    "uid": str(event['UID']),
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
                    "url": source_url,
                    "imageUrl": str(event['圖片連結'])
                }
                formatted_data["result"].append(formatted_event)

            return formatted_data

        except requests.exceptions.RequestException as e:
            print(f"獲取資料時發生錯誤：{str(e)}")
            return {"result": [], "error": str(e)}

    def get_integrated_events(self):
        # 獲取文化部整合綜藝活動資料（包含表演、美食、講座、旅遊等綜合類型之整合活動）
        return self.get_events(category="11")

    def get_festival_events(self):
        # 獲取文化部節慶活動資料
        try:
            # 設定查詢參數
            params = {
                "method": "doFindFestivalTypeJ"
            }
            raw_data = self.make_request(self.base_url, params)
            filtered_data = [self.filter_festival_data(
                festival) for festival in raw_data]

            # 建立輸出目錄
            os.makedirs("culture_api", exist_ok=True)

            # 產生檔案名稱（包含時間戳記）
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"culture_api/文化部節慶活動_{timestamp}.json"

            # 儲存資料為 JSON 檔案
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

            # 處理每筆節慶活動資料
            for festival in filtered_data:
                # 處理經緯度
                latitude = validate_coordinate(festival['緯度'], True)
                longitude = validate_coordinate(festival['經度'], False)

                # 格式化單筆節慶活動資料
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
