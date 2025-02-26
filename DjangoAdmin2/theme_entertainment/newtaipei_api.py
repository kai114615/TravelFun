import requests
import json
from datetime import datetime
import os
import csv
import io
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


def fetch_newtaipei_events():
    """
    從新北市政府開放資料平台獲取活動資訊
    """
    url = "https://data.ntpc.gov.tw/api/datasets/029e3fc2-1927-4534-8702-da7323be969b/csv"

    # 設定請求參數
    timeout = 30  # 設定30秒超時
    max_retries = 3
    retry_delay = 5  # 重試間隔5秒

    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()

            try:
                # 先嘗試解析為 JSON
                events = response.json()
            except json.JSONDecodeError:
                try:
                    # JSON 解析失敗，嘗試解析 CSV
                    csv_content = io.StringIO(response.content.decode('utf-8-sig'))
                    csv_reader = csv.DictReader(csv_content)
                    events = []
                    for row in csv_reader:
                        # 處理 picUrl 欄位，用"、"分割成列表
                        pic_urls = []
                        if row.get("picUrl"):
                            pic_urls = [url.strip() for url in row["picUrl"].split("、") if url.strip()]

                        event = {
                            "id": row.get("id", ""),
                            "title": row.get("title", ""),
                            "activedate": row.get("activedate", ""),
                            "activeenddate": row.get("activeenddate", ""),
                            "description": row.get("description", ""),
                            "classname": row.get("classname", ""),
                            "author": row.get("author", ""),
                            "place": row.get("place", ""),
                            "placeTel": row.get("placeTel", ""),
                            "address": row.get("address", ""),
                            "traffic": row.get("traffic", ""),
                            "abouturl": row.get("abouturl", ""),
                            "picUrl": pic_urls  # 儲存為列表
                        }
                        events.append(event)
                except (csv.Error, UnicodeDecodeError) as e:
                    print(f"CSV 解析錯誤: {e}")
                    raise

            # 將資料轉換為標準格式
            formatted_events = []
            for event in events:
                formatted_event = {
                    "id": event.get("id", ""),
                    "活動名稱": event.get("title", ""),
                    "活動起始日期": event.get("activedate", ""),
                    "活動結束日期": event.get("activeenddate", ""),
                    "簡介說明": event.get("description", ""),
                    "活動類別": event.get("classname", ""),
                    "主辦單位": event.get("author", ""),
                    "活動場地": event.get("place", ""),
                    "場地電話": event.get("placeTel", ""),
                    "地址": event.get("address", ""),
                    "交通說明": event.get("traffic", ""),
                    "相關連結": event.get("abouturl", ""),
                    "圖片連結": event.get("picUrl", [])  # 現在是列表
                }
                formatted_events.append(formatted_event)
            events = formatted_events

            # 建立固定名稱的輸出目錄
            output_dir = "newtaipei_api"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            # 儲存完整資料（檔名包含時間戳記）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(
                output_dir, f"新北市政府近期活動_{timestamp}.json")
            with open(output_file, "w", encoding="utf-8-sig") as f:
                json.dump(events, f, ensure_ascii=False, indent=2)

            print(f"成功獲取 {len(events)} 筆活動資料")
            print(f"資料已儲存至: {output_file}")

            # 將資料轉換為標準格式
            formatted_data = {
                "result": [],
                "queryTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total": len(events),
                "limit": len(events),
                "offset": 0
            }

            for event in events:
                formatted_event = {
                    "uid": event["id"],
                    "title": event["活動名稱"],
                    "description": event["簡介說明"],
                    "organizer": event["主辦單位"],
                    "address": event["地址"],
                    "startDate": convert_date_format(event["活動起始日期"]),
                    "endDate": convert_date_format(event["活動結束日期"]),
                    "location": event["活動場地"],
                    "latitude": None,  # 新北市的資料沒有經緯度資訊
                    "longitude": None,
                    "price": "",  # 新北市的資料沒有價格資訊
                    "url": event["相關連結"],
                    "imageUrl": event["圖片連結"],
                    # [0] if event["圖片連結"] else ""  # 使用第一張圖片，如果有的話
                }
                formatted_data["result"].append(formatted_event)

            return formatted_data

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"請求超時，{retry_delay}秒後進行第{attempt + 2}次嘗試...")
                time.sleep(retry_delay)
                continue
            print(f"請求超時，已重試{max_retries}次仍然失敗")
            return {"result": [], "error": "請求超時"}

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"請求失敗，{retry_delay}秒後進行第{attempt + 2}次嘗試... 錯誤: {e}")
                time.sleep(retry_delay)
                continue
            print(f"獲取資料失敗，已重試{max_retries}次: {e}")
            return {"result": [], "error": str(e)}

        except Exception as e:
            print(f"發生未預期的錯誤: {e}")
            return {"result": [], "error": str(e)}

        # 如果成功獲取數據，跳出重試循環
        break


if __name__ == "__main__":
    fetch_newtaipei_events()
