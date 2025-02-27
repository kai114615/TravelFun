import requests
import json
import os
from typing import Dict, Optional
from datetime import datetime
import socket
import time


def convert_date_format(date_str: Optional[str]) -> Optional[str]:
    # 將日期字串轉換為 MySQL 資料庫可接受的格式 (YYYY-MM-DD HH:MM:SS)
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


class TaipeiOpenDataAPI:
    def __init__(self, dataset_id: str = "fef040da-75d3-42bc-98dd-a292919a251a"):
        # 設定主要和備用的 API 網址
        self.primary_base_url = f"https://data.taipei/api/v1/dataset/{dataset_id}"
        self.backup_base_url = f"https://www.data.taipei/api/v1/dataset/{dataset_id}"
        self.dataset_id = dataset_id
        # 設定 API 請求標頭
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def fetch_data(self,
                   q: Optional[str] = None,
                   limit: Optional[int] = None,
                   offset: Optional[int] = None) -> Dict:
        # 從台北市資料開放平台獲取資料
        urls = [self.primary_base_url, self.backup_base_url]
        max_retries = 3  # 最大重試次數

        # 嘗試不同的 API 網址
        for url in urls:
            retry_count = 0
            while retry_count < max_retries:
                try:
                    # 設定 DNS 查詢超時時間
                    socket.setdefaulttimeout(10)

                    # 設定基本查詢參數
                    params = {
                        "scope": "resourceAquire",
                        "resource_id": self.dataset_id
                    }

                    # 加入可選的查詢參數
                    if q is not None:
                        params['q'] = q
                    if limit is not None:
                        params['limit'] = min(limit, 1000)  # 限制最大筆數為 1000
                    if offset is not None:
                        params['offset'] = offset

                    # 發送 API 請求
                    response = requests.get(
                        url,
                        params=params,
                        headers=self.headers,
                        timeout=30,  # 設定 30 秒請求超時
                        verify=True  # 啟用 SSL 驗證
                    )

                    # 檢查回應狀態
                    if response.status_code != 200:
                        print(f"錯誤回應內容: {response.text}")
                        response.raise_for_status()

                    # 解析 JSON 回應
                    raw_data = response.json()

                    # 處理並格式化資料
                    formatted_data = self._format_response_data(raw_data)
                    if formatted_data:
                        # 儲存原始資料
                        self.save_to_json(raw_data)
                        return formatted_data

                except (requests.exceptions.RequestException,
                        json.JSONDecodeError,
                        socket.timeout) as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        print(f"在 {max_retries} 次嘗試後仍無法訪問 {url}: {str(e)}")
                        break  # 嘗試下一個 URL
                    print(f"第 {retry_count} 次嘗試失敗，等待重試...")
                    time.sleep(2)  # 等待 2 秒後重試
                except Exception as e:
                    print(f"發生未預期的錯誤: {str(e)}")
                    break  # 嘗試下一個 URL

        print("所有 API 端點都無法訪問")
        return {"result": []}

    def _format_response_data(self, raw_data: Dict) -> Dict:
        # 格式化 API 回應資料
        try:
            # 建立基本資料結構
            formatted_data = {
                "result": [],
                "queryTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": raw_data.get("result", {}).get("total", 0),
                "limit": raw_data.get("result", {}).get("limit", 0),
                "offset": raw_data.get("result", {}).get("offset", 0)
            }

            # 處理每筆活動資料
            if "result" in raw_data and "results" in raw_data["result"]:
                for item in raw_data["result"]["results"]:
                    formatted_event = self._format_event(item)
                    if formatted_event:
                        formatted_data["result"].append(formatted_event)

            return formatted_data
        except Exception as e:
            print(f"格式化資料時發生錯誤: {str(e)}")
            return None

    def _format_event(self, item: Dict) -> Dict:
        # 格式化單筆活動資料
        try:
            # 根據不同的資料集 ID 處理資料
            if self.dataset_id == "1700a7e6-3d27-47f9-89d9-1811c9f7489c":
                # 展覽資訊格式
                return {
                    "uid": item.get("_id", ""),
                    "title": item.get("title", ""),
                    "description": item.get("內容", ""),
                    "organizer": "臺北市立美術館",
                    "address": "臺北市中山區中山北路三段181號",
                    "startDate": convert_date_format(item.get("startDate")),
                    "endDate": convert_date_format(item.get("endDate")),
                    "location": "臺北市立美術館",
                    "latitude": 25.072943,
                    "longitude": 121.524536,
                    "price": item.get("price", ""),
                    "url": item.get("url", ""),
                    "imageUrl": item.get("imageUrl", "")
                }
            else:
                # 一般活動資訊格式
                return {
                    "uid": item.get("_id", ""),
                    "title": item.get("title", ""),
                    "description": item.get("內容", ""),
                    "organizer": "臺北市立美術館",
                    "address": "臺北市中山區中山北路三段181號",
                    "startDate": convert_date_format(item.get("startDate")),
                    "endDate": convert_date_format(item.get("endDate")),
                    "location": "臺北市立美術館",
                    "latitude": 25.072943,
                    "longitude": 121.524536,
                    "price": item.get("price", ""),
                    "url": item.get("url", ""),
                    "imageUrl": item.get("imageUrl", "")
                }
        except Exception as e:
            print(f"格式化活動資料時發生錯誤: {str(e)}")
            return None

    def save_to_json(self, data: Dict, filename: Optional[str] = None, output_dir: str = 'tfam_api') -> str:
        # 將資料儲存為 JSON 檔案
        try:
            # 產生時間戳記
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

            # 若是第一次呼叫，設定類別變數儲存時間戳記
            if not hasattr(self, '_current_timestamp'):
                self._current_timestamp = timestamp

            # 使用已存在的時間戳記
            timestamp = self._current_timestamp

            # 建立主要輸出目錄
            os.makedirs(output_dir, exist_ok=True)

            # 根據資料集 ID 建立子目錄
            if self.dataset_id == "1700a7e6-3d27-47f9-89d9-1811c9f7489c":
                sub_dir = "臺北市立美術館_展覽資訊"
            else:
                sub_dir = "臺北市立美術館_活動資訊"

            # 建立完整的子目錄路徑
            full_output_dir = os.path.join(output_dir, sub_dir)
            os.makedirs(full_output_dir, exist_ok=True)

            # 產生檔案名稱
            if filename is None:
                filename = f'taipei_open_data_{timestamp}.json'
            else:
                if not filename.endswith('.json'):
                    filename = f'{filename}_{timestamp}.json'
                else:
                    filename = f'{filename[:-5]}_{timestamp}.json'

            # 組合完整檔案路徑
            file_path = os.path.join(full_output_dir, filename)

            # 儲存資料並加入時間戳記
            with open(file_path, 'w', encoding='utf-8') as f:
                data['timestamp'] = timestamp
                json.dump(data, f, ensure_ascii=False, indent=2)

            print(f"\n資料已成功儲存至: {file_path}")
            return file_path

        except Exception as e:
            print(f"儲存資料時發生錯誤: {str(e)}")
            return None


def main():
    # 建立 API 實例 - 使用預設資料集 ID（活動資訊）
    api_1 = TaipeiOpenDataAPI()
    # 建立第二個 API 實例 - 使用展覽資訊資料集 ID
    api_2 = TaipeiOpenDataAPI("1700a7e6-3d27-47f9-89d9-1811c9f7489c")

    # 測試不同的查詢方式
    test_cases = [
        {"description": "基本查詢（前10筆）", "params": {"limit": 10}},
    ]

    # 測試第一個 API（活動資訊）
    print("\n測試第一個 API:")
    for test_case in test_cases:
        print(f"\n執行{test_case['description']}:")
        results = api_1.fetch_data(**test_case['params'])

        if results:
            filename = f"{test_case['description'].replace(
                '（', '_').replace('）', '_').replace(' ', '_')}.json"
            api_1.save_to_json(results, filename)
        else:
            print("無法取得資料")

    # 測試第二個 API（展覽資訊）
    print("\n測試第二個 API:")
    for test_case in test_cases:
        print(f"\n執行{test_case['description']}:")
        results = api_2.fetch_data(**test_case['params'])

        if results:
            filename = f"{test_case['description'].replace(
                '（', '_').replace('）', '_').replace(' ', '_')}.json"
            api_2.save_to_json(results, filename)
        else:
            print("無法取得資料")


if __name__ == "__main__":
    main()
