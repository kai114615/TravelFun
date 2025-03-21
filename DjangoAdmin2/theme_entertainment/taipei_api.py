import requests
import json
from datetime import datetime
import os
import csv
import io
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def convert_date_format(date_str):
    # 將日期時間字串轉換為標準格式 (YYYY-MM-DD HH:MM:SS)
    if not date_str:
        return None

    # 定義可能的日期格式清單
    date_formats = [
        '%Y/%m/%d %H:%M:%S',  # 西元年/月/日 時:分:秒
        '%Y-%m-%d %H:%M:%S',  # 西元年-月-日 時:分:秒
        '%Y/%m/%d',           # 西元年/月/日
        '%Y-%m-%d',           # 西元年-月-日
        '%m/%d/%Y %H:%M:%S',  # 月/日/西元年 時:分:秒
        '%m/%d/%Y',           # 月/日/西元年
    ]

    # 嘗試各種日期格式進行轉換
    for date_format in date_formats:
        try:
            dt = datetime.strptime(date_str, date_format)
            return dt.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

    print(f"無法解析的日期格式: {date_str}")
    return None


def fetch_taipei_events():
    # 從台北市政府開放資料平台獲取活動資訊
    url = "https://www.gov.taipei/OpenData.aspx?SN=DD102593FDB1A032"

    # 設定重試策略
    retry_strategy = Retry(
        total=3,  # 最多重試 3 次
        backoff_factor=1,  # 重試間隔時間
        status_forcelist=[429, 500, 502, 503, 504],  # 增加 429 (Too Many Requests)
        allowed_methods=["GET", "POST"]  # 明確指定允許的請求方法
    )

    # 建立帶有重試機制的 session
    session = requests.Session()
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)

    # 定義手動重試參數
    max_retries = 3  # 最大重試次數
    retry_delay = 5  # 重試間隔 5 秒
    timeout = 30  # 請求超時 30 秒

    print(f"開始從 {url} 獲取台北市活動資料")

    for attempt in range(max_retries):
        try:
            # 發送 API 請求
            # print(f"第 {attempt + 1} 次發送請求")
            response = session.get(
                url,
                timeout=(15, timeout),  # 設置連接超時和讀取超時分開配置
                verify=True,  # 啟用 SSL 驗證
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                    'Accept': 'application/json, text/plain, */*',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
                }
            )
            response.raise_for_status()

            # 檢查回應內容長度
            if len(response.content) < 100:  # 若內容太短可能是錯誤頁面
                print(f"回應內容過短，可能不是有效資料: {response.content[:100]}")
                if attempt < max_retries - 1:
                    print(f"{retry_delay}秒後進行第{attempt + 2}次嘗試...")
                    time.sleep(retry_delay)
                    continue
                else:
                    print(f"回應內容無效，已達最大重試次數 {max_retries}。")
                    return {"result": []}

            try:
                # 先嘗試直接解析 JSON
                events = response.json()
                print(f"成功解析 JSON 資料，包含 {len(events)} 筆記錄")
            except json.JSONDecodeError:
                # 若 JSON 解析失敗，使用 utf-8-sig 重新解碼
                # print("直接解析 JSON 失敗，嘗試使用 utf-8-sig 解碼")
                content = response.content.decode('utf-8-sig', errors='replace')
                events = json.loads(content)
                # print(f"使用 utf-8-sig 解碼後成功解析，包含 {len(events)} 筆記錄")

            # 建立固定名稱的輸出目錄
            output_dir = "taipei_api"
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"建立輸出目錄: {output_dir}")

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

            # 處理每筆活動資料
            for event in events:
                try:
                    # 轉換日期格式
                    start_date = convert_date_format(event.get("活動開始時間", ""))
                    end_date = convert_date_format(event.get("活動結束時間", ""))

                    # 格式化單筆活動資料
                    formatted_event = {
                        "uid": str(event.get("DataSN", "")),
                        "title": str(event.get("title", "")),
                        "description": str(event.get("內容", "")),
                        # 優先使用主辦單位，若為空則使用發布單位
                        "organizer": str(event.get('主辦單位', '') if event.get('主辦單位', '').strip() else event.get('發布單位', '') or event.get('發布單位(科室)', '')),
                        "address": str(event.get("活動地址", "")),
                        "startDate": start_date,
                        "endDate": end_date,
                        "location": str(event.get("地點", "")),
                        "latitude": None,  # 台北市活動資料無經緯度資訊
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

        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                print(f"請求超時，{retry_delay}秒後進行第{attempt + 2}次嘗試...")
                time.sleep(retry_delay)
                # 每次重試增加超時時間
                timeout += 30
                continue
            else:
                print(f"請求超時，已達最大重試次數 {max_retries}。")
                return {"result": []}

        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                print(f"請求失敗，{retry_delay}秒後進行第{attempt + 2}次嘗試... 錯誤: {e}")
                time.sleep(retry_delay)
                # 每次重試增加超時時間
                timeout += 30
                continue
            else:
                print(f"請求失敗，已達最大重試次數 {max_retries}。錯誤: {e}")
                return {"result": []}

        except json.JSONDecodeError as e:
            if attempt < max_retries - 1:
                print(f"JSON解析錯誤，{retry_delay}秒後進行第{attempt + 2}次嘗試... 錯誤: {e}")
                time.sleep(retry_delay)
                continue
            else:
                print(f"JSON解析錯誤，已達最大重試次數 {max_retries}。錯誤: {e}")
                return {"result": []}

        except Exception as e:
            if attempt < max_retries - 1:
                print(f"發生未預期錯誤，{retry_delay}秒後進行第{attempt + 2}次嘗試... 錯誤: {e}")
                time.sleep(retry_delay)
                continue
            else:
                print(f"發生未預期錯誤，已達最大重試次數 {max_retries}。錯誤: {e}")
                return {"result": []}


if __name__ == "__main__":
    fetch_taipei_events()
