from django.core.management.base import BaseCommand
import os
import sys
import mysql.connector
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

# 設定檔案路徑
CONFIG = {
    'paths': {
        'json': os.path.join(project_dir, 'src', 'assets', 'theme_entertainment', 'events_data.json'),
        'sql': os.path.join(current_dir, 'events_data.sql')  # SQL 檔案存放路徑
    }
}

class Command(BaseCommand):
    help = '將JSON資料轉換為SQL並匯入MySQL資料庫'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='強制重新匯入資料，即使已經存在',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('開始匯入資料...'))

        force = options['force']

        try:
            # 匯入必要模組
            from theme_entertainment.main import check_events_data_exists, connect_to_mysql
            from theme_entertainment.main import main, import_sql_to_database, load_existing_events

            # 檢查是否已存在資料（除非強制重新匯入）
            if not force and check_events_data_exists():
                self.stdout.write(self.style.SUCCESS(f"events_data.json 已有 {len(load_existing_events())} 筆資料，跳過匯入。使用 --force 參數強制重新匯入。"))
                return

            # 1. 執行main()函數，從各API獲取資料、轉換為JSON和SQL
            self.stdout.write(self.style.SUCCESS('執行主程式，從API獲取最新資料...'))
            main()

            # 2. 建立資料庫連線
            self.stdout.write(self.style.SUCCESS('正在連接資料庫...'))
            connection = connect_to_mysql()

            # 3. 執行SQL匯入
            self.stdout.write(self.style.SUCCESS('正在匯入SQL資料到MySQL...'))
            import_sql_to_database(connection, CONFIG['paths']['sql'])

            # 4. 關閉資料庫連線
            connection.close()

            self.stdout.write(self.style.SUCCESS('資料匯入完成！'))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f'匯入資料時發生錯誤: {str(e)}'))
            raise