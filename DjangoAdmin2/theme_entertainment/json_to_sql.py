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

# 全域設定參數
CONFIG = {
    'sql': {
        'table_name': 'theme_events',  # 資料表名稱
        'datetime_fields': ['start_date', 'end_date', 'created_at', 'updated_at'],  # 日期欄位清單
    }
}

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
    # 處理空值情況
    if value is None:
        return 'NULL'

    # 處理空字串和特殊字串值
    if isinstance(value, str):
        if value.strip() == '' or value.lower() == 'null' or value.lower() == 'none':
            return "''"  # 返回空字串，而不是 NULL

        # 處理URL和特殊字元 - 保證所有單引號被正確轉義
        escaped_value = value.replace("'", "''").replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
        return f"'{escaped_value}'"

    # 處理數值型態
    if isinstance(value, (int, float)):
        return str(value)

    # 處理布林值
    if isinstance(value, bool):
        return '1' if value else '0'

    # 處理其他型態 (包括列表、字典等)
    try:
        # 如果是可JSON序列化的物件，轉換為JSON字串
        if isinstance(value, (list, dict)):
            json_str = json.dumps(value, ensure_ascii=False)
            return f"'{json_str.replace("'", "''")}'"

        # 其他情況轉為字串
        return f"'{str(value).replace("'", "''")}'"
    except:
        # 如果轉換失敗，返回空字串
        return "''"

def convert_datetime_format(date_str: str) -> str:
    """轉換日期時間格式為 MySQL 格式"""
    if not date_str or date_str == 'NULL' or date_str == 'None':
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

    # 如果所有格式都無法匹配，返回 NULL
    return 'NULL'

def process_event_data(event: Dict[str, Any]) -> Dict[str, Any]:
    """
    處理單個活動資料，確保資料欄位正確

    Args:
        event: 原始活動資料

    Returns:
        處理後的活動資料
    """
    # 處理圖片URL
    image_url = event.get('image_url')
    if isinstance(image_url, list) and image_url:
        # 如果是列表，轉換為逗號分隔的字串
        image_url = ','.join(str(url) for url in image_url if url)
    elif not image_url or image_url == 'None' or image_url == 'NULL':
        # 如果是空值，設為空字串
        image_url = ''

    # 處理經緯度資料
    latitude = event.get('latitude')
    longitude = event.get('longitude')

    # 處理無效的經緯度值
    if latitude in ['無資料', 'None', 'NULL', ''] or not latitude:
        latitude = None
    else:
        try:
            latitude = float(latitude)
        except (ValueError, TypeError):
            latitude = None

    if longitude in ['無資料', 'None', 'NULL', ''] or not longitude:
        longitude = None
    else:
        try:
            longitude = float(longitude)
        except (ValueError, TypeError):
            longitude = None

    # 回傳標準化的活動資料結構
    return {
        'uid': event.get('uid'),
        'activity_name': event.get('activity_name', ''),
        'description': event.get('description', ''),
        'organizer': event.get('organizer', ''),
        'address': event.get('address', ''),
        'start_date': event.get('start_date'),
        'end_date': event.get('end_date'),
        'location': event.get('location', ''),
        'latitude': latitude,
        'longitude': longitude,
        'ticket_price': event.get('ticket_price', ''),
        'source_url': event.get('source_url', ''),
        'image_url': image_url,
        'created_at': event.get('created_at'),
        'updated_at': event.get('updated_at')
    }

def generate_upsert_sql(table_name: str, data: Dict[str, Any]) -> str:
    """生成 UPSERT SQL 語句（插入或更新資料）

    改進版：
    1. 只處理非空值欄位
    2. 根據欄位類型特殊處理日期時間值
    3. 使用簡潔的 SQL 語法
    """
    columns = []
    values = []
    updates = []

    # 處理每個欄位的資料
    for key, value in data.items():
        # uid 是必須的欄位，其他欄位可選
        if key == 'uid' or value is not None:
            columns.append(f"`{key}`")

            # 特殊處理日期時間欄位
            if key in CONFIG['sql']['datetime_fields'] and value:
                formatted_value = convert_datetime_format(str(value))
                values.append(formatted_value)

                if key != 'uid':  # uid 是主鍵，不需要更新
                    updates.append(f"`{key}`={formatted_value}")
            else:
                formatted_value = format_value(value)
                values.append(formatted_value)

                if key != 'uid':  # uid 是主鍵，不需要更新
                    updates.append(f"`{key}`={formatted_value}")

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

def convert_json_to_sql(json_file_path: str, output_file_path: str) -> None:
    """將 JSON 檔案轉換為 SQL 檔案

    改進版：
    1. 添加更完整的 SQL 檔案標頭和尾部
    2. 使用 process_event_data 預處理資料
    3. 提供更詳細的進度與錯誤資訊
    """
    events_data = read_json_file(json_file_path)
    if not events_data:
        print("沒有找到活動資料，無法生成 SQL 檔案")
        return

    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            # 寫入 SQL 檔案標頭
            f.write("-- 自動生成的主題育樂活動 SQL 檔案\n")
            f.write(f"-- 生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- 資料筆數: {len(events_data)}\n\n")

            # 設定 MySQL 環境參數
            f.write("SET NAMES utf8mb4;\n")
            f.write("SET FOREIGN_KEY_CHECKS = 0;\n")
            f.write("SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';\n")
            f.write("SET time_zone = '+08:00';\n\n")  # 台灣時區

            # 處理每筆活動資料
            successful_events = 0
            for event in events_data:
                # 預處理活動資料
                event_data = process_event_data(event)

                # 生成 SQL 語句
                sql = generate_upsert_sql(CONFIG['sql']['table_name'], event_data)

                # 只寫入有效的 SQL 語句
                if sql:
                    f.write(f"{sql}\n")
                    successful_events += 1

            # 寫入 SQL 檔案結尾設定
            f.write("\nSET FOREIGN_KEY_CHECKS = 1;\n")

            print(f"SQL 檔案已生成: {output_file_path}")
            print(f"成功處理 {successful_events}/{len(events_data)} 筆活動資料")

    except Exception as e:
        print(f"生成 SQL 檔案時發生錯誤: {str(e)}")

def main():
    """主程式"""
    # 設定檔案路徑
    current_dir = os.path.dirname(os.path.abspath(__file__))
    django_root = os.path.dirname(current_dir)  # DjangoAdmin2 目錄
    project_dir = os.path.dirname(django_root)  # TravelFun 專案根目錄

    # 正確的 JSON 檔案路徑在 src/assets 目錄下
    json_file = os.path.join(project_dir, 'src', 'assets', 'theme_entertainment', 'events_data.json')
    sql_file = os.path.join(current_dir, 'events_data.sql')

    print(f"JSON 檔案路徑: {json_file}")
    print(f"SQL 檔案路徑: {sql_file}")

    # 執行轉換
    convert_json_to_sql(json_file, sql_file)

if __name__ == "__main__":
    main()
