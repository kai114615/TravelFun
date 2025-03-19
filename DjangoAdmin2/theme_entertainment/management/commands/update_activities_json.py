import os
import json
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from theme_entertainment.models import EntertainmentActivity

class Command(BaseCommand):
    help = '手動更新前端的活動資料JSON檔案'

    def handle(self, *args, **options):
        self.stdout.write('開始更新前端活動JSON檔案...')

        # 取得所有活動
        activities = EntertainmentActivity.objects.all().order_by('id')

        # 準備JSON資料
        data = {
            "status": "success",
            "data": [],
            "total": activities.count(),
            "page": 1,
            "total_pages": (activities.count() // 10) + (1 if activities.count() % 10 > 0 else 0)
        }

        # 轉換活動資料
        for activity in activities:
            activity_data = {
                "id": activity.id,
                "activity_name": activity.title,
                "location": activity.location,
                "start_date": activity.start_time.isoformat() if activity.start_time else None,
                "end_date": activity.end_time.isoformat() if activity.end_time else None,
                "ticket_price": activity.price or "無資料"
            }
            data["data"].append(activity_data)

        # 前端資源目錄路徑 (從Django專案根目錄回到前端目錄)
        frontend_assets_dir = os.path.join(settings.BASE_DIR, '..', 'src', 'assets')

        # 確保目錄存在
        os.makedirs(frontend_assets_dir, exist_ok=True)

        # 寫入JSON檔案
        json_path = os.path.join(frontend_assets_dir, 'activities.json')
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4, cls=DjangoJSONEncoder)

        self.stdout.write(self.style.SUCCESS(f'已成功更新前端活動JSON檔案: {json_path}'))