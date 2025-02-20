import requests
import json
from datetime import datetime
import os


def convert_date_format(date_str):
    """將日期時間字串轉換為標準格式 (YYYY-MM-DD HH:MM:SS)"""
    if not date_str:
        return None

    # 定義可能的日期格式
    date_formats = [
        '%Y/%m/%d %H:%M:%S',  # 2025/01/31 00:00:00
        '%Y-%m-%d %H:%M:%S',  # 2025-01-31 00:00:00
        '%Y/%m/%d',           # 2025/01/31
        '%Y-%m-%d',           # 2025-01-31
        '%m/%d/%Y %H:%M:%S',  # 01/31/2025 00:00:00
        '%m/%d/%Y',           # 01/31/2025
    ]

    for date_format in date_formats:
        try:
            dt = datetime.strptime(date_str, date_format)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

    print(f"無法解析的日期格式: {date_str}")
    return None


def fetch_taipei_events():
    """
    從台北市政府開放資料平台獲取活動資訊
    """
    url = "https://www.gov.taipei/OpenData.aspx?SN=DD102593FDB1A032"

    try:
        response = requests.get(url)
        response.raise_for_status()

        try:
            # 先嘗試直接解析
            events = response.json()
        except json.JSONDecodeError:
            # 如果失敗，使用 utf-8-sig 重新解碼
            content = response.content.decode('utf-8-sig')
            events = json.loads(content)

        # 建立固定名稱的輸出目錄
        output_dir = "taipei_api"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 儲存完整資料（檔名包含時間戳記）
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = os.path.join(
            output_dir, f"市政網站整合平台之熱門活動_{timestamp}.json")
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
            try:
                # 轉換日期格式
                start_date = convert_date_format(event.get("活動開始時間", ""))
                end_date = convert_date_format(event.get("活動結束時間", ""))

                # 確保所有欄位都是字串或 None
                formatted_event = {
                    "uid": str(event.get("DataSN", "")),
                    "title": str(event.get("title", "")),
                    "description": str(event.get("內容", "")),
                    "organizer": str(event.get("主辦單位", "")),
                    "address": str(event.get("活動地址", "")),
                    "startDate": start_date,
                    "endDate": end_date,
                    "location": str(event.get("地點", "")),
                    "latitude": None,
                    "longitude": None,
                    "price": str(event.get("費用", "")),
                    "url": str(event.get("Source", "")),
                    "imageUrl": str(event.get("相關圖片")[0]["url"]) if event.get("相關圖片") and len(event.get("相關圖片")) > 0 else ""
                }
                formatted_data["result"].append(formatted_event)
            except Exception as e:
                print(f"處理活動資料時發生錯誤: {e}")
                continue

        return formatted_data
        # return events

    except requests.exceptions.RequestException as e:
        print(f"獲取資料時發生錯誤: {e}")
        return {"result": []}
    except json.JSONDecodeError as e:
        print(f"解析JSON資料時發生錯誤: {e}")
        return {"result": []}
    except Exception as e:
        print(f"發生未預期的錯誤: {e}")
        return {"result": []}


if __name__ == "__main__":
    fetch_taipei_events()
