import os
import sys
import django
import time
import threading
import queue
from datetime import datetime
import mysql.connector
import json
from typing import Dict, Any, Optional, Tuple, List, Callable, Union

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
    from taipei_api import fetch_taipei_events as taipei_events  # 臺北市政府 API
    from newtaipei_api import fetch_newtaipei_events as newtaipei_events  # 新北市政府 API
    from json_to_sql import convert_json_to_sql, escape_sql_special_chars, fix_sql_command  # JSON 轉 SQL 工具和SQL處理函數
    from address_mapping import update_events_coordinates, match_coordinates, update_coordinates  # 地址對應的經緯度
except ImportError as e:
    print(f"模組匯入錯誤: {e}")
    print(f"目前的 Python 路徑: {sys.path}")
    sys.exit(1)

# API 相關定義
API_SOURCES = [
    {
        'name': '文化部展演資訊',
        'function': lambda: CultureAPI().get_events(),
        'result_path': 'result'
    },
    {
        'name': '文化部整合綜藝活動',
        'function': lambda: CultureAPI().get_integrated_events(),
        'result_path': 'result'
    },
    {
        'name': '文化部節慶活動',
        'function': lambda: CultureAPI().get_festival_events(),
        'result_path': 'result'
    },
    {
        'name': '臺北市立美術館展覽資訊',
        'function': lambda: TaipeiOpenDataAPI().fetch_data(limit=10),
        'result_path': 'result'
    },
    {
        'name': '臺北市立美術館活動資訊',
        'function': lambda: TaipeiOpenDataAPI("1700a7e6-3d27-47f9-89d9-1811c9f7489c").fetch_data(limit=10),
        'result_path': 'result'
    },
    {
        'name': '臺北市政府活動資訊',
        'function': taipei_events,
        'result_path': 'result'
    },
    {
        'name': '新北市政府活動資訊',
        'function': newtaipei_events,
        'result_path': 'result'
    }
]

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

def parse_date(date_str: Union[str, None]) -> Optional[str]:
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

def save_to_mysql(data: Dict[str, Any], connection: mysql.connector.connection.MySQLConnection) -> int:
    """將資料儲存至 MySQL 資料庫"""
    if not data:
        return 0

    cursor = None
    inserted_count = 0

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
                inserted_count += 1
            except mysql.connector.Error as err:
                print(f"插入資料時發生錯誤: {err}")
                print(f"問題資料: {event_data}")
                connection.rollback()
                continue

        return inserted_count
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

def process_event_fields(event: Dict[str, Any], is_new_event: bool, existing_event: Optional[Dict[str, Any]], current_time: str) -> Tuple[Dict[str, Any], bool]:
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

    # 更新經緯度
    coordinates_updated, (longitude, latitude) = update_coordinates(new_event)
    if coordinates_updated:
        new_event['longitude'] = longitude
        new_event['latitude'] = latitude

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
        has_changes = coordinates_updated  # 如果經緯度有更新，就標記為有變更

        # 檢查欄位變更
        for field in ['activity_name', 'description', 'organizer', 'address',
                     'start_date', 'end_date', 'location',
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

    return new_event, coordinates_updated

def save_events_to_json(events_data: List[Dict[str, Any]]) -> None:
    """將活動資料轉換成 JSON 格式並儲存"""
    if not events_data:
        print("警告: 沒有活動資料可儲存")
        return

    try:
        formatted_events = []
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        json_path = CONFIG['paths']['json']
        coordinates_update_count = 0  # 經緯度更新計數

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
            is_new_event = existing_event is None

            # 處理活動欄位
            new_event, coordinates_updated = process_event_fields(event, is_new_event, existing_event, current_time)
            if coordinates_updated:
                coordinates_update_count += 1
            formatted_events.append(new_event)

        # 寫入 JSON 檔案
        print(f"處理的活動數量: {len(formatted_events)}")
        print(f"更新經緯度數量: {coordinates_update_count}")

        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(formatted_events, f, ensure_ascii=False, indent=2)
        print(f'成功: 活動資料已儲存至 {json_path}')

    except Exception as e:
        print(f"錯誤: 儲存 JSON 檔案失敗 - {str(e)}")

def check_events_data_exists() -> bool:
    """檢查資料庫中是否已存在活動資料"""
    try:
        connection = connect_to_mysql()
        cursor = connection.cursor()

        try:
            # 檢查資料表中是否有資料
            cursor.execute("SELECT COUNT(*) FROM theme_events")
            count = cursor.fetchone()[0]
            return count > 0
        finally:
            cursor.close()
            connection.close()
    except Exception as e:
        print(f"檢查資料時發生錯誤: {str(e)}")
        return False

def load_existing_events() -> List[Dict[str, Any]]:
    """載入既有的 events_data.json 檔案"""
    try:
        json_path = CONFIG['paths']['json']
        if not os.path.exists(json_path):
            print(f"檔案不存在: {json_path}")
            return []

        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"讀取既有活動資料失敗: {str(e)}")
        return []

def update_events_data(existing_events: List[Dict[str, Any]], new_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """更新活動資料，使用 uid 作為唯一識別碼"""
    # 建立既有活動的 uid 索引
    existing_uids = {event['uid']: event for event in existing_events if event.get('uid')}

    # 更新或新增活動
    for new_event in new_events:
        uid = new_event.get('uid')
        if uid:  # 確保有有效的UID
            existing_uids[uid] = new_event

    return list(existing_uids.values())

def import_sql_to_database(connection: mysql.connector.connection.MySQLConnection, sql_file_path: str) -> Tuple[int, int]:
    """從SQL檔案匯入資料到資料庫，加強處理SQL語法問題"""
    cursor = connection.cursor()
    error_count = 0  # 計算錯誤次數
    activity_count = 0  # 實際匯入的活動數量

    try:
        # 讀取SQL檔案
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            sql_content = file.read()

        # 使用更可靠的分割方式
        commands = []
        current_command = []
        in_string = False
        escape_next = False
        string_char = None

        # 逐字符處理SQL內容
        for char in sql_content:
            if escape_next:
                current_command.append(char)
                escape_next = False
                continue

            if char == '\\':
                current_command.append(char)
                escape_next = True
                continue

            if not in_string and char in ["'", '"']:
                in_string = True
                string_char = char
                current_command.append(char)
                continue

            if in_string and char == string_char:
                in_string = False
                string_char = None
                current_command.append(char)
                continue

            if not in_string and char == ';':
                current_command.append(char)
                commands.append(''.join(current_command).strip())
                current_command = []
                continue

            current_command.append(char)

        # 處理最後一個指令
        if current_command:
            commands.append(''.join(current_command).strip())

        # 逐一執行SQL指令
        total_commands = len(commands)
        successful_commands = 0

        for i, command in enumerate(commands):
            # 跳過空指令或只包含註釋的指令
            if not command or command.strip().startswith('--'):
                continue

            try:
                cursor.execute(command)
                # 檢查是否為INSERT指令，並計算影響的行數
                if command.strip().upper().startswith('INSERT'):
                    activity_count += cursor.rowcount
                connection.commit()
                successful_commands += 1
            except Exception as e:
                error_count += 1
                connection.rollback()
                print(f"SQL指令執行錯誤 ({i+1}/{total_commands}): {str(e)}")
                print(f"問題指令: {command[:100]}...")

                # 嘗試修復並重試指令（替換特殊字符）
                try:
                    fixed_command = fix_sql_command(command)
                    if fixed_command != command:
                        cursor.execute(fixed_command)
                        # 同樣檢查是否為INSERT指令
                        if fixed_command.strip().upper().startswith('INSERT'):
                            activity_count += cursor.rowcount
                        connection.commit()
                        successful_commands += 1
                        print("修復後成功執行")
                        error_count -= 1
                except Exception as retry_error:
                    print(f"修復後仍失敗: {str(retry_error)}")

                # 如果錯誤過多，中斷執行
                if error_count > 10:
                    raise Exception(f"執行SQL指令時發生過多錯誤（超過10個），已中止匯入")

        print(f"成功執行 {successful_commands}/{total_commands} 個SQL指令")
        print(f"共匯入 {activity_count} 筆活動資料")

        return successful_commands, activity_count
    except Exception as e:
        connection.rollback()
        print(f"匯入SQL檔案時發生錯誤: {str(e)}")
        raise
    finally:
        cursor.close()

def fetch_api_with_timeout(api_func: Callable, api_name: str, api_timeout: Optional[int] = None) -> Tuple[bool, Any]:
    """
    使用逾時控制執行API呼叫的通用函式

    Args:
        api_func: 要執行的API函式
        api_name: API名稱（用於記錄日誌）
        api_timeout: 逾時時間（秒），若為None則不限時

    Returns:
        (success, result) - success表示是否成功，result為API結果或錯誤訊息
    """
    # 如果不啟用逾時機制，則直接執行API呼叫
    if api_timeout is None:
        try:
            print(f"正在取得{api_name}（無逾時限制）...")
            result = api_func()
            print(f"{api_name}取得完成！\n")
            return True, result
        except Exception as e:
            print(f"{api_name}取得失敗: {str(e)}\n")
            return False, None

    # 啟用逾時機制
    # 建立結果佇列
    result_queue = queue.Queue()

    # 定義執行緒函式
    def thread_func():
        try:
            result = api_func()
            result_queue.put(("success", result))
        except Exception as e:
            result_queue.put(("error", str(e)))

    # 啟動執行緒
    api_thread = threading.Thread(target=thread_func)
    api_thread.daemon = True
    api_thread.start()

    # 等待執行緒完成或逾時
    api_thread.join(timeout=api_timeout)

    # 檢查結果
    if not result_queue.empty():
        result_type, result = result_queue.get()
        if result_type == "success":
            print(f"{api_name}取得完成！\n")
            return True, result
        else:
            print(f"{api_name}取得失敗: {result}\n")
            return False, None
    else:
        print(f"{api_name}取得逾時（超過 {api_timeout} 秒），略過此API\n")
        return False, None

def fetch_all_api_data(api_timeout: Optional[int] = None) -> List[Dict[str, Any]]:
    """從所有API取得活動資料"""
    all_events = []
    api_success_count = 0
    api_fail_count = 0

    # 處理每個API來源
    for api_source in API_SOURCES:
        api_name = api_source['name']
        api_func = api_source['function']
        result_path = api_source.get('result_path', '')

        # print(f"正在取得{api_name}...")
        success, result = fetch_api_with_timeout(api_func, api_name, api_timeout)

        if success:
            # 根據result_path取得結果資料
            if result_path and isinstance(result, dict):
                result_data = result.get(result_path, [])
            elif isinstance(result, dict) and 'result' in result:
                result_data = result['result']
            else:
                result_data = result

            # 確保結果是列表
            if not isinstance(result_data, list):
                result_data = [result_data] if result_data else []

            # 更新活動資料
            if result_data:
                all_events = update_events_data(all_events, result_data)
                api_success_count += 1
            else:
                print(f"警告: {api_name}未返回有效資料")
                api_fail_count += 1
        else:
            api_fail_count += 1

    print(f"API呼叫統計: 成功={api_success_count}, 失敗={api_fail_count}")
    return all_events

def main() -> bool:
    """主程式進入點"""
    print(f"\n=== 開始執行資料取得程序 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    all_events = []  # 儲存所有活動資料

    try:
        # 檢查是否透過import_data.py執行（環境變數API_TIMEOUT存在）
        api_timeout_str = os.environ.get('API_TIMEOUT')
        if api_timeout_str:
            # 透過import_data.py執行，啟用API逾時機制
            try:
                api_timeout = int(api_timeout_str)
                print(f"以import_data.py模式執行，啟用API逾時機制: {api_timeout}秒")
            except ValueError:
                print(f"警告: API_TIMEOUT環境變數值'{api_timeout_str}'非有效整數，無法啟用逾時機制")
                api_timeout = None
        else:
            # 直接執行main.py，不啟用API逾時機制
            api_timeout = None
            print("以直接執行模式運行，API呼叫不設逾時限制")

        # 檢查既有資料
        if check_events_data_exists():
            print("發現既有活動資料，開始載入...")
            existing_events = load_existing_events()
            print(f"已載入 {len(existing_events)} 筆既有活動資料\n")
            all_events = existing_events

        # 從各 API 取得最新資料
        print("開始從各 API 取得最新資料...")
        api_events = fetch_all_api_data(api_timeout)
        if api_events:
            all_events = update_events_data(all_events, api_events)

        # 儲存活動資料
        print("開始處理和儲存活動資料...")
        if all_events:
            save_events_to_json(all_events)
            print("活動資料處理完成！\n")

            # 產生 SQL 檔案
            print("開始將 JSON檔 轉換為 SQL...")
            convert_json_to_sql(CONFIG['paths']['json'], CONFIG['paths']['sql'])
            print("成功: SQL 檔案已產生\n")
            return True
        else:
            print("警告: 未取得任何資料，無法產生JSON和SQL檔案\n")
            return False

    except Exception as e:
        print(f"\n執行過程中發生錯誤：{str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    main()
