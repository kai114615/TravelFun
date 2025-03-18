import json
import os
import re
import html
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

# 全域常數定義
HTML_ENTITIES = {
    '&quot;': '"',
    '&amp;': '&',
    '&lt;': '<',
    '&gt;': '>',
    '&apos;': "'"
}

DATE_FORMATS = [
    '%Y-%m-%d',      # 2023-01-01
    '%Y/%m/%d',      # 2023/01/01
    '%Y-%m-%d %H:%M:%S',  # 2023-01-01 12:00:00
    '%Y/%m/%d %H:%M:%S',  # 2023/01/01 12:00:00
    '%Y-%m-%dT%H:%M:%S',  # 2023-01-01T12:00:00
    '%Y-%m-%dT%H:%M:%S.%f',  # 2023-01-01T12:00:00.000
    '%Y-%m-%dT%H:%M:%S.%fZ'  # 2023-01-01T12:00:00.000Z
]

def read_json_file(file_path: str) -> Union[List[Dict[str, Any]], Dict[str, Any]]:
    """
    讀取JSON檔案並返回解析後的資料

    Args:
        file_path: JSON檔案路徑

    Returns:
        解析後的JSON資料，可能是字典或列表
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"錯誤: 找不到檔案 {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"錯誤: JSON解析失敗 - {str(e)}")
        return []
    except Exception as e:
        print(f"錯誤: 讀取JSON檔案時發生未知錯誤 - {str(e)}")
        return []

def escape_sql_special_chars(value: str) -> str:
    """
    對SQL特殊字元進行轉義處理

    Args:
        value: 要處理的字串

    Returns:
        處理後的字串
    """
    if not value or not isinstance(value, str):
        return value

    # 替換特殊字元
    replacements = {
        "'": "''",        # 單引號轉義
        "\\": "\\\\",     # 反斜線轉義
        "\r": "\\r",      # 回車符轉義
        "\n": "\\n",      # 換行符轉義
        "\t": "\\t"       # 制表符轉義
    }

    for char, replacement in replacements.items():
        value = value.replace(char, replacement)

    return value

def fix_sql_command(sql_command: str) -> str:
    """
    修復有問題的SQL指令，處理特殊字元和HTML實體

    Args:
        sql_command: 原始SQL指令

    Returns:
        處理後的SQL指令
    """
    if not sql_command:
        return sql_command

    # 清理HTML實體
    for entity, char in HTML_ENTITIES.items():
        sql_command = sql_command.replace(entity, char)

    # 使用html模組解碼可能的HTML實體
    sql_command = html.unescape(sql_command)

    # 移除多餘的空白
    sql_command = re.sub(r'\s+', ' ', sql_command)

    # 處理特殊字元
    sql_command = escape_sql_special_chars(sql_command)

    return sql_command

def format_value(value: Any) -> str:
    """
    格式化SQL值，將各種類型轉換為SQL字串

    Args:
        value: 要格式化的值

    Returns:
        SQL格式化後的字串
    """
    if value is None:
        return "NULL"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (list, dict)):
        # 將列表或字典轉為JSON字串
        json_str = json.dumps(value, ensure_ascii=False)
        return f"'{escape_sql_special_chars(json_str)}'"
    elif isinstance(value, str):
        return f"'{escape_sql_special_chars(value)}'"
    else:
        # 其他類型轉為字串
        return f"'{escape_sql_special_chars(str(value))}'"

def convert_datetime_format(date_str: Optional[str]) -> Optional[str]:
    """
    轉換多種日期格式為標準MySQL日期時間格式 (YYYY-MM-DD HH:MM:SS)

    Args:
        date_str: 日期字串

    Returns:
        標準格式的日期時間字串或None
    """
    if not date_str or date_str in ('', 'NULL', 'None', '無資料'):
        return None

    # 如果已經是標準MySQL格式，直接返回
    if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', date_str):
        return date_str

    # 嘗試各種日期格式
    for date_format in DATE_FORMATS:
        try:
            parsed_date = datetime.strptime(date_str, date_format)
            return parsed_date.strftime('%Y-%m-%d %H:%M:%S')
        except ValueError:
            continue

    # 如果是只有日期的格式，補上時間部分
    if re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return f"{date_str} 00:00:00"

    # 如果是只有日期的斜線格式，轉換並補上時間
    if re.match(r'^\d{4}/\d{1,2}/\d{1,2}$', date_str):
        parts = date_str.split('/')
        return f"{parts[0]}-{parts[1].zfill(2)}-{parts[2].zfill(2)} 00:00:00"

    # 處理失敗，返回None
    return None

def process_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    處理單個活動資料，確保資料欄位正確

    Args:
        event: 原始活動資料

    Returns:
        處理後的活動資料
    """
    # 欄位標準化
    processed_event = {
        "uid": event.get("uid", ""),
        "activity_name": event.get("activity_name", ""),
        "description": event.get("description", ""),
        "organizer": event.get("organizer", ""),
        "address": event.get("address", ""),
        "start_date": convert_datetime_format(event.get("start_date")),
        "end_date": convert_datetime_format(event.get("end_date")),
        "location": event.get("location", ""),
        "latitude": event.get("latitude"),
        "longitude": event.get("longitude"),
        "ticket_price": event.get("ticket_price", ""),
        "source_url": event.get("source_url", ""),
        "image_url": event.get("image_url", []),
        "created_at": event.get("created_at"),
        "updated_at": event.get("updated_at")
    }

    # 處理圖片URL，確保為JSON格式
    if isinstance(processed_event["image_url"], str):
        try:
            # 嘗試解析JSON字串
            processed_event["image_url"] = json.loads(processed_event["image_url"])
        except json.JSONDecodeError:
            # 如果不是有效的JSON字串，轉為列表
            processed_event["image_url"] = [processed_event["image_url"]] if processed_event["image_url"] else []

    # 處理經緯度，確保為浮點數或NULL
    for coord in ["latitude", "longitude"]:
        if isinstance(processed_event[coord], str) and processed_event[coord]:
            try:
                processed_event[coord] = float(processed_event[coord])
            except ValueError:
                processed_event[coord] = None

    return processed_event

def generate_upsert_sql(event: Dict[str, Any]) -> str:
    """
    生成插入或更新SQL語句

    Args:
        event: 處理後的活動資料

    Returns:
        插入或更新SQL語句
    """
    processed_event = process_event_data(event)

    # 處理圖片URL，轉為JSON格式儲存
    image_url = processed_event["image_url"]
    if image_url and not isinstance(image_url, str):
        image_url_json = json.dumps(image_url, ensure_ascii=False)
    else:
        image_url_json = '[]'

    # 生成欄位列表和值列表
    columns = [
        "uid", "activity_name", "description", "organizer", "address",
        "start_date", "end_date", "location", "latitude", "longitude",
        "ticket_price", "source_url", "image_url", "created_at", "updated_at"
    ]

    values = [
        format_value(processed_event["uid"]),
        format_value(processed_event["activity_name"]),
        format_value(processed_event["description"]),
        format_value(processed_event["organizer"]),
        format_value(processed_event["address"]),
        format_value(processed_event["start_date"]),
        format_value(processed_event["end_date"]),
        format_value(processed_event["location"]),
        format_value(processed_event["latitude"]),
        format_value(processed_event["longitude"]),
        format_value(processed_event["ticket_price"]),
        format_value(processed_event["source_url"]),
        f"'{image_url_json}'",
        format_value(processed_event["created_at"]),
        format_value(processed_event["updated_at"])
    ]

    # 生成SQL語句
    columns_str = ", ".join(columns)
    values_str = ", ".join(values)

    # UPSERT 語法 (MySQL)
    update_parts = [f"{col} = VALUES({col})" for col in columns if col != "uid"]
    update_str = ", ".join(update_parts)

    sql = f"""INSERT INTO theme_events ({columns_str}) VALUES ({values_str})
    ON DUPLICATE KEY UPDATE {update_str};"""

    return sql

def convert_json_to_sql(json_file_path: str, sql_file_path: str) -> int:
    """
    將JSON檔案轉換為SQL檔案

    Args:
        json_file_path: JSON檔案路徑
        sql_file_path: SQL檔案輸出路徑

    Returns:
        處理的活動數量
    """
    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(sql_file_path), exist_ok=True)

    # 讀取JSON檔案
    print(f"讀取JSON檔案: {json_file_path}")
    data = read_json_file(json_file_path)

    if not data:
        print("錯誤: JSON檔案為空或解析失敗")
        return 0

    # 確定資料格式 (列表或字典)
    events = data if isinstance(data, list) else data.get('result', [])

    if not events:
        print("錯誤: 找不到活動資料")
        return 0

    # 生成SQL語句
    sql_commands = []
    for event in events:
        try:
            sql_command = generate_upsert_sql(event)
            sql_commands.append(sql_command)
        except Exception as e:
            print(f"錯誤: 處理活動資料失敗 - {str(e)}")
            continue

    # 寫入SQL檔案
    try:
        with open(sql_file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(sql_commands))

        event_count = len(sql_commands)
        print(f"成功: 已將 {event_count} 筆活動資料轉換為SQL指令")
        return event_count
    except Exception as e:
        print(f"錯誤: 寫入SQL檔案失敗 - {str(e)}")
        return 0

def main():
    """主程式進入點"""
    convert_json_to_sql(CONFIG['paths']['data']['json'],
                       CONFIG['paths']['data']['sql'])

if __name__ == "__main__":
    main()
