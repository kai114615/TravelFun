import os
import sys
import django
import time
from datetime import datetime
import mysql.connector
import json
from typing import Dict, Any, Optional

# 設定專案根目錄路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
django_root = os.path.dirname(current_dir)  # DjangoAdmin2 目錄
project_dir = os.path.dirname(django_root)  # TravelFun 專案根目錄

# 將目前目錄加入 Python 路徑
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 將 DjangoAdmin2 目錄加入 Python 路徑
if django_root not in sys.path:
    sys.path.append(django_root)

# 設定 Django 設定模組
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')

# 初始化 Django 框架
try:
    django.setup()
except Exception as e:
    print(f"Django 設定錯誤: {e}")
    print(f"目前的 Python 路徑: {sys.path}")
    sys.exit(1)

# 全域設定參數
CONFIG = {
    'paths': {
        'json': os.path.join(project_dir, 'src', 'assets', 'theme_entertainment', 'events_data.json'),
        'sql': os.path.join(current_dir, 'events_data.sql')  # SQL 檔案存放路徑
    },
    'db': {
        'host': os.environ.get('DB_HOST', 'localhost'),  # 資料庫主機位址
        'user': os.environ.get('DB_USER', 'root'),      # 資料庫使用者名稱
        'password': os.environ.get('DB_PASSWORD', 'P@ssw0rd'),  # 資料庫密碼
        'database': 'fun'  # 資料庫名稱
    }
}

# 匯入相關模組
try:
    from culture_api import CultureAPI  # 文化部 API
    from tfam_api import TaipeiOpenDataAPI  # 北美館 API
    from taipei_api import fetch_taipei_events as taipei_events  # 台北市政府 API
    from newtaipei_api import fetch_newtaipei_events as newtaipei_events  # 新北市政府 API
    from json_to_sql import convert_json_to_sql  # JSON 轉 SQL 工具
except ImportError as e:
    print(f"模組匯入錯誤: {e}")
    print(f"目前的 Python 路徑: {sys.path}")
    sys.exit(1)

def init_database() -> None:
    """初始化資料庫和資料表"""
    try:
        from django.core.management import execute_from_command_line

        # 執行資料庫遷移指令
        execute_from_command_line(['manage.py', 'makemigrations', 'theme_entertainment'])
        execute_from_command_line(['manage.py', 'migrate'])

        print("資料庫初始化成功！")
    except Exception as e:
        print(f"資料庫初始化失敗：{str(e)}")
        raise

def connect_to_mysql() -> mysql.connector.connection.MySQLConnection:
    """建立 MySQL 資料庫連線"""
    return mysql.connector.connect(**CONFIG['db'])

def parse_date(date_str: str) -> str:
    """解析各種日期格式，並轉換為 MySQL 可接受的格式 (西元年-月-日)"""
    if not date_str:
        return None

    try:
        # 移除時間部分
        if ' ' in date_str:
            date_str = date_str.split(' ')[0]

        # 支援的日期格式清單
        date_formats = [
            '%Y/%m/%d',  # 西元年/月/日
            '%m/%d/%Y',  # 月/日/西元年
            '%Y-%m-%d',  # 西元年-月-日
            '%Y.%m.%d',  # 西元年.月.日
        ]

        # 嘗試解析不同格式
        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # 處理時間戳記格式
        try:
            timestamp = float(date_str)
            dt = datetime.fromtimestamp(timestamp)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            pass

        print(f"無法解析的日期格式: {date_str}")
        return None

    except Exception as e:
        print(f"日期解析錯誤 '{date_str}': {str(e)}")
        return None

def save_to_mysql(data: Dict[str, Any], connection: mysql.connector.connection.MySQLConnection) -> None:
    """將資料儲存至 MySQL 資料庫"""
    if not data:
        return

    cursor = None
    try:
        cursor = connection.cursor(buffered=True)

        # 資料表欄位對應的插入語法
        insert_sql = """
        INSERT INTO theme_events (
            uid, activity_name, description, organizer, address,
            start_date, end_date, location, latitude, longitude,
            ticket_price, source_url, image_url
        ) VALUES (
            %(uid)s, %(activity_name)s, %(description)s, %(organizer)s, %(address)s,
            %(start_date)s, %(end_date)s, %(location)s, %(latitude)s, %(longitude)s,
            %(ticket_price)s, %(source_url)s, %(image_url)s
        ) ON DUPLICATE KEY UPDATE
            activity_name = VALUES(activity_name),
            description = VALUES(description),
            organizer = VALUES(organizer),
            address = VALUES(address),
            start_date = VALUES(start_date),
            end_date = VALUES(end_date),
            location = VALUES(location),
            latitude = VALUES(latitude),
            longitude = VALUES(longitude),
            ticket_price = VALUES(ticket_price),
            source_url = VALUES(source_url),
            image_url = VALUES(image_url)
        """

        # 處理每筆活動資料
        events = data if isinstance(data, list) else data.get('result', [])
        for event in events:
            event_data = {
                'uid': event.get('uid', ''),
                'activity_name': event.get('activity_name', ''),
                'description': event.get('description', ''),
                'organizer': event.get('organizer', ''),
                'address': event.get('address', ''),
                'start_date': parse_date(event.get('start_date')) if event.get('start_date') else None,
                'end_date': parse_date(event.get('end_date')) if event.get('end_date') else None,
                'location': event.get('location', ''),
                'latitude': event.get('latitude'),
                'longitude': event.get('longitude'),
                'ticket_price': event.get('ticket_price', ''),
                'source_url': event.get('source_url', ''),
                'image_url': event.get('image_url', '')
            }

            try:
                # 執行資料庫插入
                cursor.execute(insert_sql, event_data)
                connection.commit()
            except mysql.connector.Error as err:
                print(f"插入資料時發生錯誤: {err}")
                print(f"問題資料: {event_data}")
                connection.rollback()
                continue

    except Exception as e:
        print(f"儲存資料時發生錯誤: {str(e)}")
        connection.rollback()
        raise
    finally:
        if cursor:
            cursor.close()

def process_image_url(image_url: Any) -> list:
    """處理圖片網址，統一轉換為列表格式"""
    if isinstance(image_url, str):
        return [image_url] if image_url and image_url != "無資料" else []
    elif isinstance(image_url, list):
        return image_url
    return []

def process_event_fields(event: Dict[str, Any], is_new_event: bool, existing_event: Optional[Dict[str, Any]], current_time: str) -> Dict[str, Any]:
    """處理活動欄位資料，根據是否為新活動進行不同處理"""
    # 處理日期欄位
    start_time = event.get('start_time') or event.get('startDate')
    end_time = event.get('end_time') or event.get('endDate')

    # 處理圖片網址
    image_url = process_image_url(event.get('imageUrl', []))

    # 準備新活動資料
    new_event = {
        'uid': event.get('uid', ''),
        'activity_name': event.get('title', ''),
        'description': event.get('description', ''),
        'organizer': event.get('organizer', ''),
        'address': event.get('address', ''),
        'start_date': start_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(start_time, datetime) else start_time,
        'end_date': end_time.strftime('%Y-%m-%d %H:%M:%S') if isinstance(end_time, datetime) else end_time,
        'location': event.get('location', ''),
        'latitude': event.get('latitude', ''),
        'longitude': event.get('longitude', ''),
        'ticket_price': event.get('price', ''),
        'source_url': event.get('url', ''),
        'image_url': image_url
    }

    if is_new_event:
        # 新活動處理
        new_event['created_at'] = current_time
        new_event['updated_at'] = current_time

        # 處理空值欄位
        for field in ['activity_name', 'description', 'organizer', 'address',
                     'start_date', 'end_date', 'location', 'latitude', 'longitude',
                     'ticket_price', 'source_url']:
            if not new_event.get(field) or new_event[field] == 'None':
                new_event[field] = "無資料"
    else:
        # 既有活動處理
        new_event['created_at'] = existing_event.get('created_at')
        has_changes = False

        # 檢查欄位變更
        for field in ['activity_name', 'description', 'organizer', 'address',
                     'start_date', 'end_date', 'location', 'latitude', 'longitude',
                     'ticket_price', 'source_url']:
            existing_value = existing_event.get(field)
            new_value = new_event.get(field)

            if not existing_value or existing_value in ['無資料', 'None', '']:
                if new_value and new_value not in ['None', '']:
                    new_event[field] = new_value
                    has_changes = True
                else:
                    new_event[field] = '無資料'
            else:
                new_event[field] = existing_value

        # 更新時間戳記
        if has_changes or new_event['image_url'] != existing_event.get('image_url', []):
            new_event['updated_at'] = current_time
        else:
            new_event['updated_at'] = existing_event.get('updated_at')

    return new_event

def save_events_to_json(events_data):
    """將活動資料轉換成 JSON 格式並儲存"""
    try:
        formatted_events = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        json_path = CONFIG['paths']['json']

        # 建立目標目錄
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        # 載入既有資料
        existing_events = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    old_events = json.load(f)
                    existing_events = {event.get('uid'): event for event in old_events}
            except (json.JSONDecodeError, FileNotFoundError):
                print("無法讀取既有的 events_data.json 或檔案格式錯誤")

        # 處理每個活動
        for event in events_data:
            event_uid = event.get('uid', '')
            existing_event = existing_events.get(event_uid)
            is_new_event = not existing_event

            # 處理活動欄位
            new_event = process_event_fields(event, is_new_event, existing_event, current_time)
            formatted_events.append(new_event)

        # 寫入 JSON 檔案
        print(f"JSON 檔案路徑: {json_path}")
        print(f"處理的活動數量: {len(formatted_events)}")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_events, f, ensure_ascii=False, indent=2)
        print(f'成功: 活動資料已儲存至 {json_path}')

    except Exception as e:
        print(f"錯誤: 儲存 JSON 檔案失敗 - {str(e)}")

def check_events_data_exists() -> bool:
    """檢查 events_data.json 檔案是否存在"""
    return os.path.exists(CONFIG['paths']['json'])

def load_existing_events() -> Dict[str, Any]:
    """載入既有的 events_data.json 檔案"""
    try:
        with open(CONFIG['paths']['json'], 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def update_events_data(existing_events: list, new_events: list) -> list:
    """更新活動資料，使用 uid 作為唯一識別碼"""
    # 建立既有活動的 uid 索引
    existing_uids = {event['uid']: event for event in existing_events}

    # 更新或新增活動
    for new_event in new_events:
        uid = new_event.get('uid')
        if uid:
            existing_uids[uid] = new_event

    return list(existing_uids.values())

def clean_sql_command(command: str) -> str:
    """清理 SQL 指令中的特殊字元"""
    # 替換 HTML 實體
    replacements = {
        '&nbsp;': ' ',
        '&amp;': '&',
        '&lt;': '<',
        '&gt;': '>',
        '&quot;': '"',
        '&apos;': "'",
    }

    result = command
    for entity, char in replacements.items():
        result = result.replace(entity, char)

    # 移除多餘空白
    result = ' '.join(result.split())

    return result

def import_sql_to_database(connection: mysql.connector.connection.MySQLConnection, sql_file_path: str) -> None:
    """將 SQL 檔案匯入資料庫"""
    try:
        cursor = connection.cursor()

        # 讀取 SQL 檔案
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # 分割並清理 SQL 指令
        sql_commands = sql_content.split(';')

        # 執行每個 SQL 指令
        for command in sql_commands:
            if command.strip():
                try:
                    cleaned_command = clean_sql_command(command)
                    if cleaned_command:
                        cursor.execute(cleaned_command)
                        connection.commit()
                except mysql.connector.Error as err:
                    connection.rollback()

        print(f"成功匯入 SQL 檔案: {sql_file_path}")

    except Exception as e:
        print(f"匯入 SQL 檔案時發生錯誤: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()

def main():
    """主程式進入點"""
    print(f"\n=== 開始執行資料獲取程序 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    all_events = []  # 儲存所有活動資料

    try:
        # 檢查既有資料
        if check_events_data_exists():
            print("發現既有活動資料，開始載入...")
            existing_events = load_existing_events()
            print(f"已載入 {len(existing_events)} 筆既有活動資料\n")
            all_events = existing_events

        # 從各 API 獲取最新資料
        print("開始從各 API 獲取最新資料...")

        # 1. 文化部展演資訊
        print("1. 正在獲取文化部展演資訊...")
        culture_api = CultureAPI()
        culture_events = culture_api.get_events()
        all_events = update_events_data(all_events, culture_events.get('result', []))
        print("文化部展演資訊獲取完成！\n")

        integrated_events = culture_api.get_integrated_events()
        all_events = update_events_data(all_events, integrated_events.get('result', []))
        print("文化部整合綜藝活動獲取完成！\n")

        festival_events = culture_api.get_festival_events()
        all_events = update_events_data(all_events, festival_events.get('result', []))
        print("文化部節慶活動獲取完成！\n")

        # 2. 台北市立美術館資訊
        print("2. 正在獲取台北市立美術館資訊...")
        tfam_api_1 = TaipeiOpenDataAPI()  # 展覽資訊
        tfam_api_2 = TaipeiOpenDataAPI("1700a7e6-3d27-47f9-89d9-1811c9f7489c")  # 活動資訊

        results_1 = tfam_api_1.fetch_data(limit=10)
        if results_1:
            all_events = update_events_data(all_events, results_1.get('result', []))

        results_2 = tfam_api_2.fetch_data(limit=10)
        if results_2:
            all_events = update_events_data(all_events, results_2.get('result', []))
        print("台北市立美術館資訊獲取完成！\n")

        # 3. 台北市政府活動資訊
        print("3. 正在獲取台北市政府活動資訊...")
        taipei_data = taipei_events()
        all_events = update_events_data(all_events, taipei_data.get('result', []))
        print("台北市政府活動資訊獲取完成！\n")

        # 4. 新北市政府活動資訊
        print("4. 正在獲取新北市政府活動資訊...")
        newtaipei_data = newtaipei_events()
        all_events = update_events_data(all_events, newtaipei_data.get('result', []))
        print("新北市政府活動資訊獲取完成！\n")

        # 5. 儲存 JSON 資料
        print("\n開始將資料轉換為 JSON...")
        save_events_to_json(all_events)
        print("資料已成功儲存為 JSON！\n")

        # 6. 生成 SQL 檔案
        print("\n開始將 JSON 轉換為 SQL...")
        convert_json_to_sql(CONFIG['paths']['json'], CONFIG['paths']['sql'])
        print("成功: SQL 檔案已生成\n")

        # 7. 初始化資料庫
        print("\n開始初始化資料庫...")
        init_database()
        print("資料庫初始化完成！\n")

        # 8. 建立資料庫連線
        print("\n開始建立資料庫連線...")
        connection = connect_to_mysql()
        print("資料庫連線建立成功！\n")

    except Exception as e:
        print(f"\n執行過程中發生錯誤：{str(e)}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()

if __name__ == "__main__":
    main()
