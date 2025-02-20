from culture_api import CultureAPI
from tfam_api import TaipeiOpenDataAPI
from taipei_api import fetch_taipei_events as taipei_events
from newtaipei_api import fetch_newtaipei_events as newtaipei_events
import time
from datetime import datetime
import mysql.connector
import json
from typing import Dict, Any
import os


def init_database() -> None:
    """初始化資料庫和資料表"""
    connection = None
    cursor = None
    try:
        # 先建立與MySQL的連接（不指定資料庫）
        connection = mysql.connector.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            user=os.environ.get('DB_USER', 'root'),
            password=os.environ.get('DB_PASSWORD', 'P@ssw0rd')
        )
        cursor = connection.cursor(buffered=True)  # 使用 buffered cursor

        # 建立資料庫（如果不存在）
        cursor.execute("CREATE DATABASE IF NOT EXISTS fun")
        cursor.execute("USE fun")

        # 讀取並執行SQL檔案中的建表語句
        sql_file_path = os.path.join(
            os.path.dirname(__file__), 'create_tables.sql')
        with open(sql_file_path, 'r', encoding='utf-8') as file:
            # 分割SQL語句
            sql_commands = file.read().split(';')
            for command in sql_commands:
                if command.strip():
                    try:
                        cursor.execute(command)
                    except mysql.connector.Error as e:
                        # 如果是表已存在的錯誤，則忽略
                        if e.errno == 1050:  # Table already exists
                            continue
                        else:
                            raise

        # 建立索引（如果不存在）
        indexes = [
            ("theme_events", "idx_events_uid", "uid"),
            ("theme_events", "idx_events_start_date", "start_date"),
            ("theme_events", "idx_events_end_date", "end_date"),
            ("theme_import_dates", "idx_import_dates_date", "import_date"),
            ("theme_query_results", "idx_query_results_timestamp", "query_timestamp")
        ]

        for table, index_name, column in indexes:
            try:
                cursor.execute(
                    f"CREATE INDEX {index_name} ON {table}({column})")
                print(f"已建立索引：{index_name}")
            except mysql.connector.Error as e:
                if e.errno == 1061:  # 索引已存在
                    print(f"索引已存在：{index_name}")
                    continue
                else:
                    raise

        connection.commit()
        print("資料庫初始化成功！")
    except Exception as e:
        print(f"資料庫初始化失敗：{str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def connect_to_mysql() -> mysql.connector.connection.MySQLConnection:
    """建立MySQL資料庫連接"""
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'localhost'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'P@ssw0rd'),
        database="fun"
    )


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
    """將資料儲存到MySQL資料庫，檢查並更新已存在的資料"""
    if not data:
        return

    cursor = None
    try:
        cursor = connection.cursor(buffered=True)

        # 記錄匯入時間
        current_time = datetime.now()
        cursor.execute(
            "INSERT INTO theme_import_dates (import_date, timezone_type, timezone) VALUES (%s, %s, %s)",
            (current_time, 3, "Asia/Taipei")
        )
        import_id = cursor.lastrowid

        # 儲存查詢結果資訊
        if "result" in data:
            cursor.execute(
                "INSERT INTO theme_query_results (query_timestamp, limit_count, offset_count, total_count, sort_order) VALUES (%s, %s, %s, %s, %s)",
                (data.get("queryTime", current_time.strftime("%Y-%m-%d %H:%M:%S")),
                 data.get("limit", 0),
                 data.get("offset", 0),
                 data.get("total", 0),
                 data.get("sort", ""))
            )
            query_id = cursor.lastrowid

            # 儲存活動資訊
            for idx, event in enumerate(data["result"]):
                # 檢查是否已存在相同的活動
                cursor.execute(
                    """SELECT id, start_date, end_date, ticket_price,
                              related_link, image_url, address
                       FROM theme_events WHERE uid = %s""",
                    (event.get("uid", ""),)
                )
                existing_event = cursor.fetchone()

                # 處理日期格式
                start_date = parse_date(event.get("startDate"))
                end_date = parse_date(event.get("endDate"))

                updates = []

                if existing_event:
                    # 檢查是否需要更新
                    event_id, old_start_date, old_end_date, old_price, \
                        old_link, old_image, old_address = existing_event

                    values = []

                    # 檢查各欄位是否有更新
                    if start_date and start_date != old_start_date:
                        updates.append("start_date = %s")
                        values.append(start_date)

                    if end_date and end_date != old_end_date:
                        updates.append("end_date = %s")
                        values.append(end_date)

                    if event.get("price") and event.get("price") != old_price:
                        updates.append("ticket_price = %s")
                        values.append(event.get("price"))

                    if event.get("url") and event.get("url") != old_link:
                        updates.append("related_link = %s")
                        values.append(event.get("url"))

                    if event.get("imageUrl") and event.get("imageUrl") != old_image:
                        updates.append("image_url = %s")
                        values.append(event.get("imageUrl"))

                    if event.get("address") and event.get("address") != old_address:
                        updates.append("address = %s")
                        values.append(event.get("address"))

                    # 如果有需要更新的欄位
                    if updates:
                        values.append(event_id)
                        update_query = f"""UPDATE theme_events
                                         SET {', '.join(updates)}
                                         WHERE id = %s"""
                        cursor.execute(update_query, values)

                else:
                    # 如果活動不存在，則新增
                    cursor.execute(
                        """INSERT INTO theme_events
                        (uid, activity_name, description, organizer, address,
                         start_date, end_date, location, latitude, longitude,
                         ticket_price, related_link, image_url)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                        (event.get("uid", ""),
                         event.get("title", ""),
                         event.get("description", ""),
                         event.get("organizer", ""),
                         event.get("address", ""),
                         start_date,
                         end_date,
                         event.get("location", ""),
                         event.get("latitude", None),
                         event.get("longitude", None),
                         event.get("price", ""),
                         event.get("url", ""),
                         event.get("imageUrl", ""))
                    )
                    event_id = cursor.lastrowid

                # 建立查詢結果和活動的關聯（先檢查是否已存在）
                cursor.execute(
                    """SELECT query_id, event_id FROM theme_query_event_relations
                       WHERE query_id = %s AND event_id = %s""",
                    (query_id, event_id)
                )
                existing_relation = cursor.fetchone()

                if not existing_relation:
                    cursor.execute(
                        """INSERT INTO theme_query_event_relations
                           (query_id, event_id, display_order)
                           VALUES (%s, %s, %s)""",
                        (query_id, event_id, idx + 1)
                    )
                else:
                    # 如果關聯已存在，更新 display_order
                    cursor.execute(
                        """UPDATE theme_query_event_relations
                           SET display_order = %s
                           WHERE query_id = %s AND event_id = %s""",
                        (idx + 1, query_id, event_id)
                    )

        connection.commit()

    except Exception as e:
        connection.rollback()
        raise e
    finally:
        if cursor:
            cursor.close()


def main():
    print(
        f"\n=== 開始執行資料獲取程序 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

    connection = None
    try:
        # 初始化資料庫
        print("初始化資料庫...")
        init_database()
        print("資料庫初始化完成！\n")

        # 建立資料庫連接
        connection = connect_to_mysql()

        # 1. 執行文化部展演資訊 API
        print("1. 正在獲取文化部展演資訊...")
        culture_api = CultureAPI()
        culture_events = culture_api.get_events()
        # 儲存到MySQL
        save_to_mysql(culture_events, connection)
        print("文化部展演資訊獲取完成並儲存到資料庫！\n")

        integrated_events = culture_api.get_integrated_events()
        save_to_mysql(integrated_events, connection)
        print("文化部整合綜藝活動獲取完成並儲存到資料庫！\n")

        festival_events = culture_api.get_festival_events()
        save_to_mysql(festival_events, connection)
        print("文化部節慶活動獲取完成並儲存到資料庫！\n")

        # 2. 執行台北市立美術館 API
        print("2. 正在獲取台北市立美術館資訊...")
        tfam_api_1 = TaipeiOpenDataAPI()  # 展覽資訊
        tfam_api_2 = TaipeiOpenDataAPI(
            "1700a7e6-3d27-47f9-89d9-1811c9f7489c")  # 活動資訊

        # 獲取展覽資訊
        results_1 = tfam_api_1.fetch_data(limit=10)
        if results_1:
            save_to_mysql(results_1, connection)

        # 獲取活動資訊
        results_2 = tfam_api_2.fetch_data(limit=10)
        if results_2:
            save_to_mysql(results_2, connection)
        print("台北市立美術館資訊獲取完成並儲存到資料庫！\n")

        # 3. 執行台北市政府開放資料 API
        print("3. 正在獲取台北市政府活動資訊...")
        taipei_data = taipei_events()
        save_to_mysql(taipei_data, connection)
        print("台北市政府活動資訊獲取完成並儲存到資料庫！\n")

        # 4. 執行新北市政府開放資料 API
        print("4. 正在獲取新北市政府活動資訊...")
        newtaipei_data = newtaipei_events()
        save_to_mysql(newtaipei_data, connection)
        print("新北市政府活動資訊獲取完成並儲存到資料庫！\n")

        print(
            f"\n=== 所有資料獲取完成並儲存到資料庫 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")

    except Exception as e:
        print(f"\n執行過程中發生錯誤：{str(e)}")
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    main()
