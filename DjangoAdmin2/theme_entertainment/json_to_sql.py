import json
import os
from datetime import datetime
from typing import List, Dict, Any

def read_json_file(file_path: str) -> List[Dict[str, Any]]:
    """讀取 JSON 檔案"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"讀取 JSON 檔案時發生錯誤: {str(e)}")
        return []

def format_value(value: Any) -> str:
    """格式化 SQL 值"""
    if value is None or value == '':
        return 'NULL'
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return '1' if value else '0'
    elif isinstance(value, str):
        # 特別處理日期時間欄位
        if any(field in value for field in ['created_at', 'updated_at']):
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return f"'{dt.strftime('%Y-%m-%d %H:%M:%S')}'"
            except ValueError:
                pass
        # 處理日期欄位
        elif any(field in value for field in ['start_date', 'end_date']):
            try:
                dt = datetime.strptime(value, '%Y-%m-%d %H:%M:%S')
                return f"'{dt.strftime('%Y-%m-%d')}'"  # 只返回日期部分
            except ValueError:
                pass
        # 處理其他字串中的特殊字元
        return f"'{value.replace("'", "''").replace('\\', '\\\\').replace('\n', '\\n').replace('\r', '\\r')}'"
    else:
        return f"'{str(value)}'"

def convert_datetime_format(date_str: str) -> str:
    """轉換日期時間格式為 MySQL 格式"""
    if not date_str or date_str == 'NULL':
        return 'NULL'

    try:
        # 處理不同的日期時間格式
        formats = [
            '%Y-%m-%d %H:%M:%S',  # 2025-02-22 19:55:46
            '%Y-%m-%d',           # 2025-02-22
            '%Y/%m/%d %H:%M:%S',  # 2025/02/22 19:55:46
            '%Y/%m/%d'            # 2025/02/22
        ]

        for fmt in formats:
            try:
                dt = datetime.strptime(date_str, fmt)
                # 只返回日期部分
                return f"'{dt.strftime('%Y-%m-%d')}'"
            except ValueError:
                continue

        return 'NULL'
    except Exception:
        return 'NULL'

def generate_insert_sql(table_name: str, data: Dict[str, Any]) -> str:
    """生成插入 SQL 語句"""
    columns = []
    values = []

    for key, value in data.items():
        columns.append(key)
        values.append(format_value(value))

    columns_str = ', '.join(columns)
    values_str = ', '.join(values)

    return f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"

def generate_update_sql(table_name: str, data: Dict[str, Any], uid: str) -> str:
    """生成更新 SQL 語句"""
    updates = []

    for key, value in data.items():
        if key != 'uid':  # 不更新 uid
            updates.append(f"{key} = {format_value(value)}")

    updates_str = ', '.join(updates)

    return f"UPDATE {table_name} SET {updates_str} WHERE uid = {format_value(uid)};"

def generate_upsert_sql(table_name: str, data: Dict[str, Any]) -> str:
    """生成 UPSERT SQL 語句"""
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

def convert_json_to_sql(json_file_path: str, output_file_path: str) -> None:
    """將 JSON 檔案轉換為 SQL 檔案"""
    events_data = read_json_file(json_file_path)
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

            # 生成每個事件的 SQL
            for event in events_data:
                # 準備資料
                event_data = {
                    'uid': event.get('uid'),
                    'activity_name': event.get('activity_name'),
                    'description': event.get('description'),
                    'organizer': event.get('organizer'),
                    'address': event.get('address'),
                    'start_date': event.get('start_date'),
                    'end_date': event.get('end_date'),
                    'location': event.get('location'),
                    'latitude': event.get('latitude'),
                    'longitude': event.get('longitude'),
                    'ticket_price': event.get('ticket_price'),
                    'source_url': event.get('source_url'),
                    'image_url': event.get('image_url'),
                    'created_at': event.get('created_at'),
                    'updated_at': event.get('updated_at')
                }

                # 生成 UPSERT SQL
                sql = generate_upsert_sql('theme_events', event_data)
                f.write(f"{sql}\n")

            # 寫入 SQL 檔案結尾
            f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")

        print(f"SQL 檔案已生成: {output_file_path}")

    except Exception as e:
        print(f"生成 SQL 檔案時發生錯誤: {str(e)}")

def main():
    """主程式"""
    # 設定檔案路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, 'events_data.json')
    sql_file = os.path.join(current_dir, 'events_data.sql')

    # 執行轉換
    convert_json_to_sql(json_file, sql_file)

if __name__ == "__main__":
    main()