import os
import json
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from django.core.serializers.json import DjangoJSONEncoder
from django.forms.models import model_to_dict
from .models import Events

@receiver([post_save, post_delete], sender=Events)
def update_activities_json(sender, instance=None, created=False, **kwargs):
    """
    當娛樂活動模型有變更時(新增、修改、刪除)，自動更新前端JSON檔案
    """
    # 取得所有活動
    activities = Events.objects.all().order_by('id')

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

    print(f"已更新前端活動JSON檔案: {json_path}")