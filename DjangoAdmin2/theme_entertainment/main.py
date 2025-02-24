import os
import sys
import django
import time
from datetime import datetime
import mysql.connector
import json
from typing import Dict, Any
# from django.core.cache import cache

# 設定專案根目錄
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

# 初始化 Django
try:
    django.setup()
except Exception as e:
    print(f"Django 設定錯誤: {e}")
    print(f"目前的 Python 路徑: {sys.path}")
    sys.exit(1)

# 全域設定
CONFIG = {
    'paths': {
        'json': os.path.join(project_dir, 'src', 'assets', 'theme_entertainment', 'events_data.json'),
        # SQL 檔案放在 theme_entertainment/sql 目錄下
        'sql': os.path.join(current_dir, 'events_data.sql')
    },
    'db': {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', 'P@ssw0rd'),
        'database': 'fun'
    }
}

# 導入相關模組
try:
    from culture_api import CultureAPI
    from tfam_api import TaipeiOpenDataAPI
    from taipei_api import fetch_taipei_events as taipei_events
    from newtaipei_api import fetch_newtaipei_events as newtaipei_events
    from json_to_sql import convert_json_to_sql
except ImportError as e:
    print(f"模組導入錯誤: {e}")
    print(f"目前的 Python 路徑: {sys.path}")
    sys.exit(1)


def init_database() -> None:
    """初始化資料庫和資料表"""
    try:
        # 由於已經有 models.py 定義好資料庫模型，
        # 這裡只需要執行 Django migrations 即可
        from django.core.management import execute_from_command_line

        # 執行 makemigrations
        execute_from_command_line(
            ['manage.py', 'makemigrations', 'theme_entertainment'])

        # 執行 migrate
        execute_from_command_line(['manage.py', 'migrate'])

        print("資料庫初始化成功！")
    except Exception as e:
        print(f"資料庫初始化失敗：{str(e)}")
        raise


def connect_to_mysql() -> mysql.connector.connection.MySQLConnection:
    """建立MySQL資料庫連接"""
    return mysql.connector.connect(**CONFIG['db'])


def parse_date(date_str: str) -> str:
    """解析各種可能的日期格式，並轉換為 MySQL 可接受的格式 (YYYY-MM-DD)"""
    if not date_str:
        return None

    try:
        # 移除可能的時間部分
        if ' ' in date_str:
            date_str = date_str.split(' ')[0]

        # 嘗試不同的日期格式
        date_formats = [
            '%Y/%m/%d',  # YYYY/MM/DD
            '%m/%d/%Y',  # MM/DD/YYYY
            '%Y-%m-%d',  # YYYY-MM-DD
            '%Y.%m.%d',  # YYYY.MM.DD
        ]

        for date_format in date_formats:
            try:
                parsed_date = datetime.strptime(date_str, date_format)
                return parsed_date.strftime('%Y-%m-%d')
            except ValueError:
                continue

        # 如果是時間戳記格式
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
    """將資料儲存到MySQL資料庫"""
    if not data:
        return

    cursor = None
    try:
        cursor = connection.cursor(buffered=True)

        # 修改插入語句以匹配 events_data.json 的欄位
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

        # 處理每筆資料
        events = data if isinstance(data, list) else data.get('result', [])
        for event in events:
            event_data = {
                'uid': event.get('uid', ''),
                'activity_name': event.get('activity_name', ''),
                'description': event.get('description', ''),
                # 直接獲取 organizer，不需要特別處理 list
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
                # 執行SQL插入
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


def save_events_to_json(events_data):
    """
    將活動資料轉換成JSON格式並儲存，包含更新機制
    """
    try:
        formatted_events = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        json_path = CONFIG['paths']['json']

        # 確保目標目錄存在
        os.makedirs(os.path.dirname(json_path), exist_ok=True)

        # 檢查是否存在舊的 events_data.json
        existing_events = {}
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    old_events = json.load(f)
                    existing_events = {
                        event.get('uid'): event for event in old_events}
            except (json.JSONDecodeError, FileNotFoundError):
                print("無法讀取舊的 events_data.json 或檔案格式錯誤")

        for event in events_data:
            # 處理不同的日期欄位名稱
            start_time = event.get('start_time') or event.get('startDate')
            end_time = event.get('end_time') or event.get('endDate')

            event_uid = event.get('uid', '')
            existing_event = existing_events.get(event_uid)

            # 處理圖片 URL
            image_url = event.get('imageUrl', [])
            if isinstance(image_url, str):
                # 如果是字串，轉換為列表
                image_url = [
                    image_url] if image_url and image_url != "無資料" else []
            elif not isinstance(image_url, list):
                # 如果既不是字串也不是列表，設為空列表
                image_url = []

            # 準備新的事件資料
            new_event = {
                'uid': event_uid,
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
                'image_url': image_url  # 現在儲存為列表
            }

            # 檢查是否為新事件
            is_new_event = not existing_event

            # 如果是新事件，設置時間戳記
            if is_new_event:
                new_event['created_at'] = current_time
                new_event['updated_at'] = current_time
            else:
                # 保留現有的 created_at
                new_event['created_at'] = existing_event.get('created_at')
                # 合併現有的圖片列表
                existing_images = existing_event.get('image_url', [])
                if isinstance(existing_images, list) and existing_images:
                    new_event['image_url'] = list(
                        set(existing_images + image_url))

            # 檢查所有欄位是否有變動
            has_changes = False
            for field in ['activity_name', 'description', 'organizer', 'address',
                          'start_date', 'end_date', 'location', 'latitude', 'longitude',
                          'ticket_price', 'source_url']:

                # 取得新值
                new_value = new_event.get(field)

                # 檢查新值是否為空或"None"
                if not new_value or new_value == 'None':
                    new_event[field] = "無資料"
                    # 如果是既有事件且值有變化，標記為有變動
                    if not is_new_event and existing_event.get(field) != "無資料":
                        has_changes = True
                else:
                    if is_new_event:
                        # 新事件直接使用新值
                        new_event[field] = new_value
                    else:
                        # 既有事件且現有值不為"無資料"時保留現有值
                        existing_value = existing_event.get(field)
                        if existing_value != "無資料":
                            new_event[field] = existing_value
                        else:
                            new_event[field] = new_value
                            has_changes = True

            # 根據是否有變動更新 updated_at
            if not is_new_event:
                if has_changes or new_event['image_url'] != existing_event.get('image_url', []):
                    new_event['updated_at'] = current_time
                else:
                    new_event['updated_at'] = new_event['created_at']

            formatted_events.append(new_event)

        # 添加更詳細的日誌
        print(f"JSON 檔案路徑: {json_path}")
        print(f"處理的活動數量: {len(formatted_events)}")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_events, f, ensure_ascii=False, indent=2)
        print(f'成功: 活動資料已儲存至 {json_path}')

    except Exception as e:
        print(f"錯誤: 儲存 JSON 檔案失敗 - {str(e)}")


def check_events_data_exists() -> bool:
    """檢查 events_data.json 是否存在"""
    return os.path.exists(CONFIG['paths']['json'])


def load_existing_events() -> Dict[str, Any]:
    """載入現有的 events_data.json"""
    try:
        with open(CONFIG['paths']['json'], 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def update_events_data(existing_events: list, new_events: list) -> list:
    """更新活動資料，使用 uid 作為唯一識別"""
    # 建立現有活動的 uid 索引
    existing_uids = {event['uid']: event for event in existing_events}

    # 更新或添加新活動
    for new_event in new_events:
        uid = new_event.get('uid')
        if uid:
            existing_uids[uid] = new_event

    return list(existing_uids.values())


def clean_sql_command(command: str) -> str:
    """清理 SQL 命令中的特殊字符"""
    # 替換常見的 HTML 實體
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

    # 移除多餘的空白字符
    result = ' '.join(result.split())

    return result


def import_sql_to_database(connection: mysql.connector.connection.MySQLConnection, sql_file_path: str) -> None:
    """將 SQL 檔案匯入資料庫"""
    try:
        cursor = connection.cursor()

        # 讀取 SQL 檔案
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # 分割並清理每個 SQL 命令
        sql_commands = sql_content.split(';')

        # 執行每個 SQL 命令
        for command in sql_commands:
            if command.strip():
                try:
                    # 清理 SQL 命令
                    cleaned_command = clean_sql_command(command)
                    if cleaned_command:
                        cursor.execute(cleaned_command)
                        connection.commit()
                except mysql.connector.Error as err:
                    # print(f"執行 SQL 命令時發生錯誤: {err}")
                    # print(f"問題的 SQL 命令: {cleaned_command}")
                    connection.rollback()

        print(f"成功匯入 SQL 檔案: {sql_file_path}")

    except Exception as e:
        print(f"匯入 SQL 檔案時發生錯誤: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()


def main():
    print(
        f"\n=== 開始執行資料獲取程序 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    all_events = []  # 用來收集所有活動資料

    try:
        # 檢查是否存在 events_data.json
        if check_events_data_exists():
            print("發現現有活動資料，開始載入...")
            existing_events = load_existing_events()
            print(f"已載入 {len(existing_events)} 筆現有活動資料\n")
            all_events = existing_events

        # 無論是否有現有資料，都執行 API 更新
        print("開始從各 API 獲取最新資料...")

        # 1. 執行文化部展演資訊 API
        print("1. 正在獲取文化部展演資訊...")
        culture_api = CultureAPI()
        culture_events = culture_api.get_events()
        all_events = update_events_data(
            all_events, culture_events.get('result', []))
        print("文化部展演資訊獲取完成！\n")

        integrated_events = culture_api.get_integrated_events()
        all_events = update_events_data(
            all_events, integrated_events.get('result', []))
        print("文化部整合綜藝活動獲取完成！\n")

        festival_events = culture_api.get_festival_events()
        all_events = update_events_data(
            all_events, festival_events.get('result', []))
        print("文化部節慶活動獲取完成！\n")

        # 2. 執行台北市立美術館 API
        print("2. 正在獲取台北市立美術館資訊...")
        tfam_api_1 = TaipeiOpenDataAPI()  # 展覽資訊
        tfam_api_2 = TaipeiOpenDataAPI(
            "1700a7e6-3d27-47f9-89d9-1811c9f7489c")  # 活動資訊

        results_1 = tfam_api_1.fetch_data(limit=10)
        if results_1:
            all_events = update_events_data(
                all_events, results_1.get('result', []))

        results_2 = tfam_api_2.fetch_data(limit=10)
        if results_2:
            all_events = update_events_data(
                all_events, results_2.get('result', []))
        print("台北市立美術館資訊獲取完成！\n")

        # 3. 執行台北市政府開放資料 API
        print("3. 正在獲取台北市政府活動資訊...")
        taipei_data = taipei_events()
        all_events = update_events_data(
            all_events, taipei_data.get('result', []))
        print("台北市政府活動資訊獲取完成！\n")

        # 4. 執行新北市政府開放資料 API
        print("4. 正在獲取新北市政府活動資訊...")
        newtaipei_data = newtaipei_events()
        all_events = update_events_data(
            all_events, newtaipei_data.get('result', []))
        print("新北市政府活動資訊獲取完成！\n")

        # 5. 將更新後的資料儲存為 JSON
        print("\n開始將資料轉換為 JSON...")
        save_events_to_json(all_events)
        print("資料已成功儲存為 JSON！\n")

        # 6. 執行 json_to_sql.py 生成 SQL 檔案
        print("\n開始將 JSON 轉換為 SQL...")

        convert_json_to_sql(CONFIG['paths']['json'], CONFIG['paths']['sql'])
        print("成功: SQL 檔案已生成\n")

        # 7. 初始化資料庫
        print("\n開始初始化資料庫...")
        init_database()
        print("資料庫初始化完成！\n")

        # 8. 建立資料庫連接
        print("\n開始建立資料庫連接...")
        connection = connect_to_mysql()
        print("資料庫連接建立成功！\n")

        # 9. 匯入 SQL 檔案到資料庫
        # print("\n開始匯入 SQL 檔案到資料庫...")
        # import_sql_to_database(connection, CONFIG['paths']['sql'])
        # print("SQL 檔案匯入完成！\n")

        # print(f"\n=== 所有資料處理完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
        # print(f"總共處理了 {len(all_events)} 筆活動資料")

    except Exception as e:
        print(f"\n執行過程中發生錯誤：{str(e)}")
    finally:
        if 'connection' in locals() and connection:
            connection.close()


if __name__ == "__main__":
    main()
