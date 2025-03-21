import requests
import json
from datetime import datetime
import os
import time
from requests.adapters import HTTPAdapter
from urllib3.util import Retry


def convert_date_format(date_str):
    """將日期時間字串轉換為標準格式 (YYYY-MM-DD HH:MM:SS)"""
    if not date_str:
        return None

    try:
        # 處理ISO 8601格式 (如：2023-11-04T00:00:00+08:00)
        if 'T' in date_str:
            # 處理包含時區信息的情況
            if '+' in date_str:
                # 去掉時區信息（如 +08:00）
                date_str = date_str.split('+')[0]
            elif 'Z' in date_str:
                # 處理UTC時間（Z結尾）
                date_str = date_str.replace('Z', '')

            # 將T替換為空格
            date_str = date_str.replace('T', ' ')

            # 嘗試解析標準格式
            try:
                dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                return dt.strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                # 可能包含毫秒
                try:
                    dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S.%f')
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                except ValueError:
                    pass
    except Exception as e:
        print(f"ISO 8601格式解析錯誤: {e}")

    # 如果上面的轉換失敗，使用通用的轉換方法
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
        except Exception as e:
            print(f"日期解析錯誤 ({date_format}): {e}")

    print(f"無法解析的日期格式: {date_str}")
    return None


def safe_get(data, key, default=""):
    """安全地獲取字典中的值，避免因為類型錯誤造成異常"""
    try:
        value = data.get(key, default)
        if value is None:
            return default
        return value
    except Exception:
        return default


def fetch_tourism_events():
    """從交通部觀光署觀光資訊資料庫API獲取活動資訊"""
    url = "https://media.taiwan.net.tw/XMLReleaseALL_public/activity_C_f.json"

    # 設定重試策略
    retry_strategy = Retry(
        total=3,  # 最多重試 3 次
        backoff_factor=1,  # 重試間隔時間
        status_forcelist=[429, 500, 502, 503, 504],  # 需要重試的 HTTP 狀態碼
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

    # print(f"開始從 {url} 獲取觀光署活動資料")

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

            events = []
            try:
                # 解析 JSON
                tourism_data = response.json()
                print(f"成功解析 JSON 資料")

                # 檢查資料結構
                if 'XML_Head' not in tourism_data:
                    print("資料結構不符預期，缺少 XML_Head")
                    return {"result": []}

                if 'Infos' not in tourism_data['XML_Head']:
                    print("資料結構不符預期，缺少 Infos")
                    return {"result": []}

                # 取得活動資料列表
                events_data = tourism_data['XML_Head']['Infos'].get('Info', [])
                if not events_data:
                    print("未找到活動資料列表")
                    return {"result": []}

                # 確保events是列表
                if not isinstance(events_data, list):
                    events_data = [events_data]

                events = events_data
                print(f"從觀光署API獲取 {len(events)} 筆活動資料")

            except json.JSONDecodeError:
                # 若 JSON 解析失敗，使用 utf-8-sig 重新解碼
                # print("直接解析 JSON 失敗，嘗試使用 utf-8-sig 解碼")
                content = response.content.decode('utf-8-sig', errors='replace')
                tourism_data = json.loads(content)

                # 檢查資料結構
                if 'XML_Head' not in tourism_data:
                    print("資料結構不符預期，缺少 XML_Head")
                    return {"result": []}

                if 'Infos' not in tourism_data['XML_Head']:
                    print("資料結構不符預期，缺少 Infos")
                    return {"result": []}

                # 取得活動資料列表
                events_data = tourism_data['XML_Head']['Infos'].get('Info', [])
                if not events_data:
                    print("未找到活動資料列表")
                    return {"result": []}

                # 確保events是列表
                if not isinstance(events_data, list):
                    events_data = [events_data]

                events = events_data
                # print(f"使用 utf-8-sig 解碼後成功解析，包含 {len(events)} 筆記錄")

            # 建立固定名稱的輸出目錄
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(current_dir, "tourism_api")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)
                print(f"建立輸出目錄: {output_dir}")

            # 儲存完整資料（檔名包含時間戳記）
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = os.path.join(
                output_dir, f"觀光署活動資料_{timestamp}.json")
            with open(output_file, "w", encoding="utf-8-sig") as f:
                json.dump(tourism_data, f, ensure_ascii=False, indent=2)

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
                    start_date = convert_date_format(safe_get(event, "Start"))
                    end_date = convert_date_format(safe_get(event, "End"))

                    # 組合地址
                    address = ""
                    if safe_get(event, "Add"):
                        address = safe_get(event, "Add")
                    elif safe_get(event, "Region") and safe_get(event, "Town"):
                        address = f"{safe_get(event, 'Region')}{safe_get(event, 'Town')}"

                    # 處理經緯度
                    latitude = None
                    longitude = None
                    try:
                        py_value = safe_get(event, "Py")
                        if py_value and str(py_value) != "0":
                            latitude = float(py_value)
                    except (ValueError, TypeError):
                        pass

                    try:
                        px_value = safe_get(event, "Px")
                        if px_value and str(px_value) != "0":
                            longitude = float(px_value)
                    except (ValueError, TypeError):
                        pass

                    # 處理圖片URL
                    image_urls = []
                    # 收集所有圖片欄位
                    for pic_field in ["Picture1", "Picture2", "Picture3"]:
                        pic_url = safe_get(event, pic_field)
                        if pic_url and isinstance(pic_url, str) and pic_url.strip():
                            image_urls.append(pic_url.strip())

                    # 格式化單筆活動資料
                    formatted_event = {
                        "uid": str(safe_get(event, "Id")),
                        "title": str(safe_get(event, "Name")),
                        "description": str(safe_get(event, "Description")),
                        "organizer": str(safe_get(event, "Org")),
                        "address": str(safe_get(event, "Add")),
                        "startDate": start_date,
                        "endDate": end_date,
                        "location": f"{safe_get(event, 'Region')}{safe_get(event, 'Town')}",
                        "latitude": float(safe_get(event, "Py")),
                        "longitude": float(safe_get(event, "Px")),
                        "price": str(safe_get(event, "Charge")),
                        "url": str(safe_get(event, "Website")),
                        "imageUrl": image_urls,
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
    result = fetch_tourism_events()
    print(f"取得活動數量: {len(result['result'])}")