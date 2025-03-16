import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# 設定專案根目錄路徑
current_dir = os.path.dirname(os.path.abspath(__file__))
django_root = os.path.dirname(current_dir)  # DjangoAdmin2 目錄
project_dir = os.path.dirname(django_root)  # TravelFun 專案根目錄

# 全域設定參數
CONFIG = {
    'paths': {
        'data': {
            'json': os.path.join(project_dir, 'src', 'assets', 'theme_entertainment', 'events_data.json'),
            'sql': os.path.join(current_dir, 'events_data.sql')  # SQL 檔案放在 theme_entertainment 目錄下
        }
    },
    'sql': {
        'table_name': 'theme_events',  # 資料表名稱
        'datetime_fields': ['start_date', 'end_date', 'created_at', 'updated_at'],  # 日期欄位清單
        'batch_size': 100  # 批次處理筆數
    }
}

def read_json_file(json_path: str) -> List[Dict[str, Any]]:
    # 讀取 JSON 檔案內容
    try:
        with open(json_path, 'r', encoding='utf-8-sig') as f:
            return json.load(f)
    except Exception as e:
        print(f"讀取 JSON 檔案時發生錯誤: {str(e)}")
        return []

def format_value(value: Any) -> str:
    # 格式化 SQL 值為適當的字串格式
    if value is None or value == '' or value == 'NULL':
        return 'NULL'

    # 處理數值型態
    if isinstance(value, (int, float)):
        return str(value)

    # 處理布林值
    if isinstance(value, bool):
        return '1' if value else '0'

    # 處理字串型態
    if isinstance(value, str):
        # 處理日期時間欄位
        if any(field in value for field in ['created_at', 'updated_at']):
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
            except ValueError:
                pass

        # 處理日期欄位
        if any(field in value for field in ['start_date', 'end_date']):
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return f"'{dt.strftime('%Y-%m-%d')}'"  # 只返回日期部分
            except ValueError:
                pass

        # 處理特殊字元跳脫
        # 特別處理可能導致SQL錯誤的字符
        escaped_value = value.replace("'", "''")  # 先處理單引號

        # 處理SQL註釋符號(雙連字符)
        escaped_value = escaped_value.replace('--', '\\-\\-')

        # 處理其他特殊字符
        special_chars = ['\\', '\n', '\r', '+', '%', '_']
        for char in special_chars:
            if char in escaped_value:
                escaped_value = escaped_value.replace(char, '\\' + char)

        return f"'{escaped_value}'"

    # 其他型態轉為字串
    return f"'{str(value)}'"

def convert_datetime_format(date_str: str) -> str:
    # 轉換日期時間格式為 MySQL 資料庫格式 (YYYY-MM-DD HH:MM:SS)
    if not date_str or date_str == 'NULL':
        return 'NULL'

    # 如果是已經格式化好的完整日期時間，直接返回
    if isinstance(date_str, str) and len(date_str) >= 19 and 'T' in date_str:
        try:
            # 處理 ISO 格式 (2023-06-15T14:30:00.000Z)
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
        except ValueError:
            pass  # 如果解析失敗，繼續嘗試其他格式

    # 定義支援的日期格式清單
    formats = [
        '%Y-%m-%d %H:%M:%S',  # 西元年-月-日 時:分:秒
        '%Y-%m-%dT%H:%M:%S',  # ISO 格式
        '%Y-%m-%d %H:%M',     # 西元年-月-日 時:分
        '%Y-%m-%d',           # 西元年-月-日
        '%Y/%m/%d %H:%M:%S',  # 西元年/月/日 時:分:秒
        '%Y/%m/%d %H:%M',     # 西元年/月/日 時:分
        '%Y/%m/%d'            # 西元年/月/日
    ]

    # 嘗試各種日期格式進行轉換
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            # 確保返回完整的日期時間格式
            if '%H' in fmt or '%T' in fmt:
                # 如果原始格式包含時間，保留完整時間
                return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
            else:
                # 如果原始格式只有日期，添加默認時間 00:00:00
                return f"'{dt.strftime('%Y-%m-%d')} 00:00:00'"
        except ValueError:
            continue
        except TypeError:
            # 處理非字符串類型
            try:
                if hasattr(date_str, 'strftime'):
                    # 如果是日期對象，直接格式化
                    return f"'{date_str.strftime('%Y-%m-%d %H:%M:%S')}'"
            except Exception:
                pass
            break

    # 如果所有格式都無法匹配，嘗試將其視為時間戳
    try:
        if isinstance(date_str, (int, float)):
            dt = datetime.fromtimestamp(date_str)
            return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
    except Exception:
        pass

    return 'NULL'

def generate_upsert_sql(table_name: str, data: Dict[str, Any]) -> str:
    # 生成 UPSERT SQL 語句（插入或更新資料）
    columns = []
    values = []
    updates = []

    # 記錄日期時間欄位清單
    datetime_fields = CONFIG.get('sql', {}).get('datetime_fields', [])

    # 處理每個欄位的資料
    for key, value in data.items():
        # 只處理資料不為 None 的欄位
        if value is not None:
            columns.append(f"`{key}`")

            # 特殊處理日期時間欄位
            if key in datetime_fields:
                # 確保日期時間格式正確
                formatted_value = convert_datetime_format(value)
                values.append(formatted_value)
                updates.append(f"`{key}`={formatted_value}")
            else:
                # 一般數據類型
                values.append(format_value(value))
                updates.append(f"`{key}`={format_value(value)}")

    # 忽略沒有資料的情況
    if not columns:
        return ""

    # 生成 SQL 語句
    sql = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({', '.join(values)})"

    # 如果需要更新，添加 ON DUPLICATE KEY UPDATE 子句
    if updates:
        sql += f" ON DUPLICATE KEY UPDATE {', '.join(updates)}"
    sql += ";"

    return sql

def process_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    # 處理活動資料，轉換為標準格式
    # 處理圖片網址：若為列表則合併，若為空則設為空字串
    image_url = event.get('image_url')
    if isinstance(image_url, list) and image_url:
        image_url = ','.join(image_url)
    elif not image_url or image_url == 'None':
        image_url = ''

    # 處理經緯度資料
    latitude = event.get('latitude')
    longitude = event.get('longitude')

    # 處理無效的經緯度值
    if latitude in ['無資料', 'None', ''] or not latitude:
        latitude = 'NULL'
    if longitude in ['無資料', 'None', ''] or not longitude:
        longitude = 'NULL'

    # 回傳標準化的活動資料結構
    return {
        'uid': event.get('uid'),
        'activity_name': event.get('activity_name'),
        'description': event.get('description'),
        'organizer': event.get('organizer'),
        'address': event.get('address'),
        'start_date': event.get('start_date'),
        'end_date': event.get('end_date'),
        'location': event.get('location'),
        'latitude': latitude,
        'longitude': longitude,
        'ticket_price': event.get('ticket_price'),
        'source_url': event.get('source_url'),
        'image_url': image_url,
        'created_at': event.get('created_at'),
        'updated_at': event.get('updated_at')
    }

def convert_json_to_sql(json_path: str, output_file_path: str) -> None:
    # 將 JSON 檔案轉換為 SQL 檔案
    # 讀取 JSON 資料
    events_data = read_json_file(json_path)
    if not events_data:
        return

    try:
        # 開啟輸出檔案
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # 寫入 SQL 檔案標頭資訊
            f.write("-- 自動生成的 SQL 檔案\n")
            f.write(f"-- 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 設定 MySQL 環境參數
            f.write("SET NAMES utf8mb4;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
            f.write("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';\n")
            f.write("SET time_zone = '+00:00';\n\n")

            # 處理每筆活動資料並生成 SQL
            for event in events_data:
                event_data = process_event_data(event)
                sql = generate_upsert_sql(CONFIG['sql']['table_name'], event_data)
                f.write(f"{sql}\n")

            # 寫入 SQL 檔案結尾設定
            f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")

        print(f"SQL 檔案已生成: {output_file_path}")

    except Exception as e:
        print(f"生成 SQL 檔案時發生錯誤: {str(e)}")

def main():
    # 主程式進入點
    convert_json_to_sql(CONFIG['paths']['data']['json'],
                       CONFIG['paths']['data']['sql'])

if __name__ == "__main__":
    main()
