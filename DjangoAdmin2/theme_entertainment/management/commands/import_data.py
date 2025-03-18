from django.core.management.base import BaseCommand
import os
import sys
import mysql.connector
import time
from datetime import datetime

# 設定專案根目錄路徑
current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django_root = os.path.dirname(current_dir)  # DjangoAdmin2 目錄
project_dir = os.path.dirname(django_root)  # TravelFun 專案根目錄

# 設定路徑以導入其他模組
if current_dir not in sys.path:
    sys.path.append(current_dir)

# 設定資料庫連線設定
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),  # 資料庫主機位址
    'user': os.environ.get('DB_USER', 'root'),      # 資料庫使用者名稱
    'password': os.environ.get('DB_PASSWORD', 'P@ssw0rd'),  # 資料庫密碼
    'database': 'fun'  # 資料庫名稱
}

# 設定檔案路徑與API逾時預設值
CONFIG = {
    'paths': {
        'json': os.path.join(project_dir, 'src', 'assets', 'theme_entertainment', 'events_data.json'),
        'sql': os.path.join(current_dir, 'events_data.sql')  # SQL 檔案存放路徑
    },
    'api': {
        'default_timeout': 10  # 預設API逾時時間（秒）
    }
}

class TimeoutError(Exception):
    """自定義逾時錯誤"""
    pass

class Command(BaseCommand):
    help = '將JSON資料轉換為SQL並匯入MySQL資料庫'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='強制重新匯入資料，即使已經存在',
        )
        parser.add_argument(
            '--timeout',
            type=int,
            default=300,
            help='整體執行逾時時間（秒），預設300秒，設為0表示不限時',
        )
        parser.add_argument(
            '--api-timeout',
            type=int,
            default=CONFIG['api']['default_timeout'],
            help=f'單一API呼叫逾時時間（秒），預設{CONFIG["api"]["default_timeout"]}秒',
        )

    def handle(self, *args, **options):
        # 取得命令列參數
        force = options['force']
        overall_timeout = options['timeout']
        api_timeout = options['api_timeout']

        # 設定API逾時環境變數（必須在導入main模組前設定）
        os.environ['API_TIMEOUT'] = str(api_timeout)

        self.stdout.write(self.style.SUCCESS('開始匯入資料...'))
        self.stdout.write(self.style.SUCCESS(f'設定API呼叫逾時時間: {api_timeout}秒'))

        try:
            # 匯入必要模組
            from theme_entertainment.main import check_events_data_exists, connect_to_mysql
            from theme_entertainment.main import main, import_sql_to_database, load_existing_events

            # 檢查是否已存在資料（除非強制重新匯入）
            if not force and check_events_data_exists():
                events_count = len(load_existing_events())
                self.stdout.write(self.style.SUCCESS(f"events_data.json 已有 {events_count} 筆資料，跳過匯入。使用 --force 參數強制重新匯入。"))
                return

            # 記錄開始時間
            start_time = time.time()

            # 1. 執行main()函式，從各API取得資料、轉換為JSON和SQL
            self.stdout.write(self.style.SUCCESS('執行主程式，從API取得最新資料...'))
            main_result = main()

            if not main_result:
                self.stdout.write(self.style.ERROR('主程式執行失敗，未能取得或處理資料'))
                return

            # 檢查是否超過整體逾時時間
            if overall_timeout > 0 and (time.time() - start_time) > overall_timeout:
                raise TimeoutError(f"整體執行時間超過 {overall_timeout} 秒")

            # 2. 建立資料庫連線
            self.stdout.write(self.style.SUCCESS('正在連線至資料庫...'))
            connection = connect_to_mysql()

            # 3. 執行SQL匯入
            self.stdout.write(self.style.SUCCESS('正在匯入SQL資料至MySQL...'))
            successful_commands, activity_count = import_sql_to_database(connection, CONFIG['paths']['sql'])
            self.stdout.write(self.style.SUCCESS(f'成功執行 {successful_commands} 個SQL指令，匯入 {activity_count} 筆活動資料'))

            # 4. 關閉資料庫連線
            connection.close()

            self.stdout.write(self.style.SUCCESS('資料匯入完成！'))

        except TimeoutError as e:
            self.stdout.write(self.style.ERROR(f'執行逾時: {str(e)}'))
            return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'匯入資料時發生錯誤: {str(e)}'))
            raise