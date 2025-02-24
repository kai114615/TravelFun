import json
import os
from datetime import datetime
from typing import List, Dict, Any, Optional

# 設定專案根目錄
current_dir = os.path.dirname(os.path.abspath(__file__))
django_root = os.path.dirname(current_dir)  # DjangoAdmin2 目錄
project_dir = os.path.dirname(django_root)  # TravelFun 專案根目錄

# 全域設定
CONFIG = {
    'paths': {
        'data': {
            'json': os.path.join(project_dir, 'src', 'assets', 'theme_entertainment', 'events_data.json'),
            # SQL 檔案放在 theme_entertainment 目錄下
            'sql': os.path.join(current_dir, 'events_data.sql')
        }
    },
    'sql': {
        'table_name': 'theme_events',
        'date_fields': ['start_date', 'end_date', 'created_at', 'updated_at'],
        'batch_size': 100
    }
}

def read_json_file(json_path: str) -> List[Dict[str, Any]]:
    """讀取 JSON 檔案"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"讀取 JSON 檔案時發生錯誤: {str(e)}")
        return []

def format_value(value: Any) -> str:
    """
    格式化 SQL 值

    Args:
        value: 要格式化的值

    Returns:
        str: 格式化後的 SQL 值字串
    """
    if value is None or value == '' or value == 'NULL':
        return 'NULL'

    if isinstance(value, (int, float)):
        return str(value)

    if isinstance(value, bool):
        return '1' if value else '0'

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

        # 處理特殊字元
        return f"'{value.replace("'", "''").replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')}'"

    return f"'{str(value)}'"

def convert_datetime_format(date_str: str) -> str:
    """
    轉換日期時間格式為 MySQL 格式

    Args:
        date_str: 日期時間字串

    Returns:
        str: MySQL 格式的日期時間字串
    """
    if not date_str or date_str == 'NULL':
        return 'NULL'

    formats = [
        '%Y-%m-%d %H:%M:%S',  # 2025-02-22 19:55:46
        '%Y-%m-%d',           # 2025-02-22
        '%Y/%m/%d %H:%M:%S',  # 2025/02/22 19:55:46
        '%Y/%m/%d'            # 2025/02/22
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return f"'{dt.strftime('%Y-%m-%d')}'"
        except ValueError:
            continue

    return 'NULL'

def generate_upsert_sql(table_name: str, data: Dict[str, Any]) -> str:
    """
    生成 UPSERT SQL 語句

    Args:
        table_name: 資料表名稱
        data: 要插入的資料

    Returns:
        str: UPSERT SQL 語句
    """
    columns = []
    values = []
    updates = []

    for key, value in data.items():
        columns.append(f"`{key}`")

        # 根據欄位類型處理值
        if key in ['start_date', 'end_date'] and value:
            formatted_value = convert_datetime_format(str(value))
        else:
            formatted_value = format_value(value)

        values.append(formatted_value)

        if key != 'uid':  # 不更新 uid
            updates.append(f"`{key}` = new.`{key}`")

    columns_str = ', '.join(columns)
    values_str = ', '.join(values)
    updates_str = ', '.join(updates)

    return f"""INSERT INTO `{table_name}` ({columns_str})
            VALUES ({values_str}) AS new
            ON DUPLICATE KEY UPDATE {updates_str};"""

def process_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    處理事件資料，轉換格式

    Args:
        event: 原始事件資料

    Returns:
        Dict[str, Any]: 處理後的事件資料
    """
    # 處理 image_url
    image_url = event.get('image_url')
    if isinstance(image_url, list) and image_url:
        image_url = ','.join(image_url)
    elif not image_url or image_url == 'None':
        image_url = ''

    # 處理座標
    latitude = event.get('latitude')
    longitude = event.get('longitude')

    # 處理無效值
    if latitude in ['無資料', 'None', ''] or not latitude:
        latitude = 'NULL'
    if longitude in ['無資料', 'None', ''] or not longitude:
        longitude = 'NULL'

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
    """
    將 JSON 檔案轉換為 SQL 檔案

    Args:
        json_path: JSON 檔案路徑
        output_file_path: 輸出的 SQL 檔案路徑
    """
    events_data = read_json_file(json_path)
    if not events_data:
        return

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # 寫入 SQL 檔案標頭
            f.write("-- 自動生成的 SQL 檔案\n")
            f.write(f"-- 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            # 設定 MySQL 環境
            f.write("SET NAMES utf8mb4;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
            f.write("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';\n")
            f.write("SET time_zone = '+00:00';\n\n")

            # 處理每個事件並生成 SQL
            for event in events_data:
                event_data = process_event_data(event)
                sql = generate_upsert_sql(CONFIG['sql']['table_name'], event_data)
                f.write(f"{sql}\n")

            # 寫入 SQL 檔案結尾
            f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")

        print(f"SQL 檔案已生成: {output_file_path}")

    except Exception as e:
        print(f"生成 SQL 檔案時發生錯誤: {str(e)}")

def main():
    """主程式"""
    convert_json_to_sql(CONFIG['paths']['data']['json'],
                       CONFIG['paths']['data']['sql'])

if __name__ == "__main__":
    main()
